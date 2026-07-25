#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════╗
║       SERVER KEEP-ALIVE v1.0        ║
║    passbot-e08t.onrender.com        ║
╚══════════════════════════════════════╝
Termux မှာ background run ပြီး server ကို
4 မိနစ်တစ်ကြိမ် ping ပေးသည်။
"""

import requests, time, os, sys
from datetime import datetime

# ─── CONFIG ───────────────────────────────────────────
PING_URL      = "https://passbot-e08t.onrender.com/api/keys"
PING_INTERVAL = 240   # seconds (4 minutes)
LOG_FILE      = os.path.join(os.path.expanduser("~"), ".key_admin", "keepalive.log")
MAX_LOG_LINES = 200

# ─── COLORS ───────────────────────────────────────────
G = "\033[1;32m"; R = "\033[1;31m"; Y = "\033[1;33m"
C = "\033[1;36m"; W = "\033[1;37m"; D = "\033[0;37m"; X = "\033[0m"

os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log(msg):
    line = f"[{now_str()}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
        # Trim log file
        with open(LOG_FILE) as f:
            lines = f.readlines()
        if len(lines) > MAX_LOG_LINES:
            with open(LOG_FILE, "w") as f:
                f.writelines(lines[-MAX_LOG_LINES:])
    except:
        pass

def ping():
    try:
        start = time.time()
        r = requests.get(PING_URL, timeout=15)
        elapsed = round(time.time() - start, 2)
        keys_count = 0
        try:
            data = r.json()
            keys_count = len(data.get("expirations", {}))
        except:
            pass
        if r.status_code == 200:
            log(f"✔ OK  {elapsed}s  |  keys={keys_count}  |  status={r.status_code}")
            return True
        else:
            log(f"✘ FAIL  status={r.status_code}")
            return False
    except requests.exceptions.Timeout:
        log("✘ TIMEOUT (server sleeping?) — retrying next cycle")
        return False
    except Exception as e:
        log(f"✘ ERROR: {e}")
        return False

def banner():
    os.system("clear" if os.name == "posix" else "cls")
    try: w = os.get_terminal_size()[0]
    except: w = 60
    print(f"{C}{'═' * w}{X}")
    print(f"{C}{'SERVER KEEP-ALIVE':^{w}}{X}")
    print(f"{D}{'passbot-e08t.onrender.com':^{w}}{X}")
    print(f"{C}{'═' * w}{X}")
    print(f"\n  {W}Ping URL   :{X} {D}{PING_URL}{X}")
    print(f"  {W}Interval   :{X} {Y}Every {PING_INTERVAL//60} minutes{X}")
    print(f"  {W}Log file   :{X} {D}{LOG_FILE}{X}")
    print(f"\n  {D}Ctrl+C နှိပ်ပြီး ရပ်နိုင်သည်{X}\n")
    print(f"  {D}{'─' * (w-4)}{X}")

def countdown(seconds):
    for remaining in range(seconds, 0, -1):
        mins = remaining // 60
        secs = remaining % 60
        print(f"\r  {D}Next ping in: {Y}{mins:02d}:{secs:02d}{X}    ", end="", flush=True)
        time.sleep(1)
    print()

def main():
    banner()
    log("=== Keep-alive started ===")
    ok_count = fail_count = 0

    while True:
        success = ping()
        if success: ok_count += 1
        else: fail_count += 1

        # Show stats line
        total = ok_count + fail_count
        uptime_pct = round(ok_count / total * 100, 1) if total > 0 else 0
        print(f"  {D}Stats: {G}✔ {ok_count}{X}  {R}✘ {fail_count}{X}  "
              f"Uptime: {G if uptime_pct >= 90 else Y}{uptime_pct}%{X}")

        try:
            countdown(PING_INTERVAL)
        except KeyboardInterrupt:
            print(f"\n\n  {Y}[*] Keep-alive stopped.{X}")
            log("=== Keep-alive stopped by user ===")
            sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Y}[*] Stopped.{X}\n")
        sys.exit(0)
