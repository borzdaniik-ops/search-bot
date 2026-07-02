import re, logging, aiohttp, random, string
from datetime import date
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telethon import TelegramClient

BOT = "8640914849:AAF5NCl4ajFrFR81VbdIHzRFvfANHWB6Wf4"
NUM = "2843e2a1a324f6a4420e2aa4ca9fe615"
DONATE = "https://dalink.to/daniksayko"
ADMIN = 7783324307
WL = {8562396880}
BANNED = set()
MY = "+79963212799"

tc = TelegramClient('telethon_session', 2040, "b18441a1ff607e10a989891a5462e627")
logging.basicConfig(level=logging.INFO)
FREE = {}
CODES = {}
PAID = {}
USERS = {}

CN = {"Russian Federation":"🇷🇺 Россия","Ukraine":"🇺🇦 Украина","Belarus":"🇧🇾 Беларусь","Kazakhstan":"🇰🇿 Казахстан","United States":"🇺🇸 США","Germany":"🇩🇪 Германия","France":"🇫🇷 Франция","China":"🇨🇳 Китай","United Kingdom":"🇬🇧 Британия"}
LT = {"mobile":"📱 Мобильный","landline":"☎️ Городской","voip":"💻 VoIP","toll free":"🆓 Бесплатный"}

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
async def tg(p):
    try:
        e = await tc.get_entity(p)
        n = f"{e.first_name or ''} {e.last_name or ''}".strip()
        ph = await tc.download_profile_photo(e, file=bytes) if e.photo else None
        return n, ph
    except:
        return None, None

async def info(p):
    c = p.lstrip("+")
    try:
        u = f"https://apilayer.net/api/validate?access_key={NUM}&number={c}&format=1"
        async with aiohttp.ClientSession() as s:
            async with s.get(u, timeout=aiohttp.ClientTimeout(10)) as r:
                d = await r.json()
        if d.get("valid"):
            co = CN.get(d.get("country_name",""), d.get("country_name","?"))
            li = LT.get(d.get("line_type",""), d.get("line_type","?"))
            return f"🌍 *Страна:* {co}\n📍 *Регион:* {d.get('location','?')}\n📶 *Оператор:* {d.get('carrier','?')}\n📱 *Тип:* {li}\n🔢 *Код:* +{d.get('country_code','?')}"
    except:
        pass
    return "❌ *Данные не найдены*"

async def leak(p):
    c = p.lstrip("+")
    try:
        u = f"https://leakcheck.io/api/public?check={c}"
        async with aiohttp.ClientSession() as s:
            async with s.get(u, headers={"User-Agent":"Mozilla/5.0"}, timeout=aiohttp.ClientTimeout(10)) as r:
                d = await r.json()
                if d.get("success") and d.get("found",0) > 0:
                    srcs = [s.get("name","?") for s in d.get("sources",[])]
                    return f"⚠️ *Найден в {d['found']} утечках!*\n📋 {', '.join(srcs[:5])}"
    except:
        pass
    return "✅ *Утечек не найдено*"

async def nick(n):
    sites = {"📷 Instagram":"instagram.com","🐦 Twitter":"twitter.com","💻 GitHub":"github.com","🎵 TikTok":"tiktok.com","📘 VK":"vk.com","▶️ YouTube":"youtube.com","👽 Reddit":"reddit.com","🎮 Twitch":"twitch.tv","🎯 Steam":"steamcommunity.com","👤 Facebook":"facebook.com","📌 Pinterest":"pinterest.com","👻 Snapchat":"snapchat.com"}
    res = []
    async with aiohttp.ClientSession() as s:
        for name, url in sites.items():
            try:
                async with s.get(f"https://{url}/{n}", timeout=aiohttp.ClientTimeout(3)) as r:
                    if r.status == 200: res.append(f"✅ {name}")
                    else: res.append(f"❌ {name}")
            except:
                res.append(f"⚠️ {name}")
    return "\n".join(res)

async def email_leak(email):
    try:
        u = f"https://leakcheck.io/api/public?check={email}"
        async with aiohttp.ClientSession() as s:
            async with s.get(u, headers={"User-Agent":"Mozilla/5.0"}, timeout=aiohttp.ClientTimeout(10)) as r:
                d = await r.json()
                if d.get("success") and d.get("found",0) > 0:
                    srcs = [s.get("name","?") for s in d.get("sources",[])]
                    return f"⚠️ *Найден в {d['found']} утечках!*\n📋 {', '.join(srcs[:5])}"
    except:
        pass
    return "✅ *Email чист*"

