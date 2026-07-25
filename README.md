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

## 🔑 KEY စီမံခန့်ခွဲမှု (Admin Guide)

### Key ဘယ်မှာ သိမ်းထားသလဲ?
Keys များကို API server တွင် သိမ်းဆည်းသည်:
```
https://passbot-e08t.onrender.com/api/keys
```

### Admin — Key Approve လုပ်နည်း
User ရဲ့ Device Key (`DEV-XXXXXXXXXXXX`) ကို API keys list ထဲ ထည့်ပေးရသည်။

**API Response Format ဖြစ်ရမည်:**
```json
{
  "expirations": {
    "DEV-XXXXXXXXXXXX": 1787065278
  }
}
```
- Key — User ရဲ့ Device Key
- Value — Unix timestamp (expiry ရက်)

### Key Status များ
| Status | အဓိပ္ပါယ် |
|--------|-----------|
| `Approved` ✅ | Key အတည်ပြုပြီး၊ အသုံးပြုနိုင်သည် |
| `Expired` ⏳ | Key ရက်လွန်သွားသည် — Admin ပြန် Extend လုပ်ပေးရမည် |
| `Not Registered` ❌ | Key list ထဲ မပါသေး — Admin ထည့်ပေးရမည် |
| `Time Spoofing!` ⚠️ | Device ရဲ့ နာရီ ပြောင်းထားသည် — မသုံးနိုင် |
| `Offline/Error` 📡 | Server ချိတ်မိခြင်း မရှိ — Internet စစ်ပါ |

---

## 👤 USER Guide — Key ဘယ်လိုရရှိမလဲ?

### အဆင့် ၁ — Device Key ရှာပါ
Tool ကို Run သောအခါ Main Menu တွင် Device Key ပေါ်လာသည်:
```
[*] Device Key  : DEV-XXXXXXXXXXXX
```
ဒီ Key ကို Admin ဆီ ပေးပို့ပါ (Screenshot သို့မဟုတ် Copy ကူးပြီး)။

### အဆင့် ၂ — Admin ဆီ Key တောင်းပါ
Admin ဆီ Device Key ပေးပြီး Approve တောင်းပါ။ Admin က Server မှာ Key ထည့်ပေးမည်။

### အဆင့် ၃ — Key စစ်ဆေးပါ
Admin က Approve လုပ်ပြီးသည်နှင့် Tool ကို ပြန် Run ပါ — Status `Approved` ပြမည်။

### Key Status မပြောင်းလဲပါက — Option 5 သုံးပါ
```
Main Menu → [5] Reset Expiry Date
```

---

## 🔧 Key Admin Manager

`key_admin.py` — Admin တွေ key တွေ ထည့်/ဖျက်/တိုးဖို့ script

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

## 🕐 SERVER 24H KEEP-ALIVE

Render.com free tier သည် **15 မိနစ်** သုံးမိသူမရှိရင် sleep ဖြစ်သည်။
ရုတ်တရတ် ဝင်လာသောအခါ cold start ကြောင့် **30 စက္ကန့်** ကျော် နှေးသွားနိုင်သည်။

နည်းလမ်း ၃ ခု — တစ်ခုမှ သုံးလျှင် ရပြီ၊ အကောင်းဆုံး ၃ ခုလုံး သုံးနိုင်သည်:

---

### 📱 နည်းလမ်း ၁ — Termux Keep-Alive Script

ဖုန်း on နေချိန် background မှာ ping ပေး (4 မိနစ်တစ်ကြိမ်)

```bash
# ထည့်ပြီးသား repo ကို သုံးမည်ဆိုရင်
cd scan
pip install requests
python keep_alive.py
```

**Background run ဖို့ (Termux ပိတ်ထားလဲ run နေအောင်):**
```bash
# nohup နဲ့ background run
nohup python keep_alive.py > /dev/null 2>&1 &

# Process ID စစ်ကြည့်
ps aux | grep keep_alive

# ရပ်ဖို့
kill <PID>
```

**Termux:Boot နဲ့ ဖုန်း ပြန်ဖွင့်လျှင် auto-start ဖို့:**
```bash
# Termux:Boot install လုပ်ပြီးရင်
mkdir -p ~/.termux/boot/
cat > ~/.termux/boot/keepalive.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/scan
nohup python keep_alive.py > /dev/null 2>&1 &
EOF
chmod +x ~/.termux/boot/keepalive.sh
```

Log ကြည့်ဖို့:
```bash
cat ~/.key_admin/keepalive.log
```

---

### ⚙️ နည်းလမ်း ၂ — GitHub Actions (အကောင်းဆုံး — Cloud မှာ အမြဲ run)

ဖုန်း off ထားလဲ GitHub server မှ 5 မိနစ်တစ်ကြိမ် ping ပေးမည်။

**Setup အဆင့်များ:**

1. GitHub repo ကို သွားပါ → **Settings** tab
2. **Actions → General** → "Allow all actions" enable လုပ်ပါ
3. Repo ထဲ ဒီ folder/file ဖန်တီးပါ:

