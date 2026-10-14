#!/usr/bin/env python3
"""leetcode-srs — spaced-repetition trainer for LeetCode-style interviews.

The point is *recall*, not volume. You re-derive solutions cold; the scheduler
spaces each item by how well you did, and treats lapses (failing to recall) as
the signal of what to practice next.

Item kinds:
  ds       data-structure recall card (API + complexity)
  pattern  signal -> tool decision drill (no coding)
  problem  a LeetCode problem to RE-SOLVE from memory

Quick start:
  ./srs.py init        # create db + load seed content
  ./srs.py today       # what's due
  ./srs.py review      # run a session
  ./srs.py stats       # progress + your weak spots (high-lapse items)

Grading during review (what you press):
  w  Wrong     confidently stated a WRONG answer         -> hardest reset
               (worse than blanking — you'd have shipped it in an interview)
  b  Blanked   couldn't recall the approach            -> resets, comes back tomorrow
  h  Hard      got it, but only after a hint / a slog   -> short interval
  g  Good      solved cold with normal friction         -> interval grows
  e  Easy      fast and clean                            -> interval grows a lot

Hints (press ? at any reveal/solve prompt):
  Reveals one random fragment of the answer to spark the rest of your recall.
  Each hint you take caps the grade you can claim (1 hint -> max Good, 2+ -> max
  Hard), so a hinted item comes back sooner. Grabbing a hint is fine; it just
  costs points, which is the honest signal.

Overwhelm control:
  A session is capped (see --max-problems / --max-cards) and NEW items are held
  back while you have a backlog due. Faceplanting no longer snowballs: the queue
  holds the overflow and stops adding new problems until you've drained it.
"""
import argparse
import os
import random
import re
import shutil
import sqlite3
import subprocess
import sys
import textwrap
from datetime import date, timedelta

DB_PATH = os.path.expanduser("~/.local/share/leetcode-srs/srs.db")
TODAY = date.today()

GRADE_KEYS = {"w": 0, "b": 1, "h": 3, "g": 4, "e": 5}
GRADE_LABEL = {0: "Wrong (sure of it)", 1: "Blanked", 3: "Hard", 4: "Good", 5: "Easy"}

DEFAULT_NEW_PROBLEMS = 3
DEFAULT_NEW_CARDS = 6
DEFAULT_MAX_PROBLEMS = 8      # hardest work; keep a session humane
DEFAULT_MAX_CARDS = 20        # cards are fast, allow more
NEW_PROBLEM_GATE = 6          # >= this many problems already due -> no new ones
NEW_CARD_GATE = 15            # >= this many cards already due    -> no new ones

# ---- ANSI niceties (no deps) ----------------------------------------------
def _c(code):
    return f"\033[{code}m" if sys.stdout.isatty() else ""
BOLD, DIM, RED, GRN, YEL, CYN, MAG, RST = (
    _c(1), _c(2), _c(31), _c(32), _c(33), _c(36), _c(35), _c(0))


# ---- DB --------------------------------------------------------------------
def connect():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    return con