async def ip_info(ip):
    try:
        u = f"http://ip-api.com/json/{ip}?fields=country,countryCode,city,regionName,org,isp,query,timezone"
        async with aiohttp.ClientSession() as s:
            async with s.get(u, timeout=aiohttp.ClientTimeout(5)) as r:
                d = await r.json()
        if d.get("status") == "success":
            return f"🌍 *Страна:* {d.get('country','?')} ({d.get('countryCode','?')})\n🏙 *Город:* {d.get('city','?')}\n📍 *Регион:* {d.get('regionName','?')}\n🏢 *Провайдер:* {d.get('org', d.get('isp','?'))}\n🕐 *Часовой пояс:* {d.get('timezone','?')}\n🔢 *IP:* {d.get('query','?')}"
    except:
        pass
    return "❌ *IP не найден*"

async def photo_help():
    return "📸 *Поиск по фото*\n\n🔍 [Google Images](https://lens.google.com)\n🔍 [Yandex Images](https://yandex.ru/images)\n🔍 [PimEyes](https://pimeyes.com)\n🔍 [FaceCheck](https://facecheck.id)\n🔍 [TinEye](https://tineye.com)"
async def start(update: Update, ctx):
    uid = update.effective_user.id
    f = gf(uid)
    p = PAID.get(uid,0)
    msg = (
        "```\n"
        "╔══════════════════════╗\n"
        "║   🔍 SEARCH BOT v4.0   ║\n"
        "║   by @daniksayko       ║\n"
        "╚══════════════════════╝\n"
        "```\n\n"
        "✨ *ДОБРО ПОЖАЛОВАТЬ В PREMIUM ПОИСК!* ✨\n\n"
        f"🎁 *Бесплатно сегодня:* `{f}/2`\n"
        f"💎 *Куплено запросов:* `{p}`\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📞 *ПО НОМЕРУ ТЕЛЕФОНА:*\n"
        "• 🌍 Страна и город\n"
        "• 📶 Оператор связи\n"
        "• 📱 Тип линии\n"
        "• 👤 Имя в Telegram\n"
        "• 📸 Фото профиля\n"
        "• 🛡 Утечки данных\n"
        "• 🔗 Ссылки WhatsApp/Viber\n\n"
        "👤 *ПО НИКНЕЙМУ:*\n"
        "• 12 популярных соцсетей\n"
        "• Instagram, VK, Twitter, TikTok и др.\n\n"
        "📧 *ПО EMAIL:* проверка утечек\n"
        "🌐 *ПО IP:* геолокация, провайдер\n"
        "📸 *ПО ФОТО:* ссылки на поиск по лицу\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "💳 *ТАРИФЫ:*\n"
        "🔥 `5` запросов — *1.5$*\n"
        "🔥 `10` запросов — *3.0$*\n"
        "🔥 `15` запросов — *4.5$*\n\n"
        f"💸 *Оплата:* {DONATE}\n"
        "🔑 *Активировать:* `/code КОД`\n"
        "👤 *Профиль:* `/profile`\n\n"
        "👇 *Отправь номер, ник, email, IP или фото!*"
    ).format(f=f, p=p)
    await update.message.reply_text(msg, parse_mode="Markdown", disable_web_page_preview=True)

async def profile_cmd(update: Update, ctx):
    uid = update.effective_user.id
    f = gf(uid)
    p = PAID.get(uid,0)
    vip = "⭐ ДА" if (uid == ADMIN or uid in WL) else "❌ НЕТ"
    banned = "⛔ ДА" if uid in BANNED else "✅ НЕТ"
    msg = (
        "```\n╔══════════════════════╗\n║   👤 ТВОЙ ПРОФИЛЬ     ║\n╚══════════════════════╝\n```\n\n"
        f"🆔 *ID:* `{uid}`\n"
        f"🎁 *Бесплатных:* `{f}/2`\n"
        f"💎 *Куплено:* `{p}`\n"
        f"⭐ *VIP:* {vip}\n"
        f"⛔ *Бан:* {banned}\n\n"
        f"💸 *Пополнить:* {DONATE}"
    )
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
    try:
        WL.add(int(ctx.args[0]))
        await update.message.reply_text(f"⭐ *VIP:* `{ctx.args[0]}`", parse_mode="Markdown")
    except:
        pass

