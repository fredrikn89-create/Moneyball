#!/usr/bin/env python3
"""Henter poeng per spiller per runde fra FPLs offentlige API og skriver data/player_points.json.

Bare standardbiblioteket. Ingen innlogging. Pause mellom kallene og retry med økende ventetid.
Format: {"updated", "gw", "players": {id: [navn, lag, posisjon, [poeng runde 1..gw]]}}.
Poeng for en runde er summen av alle kamper den runden; null betyr ingen kamp.
"""
import json, sys, time, urllib.request, urllib.error
from datetime import datetime, timezone

BASE = "https://fantasy.premierleague.com/api/"
UA = "Moneyball-FPL/1.0 (hobbyliga; henter data en gang i døgnet)"
DELAY = 0.3


def get(path):
    for attempt in range(5):
        try:
            req = urllib.request.Request(BASE + path, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except (urllib.error.URLError, TimeoutError):
            if attempt == 4:
                raise
            time.sleep(2 ** attempt * 2)


def main(out):
    b = get("bootstrap-static/")
    finished = [e["id"] for e in b["events"] if e.get("finished")]
    cur = max(finished) if finished else 0
    teams = {t["id"]: t["short_name"] for t in b["teams"]}
    pos = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}
    players = {}
    for e in sorted(b["elements"], key=lambda x: x["id"]):
        if e["minutes"] == 0:
            continue
        time.sleep(DELAY)
        hist = get(f"element-summary/{e['id']}/")["history"]
        pts = [None] * cur
        for m in hist:
            r = m["round"]
            if 1 <= r <= cur:
                pts[r - 1] = (pts[r - 1] or 0) + m["total_points"]
        players[str(e["id"])] = [e["web_name"], teams[e["team"]], pos[e["element_type"]], pts]
    data = {"updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"), "gw": cur, "players": players}
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    print(f"Skrev {len(players)} spillere, runde 1-{cur}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/player_points.json")