def init_schema(con):
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS items (
            id           INTEGER PRIMARY KEY,
            kind         TEXT NOT NULL,         -- ds | pattern | problem
            title        TEXT NOT NULL,         -- problem name, or card front
            back         TEXT,                  -- card back (NULL for problems)
            url          TEXT,
            pattern      TEXT,
            difficulty   TEXT,
            insight      TEXT,                  -- your derivation note
            ease         REAL NOT NULL DEFAULT 2.5,
            interval     INTEGER NOT NULL DEFAULT 0,
            reps         INTEGER NOT NULL DEFAULT 0,
            lapses       INTEGER NOT NULL DEFAULT 0,
            due_date     TEXT,                  -- ISO date; NULL = new/unscheduled
            last_reviewed TEXT,
            created      TEXT NOT NULL,
            UNIQUE(kind, title)
        );
        CREATE TABLE IF NOT EXISTS log (
            id      INTEGER PRIMARY KEY,
            item_id INTEGER NOT NULL,
            ts      TEXT NOT NULL,
            grade   INTEGER NOT NULL,
            seconds INTEGER,
            hints   INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY(item_id) REFERENCES items(id)
        );
        """
    )
    # migrate older DBs that predate the hints column
    have = {r["name"] for r in con.execute("PRAGMA table_info(log)")}
    if "hints" not in have:
        con.execute("ALTER TABLE log ADD COLUMN hints INTEGER NOT NULL DEFAULT 0")
    # hint = nudge shown by `?` (never the answer); why = reminder shown after reveal
    have = {r["name"] for r in con.execute("PRAGMA table_info(items)")}
    for col in ("hint", "why"):
        if col not in have:
            con.execute(f"ALTER TABLE items ADD COLUMN {col} TEXT")
    con.commit()


def import_seed(con):
    """Load seed_data: add new items, refresh card text/hints in place, give
    problems their pattern nudge, and retire ds/pattern cards no longer in the
    seed (problems are never removed). Existing schedules are untouched."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import seed_data as s

    added = 0
    cur = con.cursor()
    def ins(kind, title, back=None, url=None, pattern=None, difficulty=None,
            hint=None, why=None):
        nonlocal added
        try:
            cur.execute(
                "INSERT INTO items(kind,title,back,url,pattern,difficulty,hint,why,created)"
                " VALUES(?,?,?,?,?,?,?,?,?)",
                (kind, title, back, url, pattern, difficulty, hint, why, TODAY.isoformat()),
            )
            added += 1
        except sqlite3.IntegrityError:
            # already present: keep its schedule, but refresh the card text
            cur.execute("UPDATE items SET back=?, hint=?, why=? WHERE kind=? AND title=?",
                        (back, hint, why, kind, title))

    for c in s.DS_CARDS:
        ins("ds", c["front"], back=c["back"], pattern="data-structures",
            hint=c.get("hint"), why=c.get("why"))
    for c in s.PATTERN_CARDS:
        ins("pattern", c["front"], back=c["back"], pattern="pattern-decision",
            hint=c.get("hint"), why=c.get("why"))
    for title, slug, pattern, diff in s.PROBLEMS:
        nudge = s.PATTERN_NUDGES.get(pattern)
        try:
            cur.execute(
                "INSERT INTO items(kind,title,url,pattern,difficulty,hint,created)"
                " VALUES('problem',?,?,?,?,?,?)",
                (title, f"https://leetcode.com/problems/{slug}/", pattern, diff, nudge,
                 TODAY.isoformat()))
            added += 1
        except sqlite3.IntegrityError:
            cur.execute("UPDATE items SET hint=? WHERE kind='problem' AND title=?",
                        (nudge, title))

    # retire cards that the seed no longer defines (their review log goes with them)
    keep = {("ds", c["front"]) for c in s.DS_CARDS} | \
           {("pattern", c["front"]) for c in s.PATTERN_CARDS}
    stale = [r for r in cur.execute(
        "SELECT id, kind, title FROM items WHERE kind IN ('ds','pattern')").fetchall()
        if (r["kind"], r["title"]) not in keep]
    for r in stale:
        cur.execute("DELETE FROM log WHERE item_id=?", (r["id"],))
        cur.execute("DELETE FROM items WHERE id=?", (r["id"],))
    if stale:
        print(f"{DIM}  retired {len(stale)} old card(s) replaced by the new deck{RST}")
    con.commit()
    return added


# ---- SM-2 scheduling -------------------------------------------------------
def schedule(row, q):
    """Return (ease, interval, reps, lapses, due_date) after grading with q."""
    ease, interval, reps, lapses = row["ease"], row["interval"], row["reps"], row["lapses"]
    if q < 3:                       # lapse: this is the signal we want to surface
        reps = 0
        interval = 1                # back tomorrow
        lapses += 1
    else:
        if reps == 0:
            interval = 1
        elif reps == 1:
            interval = 3
        else:
            interval = max(1, round(interval * ease))
        reps += 1
    ease = max(1.3, ease + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02)))
    due = (TODAY + timedelta(days=interval)).isoformat()
    return ease, interval, reps, lapses, due


