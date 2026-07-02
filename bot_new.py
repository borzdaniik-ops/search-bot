import re, logging, aiohttp, random, string
from datetime import date
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT = "8640914849:AAF5NCl4ajFrFR81VbdIHzRFvfANHWB6Wf4"
DONATE = "https://dalink.to/daniksayko"
ADMIN = 7783324307
WL = {8562396880}
BANNED = set()
MY = "+79963212799"

logging.basicConfig(level=logging.INFO)
FREE = {}
CODES = {}
PAID = {}
STATS = {}
LAST = {}

def gf(uid):
    t = str(date.today())
    if uid in FREE and FREE[uid]["date"] == t: return FREE[uid]["count"]
    FREE[uid] = {"count":2,"date":t}
    return 2

def uf(uid):
    t = str(date.today())
    if uid in FREE and FREE[uid]["date"] == t: FREE[uid]["count"] -= 1
    else: FREE[uid] = {"count":1,"date":t}

def ok(uid): return uid == ADMIN or uid in WL or (uid in PAID and PAID[uid] > 0)

def up(uid):
    if uid in PAID and PAID[uid] > 0:
        PAID[uid] -= 1
        return True
    return False

async def info(p):
    c = p.lstrip("+")
    return f"🔍 *Номер {p}:*\n🌍 [Numverify](https://numverify.com)\n📞 [KtoZvonil](https://ktozvonil.ru/phone/{c})"

async def messengers(phone):
    c = phone.lstrip("+")
    return f"💬 [WhatsApp](https://wa.me/{c}) | [Viber](https://viber.click/{c}) | [Telegram](https://t.me/+{c}) | [Signal](https://signal.me/+{c})"

async def all_links(phone):
    c = phone.lstrip("+")
    return f"🌍 [NumLookup](https://numlookup.com/phone/{c}) | [SpyDialer](https://spydialer.com/phone/{c}) | [Truecaller](https://truecaller.com/search/{c})"

async def nick(n):
    sites = {"📷 Instagram":f"instagram.com/{n}","🐦 Twitter":f"twitter.com/{n}","💻 GitHub":f"github.com/{n}","🎵 TikTok":f"tiktok.com/@{n}","📘 VK":f"vk.com/{n}","▶️ YouTube":f"youtube.com/@{n}","👽 Reddit":f"reddit.com/user/{n}","🎮 Twitch":f"twitch.tv/{n}","🎯 Steam":f"steamcommunity.com/id/{n}","👤 Facebook":f"facebook.com/{n}","📌 Pinterest":f"pinterest.com/{n}","👻 Snapchat":f"snapchat.com/add/{n}"}
    return "\n".join([f"✅ {name}: [Ссылка](https://{url})" for name, url in sites.items()])

async def email_leak(email):
    return f"📧 [Have I Been Pwned](https://haveibeenpwned.com/account/{email}) | [LeakCheck](https://leakcheck.io/?check={email})"

async def ip_info(ip):
    return f"🌐 [ip-api.com](http://ip-api.com/{ip}) | [Whois](https://who.is/whois/{ip})"

async def start(update: Update, ctx):
    uid = update.effective_user.id
    f = gf(uid)
    p = PAID.get(uid,0)
    msg = (
        "```\n"
        "╔══════════════════════════╗\n"
        "║  🔍 ULTIMATE SEARCH v7.0  ║\n"
        "║     by @Vkgoy            ║\n"
        "╚══════════════════════════╝\n"
        "```\n\n"
        "👑 *ПРЕМИУМ-ПОИСК*\n\n"
        f"🆓 Бесплатно: `{f}/2`\n"
        f"💎 Куплено: `{p}`\n\n"
        "▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n\n"
        "📞 *НОМЕР ТЕЛЕФОНА*\n"
        "• 🔍 Ссылки на Numverify, KtoZvonil\n"
        "• 💬 Ссылки WhatsApp, Viber, Telegram, Signal\n"
        "• 🌍 Международные базы (NumLookup, SpyDialer, Truecaller)\n"
        "• 🔍 Поиск в Google и VK\n\n"
        "👤 *НИКНЕЙМ*\n"
        "• Ссылки на 12 соцсетей\n\n"
        "📧 *EMAIL*\n"
        "• Ссылки Have I Been Pwned, LeakCheck\n\n"
        "🌐 *IP* `/ip 8.8.8.8`\n"
        "💳 *BIN* `/bin 220431`\n"
        "🆔 *TG ID* `/id 123456789`\n"
        "🚗 *АВТО* `/car А123БВ177`\n"
        "📍 *АДРЕС* `/addr Москва`\n"
        "📸 *ФОТО* ссылки на поиск\n\n"
        "▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n\n"
        "💳 *ТАРИФЫ*\n"
        "🔥 5 запр. — 1.5$\n"
        "🔥 10 запр. — 3.0$\n"
        "🔥 15 запр. — 4.5$\n\n"
        f"💸 Оплата: {DONATE}\n"
        "🔑 /code КОД\n"
        "👤 /profile\n"
        "💾 /save\n"
        "📊 /stats\n\n"
        "⚡ *Отправь номер, ник, email или команду!*"
    ).format(f=f, p=p)
    await update.message.reply_text(msg, parse_mode="Markdown", disable_web_page_preview=True)

