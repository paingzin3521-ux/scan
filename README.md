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
  "keys": [
    {
      "key": "DEV-XXXXXXXXXXXX",
      "expiry": 1234567890
    }
  ]
}
```
- `key` — User ရဲ့ Device Key
- `expiry` — Unix timestamp (expiry ရက်)

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
Option 5 သည် Local Cache ကို ရှင်းပြီး Server မှ Key ကို ပြန်စစ်သည်။

---

## ⚙️ Installation (Termux)

```bash
pkg update && pkg upgrade -y
pkg install python git -y
pip install requests aiohttp pycryptodome
```

```bash
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

**Q: Offline/Error ပြနေတယ်**
→ Internet ချိတ်မိမိမိမမိ စစ်ပါ၊ Server ယာယီ Down ဖြစ်နေနိုင်သည်။

---

## 📌 Notes
- Tool သည် Termux (Android) တွင်သာ အပြည့်အဝ အလုပ်လုပ်သည်
- Storage Permission ခွင့်ပြုရမည် (Setup ဝင်ဝင်ချင်း တောင်းမည်)
- Device Key သည် Device Info အပေါ်မူတည်၍ Auto-Generate ဖြစ်သည်