def apply_grade(con, item_id, q, seconds=None, hints=0):
    row = con.execute("SELECT * FROM items WHERE id=?", (item_id,)).fetchone()
    ease, interval, reps, lapses, due = schedule(row, q)
    con.execute(
        "UPDATE items SET ease=?,interval=?,reps=?,lapses=?,due_date=?,last_reviewed=?"
        " WHERE id=?",
        (ease, interval, reps, lapses, due, TODAY.isoformat(), item_id),
    )
    con.execute("INSERT INTO log(item_id,ts,grade,seconds,hints) VALUES(?,?,?,?,?)",
                (item_id, TODAY.isoformat(), q, seconds, hints))
    con.commit()
    return interval


# ---- queue building --------------------------------------------------------
def due_items(con, kind):
    return con.execute(
        "SELECT * FROM items WHERE kind=? AND due_date IS NOT NULL AND due_date<=?"
        " ORDER BY due_date, lapses DESC",
        (kind, TODAY.isoformat()),
    ).fetchall()


def new_items(con, kind, limit):
    return con.execute(
        "SELECT * FROM items WHERE kind=? AND due_date IS NULL ORDER BY id LIMIT ?",
        (kind, limit),
    ).fetchall()


def build_queue(con, new_problems, new_cards, max_problems, max_cards, cram=False):
    """Assemble a session, capped and backlog-gated so faceplanting can't snowball.

    Returns (cards, problems, info) where info explains what was held back:
      info = {deferred_cards, deferred_problems, new_gated, due_cards, due_problems}
    """
    due_cards = due_items(con, "ds") + due_items(con, "pattern")
    due_probs = due_items(con, "problem")

    # gate NEW items while a backlog is due — drain what you have before piling on
    add_cards = new_cards if (cram or len(due_cards) < NEW_CARD_GATE) else 0
    add_probs = new_problems if (cram or len(due_probs) < NEW_PROBLEM_GATE) else 0

    cap_cards = len(due_cards) if cram else max_cards
    cap_probs = len(due_probs) if cram else max_problems

    # warm up the decision procedure first: ds + pattern cards, then problems
    cards = due_cards[:cap_cards]
    cards += new_items(con, "ds", add_cards // 2)
    cards += new_items(con, "pattern", add_cards - add_cards // 2)
    problems = due_probs[:cap_probs]
    problems += new_items(con, "problem", add_probs)

    info = {
        "due_cards": len(due_cards),
        "due_problems": len(due_probs),
        "deferred_cards": max(0, len(due_cards) - cap_cards),
        "deferred_problems": max(0, len(due_probs) - cap_probs),
        # "gated" only if you WANTED new items but the backlog suppressed them
        "new_gated": (new_problems > 0 and add_probs == 0)
                     or (new_cards > 0 and add_cards == 0),
    }
    return cards, problems, info


# ---- hints -----------------------------------------------------------------
def grade_cap(hints):
    """Best grade you may claim after taking `hints` hints.
    0 -> 5 (Easy ok), 1 -> 4 (Good), 2+ -> 3 (Hard). Never caps below Hard;
    a full blank is always yours to declare honestly."""
    return max(3, 5 - hints)


class Hinter:
    """Hands out hint tiers in order and counts how many you took.

    A tier is a nudge that points at the answer without containing it (the
    card's `hint`; for problems the pattern nudge, then the pattern name, then
    your own note). Empty tiers are skipped. The answer itself is never a hint."""
    def __init__(self, tiers):
        self.chunks = [t.strip() for t in tiers if t and t.strip()]
        self.used = 0

    def reveal(self):
        if self.used >= len(self.chunks):
            return None
        frag = self.chunks[self.used]
        self.used += 1
        return frag

    def status(self):
        """Short inline label for the prompt, e.g. '(1 hint, costs points)'."""
        if not self.chunks:
            return ""
        if self.used == 0:
            n = len(self.chunks)
            return f"{DIM}(? = hint, {n} available, costs points){RST}"
        left = len(self.chunks) - self.used
        cap = GRADE_LABEL[grade_cap(self.used)]
        return f"{YEL}({self.used} hint(s), {left} left, grade capped at {cap}){RST}"


def offer_hint(hinter):
    """Print the next fragment; return True if one was shown."""
    frag = hinter.reveal()
    if frag is None:
        print(f"{DIM}    (no more hints){RST}")
        return False
    print(f"{YEL}    hint: {frag}{RST}")
    return True


# ---- review session --------------------------------------------------------
def wrap(text, indent="    "):
    return "\n".join(textwrap.fill(line, 76, initial_indent=indent,
                                   subsequent_indent=indent)
                     for line in text.splitlines())


def ask_grade(prompt="  grade [w]rong-but-sure [b]lanked [h]ard [g]ood [e]asy"
                     "  (s=skip q=quit): ",
              cap=5):
    while True:
        raw = input(prompt).strip().lower()
        if raw in ("q", "quit"):
            return "quit"
        if raw in ("s", "skip", ""):
            return "skip"
        if raw in GRADE_KEYS:
            q = GRADE_KEYS[raw]
            if q > cap:
                print(f"{DIM}    (capped at {GRADE_LABEL[cap]} — you took hints){RST}")
                q = cap
            return q
        print("    (press w, b, h, g, e, s, or q — w = you were confident AND wrong)")


def review_card(con, row):
    tag = "DS" if row["kind"] == "ds" else "PATTERN"
    print(f"\n{MAG}{BOLD}[{tag}]{RST} {BOLD}{row['title']}{RST}")
    hinter = Hinter([row["hint"]])
    while True:
        ans = input(f"{DIM}  ...recall it. Enter to reveal · {RST}"
                    f"{hinter.status()}{DIM} > {RST}").strip().lower()
        if ans in ("?", "hint"):
            offer_hint(hinter)
            continue
        break
    print(f"{GRN}{wrap(row['back'])}{RST}")
    if row["why"]:
        print(f"{DIM}{wrap(row['why'])}{RST}")
    q = ask_grade(cap=grade_cap(hinter.used))
    if q == "quit":
        return "quit"
    if q == "skip":
        return "skip"
    iv = apply_grade(con, row["id"], q, hints=hinter.used)
    print(f"{DIM}  {GRADE_LABEL[q]} -> next in {iv}d{RST}")
    return "done"


def run_coach(row):
    """Ask the student for their intended approach, then have Gemma compare it
    to the known-correct pattern and coach. Best-effort: silent on failure."""
    import coach as _coach
    approach = input(
        f"{CYN}  Before coding, state your approach in a sentence "
        f"(pattern + key idea + complexity), or Enter to skip the coach:\n  > {RST}"
    ).strip()
    if not approach:
        return
    print(f"{DIM}  asking Gemma...{RST}", end="", flush=True)
    res = _coach.check_approach(
        row["title"], row["difficulty"], row["pattern"], approach)
    print("\r" + " " * 24 + "\r", end="")  # wipe the 'asking' line
    if not res:
        print(f"{DIM}  (coach unavailable — Ollama not responding; carry on){RST}")
        return
    mark = {"on_track": f"{GRN}✓ on track{RST}",
            "partial": f"{YEL}~ partial{RST}",
            "off_track": f"{RED}✗ off track{RST}"}[res["verdict"]]
    print(f"  coach: {mark}")
    if res["feedback"]:
        print(f"{wrap(res['feedback'])}")
    if res["watch_out"]:
        print(f"{YEL}{wrap('watch out: ' + res['watch_out'])}{RST}")


def open_in_nvim(url):
    """Spawn a new kitty window with nvim opened straight to this problem.

    Relies on the `:LeetSlug <slug>` command defined in the nvim leetcode.nvim
    spec. Best-effort: prints why and carries on if anything's missing."""
    if not url:
        print(f"{DIM}  (no url on this item to open){RST}")
        return
    m = re.search(r"/problems/([^/?#]+)", url)
    if not m:
        print(f"{DIM}  (couldn't parse a slug from {url}){RST}")
        return
    slug = m.group(1)
    if not shutil.which("kitty"):
        print(f"{DIM}  (kitty not on PATH — open manually: nvim -c 'LeetSlug {slug}'){RST}")
        return
    try:
        # `kitty <prog> [args]` launches prog in a fresh window instead of a shell.
        subprocess.Popen(
            ["kitty", "nvim", "-c", f"LeetSlug {slug}"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        print(f"{GRN}  opening {slug} in nvim…{RST} {DIM}(solve there, come back to grade){RST}")
    except OSError as e:
        print(f"{DIM}  (couldn't launch nvim: {e}){RST}")


def review_problem(con, row, coach_on=False):
    diff = row["difficulty"] or ""
    dcol = {"Easy": GRN, "Medium": YEL, "Hard": RED}.get(diff, "")
    print(f"\n{CYN}{BOLD}[PROBLEM]{RST} {BOLD}{row['title']}{RST}  {dcol}{diff}{RST}")
    print(f"{DIM}  {row['url']}{RST}")
    if row["lapses"]:
        print(f"{RED}  (you've blanked on this {row['lapses']}x — focus here){RST}")
    if coach_on:
        run_coach(row)
    print(f"{DIM}  Now solve it COLD: commit to the plan, then code it. "
          f"No peeking until you're done.{RST}")
    # hint tiers: a nudge that doesn't name the tool, then the pattern, then your note
    hinter = Hinter([row["hint"],
                     f"pattern: {row['pattern']}" if row["pattern"] else None,
                     f"your note: {row['insight']}" if row["insight"] else None])
    while True:
        ans = input(f"{DIM}  [o] open in nvim · [?] hint · Enter when done "
                    f"(reveal pattern + note){RST} {hinter.status()} ").strip().lower()
        if ans == "o":
            open_in_nvim(row["url"])
            continue
        if ans in ("?", "hint"):
            offer_hint(hinter)
            continue
        break
    print(f"  pattern: {YEL}{row['pattern']}{RST}")
    if row["insight"]:
        print(f"  your note:\n{GRN}{wrap(row['insight'])}{RST}")
    q = ask_grade("  graded on COLD recall — [w]rong-but-sure [b]lanked [h]ard "
                  "[g]ood [e]asy (s=skip q=quit): ", cap=grade_cap(hinter.used))
    if q == "quit":
        return "quit"
    if q == "skip":
        return "skip"
    iv = apply_grade(con, row["id"], q, hints=hinter.used)
    print(f"{DIM}  {GRADE_LABEL[q]} -> next in {iv}d{RST}")
    # capture the derivation insight, especially on a miss
    if q <= 3:
        ask = ("you were sure and wrong — what misled you, and what's the "
               "real trigger?" if q == 0 else "what trigger/insight did you miss?")
        note = input(f"{YEL}  {ask} (Enter to skip)\n  > {RST}").strip()
        if note:
            prev = row["insight"]
            merged = note if not prev else f"{prev}\n{note}"
            con.execute("UPDATE items SET insight=? WHERE id=?", (merged, row["id"]))
            con.commit()
    return "done"


def cmd_review(con, args):
    cards, problems, info = build_queue(
        con, args.new_problems, args.new_cards,
        args.max_problems, args.max_cards, cram=args.cram)
    if args.cards_only:
        problems = []
    if args.problems_only:
        cards = []
    queue = list(cards) + list(problems)
    if not queue:
        print(f"{GRN}Nothing due. Inbox zero.{RST} "
              f"Add problems with `srs.py add`, or come back tomorrow.")
        return
    coach_on = False
    if problems and not args.no_coach:
        import coach as _coach
        coach_on = _coach.available()
    coach_note = (f"{GRN}coach on ({_coach.MODEL.split(':')[0]}){RST}" if coach_on
                  else f"{DIM}coach off{RST}")
    print(f"{BOLD}Session:{RST} {len(cards)} cards + {len(problems)} problems "
          f"= {len(queue)} items. {DIM}Cards first to warm up the decision drill.{RST} "
          f"{coach_note}")
    # be transparent about what the throttle held back, so nothing feels "lost"
    deferred = info["deferred_problems"] + info["deferred_cards"]
    if deferred:
        bits = []
        if info["deferred_problems"]:
            bits.append(f"{info['deferred_problems']} problems")
        if info["deferred_cards"]:
            bits.append(f"{info['deferred_cards']} cards")
        print(f"{YEL}  Holding back {' + '.join(bits)} to keep this session "
              f"manageable.{RST} {DIM}Finish these, run `review` again for the next batch.{RST}")
    if info["new_gated"]:
        print(f"{DIM}  New items paused while you have a backlog — clear it and "
              f"they resume automatically. (--cram to override.){RST}")
    done = 0
    for row in queue:
        kind = row["kind"]
        result = review_card(con, row) if kind in ("ds", "pattern") \
            else review_problem(con, row, coach_on=coach_on)
        if result == "quit":
            break
        if result == "done":
            done += 1
    print(f"\n{BOLD}Done: {done} item(s) reviewed.{RST} Run `srs.py stats` to see progress.")


# ---- other commands --------------------------------------------------------
def counts(con):
    q = TODAY.isoformat()
    def n(sql, *a):
        return con.execute(sql, a).fetchone()[0]
    out = {}
    for k in ("ds", "pattern", "problem"):
        out[k] = {
            "due": n("SELECT COUNT(*) FROM items WHERE kind=? AND due_date IS NOT NULL AND due_date<=?", k, q),
            "new": n("SELECT COUNT(*) FROM items WHERE kind=? AND due_date IS NULL", k),
            "total": n("SELECT COUNT(*) FROM items WHERE kind=?", k),
        }
    return out


def cmd_today(con, args):
    c = counts(con)
    label = {"ds": "DS cards", "pattern": "Pattern cards", "problem": "Problems"}
    print(f"{BOLD}Due today ({TODAY.isoformat()}):{RST}")
    total_due = 0
    for k in ("ds", "pattern", "problem"):
        d, nw, tot = c[k]["due"], c[k]["new"], c[k]["total"]
        total_due += d
        print(f"  {label[k]:<14} {YEL}{d:>3} due{RST}  "
              f"{DIM}{nw} new available, {tot} total{RST}")
    if total_due:
        print(f"\n  -> {BOLD}{total_due} reviews waiting.{RST} Run `srs.py review`.")
        if c["problem"]["due"] > DEFAULT_MAX_PROBLEMS:
            print(f"  {DIM}(you'll get {DEFAULT_MAX_PROBLEMS} problems at a time — "
                  f"drain in batches, new items stay paused until it clears.){RST}")
    else:
        print(f"\n  {GRN}No reviews due.{RST} `srs.py review` will pull in new items.")


def cmd_stats(con, args):
    total = con.execute("SELECT COUNT(*) FROM log").fetchone()[0]
    studied = con.execute(
        "SELECT COUNT(*) FROM items WHERE last_reviewed IS NOT NULL").fetchone()[0]
    print(f"{BOLD}Overall:{RST} {total} reviews logged, {studied} items started.")

    # accuracy over last 30 days
    cutoff = (TODAY - timedelta(days=30)).isoformat()
    rows = con.execute("SELECT grade FROM log WHERE ts>=?", (cutoff,)).fetchall()
    if rows:
        good = sum(1 for r in rows if r["grade"] >= 4)
        missed = sum(1 for r in rows if r["grade"] < 3)
        sure_wrong = sum(1 for r in rows if r["grade"] == 0)
        print(f"{BOLD}Last 30d:{RST} {len(rows)} reviews — "
              f"{GRN}{good} clean{RST}, {RED}{missed} missed{RST} "
              f"({100*good//max(1,len(rows))}% clean recall).")
        if sure_wrong:
            print(f"{RED}         {sure_wrong} of those were confident wrong "
                  f"answers{RST} {DIM}— the ones that fail interviews silently; "
                  f"they come back hardest.{RST}")
    hinted = con.execute(
        "SELECT COUNT(*) FROM log WHERE ts>=? AND hints>0", (cutoff,)).fetchone()[0]
    if hinted:
        print(f"{DIM}         {hinted} of those leaned on a hint "
              f"(items you needed a nudge for come back sooner).{RST}")

    print(f"\n{BOLD}Your weak spots{RST} {DIM}(highest lapses — practice these){RST}:")
    weak = con.execute(
        "SELECT title, kind, pattern, lapses, interval FROM items "
        "WHERE lapses>0 ORDER BY lapses DESC, interval ASC LIMIT 12").fetchall()
    if not weak:
        print(f"  {DIM}none yet — lapses show up here once you start blanking on things{RST}")
    for r in weak:
        print(f"  {RED}{r['lapses']}x{RST}  {r['title']} "
              f"{DIM}[{r['pattern']}]{RST}")

    # weakest patterns by blank-rate
    print(f"\n{BOLD}Blank-rate by pattern{RST} {DIM}(problems only){RST}:")
    pats = con.execute(
        "SELECT i.pattern, "
        "  SUM(CASE WHEN l.grade<3 THEN 1 ELSE 0 END) blanks, COUNT(*) n "
        "FROM log l JOIN items i ON i.id=l.item_id "
        "WHERE i.kind='problem' GROUP BY i.pattern "
        "HAVING n>=2 ORDER BY 1.0*blanks/n DESC LIMIT 8").fetchall()
    if not pats:
        print(f"  {DIM}not enough data yet{RST}")
    for r in pats:
        rate = 100 * r["blanks"] // r["n"]
        bar = "█" * (rate // 10)
        print(f"  {r['pattern']:<22} {RED}{bar}{RST} {rate}% ({r['blanks']}/{r['n']})")


def cmd_add(con, args):
    url = args.url
    if not url and args.slug:
        url = f"https://leetcode.com/problems/{args.slug}/"
    try:
        con.execute(
            "INSERT INTO items(kind,title,url,pattern,difficulty,created) "
            "VALUES('problem',?,?,?,?,?)",
            (args.name, url, args.pattern, args.difficulty, TODAY.isoformat()))
        con.commit()
        print(f"{GRN}Added problem:{RST} {args.name}")
    except sqlite3.IntegrityError:
        print(f"{YEL}Already exists:{RST} {args.name}")


def cmd_addcard(con, args):
    try:
        con.execute(
            "INSERT INTO items(kind,title,back,pattern,hint,why,created) "
            "VALUES('pattern',?,?,?,?,?,?)",
            (args.front, args.back, "pattern-decision", args.hint, args.why,
             TODAY.isoformat()))
        con.commit()
        print(f"{GRN}Added pattern card.{RST}")
    except sqlite3.IntegrityError:
        print(f"{YEL}Already exists.{RST}")


def cmd_list(con, args):
    sql = "SELECT id,kind,title,pattern,difficulty,due_date,lapses,reps FROM items WHERE 1=1"
    a = []
    if args.kind:
        sql += " AND kind=?"; a.append(args.kind)
    if args.pattern:
        sql += " AND pattern LIKE ?"; a.append(f"%{args.pattern}%")
    if args.due:
        sql += " AND due_date IS NOT NULL AND due_date<=?"; a.append(TODAY.isoformat())
    sql += " ORDER BY kind, pattern, title"
    for r in con.execute(sql, a).fetchall():
        due = r["due_date"] or "new"
        print(f"  {r['id']:>3} {DIM}{r['kind']:<8}{RST} {r['title']:<48} "
              f"{DIM}{r['pattern'] or '':<18} due:{due} lapses:{r['lapses']}{RST}")


def cmd_note(con, args):
    row = con.execute("SELECT * FROM items WHERE id=?", (args.id,)).fetchone()
    if not row:
        print(f"{RED}No item #{args.id}{RST}"); return
    print(f"{BOLD}{row['title']}{RST}")
    if row["insight"]:
        print(f"{DIM}current note:{RST}\n{row['insight']}")
    new = args.text or input("new note (replaces): ").strip()
    if new:
        con.execute("UPDATE items SET insight=? WHERE id=?", (new, args.id))
        con.commit()
        print(f"{GRN}Saved.{RST}")


def cmd_init(con, args):
    init_schema(con)
    n = import_seed(con)
    c = counts(con)
    print(f"{GRN}Initialized{RST} at {DB_PATH}")
    print(f"  loaded {n} new items "
          f"({c['ds']['total']} DS cards, {c['pattern']['total']} pattern cards, "
          f"{c['problem']['total']} problems)")
    print(f"  next: {BOLD}./srs.py review{RST}")


def cmd_import(con, args):
    init_schema(con)
    n = import_seed(con)
    print(f"{GRN}Imported {n} new item(s){RST} (existing schedules untouched).")


# ---- CLI -------------------------------------------------------------------
def main():
    p = argparse.ArgumentParser(
        prog="srs.py", description="Spaced-repetition trainer for coding interviews.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init", help="create db and load seed content")
    sub.add_parser("import", help="(re)load seed_data.py, keeping existing schedules")
    sub.add_parser("today", help="show what's due")

    r = sub.add_parser("review", help="run a review session")
    r.add_argument("--new-problems", type=int, default=DEFAULT_NEW_PROBLEMS)
    r.add_argument("--new-cards", type=int, default=DEFAULT_NEW_CARDS)
    r.add_argument("--max-problems", type=int, default=DEFAULT_MAX_PROBLEMS,
                   help="cap problems per session (overflow held for next run)")
    r.add_argument("--max-cards", type=int, default=DEFAULT_MAX_CARDS,
                   help="cap cards per session")
    r.add_argument("--cram", action="store_true",
                   help="lift the session caps and new-item gating (drain everything)")
    r.add_argument("--cards-only", action="store_true")
    r.add_argument("--problems-only", action="store_true")
    r.add_argument("--no-coach", action="store_true",
                   help="disable the Gemma approach-checker")

    sub.add_parser("stats", help="progress + weak spots")

    a = sub.add_parser("add", help="add a problem")
    a.add_argument("name")
    a.add_argument("--slug", help="leetcode slug (builds the url)")
    a.add_argument("--url")
    a.add_argument("--pattern", default="")
    a.add_argument("--difficulty", default="")

    ac = sub.add_parser("addcard", help="add a pattern-decision card")
    ac.add_argument("front"); ac.add_argument("back")
    ac.add_argument("--hint", help="nudge shown by ? (must not contain the answer)")
    ac.add_argument("--why", help="reminder printed after the reveal")

    l = sub.add_parser("list", help="list items")
    l.add_argument("--kind", choices=["ds", "pattern", "problem"])
    l.add_argument("--pattern"); l.add_argument("--due", action="store_true")

    nt = sub.add_parser("note", help="edit an item's derivation note")
    nt.add_argument("id", type=int); nt.add_argument("text", nargs="?")

    args = p.parse_args()
    con = connect()
    init_schema(con)
    dispatch = {
        "init": cmd_init, "import": cmd_import, "today": cmd_today,
        "review": cmd_review, "stats": cmd_stats, "add": cmd_add,
        "addcard": cmd_addcard, "list": cmd_list, "note": cmd_note,
    }
    try:
        dispatch[args.cmd](con, args)
    except (KeyboardInterrupt, EOFError):
        print(f"\n{DIM}bye{RST}")


if __name__ == "__main__":
    main()