async def profile_cmd(update: Update, ctx):
    uid = update.effective_user.id
    f = gf(uid)
    p = PAID.get(uid,0)
    vip = "⭐ ДА" if (uid == ADMIN or uid in WL) else "❌ НЕТ"
    banned = "⛔ ДА" if uid in BANNED else "✅ НЕТ"
    msg = f"👤 *ПРОФИЛЬ*\n\n🆔 ID: `{uid}`\n🎁 Бесплатных: `{f}/2`\n💎 Куплено: `{p}`\n⭐ VIP: {vip}\n⛔ Бан: {banned}\n\n💸 Пополнить: {DONATE}"
    await update.message.reply_text(msg, parse_mode="Markdown", disable_web_page_preview=True)

async def code_cmd(update: Update, ctx):
    uid = update.effective_user.id
    if not ctx.args: return
    c = ctx.args[0].upper()
    if c in CODES:
        q = CODES.pop(c)
        PAID[uid] = PAID.get(uid,0) + q
        await update.message.reply_text(f"🎉 *+{q}* запросов. Баланс: `{PAID[uid]}`", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ *Неверный код*", parse_mode="Markdown")

async def gen_cmd(update: Update, ctx):
    if update.effective_user.id != ADMIN: return
    q = int(ctx.args[0]) if ctx.args else 5
    c = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    CODES[c] = q
    await update.message.reply_text(f"🎫 Код на `{q}`: `{c}`", parse_mode="Markdown")

async def vip_cmd(update: Update, ctx):
    if update.effective_user.id != ADMIN: return
    try: WL.add(int(ctx.args[0])); await update.message.reply_text(f"⭐ *VIP:* `{ctx.args[0]}`", parse_mode="Markdown")
    except: pass

async def unvip_cmd(update: Update, ctx):
    if update.effective_user.id != ADMIN: return
    try: WL.discard(int(ctx.args[0])); await update.message.reply_text(f"❌ *Не VIP:* `{ctx.args[0]}`", parse_mode="Markdown")
    except: pass

async def list_cmd(update: Update, ctx):
    if update.effective_user.id != ADMIN: return
    await update.message.reply_text(f"VIP: {WL}\nКоды: {CODES}")

async def stats_cmd(update: Update, ctx):
    if update.effective_user.id != ADMIN: return
    top = sorted(STATS.items(), key=lambda x: x[1], reverse=True)[:10]
    msg = "📊 *Топ-10:*\n\n" + "\n".join([f"📞 `{p}` — {c} раз" for p, c in top])
    await update.message.reply_text(msg, parse_mode="Markdown")

async def save_cmd(update: Update, ctx):
    uid = update.effective_user.id
    if uid not in LAST: await update.message.reply_text("❌ Нет результатов"); return
    await update.message.reply_text(LAST[uid], parse_mode="Markdown", disable_web_page_preview=True)

async def handle(update: Update, ctx):
    uid = update.effective_user.id
    t = update.message.text.strip() if update.message.text else ""
    
    if update.message.photo:
        if not ok(uid) and gf(uid) <= 0: await update.message.reply_text(f"🔒 Нет доступа\n{DONATE}"); return
        await update.message.reply_text("📸 *Поиск по фото:*\n\n🔍 [Google Images](https://lens.google.com)\n🔍 [Yandex Images](https://yandex.ru/images)\n🔍 [FaceCheck](https://facecheck.id)\n🔍 [Search4faces](https://search4faces.com)", parse_mode="Markdown", disable_web_page_preview=True)
        return
    
    if t.startswith("/car "):
        if not ok(uid) and gf(uid) <= 0: await update.message.reply_text(f"🔒 Нет доступа\n{DONATE}"); return
        await update.message.reply_text(f"🚗 *Авто:* [Поиск](https://carnumber.ru/api/v1?number={t[5:].strip().upper()})", parse_mode="Markdown", disable_web_page_preview=True)
        return
    if t.startswith("/addr "):
        if not ok(uid) and gf(uid) <= 0: await update.message.reply_text(f"🔒 Нет доступа\n{DONATE}"); return
        await update.message.reply_text(f"📍 *Адрес:* [Поиск](https://nominatim.openstreetmap.org/search?q={t[6:].strip()})", parse_mode="Markdown", disable_web_page_preview=True)
        return
    if t.startswith("/bin "):
        if not ok(uid) and gf(uid) <= 0: await update.message.reply_text(f"🔒 Нет доступа\n{DONATE}"); return
        await update.message.reply_text(f"💳 *BIN:* [Поиск](https://lookup.binlist.net/{t[5:].strip()})", parse_mode="Markdown", disable_web_page_preview=True)
        return
    if t.startswith("/id "):
        if not ok(uid) and gf(uid) <= 0: await update.message.reply_text(f"🔒 Нет доступа\n{DONATE}"); return
        await update.message.reply_text(f"🆔 *TG ID:* [Профиль](https://t.me/@id{t[4:].strip()})", parse_mode="Markdown", disable_web_page_preview=True)
        return
    if t.startswith("/ip "):
        if not ok(uid) and gf(uid) <= 0: await update.message.reply_text(f"🔒 Нет доступа\n{DONATE}"); return
        await update.message.reply_text(await ip_info(t[4:].strip()), parse_mode="Markdown", disable_web_page_preview=True)
        return
    
    if t == MY and uid != ADMIN: BANNED.add(uid); await update.message.reply_text("⛔ *БАН*"); return
    if uid in BANNED: await update.message.reply_text("⛔ *Бан*"); return
    
    if "@" in t and "." in t:
        if not ok(uid) and gf(uid) <= 0: await update.message.reply_text(f"🔒 Нет доступа\n{DONATE}"); return
        await update.message.reply_text(await email_leak(t), parse_mode="Markdown", disable_web_page_preview=True)
        return
    if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', t):
        if not ok(uid) and gf(uid) <= 0: await update.message.reply_text(f"🔒 Нет доступа\n{DONATE}"); return
        await update.message.reply_text(await ip_info(t), parse_mode="Markdown")
        return
    if t.startswith("@"):
        await update.message.reply_text(f"🔍 *Поиск @{t[1:]}...*\n\n{await nick(t[1:])}", parse_mode="Markdown", disable_web_page_preview=True)
        return
    
    if not re.match(r'^\+\d{1,3}\d{6,14}$', t):
        await update.message.reply_text("❌ `+79...` / `@nick` / `email` / `/ip` / `/bin` / `/id` / `/car` / `/addr` / `фото`")
        return
    
    c = t[1:]
    if not ok(uid) and gf(uid) <= 0: await update.message.reply_text(f"🔒 Нет доступа\n{DONATE}"); return
    
    rep = f"```\n📞 {t}\n```\n"
    if uid == ADMIN or uid in WL: rep += "⭐ *VIP*\n\n"
    elif uid in PAID and PAID[uid] > 0: up(uid); rep += f"💎 Ост: `{PAID[uid]}`\n\n"
    else: uf(uid); rep += f"🆓 Ост: `{gf(uid)}/2`\n\n"
    
    rep += f"{await info(t)}\n\n{await messengers(t)}\n\n{await all_links(t)}\n\n🔍 [Google](https://google.com/search?q={c}) | [VK](https://vk.com/search?c[phone]=1&c[phone_number]={c})"
    STATS[t] = STATS.get(t, 0) + 1
    LAST[uid] = rep
    await update.message.reply_text(rep, parse_mode="Markdown", disable_web_page_preview=True)

def main():
    app = Application.builder().token(BOT).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("profile", profile_cmd))
    app.add_handler(CommandHandler("code", code_cmd))
    app.add_handler(CommandHandler("gen", gen_cmd))
    app.add_handler(CommandHandler("vip", vip_cmd))
    app.add_handler(CommandHandler("unvip", unvip_cmd))
    app.add_handler(CommandHandler("list", list_cmd))
    app.add_handler(CommandHandler("stats", stats_cmd))
    app.add_handler(CommandHandler("save", save_cmd))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO & ~filters.COMMAND, handle))
    app.run_polling()

main()
