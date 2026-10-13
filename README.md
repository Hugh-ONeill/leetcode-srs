# leetcode-srs

A spaced-repetition trainer for LeetCode-style interviews. Built to fix the
specific failure mode of grinding NeetCode 150 and *still* blanking on problems
you've already done: that's a **recall** problem, and volume doesn't fix it.
Active recall + spacing + treating lapses as the signal does.

## The method this enforces

1. **Recall, not recognition.** You re-solve problems *cold* — state the
   approach from memory before looking. Re-reading solutions feels like
   learning but isn't.
2. **Spacing.** Each item comes back at an expanding interval (SM-2). Items you
   blank on reset and return tomorrow; items you nail drift weeks out.
3. **Two card types before problems.** Most interview panic is "I can't recall
   the *structure*" or "I don't know *which tool* this wants." Those are
   drilled directly:
   - **DS cards** — the API + complexity of each structure.
   - **Pattern cards** — a problem-shape on the front, the tool + why on the back.
   A review session warms up with these *before* you touch a problem.
4. **Log the derivation, not the code.** When you blank on a problem it asks
   what *trigger* you missed ("array was sorted → two pointers") and saves it.
   Next time, that note is your hint.

## Usage

```bash
./srs.py init        # one-time: create db + load seed (already done)
./srs.py today       # what's due
./srs.py review      # run a session (cards first, then problems)
./srs.py stats       # progress + your weak spots + blank-rate by pattern
```

Grading keys during review:

| key | meaning | effect |
|-----|---------|--------|
| `w` | **Wrong-but-sure** — confidently stated an answer that was wrong | hardest reset, back tomorrow |
| `b` | **Blanked** — couldn't recall the approach | resets, back tomorrow |
| `h` | **Hard** — got it after a hint/slog | short interval |
| `g` | **Good** — solved cold, normal friction | interval grows |
| `e` | **Easy** — fast and clean | interval grows a lot |

`s` skips, `q` quits the session (progress so far is saved).

**Why `w` is separate from `b`:** blanking is honest ignorance — you know you
don't know. A confident wrong answer is the failure mode that actually sinks
interviews, because nothing tells you to double-check. So `w` takes the biggest
ease penalty (SM-2 q=0 vs q=1): the item comes back tomorrow like a blank, but
its future intervals regrow slower, and `stats` counts these separately.

### Hints (press `?`)

At any reveal/solve prompt, press **`?`** to uncover one *random* fragment of
the answer. Randomized (not first-to-last) so it's a real partial cue that varies
each time, meant to spark the rest of your recall rather than hand you the answer.

Taking a hint costs points: it **caps the grade you can claim** — 1 hint → max
**Good**, 2+ → max **Hard**. That flows straight through the scheduler, so a
hinted item comes back sooner, exactly proportional to how much help you needed.
Grabbing a hint is fine and often worth it; the cap just keeps the signal honest.
`stats` shows how many recent reviews leaned on one.

### Overwhelm control (no more snowballing)

Blanking used to compound: lapsed problems reset to due-tomorrow *and* new ones
kept getting added, so a bad streak buried you. Now a session is **capped**
(default 8 problems / 20 cards, most-overdue first) and **new items are held
back while you have a backlog**. Faceplant → the queue holds the overflow and
stops adding new problems until you've drained it; then intake resumes on its
own. Each session tells you exactly what it held back — nothing is lost.

### Tuning a session

```bash
./srs.py review --new-problems 5      # pull in more new problems (default 3)
./srs.py review --max-problems 12     # bigger cap when you're fresh (default 8)
./srs.py review --max-cards 30        # cap on cards per session (default 20)
./srs.py review --cram                # lift the caps + gating: drain everything
./srs.py review --cards-only          # just drill DS + pattern cards
./srs.py review --problems-only       # skip cards
./srs.py review --no-coach            # disable the Gemma approach-checker
```

## Solving in nvim