```
.github/
  workflows/
    keep_alive.yml
```

4. `keep_alive.yml` ထဲမှာ ဒီ code ထည့်ပါ:

```yaml
name: Server Keep-Alive

on:
  schedule:
    - cron: '*/5 * * * *'   # every 5 minutes
  workflow_dispatch:         # manual trigger button

jobs:
  ping:
    runs-on: ubuntu-latest
    steps:
      - name: Ping passbot server
        run: |
          echo "Pinging at $(date)"
          STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 20 \
            https://passbot-e08t.onrender.com/api/keys)
          if [ "$STATUS" = "200" ]; then
            echo "✔ Server alive — HTTP $STATUS"
          else
            echo "✘ HTTP $STATUS"
            exit 1
          fi
```

5. File save လုပ်ပြီးရင် **Actions tab** တွင် workflow run နေသည် မြင်ရမည်

> ⚠️ **Note:** GitHub Actions cron သည် free repo တွင် ±5 မိနစ် နောက်ကျနိုင်သည်

---

### ☁️ နည်းလမ်း ၃ — UptimeRobot (အပိုအလုပ်မလုပ်ဘဲ Cloud ကနေ monitor)

အခမဲ့ — ဖုန်းမလိုဘဲ cloud ကနေ 5 မိနစ်တစ်ကြိမ် ping ပေးသည်

**Setup (5 မိနစ်):**

1. [uptimerobot.com](https://uptimerobot.com) ကို သွားပြီး **Free account** ဖွင့်ပါ
2. Dashboard → **"+ Add New Monitor"** နှိပ်ပါ
3. Settings:
   - **Monitor Type:** `HTTP(s)`
   - **Friendly Name:** `Passbot Server`
   - **URL:** `https://passbot-e08t.onrender.com/api/keys`
   - **Monitoring Interval:** `5 minutes`
4. **"Create Monitor"** နှိပ်ပြီး ပြီးပြီ ✔

Dashboard တွင် uptime %, response time graph မြင်ရမည်။
Server down ဖြစ်ရင် email alert ပေးမည်။

---

### 🆚 နည်းလမ်းများ နှိုင်းယှဉ်ချက်

| နည်းလမ်း | ဖုန်းလိုသလား | ဆာဗာ Off ဖုန်း | Setup အချိန် | Alert |
|-----------|------------|----------------|-------------|-------|
| Termux Script | ✅ လိုသည် | ❌ ရပ်မည် | 1 မိနစ် | ❌ |
| GitHub Actions | ❌ မလို | ✅ run မည် | 5 မိနစ် | ✅ |
| UptimeRobot | ❌ မလို | ✅ run မည် | 5 မိနစ် | ✅ Email |

**အကြံပြုချက်:** GitHub Actions + UptimeRobot ၂ ခုလုံး သုံးပါ

---

### 💡 Render.com Paid Plan အကြောင်း

| Plan | စျေးနှုန်း | Sleep | Notes |
|------|---------|-------|-------|
| Free | $0 | ✅ (15 min) | Keep-alive script လိုသည် |
| Starter | $7/mo | ❌ Always-on | ပိုကောင်းသည် |

Free plan + keep-alive နည်းလမ်းသုံးမည်ဆိုရင် **GitHub Actions + UptimeRobot** ပေါင်းသုံးခြင်းသည် paid plan နဲ့ ဆင်တူသောအဖြေဖြစ်သည်။

---

## ⚙️ Installation (Termux)

```bash
pkg update && pkg upgrade -y
pkg install python git -y
pip install requests aiohttp pycryptodome
git clone https://github.com/paingzin3521-ux/scan.git
cd scan
python "scan (2).py"
```

---

## ❓ အဖြစ်များသော ပြဿနာများ

**Q: Key Approved ဖြစ်နေပါတယ် ဒါပေမဲ့ Option 4 မအလုပ်မလုပ်ဘူး**
→ Option 3 ကို ဦးစွာ Run ပြီး Active Devices စစ်ပါ။

**Q: Not Registered ပြနေတယ်**
→ Device Key ကို Admin ဆီ ပေးပြီး Approve တောင်းပါ။

**Q: Expired ပြနေတယ်**
→ Admin ဆီ ပြောပြီး Key Extend တောင်းပါ၊ ပြီးရင် Option 5 နှိပ်ပါ။

**Q: Server ဖြေကြားမှုနှေးနေတယ်**
→ Server sleep ဖြစ်နေနိုင်သည် — Keep-alive script setup လုပ်ပါ။

**Q: Offline/Error ပြနေတယ်**
→ Internet စစ်ပါ၊ Server ယာယီ Down ဖြစ်နေနိုင်သည်။

---

## 📌 Notes
- Tool သည် Termux (Android) တွင်သာ အပြည့်အဝ အလုပ်လုပ်သည်
- Storage Permission ခွင့်ပြုရမည် (Setup ဝင်ဝင်ချင်း တောင်းမည်)
- Device Key သည် Device Info အပေါ်မူတည်၍ Auto-Generate ဖြစ်သည်
