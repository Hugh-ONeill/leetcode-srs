#!/usr/bin/env bash
# Fired by the systemd user timer. Posts a PERSISTENT dunst notification (never
# expires) with the due count. Clicking the action opens a kitty window running
# the review session — i.e. clicking the reminder drops you straight into the
# thing you answer the questions in.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRS="$HERE/srs.py"

# how many reviews are waiting?
due=$("$SRS" today 2>/dev/null | grep -oE '[0-9]+ reviews waiting' | grep -oE '^[0-9]+')

if [ -n "${due:-}" ]; then
    body="$due reviews due. Click to start a session."
    urgency=normal
else
    body="No reviews due — new problems available. Click to practice anyway."
    urgency=low
fi

# -t 0  => never time out; the notification stays until you click or dismiss it.
# -A    => a clickable action; dunstify prints its key to stdout when invoked.
action=$(dunstify -u "$urgency" -t 0 -i applications-education \
    -A "default,Open review session" \
    "LeetCode SRS" "$body")

if [ "$action" = "default" ]; then
    # --hold keeps the window open after the session ends so you can read stats.
    exec kitty --hold -e "$SRS" review
fi
