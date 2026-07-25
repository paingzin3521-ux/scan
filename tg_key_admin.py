#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════╗
║     TELEGRAM KEY ADMIN BOT v2.0         ║
║   passbot-e08t.onrender.com             ║
╚══════════════════════════════════════════╝

Features:
  - User: DEV-XXX ပို့ပြီး Key တောင်းနိုင်
  - Admin: Approve/Deny/Extend button နှိပ်ရုံ
  - User: Approve ဖြစ်ချင်း auto-notification ရ

Install:
  pip install python-telegram-bot requests

Run:
  TELEGRAM_BOT_TOKEN="..." TELEGRAM_ADMIN_ID="..." python tg_key_admin.py
"""

import os, json, logging, requests
from datetime import datetime, timedelta
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

# ─── CONFIG ───────────────────────────────────────────────────────────────────
BOT_TOKEN  = os.environ.get("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN")
ADMIN_ID   = int(os.environ.get("TELEGRAM_ADMIN_ID", "0"))
API_URL    = "https://passbot-e08t.onrender.com/api/keys"
LOCAL_FILE = os.path.join(os.path.expanduser("~"), ".key_admin", "keys.json")
REQ_FILE   = os.path.join(os.path.expanduser("~"), ".key_admin", "requests.json")

os.makedirs(os.path.dirname(LOCAL_FILE), exist_ok=True)
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# ─── CONVERSATION STATES ──────────────────────────────────────────────────────
ADD_KEY, ADD_DAYS, REMOVE_KEY, EXTEND_KEY, EXTEND_DAYS, CHECK_KEY, \
SET_DAYS_APPROVE, BROADCAST_MSG = range(8)

# ─── KEY HELPERS ──────────────────────────────────────────────────────────────
def load_keys():
    if os.path.exists(LOCAL_FILE):
        try:
            with open(LOCAL_FILE) as f:
                return json.load(f).get("expirations", {})
        except: pass
    return {}

def save_keys(keys):
    with open(LOCAL_FILE, "w") as f:
        json.dump({"expirations": keys}, f, indent=2)

def load_requests():
    if os.path.exists(REQ_FILE):
        try:
            with open(REQ_FILE) as f:
                return json.load(f)
        except: pass
    return {}

def save_requests(reqs):
    with open(REQ_FILE, "w") as f:
        json.dump(reqs, f, indent=2)

def ts_to_str(ts):
    try:
        dt  = datetime.fromtimestamp(int(ts))
        now = datetime.now()
        diff = dt - now
        if diff.total_seconds() <= 0:
            return "❌ EXPIRED"
        days  = diff.days
        hours = diff.seconds // 3600
        date  = dt.strftime("%Y-%m-%d")
        if ts >= 9999999990:
            return "♾️ Permanent"
        elif days > 30:
            return f"✅ {days}d  ({date})"
        elif days > 0:
            return f"🟡 {days}d {hours}h  ({date})"
        else:
            mins = (diff.seconds % 3600) // 60
            return f"🔴 {hours}h {mins}m left"
    except:
        return "❓ Unknown"

def days_to_ts(days):
    return int((datetime.now() + timedelta(days=days)).timestamp())

def is_admin(update: Update):
    return update.effective_user.id == ADMIN_ID

# ─── /start ───────────────────────────────────────────────────────────────────
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if is_admin(update):
        # Admin menu
        keys  = load_keys()
        reqs  = load_requests()
        now   = datetime.now().timestamp()
        act   = sum(1 for v in keys.values() if v > now)
        exp   = len(keys) - act
        pend  = len(reqs)
        text  = (
            "🔑 *Key Admin Bot v2.0*\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"✅ Active : `{act}`\n"
            f"❌ Expired: `{exp}`\n"
            f"📦 Total  : `{len(keys)}`\n"
            f"📨 Pending: `{pend}`\n"
            f"━━━━━━━━━━━━━━━━━"
        )
        kb = [
            [InlineKeyboardButton("📨 Pending Requests", callback_data="pending")],
            [InlineKeyboardButton("📋 List Keys",         callback_data="list"),
             InlineKeyboardButton("➕ Add Key",            callback_data="add")],
            [InlineKeyboardButton("🗑 Remove Key",        callback_data="remove"),
             InlineKeyboardButton("⏫ Extend Key",         callback_data="extend")],
            [InlineKeyboardButton("🔍 Check Key",         callback_data="check"),
             InlineKeyboardButton("🔄 Sync Server",       callback_data="fetch")],
            [InlineKeyboardButton("⚠️ Expired",           callback_data="expired"),
             InlineKeyboardButton("🧹 Clean",             callback_data="clean")],
            [InlineKeyboardButton("📢 Broadcast",         callback_data="broadcast")],
        ]
        await update.message.reply_text(
            text, parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(kb)
        )
    else:
        # User welcome
        keys = load_keys()
        dev_key = None
        # Check if user already has an active key
        reqs = load_requests()
        uid  = str(user.id)
        user_key = None
        for k, v in reqs.items():
            if str(v.get("user_id")) == uid:
                user_key = k
                break

        text = (
            f"👋 *မင်္ဂလာပါ {user.first_name}!*\n\n"
            "🔑 Wifi Bypass Tool အသုံးပြုဖို့ Key လိုအပ်ပါသည်။\n\n"
            "📱 *Key တောင်းနည်း:*\n"
            "1. Tool run ပါ — Main Menu မှာ `Device ID` ကောပီကူးပါ\n"
            "2. Bot ကို ဒီ format နဲ့ ပို့ပါ:\n\n"
            "   `DEV-XXXXXXXXXXXX`\n\n"
            "3. Admin approve လုပ်ပြီးချင်း notification ရမည်\n\n"
            "━━━━━━━━━━━━━━━━━\n"
        )
        if user_key and user_key in keys:
            status = ts_to_str(keys[user_key])
            text += f"🔑 သင့် Key: `{user_key}`\nStatus: {status}"
        else:
            text += "_Device ID ကို ဒါပဲ bot ကိုပို့ပါ_"

        await update.message.reply_text(text, parse_mode="Markdown")

# ─── USER SENDS DEV KEY ───────────────────────────────────────────────────────
async def handle_user_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user    = update.effective_user
    text_in = update.message.text.strip().upper()

    # Admin text handling → unknown
    if is_admin(update):
        await update.message.reply_text("❓ /start နှိပ်ပြီး menu ဖွင့်ပါ")
        return

    # Check if it looks like a Device Key
    if text_in.startswith("DEV-") and len(text_in) == 16:
        dev_key = text_in
        keys    = load_keys()
        reqs    = load_requests()
        now_ts  = datetime.now().timestamp()

        # Already active?
        if dev_key in keys and keys[dev_key] > now_ts:
            await update.message.reply_text(
                f"✅ `{dev_key}` — Active ဖြစ်နေပြီ!\n"
                f"Status: {ts_to_str(keys[dev_key])}",
                parse_mode="Markdown"
            )
            return

        # Save request
        reqs[dev_key] = {
            "user_id":   user.id,
            "username":  user.username or "",
            "name":      user.full_name,
            "requested": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "status":    "pending"
        }
        save_requests(reqs)

        # Notify user
        await update.message.reply_text(
            f"📨 *Request ပို့ပြီးပြီ!*\n\n"
            f"Key: `{dev_key}`\n"
            f"Admin approve လုပ်ပြီးချင်း notification ရမည် ⏳",
            parse_mode="Markdown"
        )

        # Notify admin with Approve/Deny buttons
        uname = f"@{user.username}" if user.username else user.full_name
        kb = [
            [
                InlineKeyboardButton("✅ Approve 7d",   callback_data=f"apv7|{dev_key}|{user.id}"),
                InlineKeyboardButton("✅ Approve 30d",  callback_data=f"apv30|{dev_key}|{user.id}"),
            ],
            [
                InlineKeyboardButton("⚙️ Custom Days",  callback_data=f"apvc|{dev_key}|{user.id}"),
                InlineKeyboardButton("❌ Deny",          callback_data=f"deny|{dev_key}|{user.id}"),
            ],
        ]
        await ctx.bot.send_message(
            ADMIN_ID,
            f"📨 *Key Request*\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"👤 User  : {uname} (`{user.id}`)\n"
            f"🔑 Key   : `{dev_key}`\n"
            f"🕐 Time  : {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            f"━━━━━━━━━━━━━━━━━",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(kb)
        )
    else:
        await update.message.reply_text(
            "❓ Device ID ကို ဒီ format နဲ့ ပို့ပါ:\n`DEV-XXXXXXXXXXXX`",
            parse_mode="Markdown"
        )

# ─── APPROVE / DENY CALLBACKS ─────────────────────────────────────────────────
async def handle_callbacks(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q    = update.callback_query
    await q.answer()
    data = q.data

    # ── APPROVE (7d / 30d / custom) ──
    if data.startswith("apv"):
        parts   = data.split("|")
        action  = parts[0]   # apv7 / apv30 / apvc
        dev_key = parts[1]
        user_id = int(parts[2])

        if action == "apvc":
            # Custom days — ask admin
            ctx.user_data["apvc_key"] = dev_key
            ctx.user_data["apvc_uid"] = user_id
            await q.message.reply_text(
                f"⚙️ `{dev_key}` ကို ဘယ်နှစ်ရက် approve မလဲ?\n(0 = Permanent)",
                parse_mode="Markdown"
            )
            return SET_DAYS_APPROVE

        days   = 7 if action == "apv7" else 30
        expiry = days_to_ts(days)
        keys   = load_keys()
        keys[dev_key] = expiry
        save_keys(keys)

        # Update request status
        reqs = load_requests()
        if dev_key in reqs:
            reqs[dev_key]["status"] = "approved"
            save_requests(reqs)

        # Edit admin message
        await q.message.edit_text(
            q.message.text + f"\n\n✅ *Approved {days}d* — {ts_to_str(expiry)}",
            parse_mode="Markdown"
        )

        # Notify user
        try:
            await ctx.bot.send_message(
                user_id,
                f"🎉 *Key Approved!*\n\n"
                f"🔑 Key   : `{dev_key}`\n"
                f"⏳ Expiry: *{days} ရက်*\n"
                f"📅 Until : {datetime.fromtimestamp(expiry).strftime('%Y-%m-%d')}\n\n"
                f"Tool ကို ပြန် Run ပြီး Option 5 (Reset) နှိပ်ပါ ✔",
                parse_mode="Markdown"
            )
        except Exception as e:
            logging.warning(f"Cannot notify user {user_id}: {e}")

    # ── DENY ──
    elif data.startswith("deny"):
        parts   = data.split("|")
        dev_key = parts[1]
        user_id = int(parts[2])

        reqs = load_requests()
        if dev_key in reqs:
            reqs[dev_key]["status"] = "denied"
            save_requests(reqs)

        await q.message.edit_text(
            q.message.text + "\n\n❌ *Denied*",
            parse_mode="Markdown"
        )
        try:
            await ctx.bot.send_message(
                user_id,
                f"❌ *Key Denied*\n\n"
                f"Key `{dev_key}` ကို admin က deny လုပ်သည်။\n"
                f"ပြဿနာရှိရင် admin ကို ဆက်သွယ်ပါ။",
                parse_mode="Markdown"
            )
        except Exception as e:
            logging.warning(f"Cannot notify user {user_id}: {e}")

    # ── PENDING LIST ──
    elif data == "pending":
        if not is_admin(update): return
        reqs = load_requests()
        pending = {k:v for k,v in reqs.items() if v.get("status") == "pending"}
        if not pending:
            await q.message.reply_text("📭 Pending request မရှိပါ")
            return
        lines = ["📨 *Pending Requests*\n━━━━━━━━━━━━━━━━━"]
        for dev_key, info in pending.items():
            uname = f"@{info['username']}" if info.get('username') else info.get('name','?')
            lines.append(
                f"🔑 `{dev_key}`\n"
                f"   👤 {uname}  🕐 {info.get('requested','')}"
            )
            kb_row = [
                InlineKeyboardButton("✅ 7d",  callback_data=f"apv7|{dev_key}|{info['user_id']}"),
                InlineKeyboardButton("✅ 30d", callback_data=f"apv30|{dev_key}|{info['user_id']}"),
                InlineKeyboardButton("❌ Deny",callback_data=f"deny|{dev_key}|{info['user_id']}"),
            ]
            await q.message.reply_text(
                f"📨 *Request*\n🔑 `{dev_key}`\n👤 {uname}",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([kb_row])
            )
        return

    # ── LIST ──
    elif data == "list":
        if not is_admin(update): return
        await show_list(update, ctx)
        return

    # ── ADD ──
    elif data == "add":
        if not is_admin(update): return
        await q.message.reply_text(
            "➕ *Key ထည့်ရန်*\n\nDevice Key ထည့်ပါ:\n`DEV-XXXXXXXXXXXX`",
            parse_mode="Markdown"
        )
        return ADD_KEY

    # ── REMOVE ──
    elif data == "remove":
        if not is_admin(update): return
        await q.message.reply_text(
            "🗑 *Key ဖျက်ရန်*\n\nDevice Key ထည့်ပါ:\n`DEV-XXXXXXXXXXXX`",
            parse_mode="Markdown"
        )
        return REMOVE_KEY

    # ── EXTEND ──
    elif data == "extend":
        if not is_admin(update): return
        await q.message.reply_text(
            "⏫ *Key တိုးရန်*\n\nDevice Key ထည့်ပါ:\n`DEV-XXXXXXXXXXXX`",
            parse_mode="Markdown"
        )
        return EXTEND_KEY

    # ── CHECK ──
    elif data == "check":
        if not is_admin(update): return
        await q.message.reply_text(
            "🔍 *Key စစ်ရန်*\n\nDevice Key ထည့်ပါ:\n`DEV-XXXXXXXXXXXX`",
            parse_mode="Markdown"
        )
        return CHECK_KEY

    # ── FETCH ──
    elif data == "fetch":
        if not is_admin(update): return
        await do_fetch(update, ctx)

    # ── EXPIRED ──
    elif data == "expired":
        if not is_admin(update): return
        await show_expired(update, ctx)

    # ── CLEAN ──
    elif data == "clean":
        if not is_admin(update): return
        await do_clean(update, ctx)

    # ── BROADCAST ──
    elif data == "broadcast":
        if not is_admin(update): return
        await q.message.reply_text(
            "📢 *Broadcast Message*\n\nUser အားလုံးကို ပို့မည့် message ရေးပါ:",
            parse_mode="Markdown"
        )
        return BROADCAST_MSG

# ─── CUSTOM DAYS APPROVE ──────────────────────────────────────────────────────
async def set_days_approve(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update): return ConversationHandler.END
    try:
        days = int(update.message.text.strip())
    except:
        await update.message.reply_text("❌ ဂဏန်းတစ်ခု ထည့်ပါ")
        return SET_DAYS_APPROVE

    dev_key = ctx.user_data.get("apvc_key")
    user_id = ctx.user_data.get("apvc_uid")
    expiry  = 9999999999 if days == 0 else days_to_ts(days)
    keys    = load_keys()
    keys[dev_key] = expiry
    save_keys(keys)

    reqs = load_requests()
    if dev_key in reqs:
        reqs[dev_key]["status"] = "approved"
        save_requests(reqs)

    label = "♾️ Permanent" if days == 0 else f"{days} ရက်"
    await update.message.reply_text(
        f"✅ *Approved!*\n🔑 `{dev_key}`\n⏳ {label}",
        parse_mode="Markdown"
    )
    try:
        await ctx.bot.send_message(
            user_id,
            f"🎉 *Key Approved!*\n\n"
            f"🔑 Key: `{dev_key}`\n"
            f"⏳ Expiry: *{label}*\n\n"
            f"Tool ကို ပြန် Run ပြီး Option 5 (Reset) နှိပ်ပါ ✔",
            parse_mode="Markdown"
        )
    except: pass
    ctx.user_data.clear()
    return ConversationHandler.END

# ─── BROADCAST ────────────────────────────────────────────────────────────────
async def do_broadcast(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update): return ConversationHandler.END
    msg  = update.message.text.strip()
    reqs = load_requests()
    sent = fail = 0
    user_ids = set(str(v["user_id"]) for v in reqs.values() if "user_id" in v)
    for uid in user_ids:
        try:
            await ctx.bot.send_message(int(uid), f"📢 *Admin Message*\n\n{msg}", parse_mode="Markdown")
            sent += 1
        except:
            fail += 1
    await update.message.reply_text(
        f"📢 Broadcast ပြီးပြီ\n✅ Sent: {sent}  ❌ Failed: {fail}",
        parse_mode="Markdown"
    )
    return ConversationHandler.END

# ─── LIST ─────────────────────────────────────────────────────────────────────
async def show_list(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    keys = load_keys()
    msg  = update.callback_query.message if update.callback_query else update.message
    if not keys:
        await msg.reply_text("📭 Key မရှိသေးပါ"); return
    now    = datetime.now().timestamp()
    active = {k:v for k,v in keys.items() if v > now}
    expired= {k:v for k,v in keys.items() if v <= now}
    lines  = ["📋 *Key List*\n━━━━━━━━━━━━━━━━━"]
    for k,v in sorted(active.items(), key=lambda x:x[1]):
        lines.append(f"`{k}`\n  {ts_to_str(v)}")
    if expired:
        lines.append("\n*Expired:*")
        for k,v in sorted(expired.items(), key=lambda x:x[1]):
            lines.append(f"`{k}`\n  {ts_to_str(v)}")
    lines.append(f"\n━━━━━━━━━━━━━━━━━\n✅`{len(active)}`  ❌`{len(expired)}`  📦`{len(keys)}`")
    text = "\n".join(lines)
    chunks = [text[i:i+3800] for i in range(0, len(text), 3800)]
    for chunk in chunks:
        await msg.reply_text(chunk, parse_mode="Markdown")

# ─── ADD KEY CONV ─────────────────────────────────────────────────────────────
async def add_key_input(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update): return ConversationHandler.END
    dev_key = update.message.text.strip().upper()
    if not dev_key.startswith("DEV-") or len(dev_key) != 16:
        await update.message.reply_text("❌ Format: `DEV-XXXXXXXXXXXX`", parse_mode="Markdown")
        return ADD_KEY
    ctx.user_data["add_key"] = dev_key
    await update.message.reply_text(
        f"Key: `{dev_key}`\nရက်အရေအတွက်? (0=Permanent)", parse_mode="Markdown"
    )
    return ADD_DAYS

async def add_days_input(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update): return ConversationHandler.END
    try: days = int(update.message.text.strip())
    except:
        await update.message.reply_text("❌ ဂဏန်းထည့်ပါ"); return ADD_DAYS
    dev_key = ctx.user_data.get("add_key")
    expiry  = 9999999999 if days == 0 else days_to_ts(days)
    keys    = load_keys(); keys[dev_key] = expiry; save_keys(keys)
    label   = "♾️ Permanent" if days == 0 else f"{days} ရက်"
    await update.message.reply_text(
        f"✅ *Approved!*\n🔑 `{dev_key}`\n⏳ {label}\n{ts_to_str(expiry)}",
        parse_mode="Markdown"
    )
    ctx.user_data.clear(); return ConversationHandler.END

# ─── REMOVE KEY CONV ──────────────────────────────────────────────────────────
async def remove_key_input(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update): return ConversationHandler.END
    dev_key = update.message.text.strip().upper()
    keys    = load_keys()
    if dev_key not in keys:
        await update.message.reply_text(f"❌ `{dev_key}` မတွေ့ပါ", parse_mode="Markdown")
        return REMOVE_KEY
    del keys[dev_key]; save_keys(keys)
    await update.message.reply_text(f"🗑 `{dev_key}` ဖျက်ပြီး", parse_mode="Markdown")
    return ConversationHandler.END

# ─── EXTEND KEY CONV ──────────────────────────────────────────────────────────
async def extend_key_input(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update): return ConversationHandler.END
    dev_key = update.message.text.strip().upper()
    keys    = load_keys()
    if dev_key not in keys:
        await update.message.reply_text(f"❌ `{dev_key}` မတွေ့ပါ", parse_mode="Markdown")
        return EXTEND_KEY
    ctx.user_data["extend_key"] = dev_key
    await update.message.reply_text(
        f"Key: `{dev_key}`\nလက်ရှိ: {ts_to_str(keys[dev_key])}\nဘယ်နှစ်ရက် တိုးမလဲ?",
        parse_mode="Markdown"
    )
    return EXTEND_DAYS

async def extend_days_input(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update): return ConversationHandler.END
    try: extra = int(update.message.text.strip())
    except:
        await update.message.reply_text("❌ ဂဏန်းထည့်ပါ"); return EXTEND_DAYS
    dev_key = ctx.user_data.get("extend_key")
    keys    = load_keys()
    base    = max(keys[dev_key], datetime.now().timestamp())
    keys[dev_key] = int(base + extra * 86400); save_keys(keys)
    await update.message.reply_text(
        f"✅ `{dev_key}`\n+{extra} ရက် တိုးပြီး\nNew: {ts_to_str(keys[dev_key])}",
        parse_mode="Markdown"
    )
    ctx.user_data.clear(); return ConversationHandler.END

# ─── CHECK KEY CONV ───────────────────────────────────────────────────────────
async def check_key_input(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update): return ConversationHandler.END
    dev_key = update.message.text.strip().upper()
    keys    = load_keys()
    reqs    = load_requests()
    if dev_key in keys:
        req_info = reqs.get(dev_key, {})
        uname = req_info.get("name", "Unknown") if req_info else "Unknown"
        await update.message.reply_text(
            f"🔍 *Key Info*\n\n🔑 `{dev_key}`\n"
            f"👤 User  : {uname}\n"
            f"📅 Status: {ts_to_str(keys[dev_key])}",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            f"❌ `{dev_key}` — Not Registered", parse_mode="Markdown"
        )
    return ConversationHandler.END

# ─── FETCH / EXPIRED / CLEAN ──────────────────────────────────────────────────
async def do_fetch(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.callback_query.message if update.callback_query else update.message
    wait = await msg.reply_text("🔄 Fetching...")
    try:
        r    = requests.get(API_URL, timeout=10)
        data = r.json().get("expirations", {})
        save_keys(data)
        now  = datetime.now().timestamp()
        act  = sum(1 for v in data.values() if v > now)
        await wait.edit_text(
            f"✅ Sync OK!\n📦 Total: `{len(data)}`  ✅ Active: `{act}`",
            parse_mode="Markdown"
        )
    except Exception as e:
        await wait.edit_text(f"❌ Error: `{e}`", parse_mode="Markdown")

async def show_expired(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg  = update.callback_query.message if update.callback_query else update.message
    keys = load_keys(); now = datetime.now().timestamp()
    exp  = {k:v for k,v in keys.items() if v <= now}
    sn   = {k:v for k,v in keys.items() if 0 < v-now < 3*86400}
    if not exp and not sn:
        await msg.reply_text("✅ Key အားလုံး Active"); return
    lines = ["⚠️ *Expired / Expiring Soon*\n"]
    if exp:
        lines.append("*Expired:*")
        for k,v in exp.items():
            lines.append(f"❌ `{k}`  ({datetime.fromtimestamp(v).strftime('%Y-%m-%d')})")
    if sn:
        lines.append("\n*Soon (<3d):*")
        for k,v in sn.items():
            lines.append(f"🟡 `{k}`  {ts_to_str(v)}")
    await msg.reply_text("\n".join(lines), parse_mode="Markdown")

async def do_clean(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg  = update.callback_query.message if update.callback_query else update.message
    keys = load_keys(); now = datetime.now().timestamp()
    before  = len(keys)
    cleaned = {k:v for k,v in keys.items() if v > now}
    save_keys(cleaned)
    await msg.reply_text(
        f"🧹 Done!\nRemoved: `{before-len(cleaned)}`  Remaining: `{len(cleaned)}`",
        parse_mode="Markdown"
    )

# ─── /mystatus (user command) ─────────────────────────────────────────────────
async def my_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if is_admin(update): return
    user = update.effective_user
    reqs = load_requests()
    keys = load_keys()
    uid  = str(user.id)
    user_key = next((k for k,v in reqs.items() if str(v.get("user_id"))==uid), None)
    if user_key and user_key in keys:
        await update.message.reply_text(
            f"🔑 Key: `{user_key}`\nStatus: {ts_to_str(keys[user_key])}",
            parse_mode="Markdown"
        )
    elif user_key:
        await update.message.reply_text(
            f"⏳ Request pending — Admin approve လုပ်နေသည်..."
        )
    else:
        await update.message.reply_text(
            "❌ Key မရှိသေး — `DEV-XXXXXXXXXXXX` ပို့ပြီး Request လုပ်ပါ"
        )

async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data.clear()
    await update.message.reply_text("❌ ပယ်ဖျက်ပြီး /start ပြန်နှိပ်ပါ")
    return ConversationHandler.END

# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_callbacks)],
        states={
            ADD_KEY:          [MessageHandler(filters.TEXT & ~filters.COMMAND, add_key_input)],
            ADD_DAYS:         [MessageHandler(filters.TEXT & ~filters.COMMAND, add_days_input)],
            REMOVE_KEY:       [MessageHandler(filters.TEXT & ~filters.COMMAND, remove_key_input)],
            EXTEND_KEY:       [MessageHandler(filters.TEXT & ~filters.COMMAND, extend_key_input)],
            EXTEND_DAYS:      [MessageHandler(filters.TEXT & ~filters.COMMAND, extend_days_input)],
            CHECK_KEY:        [MessageHandler(filters.TEXT & ~filters.COMMAND, check_key_input)],
            SET_DAYS_APPROVE: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_days_approve)],
            BROADCAST_MSG:    [MessageHandler(filters.TEXT & ~filters.COMMAND, do_broadcast)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False,
    )

    app.add_handler(CommandHandler("start",    start))
    app.add_handler(CommandHandler("mystatus", my_status))
    app.add_handler(CommandHandler("cancel",   cancel))
    app.add_handler(conv)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_message))

    print("🤖 Key Admin Bot v2.0 running...")
    print(f"   Admin ID : {ADMIN_ID}")
    print(f"   Bot Link : https://t.me/{app.bot.username if hasattr(app,'bot') else '...'}")
    print()
    print("   User Flow:")
    print("   User → DEV-XXX ပို့ → Admin notification → Approve/Deny → User auto-reply")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