async def unvip_cmd(update: Update, ctx):
    if update.effective_user.id != ADMIN: return
    try:
        WL.discard(int(ctx.args[0]))
        await update.message.reply_text(f"❌ *Не VIP:* `{ctx.args[0]}`", parse_mode="Markdown")
    except:
        pass

async def list_cmd(update: Update, ctx):
    if update.effective_user.id != ADMIN: return
    await update.message.reply_text(f"VIP: {WL}\nКоды: {CODES}")
async def handle(update: Update, ctx):
    uid = update.effective_user.id
    t = update.message.text.strip() if update.message.text else ""
    if uid not in USERS: USERS[uid] = str(date.today())
    
    if update.message.photo:
        if not ok(uid) and gf(uid) <= 0:
            await update.message.reply_text(f"🔒 Нет доступа\n{DONATE}", disable_web_page_preview=True)
            return
        await update.message.reply_text(await photo_help(), parse_mode="Markdown", disable_web_page_preview=True)
        return
    
    if t == MY and uid != ADMIN:
        BANNED.add(uid)
        await update.message.reply_text("⛔ *БАН*", parse_mode="Markdown")
        return
    
    if uid in BANNED:
        await update.message.reply_text("⛔ *Бан*", parse_mode="Markdown")
        return
    
    if "@" in t and "." in t:
        if not ok(uid) and gf(uid) <= 0:
            await update.message.reply_text(f"🔒 Нет доступа\n{DONATE}", disable_web_page_preview=True)
            return
        await update.message.reply_text(f"📧 *Поиск {t}...*", parse_mode="Markdown")
        r = await email_leak(t)
        await update.message.reply_text(f"📧 {t}:\n{r}", parse_mode="Markdown")
        return
    
    if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', t):
        if not ok(uid) and gf(uid) <= 0:
            await update.message.reply_text(f"🔒 Нет доступа\n{DONATE}", disable_web_page_preview=True)
            return
        await update.message.reply_text(f"🌐 *Поиск IP...*", parse_mode="Markdown")
        r = await ip_info(t)
        await update.message.reply_text(f"🌐 IP:\n{r}", parse_mode="Markdown")
        return
    
    if t.startswith("@"):
        await update.message.reply_text(f"🔍 *Поиск @{t[1:]}...*", parse_mode="Markdown")
        r = await nick(t[1:])
        await update.message.reply_text(f"```\n👤 @{t[1:]}\n```\n{r}", parse_mode="Markdown")
        return
    
    if not re.match(r'^\+\d{1,3}\d{6,14}$', t):
        await update.message.reply_text("❌ `+79...` / `@nick` / `email` / `IP` / `фото`", parse_mode="Markdown")
        return
    
    c = t[1:]
    if not ok(uid) and gf(uid) <= 0:
        await update.message.reply_text(f"🔒 Нет доступа\n{DONATE}", disable_web_page_preview=True)
        return
    
    await update.message.reply_text("🔍 *Поиск...* ⏳", parse_mode="Markdown")
    
    rep = f"```\n📞 {t}\n```\n"
    if uid == ADMIN or uid in WL: rep += "⭐ *VIP*\n\n"
    elif uid in PAID and PAID[uid] > 0:
        up(uid)
        rep += f"💎 Ост: `{PAID[uid]}`\n\n"
    else:
        uf(uid)
        rep += f"🆓 Ост: `{gf(uid)}/2`\n\n"
    
    rep += f"{await info(t)}\n\n"
    n, ph = await tg(t)
    if n:
        rep += f"👤 *TG:* `{n}`\n"
        if ph: await update.message.reply_photo(ph)
    else:
        rep += "👤 *TG:* ❌\n"
    
    rep += f"\n🛡 {await leak(t)}\n\n"
    rep += f"🔗 [WA](https://wa.me/{c}) | [TG](https://t.me/+{c})"
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
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO & ~filters.COMMAND, handle))
    app.run_polling()

main()
