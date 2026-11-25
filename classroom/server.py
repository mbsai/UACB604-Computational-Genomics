#!/usr/bin/env python3
"""
UACB-604 live classroom server.

Runs on the teacher's laptop and serves the course slides over the classroom network.
Students join with their name; their screens follow the teacher's slide; answers to
games and quizzes are collected and shown on the projector.

Uses only the Python standard library (Python 3.8+). Start it with:

    python3 classroom/server.py

Then follow the instructions it prints.
"""
import argparse
import csv
import datetime as dt
import io
import json
import os
import re
import secrets
import socket
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------- shared state
COND = threading.Condition()
STATE = {"deck": None, "h": 0, "v": 0, "f": -1}
SEQ = [0]                      # bumps whenever something students/teacher should hear about
STUDENTS = {}                  # id -> {"name", "joined"}
ANSWERS = {}                   # (sid, deck, qid) -> record
CONFIG = {"key": None, "data_file": None, "url": None}


def bump():
    with COND:
        SEQ[0] += 1
        COND.notify_all()


def public_snapshot():
    """What every connected screen receives: where the teacher is and simple counts."""
    deck, h = STATE["deck"], STATE["h"]
    answered = {k[0] for k, a in ANSWERS.items() if a["deck"] == deck and a["slide"] == h}
    return dict(STATE, seq=SEQ[0], joined=len(STUDENTS), answered=len(answered))


def save():
    if not CONFIG["data_file"]:
        return
    data = {"students": STUDENTS, "answers": list(ANSWERS.values())}
    tmp = CONFIG["data_file"] + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(data, fh, indent=1)
    os.replace(tmp, CONFIG["data_file"])


def results_for(deck, slide=None):
    rows = [a for a in ANSWERS.values() if a["deck"] == deck and (slide is None or a["slide"] == slide)]
    questions = {}
    board = {}
    for a in sorted(rows, key=lambda r: r["time"]):
        q = questions.setdefault(a["qid"], {"qid": a["qid"], "label": a["label"], "right": [], "wrong": []})
        (q["right"] if a["correct"] else q["wrong"]).append(a["name"])
        b = board.setdefault(a["sid"], {"name": a["name"], "correct": 0, "attempted": 0})
        b["attempted"] += 1
        b["correct"] += 1 if a["correct"] else 0
    ranked = sorted(board.values(), key=lambda b: (-b["correct"], b["attempted"], b["name"].lower()))
    return {"students": len(STUDENTS), "questions": list(questions.values()), "board": ranked}


def list_lectures():
    out = []
    for unit in sorted(os.listdir(REPO)):
        udir = os.path.join(REPO, unit)
        if not (unit.startswith("unit") and os.path.isdir(udir)):
            continue
        for f in sorted(os.listdir(udir)):
            if re.match(r"^\d+\.\d+_.*\.html$", f):
                title = f
                with open(os.path.join(udir, f), encoding="utf-8") as fh:
                    m = re.search(r"<title>(.*?)</title>", fh.read(4000), re.S)
                    if m:
                        title = m.group(1).strip()
                out.append({"path": f"{unit}/{f}", "title": title})
    return out


