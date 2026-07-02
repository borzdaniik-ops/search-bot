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
    return f"🔍 *Номер {p}:*\n\n🌍 [Numverify](https://numverify.com)\n📞 [KtoZvonil](https://ktozvonil.ru/phone/{c})\n🔗 [WhoCallsMe](https://whocallsme.com/Phone-Number.aspx/{c})"

async def messengers(phone):
    clean = phone.lstrip("+")
    return f"💬 *Мессенджеры:*\n✅ [WhatsApp](https://wa.me/{clean})\n✅ [Viber](https://viber.click/{clean})\n✅ [Telegram](https://t.me/+{clean})\n✅ [Signal](https://signal.me/+{clean})"

async def tg_search_groups(phone):
    c = phone.lstrip("+")
    return f"🔍 *TG поиск:* [Нажми](tg://search?query={c})"

async def map_link(phone):
    c = phone.lstrip("+")
    return f"🗺 *Карта:* [Google Maps](https://maps.google.com/?q={c})"

async def ua_links(phone):
    c = phone.lstrip("+")
    return f"🔍 *UA поиск:*\n• [KtoZvonil](https://ktozvonil.com.ua/phone/{c})\n• [Dovidnyk](https://telefonnyjdovidnyk.com.ua/nomer/{c})"

async def all_links(phone):
    c = phone.lstrip("+")
    return (
        f"🔍 *Международный поиск:*\n"
        f"🇷🇺 [KtoZvonil.ru](https://ktozvonil.ru/phone/{c})\n"
        f"🇺🇦 [KtoZvonil.ua](https://ktozvonil.com.ua/phone/{c})\n"
        f"🇧🇾 [KtoZvonil.by](https://ktozvonil.by/phone/{c})\n"
        f"🇰🇿 [KtoZvonil.kz](https://ktozvonil.kz/phone/{c})\n"
        f"🌍 [NumLookup](https://numlookup.com/phone/{c})\n"
        f"🌍 [SpyDialer](https://spydialer.com/phone/{c})\n"
        f"🌍 [ZLookup](https://zlookup.com/phone/{c})\n"
        f"🌍 [Truecaller](https://truecaller.com/search/{c})"
    )

async def nick(n):
    sites = {"📷 Instagram":f"instagram.com/{n}","🐦 Twitter":f"twitter.com/{n}","💻 GitHub":f"github.com/{n}","🎵 TikTok":f"tiktok.com/@{n}","📘 VK":f"vk.com/{n}","▶️ YouTube":f"youtube.com/@{n}","👽 Reddit":f"reddit.com/user/{n}","🎮 Twitch":f"twitch.tv/{n}","🎯 Steam":f"steamcommunity.com/id/{n}","👤 Facebook":f"facebook.com/{n}","📌 Pinterest":f"pinterest.com/{n}","👻 Snapchat":f"snapchat.com/add/{n}"}
    return "\n".join([f"✅ {name}: [Ссылка](https://{url})" for name, url in sites.items()])

async def email_leak(email):
    return f"📧 *{email}*\n\n🔍 [Have I Been Pwned](https://haveibeenpwned.com/account/{email})\n🔍 [LeakCheck](https://leakcheck.io/?check={email})"

async def email_social(email):
    local = email.split("@")[0]
    return f"🔍 *Профили по email:*\n📸 [Gravatar](https://gravatar.com/{local})\n💻 [GitHub](https://github.com/{local})\n📘 [VK](https://vk.com/{local})\n🐦 [Twitter](https://twitter.com/{local})"

async def ip_info(ip):
    return f"🌐 *IP:* `{ip}`\n\n🔍 [ip-api.com](http://ip-api.com/{ip}) | [Whois](https://who.is/whois/{ip})"

async def car_info(g):
    return f"🚗 *Авто:* [Поиск](https://carnumber.ru/api/v1?number={g})"

async def address_info(a):
    return f"📍 *Адрес:* [Поиск](https://nominatim.openstreetmap.org/search?q={a}&format=json&limit=1&accept-language=ru)"

async def bin_info(bin):
    return f"💳 *BIN:* `{bin}`\n\n🔍 [binlist.net](https://lookup.binlist.net/{bin}) | [Банки.ру](https://www.banki.ru/banks/bin/?bin={bin})"

async def tg_id_info(uid):
    return f"🆔 *Telegram ID:* `{uid}`\n\n🔗 [t.me/@id{uid}](https://t.me/@id{uid})"

async def stats_cmd(update: Update, ctx):
    if update.effective_user.id != ADMIN: return
    top = sorted(STATS.items(), key=lambda x: x[1], reverse=True)[:10]
    msg = "📊 *Топ-10 искомых номеров:*\n\n" + "\n".join([f"📞 `{p}` — {c} раз" for p, c in top])
    await update.message.reply_text(msg, parse_mode="Markdown")

