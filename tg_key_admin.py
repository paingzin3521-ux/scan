#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════╗
║     TELEGRAM KEY ADMIN BOT v1.0         ║
║   passbot-e08t.onrender.com             ║
╚══════════════════════════════════════════╝

Install:
  pip install python-telegram-bot requests

Run:
  python tg_key_admin.py
"""

import os, json, logging, requests
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

# ─── CONFIG ───────────────────────────────────────────────────────────────────
BOT_TOKEN  = os.environ.get("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN")
ADMIN_ID   = int(os.environ.get("TELEGRAM_ADMIN_ID", "0"))
API_URL    = "https://passbot-e08t.onrender.com/api/keys"
LOCAL_FILE = os.path.join(os.path.expanduser("~"), ".key_admin", "keys.json")

os.makedirs(os.path.dirname(LOCAL_FILE), exist_ok=True)
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# ─── CONVERSATION STATES ──────────────────────────────────────────────────────
ADD_KEY, ADD_DAYS, REMOVE_KEY, EXTEND_KEY, EXTEND_DAYS, CHECK_KEY = range(6)

# ─── KEY HELPERS ──────────────────────────────────────────────────────────────
def load_keys():
    if os.path.exists(LOCAL_FILE):
        try:
            with open(LOCAL_FILE) as f:
                return json.load(f).get("expirations", {})
        except:
            pass
    return {}

def save_keys(keys):
    with open(LOCAL_FILE, "w") as f:
        json.dump({"expirations": keys}, f, indent=2)

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
            return f"♾️ Permanent"
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

def admin_only(func):
    async def wrapper(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if not is_admin(update):
            await update.effective_message.reply_text("⛔ Admin only.")
            return ConversationHandler.END
        return await func(update, ctx)
    return wrapper

# ─── /start ───────────────────────────────────────────────────────────────────
@admin_only
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    keys  = load_keys()
    now   = datetime.now().timestamp()
    act   = sum(1 for v in keys.values() if v > now)
    exp   = len(keys) - act
    text  = (
        "🔑 *Key Admin Bot*\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"✅ Active : `{act}`\n"
        f"❌ Expired: `{exp}`\n"
        f"📦 Total  : `{len(keys)}`\n"
        f"━━━━━━━━━━━━━━━━━"
    )
    kb = [
        [InlineKeyboardButton("📋 List Keys",    callback_data="list"),
         InlineKeyboardButton("➕ Add Key",       callback_data="add")],
        [InlineKeyboardButton("🗑 Remove Key",   callback_data="remove"),
         InlineKeyboardButton("⏫ Extend Key",    callback_data="extend")],
        [InlineKeyboardButton("🔍 Check Key",    callback_data="check"),
         InlineKeyboardButton("🔄 Sync Server",  callback_data="fetch")],
        [InlineKeyboardButton("⚠️ Expired List", callback_data="expired"),
         InlineKeyboardButton("🧹 Clean Expired",callback_data="clean")],
    ]
    await update.message.reply_text(
        text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# ─── MENU BUTTON ──────────────────────────────────────────────────────────────
async def menu_button(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.callback_query.answer("⛔ Admin only.")
        return
    q = update.callback_query
    await q.answer()
    data = q.data

    if data == "list":
        await show_list(update, ctx)
    elif data == "add":
        await q.message.reply_text(
            "➕ *Key ထည့်ရန်*\n\nDevice Key ထည့်ပါ:\n`DEV-XXXXXXXXXXXX`",
            parse_mode="Markdown"
        )
        return ADD_KEY
    elif data == "remove":
        keys = load_keys()
        if not keys:
            await q.message.reply_text("📭 Key မရှိသေးပါ")
            return
        await q.message.reply_text(
            "🗑 *Key ဖျက်ရန်*\n\nDevice Key ထည့်ပါ:\n`DEV-XXXXXXXXXXXX`",
            parse_mode="Markdown"
        )
        return REMOVE_KEY
    elif data == "extend":
        keys = load_keys()
        if not keys:
            await q.message.reply_text("📭 Key မရှိသေးပါ")
            return
        await q.message.reply_text(
            "⏫ *Key သက်တမ်းတိုးရန်*\n\nDevice Key ထည့်ပါ:\n`DEV-XXXXXXXXXXXX`",
            parse_mode="Markdown"
        )
        return EXTEND_KEY
    elif data == "check":
        await q.message.reply_text(
            "🔍 *Key စစ်ဆေးရန်*\n\nDevice Key ထည့်ပါ:\n`DEV-XXXXXXXXXXXX`",
            parse_mode="Markdown"
        )
        return CHECK_KEY
    elif data == "fetch":
        await do_fetch(update, ctx)
    elif data == "expired":
        await show_expired(update, ctx)
    elif data == "clean":
        await do_clean(update, ctx)

# ─── LIST ─────────────────────────────────────────────────────────────────────
async def show_list(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    keys = load_keys()
    msg  = update.callback_query.message if update.callback_query else update.message
    if not keys:
        await msg.reply_text("📭 Key မရှိသေးပါ")
        return

    now    = datetime.now().timestamp()
    active = {k:v for k,v in keys.items() if v > now}
    expired= {k:v for k,v in keys.items() if v <= now}

    lines = ["📋 *Key List*\n━━━━━━━━━━━━━━━━━"]
    for k, v in sorted(active.items(), key=lambda x: x[1]):
        lines.append(f"`{k}`\n  {ts_to_str(v)}")
    if expired:
        lines.append("\n*Expired:*")
        for k, v in sorted(expired.items(), key=lambda x: x[1]):
            lines.append(f"`{k}`\n  {ts_to_str(v)}")
    lines.append(f"\n━━━━━━━━━━━━━━━━━")
    lines.append(f"✅ `{len(active)}`  ❌ `{len(expired)}`  📦 `{len(keys)}`")

    text = "\n".join(lines)
    # Split if too long
    if len(text) > 4000:
        chunks = []
        current = ""
        for line in lines:
            if len(current) + len(line) > 3800:
                chunks.append(current)
                current = ""
            current += line + "\n"
        if current:
            chunks.append(current)
        for chunk in chunks:
            await msg.reply_text(chunk, parse_mode="Markdown")
    else:
        await msg.reply_text(text, parse_mode="Markdown")

# ─── ADD KEY ──────────────────────────────────────────────────────────────────
async def add_key_input(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return ConversationHandler.END
    dev_key = update.message.text.strip().upper()
    if not dev_key.startswith("DEV-") or len(dev_key) != 16:
        await update.message.reply_text(
            "❌ Format မမှန်ပါ\n\n`DEV-XXXXXXXXXXXX` (DEV- နောက် 12 လုံး)",
            parse_mode="Markdown"
        )
        return ADD_KEY
    ctx.user_data["add_key"] = dev_key
    keys = load_keys()
    exists = "⚠️ ရှိပြီးသား — overwrite ဖြစ်မည်\n\n" if dev_key in keys else ""
    await update.message.reply_text(
        f"{exists}✅ Key: `{dev_key}`\n\nရက်အရေအတွက် ထည့်ပါ:\n"
        "`7` = 1 week  |  `30` = 1 month  |  `0` = Permanent",
        parse_mode="Markdown"
    )
    return ADD_DAYS

async def add_days_input(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return ConversationHandler.END
    try:
        days = int(update.message.text.strip())
    except:
        await update.message.reply_text("❌ ဂဏန်းတစ်ခု ထည့်ပါ (e.g. 30)")
        return ADD_DAYS

    dev_key = ctx.user_data.get("add_key")
    expiry  = 9999999999 if days == 0 else days_to_ts(days)
    keys    = load_keys()
    keys[dev_key] = expiry
    save_keys(keys)

    label = "♾️ Permanent" if days == 0 else f"{days} ရက်"
    await update.message.reply_text(
        f"✅ *Key Approved!*\n\n"
        f"Key   : `{dev_key}`\n"
        f"Expiry: `{label}`\n"
        f"Status: {ts_to_str(expiry)}",
        parse_mode="Markdown"
    )
    ctx.user_data.clear()
    return ConversationHandler.END

# ─── REMOVE KEY ───────────────────────────────────────────────────────────────
async def remove_key_input(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return ConversationHandler.END
    dev_key = update.message.text.strip().upper()
    keys    = load_keys()
    if dev_key not in keys:
        await update.message.reply_text(
            f"❌ `{dev_key}` မတွေ့ပါ", parse_mode="Markdown"
        )
        return REMOVE_KEY
    del keys[dev_key]
    save_keys(keys)
    await update.message.reply_text(
        f"🗑 *Key Removed!*\n\n`{dev_key}` ကို ဖျက်ပြီးပြီ",
        parse_mode="Markdown"
    )
    return ConversationHandler.END

# ─── EXTEND KEY ───────────────────────────────────────────────────────────────
async def extend_key_input(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return ConversationHandler.END
    dev_key = update.message.text.strip().upper()
    keys    = load_keys()
    if dev_key not in keys:
        await update.message.reply_text(
            f"❌ `{dev_key}` မတွေ့ပါ", parse_mode="Markdown"
        )
        return EXTEND_KEY
    ctx.user_data["extend_key"] = dev_key
    await update.message.reply_text(
        f"⏫ Key: `{dev_key}`\n"
        f"လက်ရှိ: {ts_to_str(keys[dev_key])}\n\n"
        f"ဘယ်နှစ်ရက် တိုးမလဲ?",
        parse_mode="Markdown"
    )
    return EXTEND_DAYS

async def extend_days_input(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return ConversationHandler.END
    try:
        extra = int(update.message.text.strip())
    except:
        await update.message.reply_text("❌ ဂဏန်းတစ်ခု ထည့်ပါ")
        return EXTEND_DAYS

    dev_key = ctx.user_data.get("extend_key")
    keys    = load_keys()
    now_ts  = datetime.now().timestamp()
    base    = max(keys[dev_key], now_ts)
    keys[dev_key] = int(base + extra * 86400)
    save_keys(keys)

    await update.message.reply_text(
        f"✅ *Extended!*\n\n"
        f"Key   : `{dev_key}`\n"
        f"Added : `+{extra} ရက်`\n"
        f"New   : {ts_to_str(keys[dev_key])}",
        parse_mode="Markdown"
    )
    ctx.user_data.clear()
    return ConversationHandler.END

# ─── CHECK KEY ────────────────────────────────────────────────────────────────
async def check_key_input(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return ConversationHandler.END
    dev_key = update.message.text.strip().upper()
    keys    = load_keys()
    if dev_key in keys:
        await update.message.reply_text(
            f"🔍 *Key Info*\n\n"
            f"Key   : `{dev_key}`\n"
            f"Status: {ts_to_str(keys[dev_key])}",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            f"❌ `{dev_key}` မတွေ့ပါ — Not Registered",
            parse_mode="Markdown"
        )
    return ConversationHandler.END

# ─── FETCH FROM SERVER ────────────────────────────────────────────────────────
async def do_fetch(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.callback_query.message if update.callback_query else update.message
    wait = await msg.reply_text("🔄 Server မှ ဆွဲယူနေသည်...")
    try:
        r    = requests.get(API_URL, timeout=10)
        data = r.json().get("expirations", {})
        save_keys(data)
        now    = datetime.now().timestamp()
        active = sum(1 for v in data.values() if v > now)
        await wait.edit_text(
            f"✅ *Sync Complete!*\n\n"
            f"📦 Total  : `{len(data)}`\n"
            f"✅ Active : `{active}`\n"
            f"❌ Expired: `{len(data)-active}`",
            parse_mode="Markdown"
        )
    except Exception as e:
        await wait.edit_text(f"❌ Server Error: `{e}`", parse_mode="Markdown")

# ─── EXPIRED LIST ─────────────────────────────────────────────────────────────
async def show_expired(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg  = update.callback_query.message if update.callback_query else update.message
    keys = load_keys()
    now  = datetime.now().timestamp()
    exp  = {k:v for k,v in keys.items() if v <= now}
    sn   = {k:v for k,v in keys.items() if 0 < v - now < 3*86400}

    if not exp and not sn:
        await msg.reply_text("✅ Key အားလုံး Active — ပြဿနာမရှိပါ")
        return

    lines = ["⚠️ *Expired / Expiring Soon*\n"]
    if exp:
        lines.append("*Expired:*")
        for k, v in exp.items():
            dt = datetime.fromtimestamp(v).strftime("%Y-%m-%d")
            lines.append(f"❌ `{k}`  ({dt})")
    if sn:
        lines.append("\n*Expiring < 3 days:*")
        for k, v in sn.items():
            lines.append(f"🟡 `{k}`  {ts_to_str(v)}")

    await msg.reply_text("\n".join(lines), parse_mode="Markdown")

# ─── CLEAN EXPIRED ────────────────────────────────────────────────────────────
async def do_clean(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg  = update.callback_query.message if update.callback_query else update.message
    keys = load_keys()
    now  = datetime.now().timestamp()
    before  = len(keys)
    cleaned = {k:v for k,v in keys.items() if v > now}
    removed = before - len(cleaned)
    save_keys(cleaned)
    await msg.reply_text(
        f"🧹 *Clean Complete!*\n\n"
        f"Removed : `{removed}` expired keys\n"
        f"Remaining: `{len(cleaned)}` active keys",
        parse_mode="Markdown"
    )

# ─── CANCEL ───────────────────────────────────────────────────────────────────
async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data.clear()
    await update.message.reply_text("❌ ပယ်ဖျက်ပြီး /start ကို ပြန်နှိပ်ပါ")
    return ConversationHandler.END

# ─── UNKNOWN ──────────────────────────────────────────────────────────────────
async def unknown(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return
    await update.message.reply_text("❓ /start နှိပ်ပြီး menu ဖွင့်ပါ")

# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Conversation handler
    conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(menu_button)],
        states={
            ADD_KEY:     [MessageHandler(filters.TEXT & ~filters.COMMAND, add_key_input)],
            ADD_DAYS:    [MessageHandler(filters.TEXT & ~filters.COMMAND, add_days_input)],
            REMOVE_KEY:  [MessageHandler(filters.TEXT & ~filters.COMMAND, remove_key_input)],
            EXTEND_KEY:  [MessageHandler(filters.TEXT & ~filters.COMMAND, extend_key_input)],
            EXTEND_DAYS: [MessageHandler(filters.TEXT & ~filters.COMMAND, extend_days_input)],
            CHECK_KEY:   [MessageHandler(filters.TEXT & ~filters.COMMAND, check_key_input)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False,
    )

    app.add_handler(CommandHandler("start",   start))
    app.add_handler(CommandHandler("list",    lambda u,c: show_list(u,c)))
    app.add_handler(CommandHandler("fetch",   do_fetch))
    app.add_handler(CommandHandler("expired", show_expired))
    app.add_handler(CommandHandler("clean",   do_clean))
    app.add_handler(conv)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))

    print("🤖 Key Admin Bot running...")
    print(f"   Admin ID : {ADMIN_ID}")
    print(f"   Keys file: {LOCAL_FILE}")
    print("   /start — menu ဖွင့်ပါ")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
