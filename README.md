# 🔍 SCAN - Wifi Bypass Tool

> Termux အတွက် Wifi Bypass Tool — IP/MAC Scan, Device Test, Bypass နဲ့ License Key System ပါဝင်သည်။

---

## 📋 Menu Options

| Option | Function |
|--------|----------|
| `1` | Setup Wifi |
| `2` | Scan IP/MAC (Table View) |
| `3` | Test Active Devices |
| `4` | Wifi Bypass (Device Select) |
| `5` | Reset Expiry Date |
| `0` | Exit |

---

## 🤖 Telegram Key Admin Bot

**`tg_key_admin.py`** — Telegram မှတဆင့် Key တွေ Approve/Deny/Extend လုပ်နိုင်သော Bot

### Setup

**အဆင့် ၁ — Bot ဖန်တီးပါ**
1. Telegram မှာ [@BotFather](https://t.me/BotFather) ကို ဖွင့်ပါ
2. `/newbot` ပို့ပြီး Bot name နဲ့ username ထည့်ပါ
3. ရလာသော Token ကို မှတ်ထားပါ (`123456789:ABCdef...`)

**အဆင့် ၂ — Admin ID ရှာပါ**
1. [@userinfobot](https://t.me/userinfobot) ကို message တစ်ခုပို့ပါ
2. ပြန်ပို့လာသော `Id:` နံပါတ်ကို မှတ်ထားပါ

**အဆင့် ၃ — Run ပါ**
```bash
cd scan
pip install python-telegram-bot requests

# Token နဲ့ Admin ID ထည့်ပြီး run
TELEGRAM_BOT_TOKEN="YOUR_TOKEN" TELEGRAM_ADMIN_ID="YOUR_ID" python tg_key_admin.py
```

**သို့မဟုတ် `.env` file သုံး:**
```bash
# .env file ဖန်တီးပါ
echo 'TELEGRAM_BOT_TOKEN=YOUR_TOKEN' > .env
echo 'TELEGRAM_ADMIN_ID=YOUR_ID'    >> .env

# python-dotenv install
pip install python-dotenv

# tg_key_admin.py ထဲ ဒီ ၂ ကြောင်း ထည့်ပါ (ထိပ်ဆုံးမှာ):
# from dotenv import load_dotenv
# load_dotenv()
python tg_key_admin.py
```

### Bot Commands

| Command | လုပ်ဆောင်ချက် |
|---------|--------------|
| `/start` | Main menu ဖွင့်ရန် |
| `/list` | Key အားလုံး ကြည့်ရန် |
| `/fetch` | Server မှ Sync ဆွဲယူရန် |
| `/expired` | Expired key တွေ ကြည့်ရန် |
| `/clean` | Expired key အားလုံး ဖျက်ရန် |
| `/cancel` | လုပ်ဆောင်မှု ဖျက်သိမ်းရန် |

### Bot Buttons (Inline Keyboard)

```
📋 List Keys    ➕ Add Key
🗑 Remove Key  ⏫ Extend Key
🔍 Check Key   🔄 Sync Server
⚠️ Expired      🧹 Clean Expired
```

### Add Key Flow (Bot Chat ထဲမှာ)

```
သင်  →  /start
Bot  →  [Menu Buttons]
သင်  →  ➕ Add Key နှိပ်
Bot  →  "Device Key ထည့်ပါ"
သင်  →  DEV-XXXXXXXXXXXX
Bot  →  "ရက်အရေအတွက် ထည့်ပါ"
သင်  →  30
Bot  →  ✅ Key Approved! DEV-XXXX | 30 ရက်
```

### Background Run (Termux)

```bash
# Background မှာ ထားဖို့
nohup TELEGRAM_BOT_TOKEN="TOKEN" TELEGRAM_ADMIN_ID="ID" python tg_key_admin.py &

# Log ကြည့်
cat nohup.out

# ရပ်ဖို့
pkill -f tg_key_admin.py
```

---

## 🔧 Key Admin Script (Terminal)

`key_admin.py` — Colored terminal UI နဲ့ key manage လုပ်ဖို့

```bash
python key_admin.py
```

| Option | လုပ်ဆောင်ချက် |
|--------|--------------|
| `1` | Key တွေအားလုံး ကြည့်ရန် |
| `2` | Key အသစ် Approve လုပ်ရန် |
| `3` | Key ဖျက်/Deny လုပ်ရန် |
| `4` | Key သက်တမ်း တိုးရန် |
| `5` | Server မှ Sync ဆွဲယူရန် |
| `6` | Expired Keys စစ်ဆေးရန် |
| `7` | JSON Export ကြည့်ရန် |
| `8` | Expired Keys အားလုံး ဖျက်ရန် |

---

## 🔑 KEY စီမံခန့်ခွဲမှု

### Key ဘယ်မှာ သိမ်းထားသလဲ?
```
https://passbot-e08t.onrender.com/api/keys
```

### Key Status များ
| Status | အဓိပ္ပါယ် |
|--------|-----------|
| `Approved` ✅ | Key အတည်ပြုပြီး၊ အသုံးပြုနိုင်သည် |
| `Expired` ⏳ | Key ရက်လွန်သွားသည် — Admin ပြန် Extend လုပ်ပေးရမည် |
| `Not Registered` ❌ | Key list ထဲ မပါသေး — Admin ထည့်ပေးရမည် |
| `Time Spoofing!` ⚠️ | Device ရဲ့ နာရီ ပြောင်းထားသည် — မသုံးနိုင် |
| `Offline/Error` 📡 | Server ချိတ်မိခြင်း မရှိ — Internet စစ်ပါ |

### USER — Key ဘယ်လိုရမလဲ?
1. Tool run ပြီး Main Menu မှာ `DEV-XXXXXXXXXXXX` Key ကို Admin ဆီ ပေးပါ
2. Admin က Bot ကနေ Approve လုပ်ပေးမည်
3. Tool ကို ပြန် Run ပါ — `Approved` ပြမည်
4. Status မပြောင်းရင် Option `5` (Reset Expiry) နှိပ်ပါ

---

## 🕐 SERVER 24H KEEP-ALIVE

### 📱 နည်းလမ်း ၁ — Termux Script
```bash
pip install requests
python keep_alive.py
```
Background run:
```bash
nohup python keep_alive.py > /dev/null 2>&1 &
```

### ⚙️ နည်းလမ်း ၂ — GitHub Actions
Repo ထဲ `.github/workflows/keep_alive.yml` ဖိုင်ဖန်တီးပြီး:
```yaml
name: Server Keep-Alive
on:
  schedule:
    - cron: '*/5 * * * *'
  workflow_dispatch:
jobs:
  ping:
    runs-on: ubuntu-latest
    steps:
      - name: Ping
        run: |
          STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 20 \
            https://passbot-e08t.onrender.com/api/keys)
          echo "HTTP $STATUS"
```

### ☁️ နည်းလမ်း ၃ — UptimeRobot (အကောင်းဆုံး)
1. [uptimerobot.com](https://uptimerobot.com) — Free account ဖွင့်ပါ
2. **+ Add New Monitor** → HTTP(s)
3. URL: `https://passbot-e08t.onrender.com/api/keys`
4. Interval: `5 minutes` → Create ✔

---

## ⚙️ Installation (Termux)

```bash
pkg update && pkg upgrade -y
pkg install python git -y
pip install requests aiohttp pycryptodome python-telegram-bot
git clone https://github.com/paingzin3521-ux/scan.git
cd scan
python "scan (2).py"
```

---

## 📁 Files

| File | အသုံး |
|------|-------|
| `scan (2).py` | Main Wifi Bypass Tool |
| `tg_key_admin.py` | Telegram Bot Key Admin |
| `key_admin.py` | Terminal Key Admin |
| `keep_alive.py` | Server Keep-Alive Ping |

---

## ❓ FAQ

**Q: Key Approved ဖြစ်နေပါတယ် ဒါပေမဲ့ Option 4 မအလုပ်မလုပ်ဘူး**
→ Option 3 ကို ဦးစွာ Run ပြီး Active Devices စစ်ပါ။

**Q: Not Registered ပြနေတယ်**
→ Device Key ကို Admin ဆီ ပေးပြီး Bot ကနေ Approve တောင်းပါ။

**Q: Server ဖြေကြားမှုနှေးနေတယ်**
→ Keep-alive setup မလုပ်ရသေး — UptimeRobot သုံးပါ။

**Q: Bot မတုံ့ပြန်ဘူး**
→ Token နဲ့ Admin ID မှန်မမှန် စစ်ပါ၊ `python tg_key_admin.py` ပြန် run ပါ။