async def save_cmd(update: Update, ctx):
    uid = update.effective_user.id
    if uid not in LAST:
        await update.message.reply_text("❌ Нет сохранённых результатов")
        return
    with open(f"/sdcard/Download/search_{uid}.txt", "w") as f:
        f.write(LAST[uid])
    await update.message.reply_text(f"✅ Сохранено в /sdcard/Download/search_{uid}.txt")

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
        "• 🔍 Ссылки на поиск\n"
        "• 💬 WhatsApp, Viber, Signal\n"
        "• 🗺 Карта региона\n"
        "• 🔍 Поиск в Telegram\n"
        "• 🌍 Международные базы\n\n"
        "👤 *НИКНЕЙМ*\n"
        "• 12 соцсетей с ссылками\n\n"
        "📧 *EMAIL*\n"
        "• Утечки + профили\n\n"
        "🌐 *IP* `/ip 8.8.8.8`\n"
        "💳 *BIN* `/bin 220431`\n"
        "🆔 *TG ID* `/id 123456789`\n"
        "🚗 *АВТО* `/car А123БВ177`\n"
        "📍 *АДРЕС* `/addr Москва`\n"
        "📸 *ФОТО* поиск по лицу\n\n"
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
    msg = f"👤 *ТВОЙ ПРОФИЛЬ*\n\n🆔 ID: `{uid}`\n🎁 Бесплатных: `{f}/2`\n💎 Куплено: `{p}`\n⭐ VIP: {vip}\n⛔ Бан: {banned}\n\n💸 Пополнить: {DONATE}"
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

async def handle(update: Update, ctx):
    uid = update.effective_user.id
    t = update.message.text.strip() if update.message.text else ""
    
    if update.message.photo:
        if not ok(uid) and gf(uid) <= 0: await update.message.reply_text(f"🔒 Нет доступа\n{DONATE}"); return
        await update.message.reply_text("📸 *Поиск по фото:*\n\n🔍 [Google Images](https://lens.google.com)\n🔍 [Yandex Images](https://yandex.ru/images)\n🔍 [FaceCheck](https://facecheck.id)\n🔍 [Search4faces](https://search4faces.com)", parse_mode="Markdown", disable_web_page_preview=True)
        return
    
    if t.startswith("/car "):
        if not ok(uid) and gf(uid) <= 0: await update.message.reply_text(f"🔒 Нет доступа\n{DONATE}"); return
        await update.message.reply_text("🚗 *Поиск...*", parse_mode="Markdown")
        await update.message.reply_text(await car_info(t[5:].strip().upper()), parse_mode="Markdown", disable_web_page_preview=True)
        return
    
    if t.startswith("/addr "):
        if not ok(uid) and gf(uid) <= 0: await update.message.reply_text(f"🔒 Нет доступа\n{DONATE}"); return
        await update.message.reply_text("📍 *Поиск...*", parse_mode="Markdown")
        await update.message.reply_text(await address_info(t[6:].strip()), parse_mode="Markdown", disable_web_page_preview=True)
        return
    
    if t.startswith("/bin "):
        if not ok(uid) and gf(uid) <= 0: await update.message.reply_text(f"🔒 Нет доступа\n{DONATE}"); return
        await update.message.reply_text(await bin_info(t[5:].strip()), parse_mode="Markdown", disable_web_page_preview=True)
        return
    
    if t.startswith("/id "):
        if not ok(uid) and gf(uid) <= 0: await update.message.reply_text(f"🔒 Нет доступа\n{DONATE}"); return
        await update.message.reply_text(await tg_id_info(t[4:].strip()), parse_mode="Markdown", disable_web_page_preview=True)
        return
    
    if t.startswith("/ip "):
        if not ok(uid) and gf(uid) <= 0: await update.message.reply_text(f"🔒 Нет доступа\n{DONATE}"); return
        await update.message.reply_text(await ip_info(t[4:].strip()), parse_mode="Markdown", disable_web_page_preview=True)
        return
    
    if t == MY and uid != ADMIN: BANNED.add(uid); await update.message.reply_text("⛔ *БАН*"); return
    if uid in BANNED: await update.message.reply_text("⛔ *Бан*"); return
    
    if "@" in t and "." in t:
        if not ok(uid) and gf(uid) <= 0: await update.message.reply_text(f"🔒 Нет доступа\n{DONATE}"); return
        await update.message.reply_text(await email_leak(t) + "\n\n" + await email_social(t), parse_mode="Markdown", disable_web_page_preview=True)
        return
    
    if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', t):
        if not ok(uid) and gf(uid) <= 0: await update.message.reply_text(f"🔒 Нет доступа\n{DONATE}"); return
        await update.message.reply_text(await ip_info(t), parse_mode="Markdown")
        return
    
    if t.startswith("@"):
        await update.message.reply_text(f"🔍 *Поиск @{t[1:]}...*", parse_mode="Markdown")
        await update.message.reply_text(f"```\n👤 @{t[1:]}\n```\n{await nick(t[1:])}", parse_mode="Markdown", disable_web_page_preview=True)
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
    
    rep += f"{await info(t)}\n\n📱 *Мессенджеры:*\n{await messengers(t)}\n\n"
    rep += f"👤 *TG:* [Открыть](https://t.me/+{c})\n"
    STATS[t] = STATS.get(t, 0) + 1
    rep += f"\n{await map_link(t)}\n"
    rep += f"\n{await ua_links(t)}\n"
    rep += f"{await all_links(t)}\n"
    rep += f"{await tg_search_groups(t)}\n"
    rep += f"🔍 [Google](https://google.com/search?q={c}) | [VK](https://vk.com/search?c[phone]=1&c[phone_number]={c})\n"
    rep += f"🔗 [WA](https://wa.me/{c}) | [TG](https://t.me/+{c})"
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