# ---------------------------------------------------------------- HTTP handler
class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=REPO, **kw)

    def log_message(self, fmt, *args):  # keep the terminal quiet
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    # -- helpers
    def send_json(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def body_json(self):
        n = int(self.headers.get("Content-Length") or 0)
        try:
            return json.loads(self.rfile.read(n) or b"{}")
        except ValueError:
            return {}

    def is_teacher(self, q=None, body=None):
        k = (body or {}).get("key") or (q or {}).get("key", [None])[0]
        return k is not None and secrets.compare_digest(str(k), CONFIG["key"])

    # -- GET
    def do_GET(self):
        url = urlparse(self.path)
        q = parse_qs(url.query)
        p = url.path
        if p == "/":
            self.send_response(302)
            self.send_header("Location", "/classroom/join.html")
            self.end_headers()
            return
        if not p.startswith("/api/"):
            return super().do_GET()
        if p == "/api/ping":
            return self.send_json({"ok": True})
        if p == "/api/state":
            with COND:
                return self.send_json(public_snapshot())
        if p == "/api/events":
            return self.stream()
        if p == "/api/whoami":
            sid = q.get("id", [""])[0]
            return self.send_json({"ok": sid in STUDENTS, "name": STUDENTS.get(sid, {}).get("name")})
        # ---- teacher-only below
        if not self.is_teacher(q):
            return self.send_json({"error": "teacher key required"}, 403)
        if p == "/api/info":
            return self.send_json({"url": CONFIG["url"], "lectures": list_lectures(), "data_file": CONFIG["data_file"]})
        if p == "/api/roster":
            with COND:
                names = sorted((s["name"] for s in STUDENTS.values()), key=str.lower)
            return self.send_json({"names": names})
        if p == "/api/results":
            deck = q.get("deck", [""])[0]
            slide = q.get("slide", [None])[0]
            with COND:
                return self.send_json(results_for(deck, int(slide) if slide is not None else None))
        if p == "/api/export.csv":
            buf = io.StringIO()
            w = csv.writer(buf)
            w.writerow(["time", "name", "lecture", "slide", "question", "label", "correct", "answer"])
            with COND:
                for a in sorted(ANSWERS.values(), key=lambda r: r["time"]):
                    w.writerow([a["time"], a["name"], a["deck"], a["slide"] + 1, a["qid"], a["label"],
                                int(a["correct"]), a["answer"]])
            body = buf.getvalue().encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/csv")
            self.send_header("Content-Disposition", "attachment; filename=class_results_%s.csv" % dt.date.today())
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_json({"error": "unknown endpoint"}, 404)

    def stream(self):
        """Server-sent events: push a snapshot whenever something changes."""
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        last = -1
        try:
            while True:
                with COND:
                    COND.wait_for(lambda: SEQ[0] != last, timeout=15)
                    snap = public_snapshot()
                if snap["seq"] != last:
                    last = snap["seq"]
                    self.wfile.write(b"data: " + json.dumps(snap).encode() + b"\n\n")
                else:
                    self.wfile.write(b": keep-alive\n\n")
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, OSError):
            return

    # -- POST
    def do_POST(self):
        p = urlparse(self.path).path
        body = self.body_json()
        if p == "/api/join":
            name = re.sub(r"\s+", " ", str(body.get("name", ""))).strip()[:40]
            if len(name) < 2:
                return self.send_json({"error": "Please enter your name"}, 400)
            with COND:
                sid = next((i for i, s in STUDENTS.items() if s["name"].lower() == name.lower()), None)
                if sid is None:
                    sid = secrets.token_hex(8)
                    STUDENTS[sid] = {"name": name, "joined": dt.datetime.now().isoformat(timespec="seconds")}
                    save()
            bump()
            return self.send_json({"id": sid, "name": STUDENTS[sid]["name"]})
        if p == "/api/answer":
            sid = str(body.get("id", ""))
            with COND:
                if sid not in STUDENTS:
                    return self.send_json({"error": "unknown student, please join again"}, 401)
                deck, qid = str(body.get("deck", ""))[:200], str(body.get("qid", ""))[:80]
                k = (sid, deck, qid)
                if k in ANSWERS:
                    return self.send_json({"locked": True})
                ANSWERS[k] = {
                    "sid": sid, "name": STUDENTS[sid]["name"], "deck": deck, "qid": qid,
                    "slide": int(body.get("slide") or 0), "label": str(body.get("label", qid))[:200],
                    "correct": bool(body.get("correct")), "answer": str(body.get("answer", ""))[:200],
                    "time": dt.datetime.now().isoformat(timespec="seconds"),
                }
                save()
            bump()
            return self.send_json({"ok": True})
        # ---- teacher-only below
        if not self.is_teacher(body=body):
            return self.send_json({"error": "teacher key required"}, 403)
        if p == "/api/state":
            with COND:
                STATE.update(deck=str(body.get("deck") or ""), h=int(body.get("h") or 0),
                             v=int(body.get("v") or 0), f=int(body.get("f") if body.get("f") is not None else -1))
            bump()
            return self.send_json({"ok": True})
        if p == "/api/clear":
            with COND:
                ANSWERS.clear()
                if body.get("students"):
                    STUDENTS.clear()
                save()
            bump()
            return self.send_json({"ok": True})
        self.send_json({"error": "unknown endpoint"}, 404)


# ---------------------------------------------------------------- main
def lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))   # no packet is sent; this just picks the outgoing interface
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", type=int, default=8604)
    ap.add_argument("--key", help="teacher key (default: a new random one each run)")
    ap.add_argument("--data", default=os.path.join(os.path.dirname(REPO), "class_data"),
                    help="folder for saved answers (default: class_data next to the course folder)")
    args = ap.parse_args()

    CONFIG["key"] = args.key or secrets.token_hex(3)
    os.makedirs(args.data, exist_ok=True)
    CONFIG["data_file"] = os.path.join(args.data, dt.datetime.now().strftime("class_%Y-%m-%d_%H%M.json"))
    ip = lan_ip()
    CONFIG["url"] = f"http://{ip}:{args.port}"

    srv = ThreadingHTTPServer(("0.0.0.0", args.port), Handler)
    srv.daemon_threads = True
    line = "=" * 64
    print(line)
    print(" UACB-604 live classroom is running")
    print(line)
    print(f" Students open:   {CONFIG['url']}")
    print(f" You (teacher):   http://localhost:{args.port}/classroom/teacher.html?key={CONFIG['key']}")
    print(f" Answers saved to {CONFIG['data_file']}")
    print(" Press Ctrl+C to stop.")
    print(line, flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped. Answers are saved in", CONFIG["data_file"])


if __name__ == "__main__":
    main()
