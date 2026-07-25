#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════╗
║       KEY ADMIN MANAGER v1.0        ║
║     passbot-e08t.onrender.com       ║
╚══════════════════════════════════════╝
"""

import os, json, sys, time, requests
from datetime import datetime, timedelta

# ─── COLORS ───────────────────────────────────────────
R  = "\033[1;31m"   # Red
G  = "\033[1;32m"   # Green
Y  = "\033[1;33m"   # Yellow
C  = "\033[1;36m"   # Cyan
P  = "\033[1;35m"   # Purple
B  = "\033[1;34m"   # Blue
W  = "\033[1;37m"   # White
DIM= "\033[0;37m"   # Dim
X  = "\033[0m"      # Reset

# ─── CONFIG ───────────────────────────────────────────
API_URL    = "https://passbot-e08t.onrender.com/api/keys"
LOCAL_FILE = os.path.join(os.path.expanduser("~"), ".key_admin", "keys.json")
os.makedirs(os.path.dirname(LOCAL_FILE), exist_ok=True)

# ─── HELPERS ──────────────────────────────────────────
def clr():
    os.system("clear" if os.name == "posix" else "cls")

def line(char="─", color=Y):
    try:    w = os.get_terminal_size()[0]
    except: w = 60
    print(f"{color}{char * w}{X}")

def banner():
    clr()
    line("═", C)
    print(f"{C}{'KEY ADMIN MANAGER v1.0':^60}{X}")
    print(f"{DIM}{'passbot-e08t.onrender.com':^60}{X}")
    line("═", C)
    print()

def ts_to_str(ts):
    """Convert unix timestamp to readable string."""
    try:
        dt = datetime.fromtimestamp(int(ts))
        now = datetime.now()
        diff = dt - now
        if diff.total_seconds() <= 0:
            return f"{R}EXPIRED{X}"
        days  = diff.days
        hours = diff.seconds // 3600
        mins  = (diff.seconds % 3600) // 60
        date_str = dt.strftime("%Y-%m-%d %H:%M")
        if days > 365:
            return f"{G}∞ Permanent  ({date_str}){X}"
        elif days > 0:
            return f"{G}{days}d {hours}h  ({date_str}){X}"
        elif hours > 0:
            return f"{Y}{hours}h {mins}m  ({date_str}){X}"
        else:
            return f"{R}{mins}m left  ({date_str}){X}"
    except:
        return f"{R}Invalid{X}"

def days_to_ts(days):
    return int((datetime.now() + timedelta(days=days)).timestamp())

# ─── LOAD / SAVE ──────────────────────────────────────
def load_keys():
    if os.path.exists(LOCAL_FILE):
        try:
            with open(LOCAL_FILE) as f:
                data = json.load(f)
                return data.get("expirations", {})
        except:
            pass
    return {}

def save_keys(keys_dict):
    with open(LOCAL_FILE, "w") as f:
        json.dump({"expirations": keys_dict}, f, indent=2)

# ─── API FETCH ────────────────────────────────────────
def fetch_from_server():
    try:
        print(f"\n{Y}[*] Server မှ key တွေ ဆွဲယူနေသည်...{X}")
        r = requests.get(API_URL, timeout=8)
        data = r.json()
        keys = data.get("expirations", {})
        save_keys(keys)
        print(f"{G}[ ✔ ] {len(keys)} keys ရရှိပြီ — local ကို save လုပ်ပြီးပြီ{X}")
        time.sleep(1)
        return keys
    except Exception as e:
        print(f"{R}[ ✘ ] Server ချိတ်မရ: {e}{X}")
        time.sleep(2)
        return load_keys()

# ─── LIST KEYS ────────────────────────────────────────
def list_keys(keys):
    banner()
    line()
    now = datetime.now().timestamp()
    if not keys:
        print(f"{Y}  [ ! ] Key မရှိသေးပါ{X}\n")
        input(f"{DIM}  Enter နှိပ်ပြီး ပြန်သွားရန်...{X}")
        return

    active  = {k:v for k,v in keys.items() if v > now}
    expired = {k:v for k,v in keys.items() if v <= now}

    print(f"{W}  {'#':<4} {'DEVICE KEY':<22} {'STATUS / EXPIRY'}{X}")
    line("─", DIM)

    i = 1
    for k, v in sorted(active.items(), key=lambda x: x[1]):
        print(f"  {DIM}{i:<4}{X}{C}{k:<22}{X}  {ts_to_str(v)}")
        i += 1
    for k, v in sorted(expired.items(), key=lambda x: x[1]):
        print(f"  {DIM}{i:<4}{X}{R}{k:<22}{X}  {ts_to_str(v)}")
        i += 1

    line("─", DIM)
    print(f"\n  {G}Active : {len(active)}{X}   {R}Expired: {len(expired)}{X}   {W}Total  : {len(keys)}{X}\n")
    input(f"{DIM}  Enter နှိပ်ပြီး ပြန်သွားရန်...{X}")

# ─── ADD KEY ──────────────────────────────────────────
def add_key(keys):
    banner()
    print(f"{C}  ══ KEY ထည့်ရန် ══{X}\n")

    dev_key = input(f"{W}  Device Key (DEV-XXXXXXXXXXXX) : {X}").strip().upper()
    if not dev_key:
        print(f"{R}  [ ✘ ] Key မထည့်ရေ{X}"); time.sleep(1); return keys

    if not dev_key.startswith("DEV-") or len(dev_key) != 16:
        print(f"{Y}  [ ! ] Format: DEV-XXXXXXXXXXXX (16 characters){X}"); time.sleep(2); return keys

    if dev_key in keys:
        print(f"{Y}  [ ! ] '{dev_key}' ရှိပြီးသား{X}")
        choice = input(f"{W}  Overwrite လုပ်မလား? (y/n): {X}").strip().lower()
        if choice != 'y': return keys

    print(f"\n  {DIM}သက်တမ်း ရက်အရေအတွက်:{X}")
    print(f"  {DIM}  7  = 1 week{X}")
    print(f"  {DIM}  30 = 1 month{X}")
    print(f"  {DIM}  0  = Permanent (never expire){X}\n")

    days_str = input(f"{W}  ရက်အရေအတွက် (default=30): {X}").strip()
    try:
        days = int(days_str) if days_str else 30
    except:
        print(f"{R}  [ ✘ ] ဂဏန်းတစ်ခု ထည့်ပါ{X}"); time.sleep(1); return keys

    if days == 0:
        expiry = 9999999999  # permanent
    else:
        expiry = days_to_ts(days)

    keys[dev_key] = expiry
    save_keys(keys)
    print(f"\n{G}  [ ✔ ] '{dev_key}' ကို {days if days else '∞'} ရက် approve လုပ်ပြီး{X}")
    print(f"  {DIM}Expiry : {ts_to_str(expiry)}{X}\n")
    input(f"{DIM}  Enter နှိပ်ပြီး ပြန်သွားရန်...{X}")
    return keys

# ─── REMOVE KEY ───────────────────────────────────────
def remove_key(keys):
    banner()
    print(f"{C}  ══ KEY ဖျက်ရန် ══{X}\n")

    if not keys:
        print(f"{Y}  Key မရှိသေးပါ{X}"); time.sleep(1); return keys

    # Show list first
    items = list(keys.items())
    for i, (k, v) in enumerate(items, 1):
        print(f"  {DIM}[{i}]{X}  {C}{k}{X}  {ts_to_str(v)}")

    print()
    choice = input(f"{W}  ဖျက်ချင်တဲ့ Key နဲ့ နံပါတ် (သို့) DEV-... ထည့်ပါ: {X}").strip()

    target = None
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(items):
            target = items[idx][0]
    elif choice.upper().startswith("DEV-"):
        target = choice.upper()

    if not target or target not in keys:
        print(f"{R}  [ ✘ ] မတွေ့ပါ{X}"); time.sleep(1); return keys

    confirm = input(f"\n{R}  '{target}' ကို ဖျက်မည် — သေချာလား? (y/n): {X}").strip().lower()
    if confirm == 'y':
        del keys[target]
        save_keys(keys)
        print(f"{G}  [ ✔ ] ဖျက်ပြီးပြီ{X}")
    else:
        print(f"{Y}  [ ! ] ဖျက်ခြင်းမပြုပါ{X}")
    time.sleep(1)
    return keys

# ─── EXTEND KEY ───────────────────────────────────────
def extend_key(keys):
    banner()
    print(f"{C}  ══ KEY သက်တမ်း တိုးရန် ══{X}\n")

    if not keys:
        print(f"{Y}  Key မရှိသေးပါ{X}"); time.sleep(1); return keys

    items = list(keys.items())
    for i, (k, v) in enumerate(items, 1):
        print(f"  {DIM}[{i}]{X}  {C}{k}{X}  {ts_to_str(v)}")

    print()
    choice = input(f"{W}  တိုးချင်တဲ့ Key နဲ့ နံပါတ် (သို့) DEV-... ထည့်ပါ: {X}").strip()

    target = None
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(items):
            target = items[idx][0]
    elif choice.upper().startswith("DEV-"):
        target = choice.upper()

    if not target or target not in keys:
        print(f"{R}  [ ✘ ] မတွေ့ပါ{X}"); time.sleep(1); return keys

    days_str = input(f"\n{W}  ဘယ်နှစ်ရက် တိုးမလဲ: {X}").strip()
    try:
        extra_days = int(days_str)
    except:
        print(f"{R}  [ ✘ ] ဂဏန်းတစ်ခု ထည့်ပါ{X}"); time.sleep(1); return keys

    current_ts = keys[target]
    now_ts = datetime.now().timestamp()
    base_ts = max(current_ts, now_ts)  # if expired, extend from now
    keys[target] = int(base_ts + extra_days * 86400)

    save_keys(keys)
    print(f"\n{G}  [ ✔ ] '{target}' ကို {extra_days} ရက် တိုးပြီး{X}")
    print(f"  {DIM}New expiry: {ts_to_str(keys[target])}{X}\n")
    input(f"{DIM}  Enter နှိပ်ပြီး ပြန်သွားရန်...{X}")
    return keys

# ─── BULK EXPIRE CHECK ────────────────────────────────
def expired_summary(keys):
    banner()
    now = datetime.now().timestamp()
    expired = {k:v for k,v in keys.items() if v <= now}
    expiring_soon = {k:v for k,v in keys.items() if 0 < v - now < 3*86400}

    if expired:
        print(f"{R}  ══ EXPIRED KEYS ({len(expired)}) ══{X}\n")
        for k, v in expired.items():
            dt = datetime.fromtimestamp(v).strftime("%Y-%m-%d")
            print(f"  {R}✘ {k}  (expired {dt}){X}")
        print()

    if expiring_soon:
        print(f"{Y}  ══ EXPIRING SOON < 3 days ({len(expiring_soon)}) ══{X}\n")
        for k, v in expiring_soon.items():
            print(f"  {Y}⚠ {k}  {ts_to_str(v)}{X}")
        print()

    if not expired and not expiring_soon:
        print(f"{G}  [ ✔ ] Key အားလုံး Active — ကောင်းနေပါတယ်{X}\n")

    print(f"\n{DIM}  Local file: {LOCAL_FILE}{X}\n")
    input(f"{DIM}  Enter နှိပ်ပြီး ပြန်သွားရန်...{X}")

# ─── EXPORT / SHOW JSON ───────────────────────────────
def show_json(keys):
    banner()
    print(f"{C}  ══ JSON Output (Server တင်ဖို့) ══{X}\n")
    out = json.dumps({"expirations": keys}, indent=2)
    print(f"{DIM}{out}{X}")
    print(f"\n{Y}  [ * ] ဒီ JSON ကို server မှာ keys.json အဖြစ် replace လုပ်ပါ{X}")
    print(f"  {DIM}File: {LOCAL_FILE}{X}\n")
    input(f"{DIM}  Enter နှိပ်ပြီး ပြန်သွားရန်...{X}")

# ─── REMOVE ALL EXPIRED ───────────────────────────────
def clean_expired(keys):
    now = datetime.now().timestamp()
    before = len(keys)
    keys = {k:v for k,v in keys.items() if v > now}
    removed = before - len(keys)
    save_keys(keys)
    print(f"\n{G}  [ ✔ ] Expired keys {removed} ခု ဖျက်ပြီး{X}")
    time.sleep(1.5)
    return keys

# ─── MAIN MENU ────────────────────────────────────────
def main():
    keys = load_keys()

    while True:
        banner()
        now = datetime.now().timestamp()
        active  = sum(1 for v in keys.values() if v > now)
        expired = sum(1 for v in keys.values() if v <= now)

        print(f"  {W}Keys:{X}  {G}Active {active}{X}  ·  {R}Expired {expired}{X}  ·  {DIM}Total {len(keys)}{X}\n")
        line("─", DIM)
        print(f"  {C}[1]{X}  {W}Key တွေ ကြည့်ရန် (List){X}")
        print(f"  {C}[2]{X}  {W}Key အသစ် ထည့်ရန် (Add / Approve){X}")
        print(f"  {C}[3]{X}  {W}Key ဖျက်ရန် (Remove / Deny){X}")
        print(f"  {C}[4]{X}  {W}Key သက်တမ်း တိုးရန် (Extend){X}")
        print(f"  {C}[5]{X}  {W}Server မှ Sync ဆွဲယူရန် (Fetch){X}")
        print(f"  {C}[6]{X}  {W}Expired Keys စစ်ဆေးရန်{X}")
        print(f"  {C}[7]{X}  {W}JSON Export ကြည့်ရန်{X}")
        print(f"  {C}[8]{X}  {R}Expired Keys အားလုံး ဖျက်ရန{X}")
        print(f"  {C}[0]{X}  {DIM}ထွက်ရန် (Exit){X}")
        line("─", DIM)

        choice = input(f"\n  {Y}ရွေးပါ → {X}").strip()

        if   choice == '1': list_keys(keys)
        elif choice == '2': keys = add_key(keys)
        elif choice == '3': keys = remove_key(keys)
        elif choice == '4': keys = extend_key(keys)
        elif choice == '5': keys = fetch_from_server()
        elif choice == '6': expired_summary(keys)
        elif choice == '7': show_json(keys)
        elif choice == '8':
            confirm = input(f"{R}  Expired key အားလုံး ဖျက်မည် — သေချာလား? (y/n): {X}").strip().lower()
            if confirm == 'y': keys = clean_expired(keys)
        elif choice == '0':
            print(f"\n{Y}  [*] Exiting...{X}\n"); sys.exit()
        else:
            print(f"{R}  [!] မမှန်ပါ{X}"); time.sleep(0.8)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Y}  [*] Program terminated.{X}\n")
        sys.exit(0)