When a problem comes up in a review, press **`o`** at the solve prompt to open
that exact problem in a fresh kitty + nvim window via
[leetcode.nvim](https://github.com/kawre/leetcode.nvim) — description in a split,
a `python3` code buffer, and `:Leet run` / `:Leet test` / `:Leet submit` against
LeetCode. Solve there, alt-tab back to the review window, and grade as usual.
(Pressing Enter instead reveals the pattern + your note, same as before; press
**`?`** for a hint — the pattern name, then your own past insight note, one
fragment at a time — at the cost of a capped grade.)

It opens straight to the problem (not the picker) through a custom `:LeetSlug
<slug>` command defined in the nvim spec; srs.py extracts the slug from the
stored URL and shells out `kitty nvim -c "LeetSlug <slug>"`.

**One-time setup:** sign in once inside nvim with `:Leet cookie update` (paste
your browser's `Cookie` *request* header). The description renders without it,
but run/submit need it. If kitty/nvim/the plugin isn't there, the keypress just
prints a fallback and the terminal flow is unchanged.

## The Gemma approach-checker

Before you code each problem, the review asks you to **state your approach in a
sentence** (pattern + key idea + complexity). Your local Gemma
(`gemma4:26b-a4b-it-q4_K_M` via Ollama) — given the problem's *known* correct
pattern as private ground truth — compares your stated approach to it and coaches
you, **without** writing code or handing you the solution:

- `✓ on track` — you picked the intended technique; it may flag one pitfall.
- `~ partial` — correct but wrong/suboptimal technique (e.g. brute force); it
  nudges you toward the intended complexity with a leading question.
- `✗ off track` — wrong direction; it points you at the right *family* of tool.

This catches wrong-pattern picks in 10 seconds instead of 20 minutes of coding
down a dead end. Press Enter at the approach prompt to skip the coach for a
problem. It's on by default when Ollama is reachable and **degrades silently**
if it isn't (no Ollama → the review just runs without it).

Config via env vars (defaults match your job-scan setup):

```bash
SRS_COACH_MODEL=gemma4:26b-a4b-it-q4_K_M   # interactive MoE; fast
SRS_OLLAMA_HOST=http://localhost:11434
```

Lives in `coach.py`; stdlib `urllib` only, `think:false` + `keep_alive=10m` so
the model stays warm across a session.

### Adding your own

```bash
./srs.py add "Spiral Matrix" --slug spiral-matrix --pattern "Arrays & Hashing" --difficulty Medium
./srs.py addcard "Front of the card" "Back of the card"
./srs.py note 32 "the insight I keep missing"
./srs.py list --kind problem --pattern Graphs
```

To add a batch, edit `seed_data.py` then `./srs.py import` — existing items and
their schedules are left untouched.

## Daily session

There is no reminder to click. A systemd **user** unit opens the day's review in
its own kitty window as soon as the morning job-scan report is written
(`job-scan.service` names it in `OnSuccess=`/`OnFailure=`, so it fires whichever
way the scan ends, usually between 07:10 and 07:35). The window sits at the
first prompt until you get to the keyboard, and the session is over before
you'd normally open a project. Close the window when you're done: while it is
open the unit counts as running and the next morning's trigger is a no-op.

```bash
systemctl --user start leetcode-srs-daily.service   # open a session now
systemctl --user status leetcode-srs-daily.service
```

The unit is `systemd/leetcode-srs-daily.service`, linked into
`~/.config/systemd/user/`. It replaced a 09:30 notification (2026-10-13) that
was dismissed every day because it landed mid-flow or after hours.


## Files

- `srs.py` — the whole engine (CLI, SM-2 scheduler, SQLite).
- `seed_data.py` — DS cards, pattern cards, and the problem backlog. Edit + `import`.
- `systemd/` — the daily-session unit (linked into `~/.config/systemd/user/`).
- DB lives at `~/.local/share/leetcode-srs/srs.db`.

## How to actually use it (the habit)

- **One short session a day** beats a weekend cram. 6 cards + 3 problems is ~30
  min and is the whole point.
- **Be honest grading.** "I eventually got it after peeking" is **Hard** at best,
  often **Blanked**. Inflating grades just hides the items you need. If you needed
  a nudge, take a `?` hint instead of peeking — it caps the grade for you.
- **Use `w` when the reveal surprises you.** If you committed to an answer and
  the reveal proved it wrong, that's **Wrong-but-sure**, not Blanked — and if the
  coach flags your stated approach `off_track` when you felt certain, believe it.
- **A backlog is a signal, not a debt.** If problems are piling up, you're being
  told to slow the intake, not grind harder. Let the gate hold new items; clear
  8 a day and it drains itself.
- **A problem isn't 'done' when you solve it once.** It's done when it's drifted
  weeks out because you keep re-deriving it cold.
- **Watch `stats`.** The blank-rate-by-pattern bars tell you which pattern to
  spend a focused weekend on.
