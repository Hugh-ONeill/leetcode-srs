"""Gemma-backed 'state your approach before coding' checker.

Grounded design: we already KNOW the correct pattern for each problem (it's in
the db), so Gemma isn't asked to solve anything — only to compare the student's
stated approach against the known-correct technique and coach accordingly. That
keeps it from hallucinating a wrong 'answer'.

Stdlib only (urllib) so srs.py stays dependency-free. Mirrors the job-scan call
convention: think:false (Gemma's CoT is ~10x slower for the same output) and
keep_alive so the model stays resident between problems in a session.
"""
import json
import os
import urllib.error
import urllib.request

HOST = os.environ.get("SRS_OLLAMA_HOST", "http://localhost:11434")
MODEL = os.environ.get("SRS_COACH_MODEL", "gemma4:26b-a4b-it-q4_K_M")

SYSTEM = (
    "You are a terse coding-interview coach. The student states the approach "
    "they intend to use on a LeetCode problem BEFORE they write any code. You "
    "are privately told the correct technique. Compare their approach to it and "
    "coach them. Verdict rubric: 'on_track' = they identified the intended "
    "technique (right data structure / pattern and the right complexity class); "
    "'partial' = it would produce correct answers but is the WRONG technique or "
    "a worse complexity than intended (e.g. brute force when a hash map / two "
    "pointers / etc. is expected) — push them toward the intended technique's "
    "complexity; 'off_track' = the approach is wrong or wouldn't solve it. "
    "Hard rules: never write code; never hand them the full algorithm. On "
    "'partial'/'off_track' nudge with a leading question toward the right FAMILY "
    "of technique (e.g. 'what would let you find the complement in O(1)?'); only "
    "name the exact technique if they are completely lost. Do not pad. Respond "
    "with JSON only."
)

USER_TMPL = """Problem: {title} ({difficulty})
Correct technique (private ground truth — do not just blurt it back): {pattern}
Student's stated approach: {approach}

Respond ONLY with this JSON object:
{{"verdict": "on_track | partial | off_track",
  "feedback": "<= 2 sentences of coaching, no code, no full solution",
  "watch_out": "one pitfall or edge case to keep in mind, or empty string"}}"""


def available(timeout=1.5):
    """Quick reachability probe so review can silently skip the coach if Ollama
    is down."""
    try:
        with urllib.request.urlopen(f"{HOST}/api/tags", timeout=timeout) as r:
            return r.status == 200
    except (urllib.error.URLError, OSError):
        return False


def check_approach(title, difficulty, pattern, approach, timeout=90):
    """Return a dict {verdict, feedback, watch_out} or None on any failure.

    timeout is generous because the first call of a session may cold-load the
    17 GB model; keep_alive then keeps it warm for the rest.
    """
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": USER_TMPL.format(
                title=title, difficulty=difficulty or "?",
                pattern=pattern or "?", approach=approach)},
        ],
        "stream": False,
        "format": "json",
        "think": False,         # CoT is ~10x slower for the same JSON
        "keep_alive": "10m",    # stay resident across the session
        "options": {"temperature": 0.2, "num_ctx": 4096},
    }
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{HOST}/api/chat", data=data,
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = json.loads(r.read().decode())
        content = body.get("message", {}).get("content", "")
        obj = json.loads(content)
    except (urllib.error.URLError, OSError, json.JSONDecodeError, KeyError):
        return None
    verdict = str(obj.get("verdict", "")).strip().lower().replace(" ", "_")
    if verdict not in ("on_track", "partial", "off_track"):
        verdict = "partial"
    return {
        "verdict": verdict,
        "feedback": str(obj.get("feedback", "")).strip(),
        "watch_out": str(obj.get("watch_out", "")).strip(),
    }
