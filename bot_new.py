import re, logging, aiohttp, random, string, base64, asyncio
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
STATS = {}
LAST = {}

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
    return f"🔍 *Номер {p}:*\n\n🌍 [Numverify](https://numverify.com)\n📞 [KtoZvonil](https://ktozvonil.ru/phone/{c})\n🔗 [WhoCallsMe](https://whocallsme.com/Phone-Number.aspx/{c})"

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

async def messengers(phone):
    clean = phone.lstrip("+")
    async def check(msg, url):
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(url, timeout=aiohttp.ClientTimeout(3)) as r:
                    return f"✅ {msg}" if r.status == 200 else f"❌ {msg}"
        except: return f"⚠️ {msg}"
    tasks = [
        check("WhatsApp", f"https://wa.me/{clean}"),
        check("Viber", f"https://viber.click/{clean}"),
        check("Signal", f"https://signal.me/+{clean}")
    ]
    results = await asyncio.gather(*tasks)
    try:
        entity = await tc.get_entity(f"+{clean}")
        results.append("✅ Telegram")
    except:
        results.append("❌ Telegram")
    return "\n".join(results)

async def spam_multi(phone):
    c = phone.lstrip("+")
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(f"https://spamcheck.ru/api/v1/check?phone={c}", timeout=aiohttp.ClientTimeout(5)) as r:
                if r.status == 200:
                    d = await r.json()
                    if d.get("spam"):
                        return f"🛡 *Спам:* ⚠️ {d.get('rating','?')} жалоб"
    except: pass
    return "🛡 *Спам:* ✅ Не замечен"

async def tg_search_groups(phone):
    c = phone.lstrip("+")
    return f"🔍 *TG поиск:* [Нажми](tg://search?query={c})"

async def extra_operator(phone):
    c = phone.lstrip("+")
    try:
        u = f"https://htmlweb.ru/geo/api.php?telcod={c}&json"
        async with aiohttp.ClientSession() as s:
            async with s.get(u, timeout=aiohttp.ClientTimeout(10)) as r:
                d = await r.json()
        if d.get("country"):
            op = d.get("0",{}).get("oper","?")
            reg = d.get("0",{}).get("name","?")
            return f"📶 *Доп. оператор:* {op}\n📍 *Регион:* {reg}"
    except: pass
    return ""

async def map_link(phone):
    c = phone.lstrip("+")
    try:
        u = f"https://apilayer.net/api/validate?access_key={NUM}&number={c}&format=1"
        async with aiohttp.ClientSession() as s:
            async with s.get(u, timeout=aiohttp.ClientTimeout(10)) as r:
                d = await r.json()
        if d.get("valid") and d.get("location"):
            loc = d.get("location","")
            return f"🗺 *Карта:* [Google Maps](https://maps.google.com/?q={loc})"
    except: pass
    return ""

async def ua_operator(phone):
    c = phone.lstrip("+")
    try:
        u = f"https://htmlweb.ru/geo/api.php?telcod={c}&json"
        async with aiohttp.ClientSession() as s:
            async with s.get(u, timeout=aiohttp.ClientTimeout(10)) as r:
                d = await r.json()
        if d.get("country") == "Украина":
            op = d.get("0",{}).get("oper","?")
            reg = d.get("0",{}).get("name","?")
            city = d.get("0",{}).get("city","?")
            return f"🇺🇦 *Украина*\n📶 *Оператор:* {op}\n📍 *Регион:* {reg}\n🏙 *Город:* {city}"
    except: pass
    return ""

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
    async def check(name, url):
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(f"https://{url}", timeout=aiohttp.ClientTimeout(2)) as r:
                    return f"✅ {name}: [Ссылка](https://{url})" if r.status == 200 else f"❌ {name}"
        except: return f"⚠️ {name}"
    tasks = [check(name, url) for name, url in sites.items()]
    results = await asyncio.gather(*tasks)
    return "\n".join(results)

async def email_leak(email):
    return f"📧 *{email}*\n\n🔍 [Have I Been Pwned](https://haveibeenpwned.com/account/{email})\n🔍 [LeakCheck](https://leakcheck.io/?check={email})"

async def email_social(email):
    local = email.split("@")[0]
    return f"🔍 *Профили по email:*\n📸 [Gravatar](https://gravatar.com/{local})\n💻 [GitHub](https://github.com/{local})\n📘 [VK](https://vk.com/{local})\n🐦 [Twitter](https://twitter.com/{local})"

async def ip_info(ip):
    return f"🌐 *IP:* `{ip}`\n\n🔍 [ip-api.com](http://ip-api.com/{ip}) | [Whois](https://who.is/whois/{ip})"

async def car_info(g):
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(f"https://carnumber.ru/api/v1?number={g}", timeout=aiohttp.ClientTimeout(10)) as r:
                d = await r.json()
        if d.get("success"):
            c = d.get("data", {})
            return f"🚗 *Авто:* {c.get('brand','?')} {c.get('model','?')}\n📅 Год: {c.get('year','?')}\n🎨 Цвет: {c.get('color','?')}"
    except: pass
    return "❌ *Авто не найдено*"

async def address_info(a):
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(f"https://nominatim.openstreetmap.org/search?q={a}&format=json&limit=1&accept-language=ru", headers={"User-Agent":"Mozilla/5.0"}, timeout=aiohttp.ClientTimeout(10)) as r:
                d = await r.json()
        if d:
            p = d[0]
            return f"📍 *Адрес:* {p.get('display_name','?')}\n🌐 Координаты: {p.get('lat','?')}, {p.get('lon','?')}\n🔗 [Кадастровая карта](https://pkk.rosreestr.ru/#/search/{p.get('lat','?')},{p.get('lon','?')}/)"
    except: pass
    return "❌ *Адрес не найден*"

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
        "• 🌍 Страна, город, регион\n"
        "• 📶 Оператор, тип линии\n"
        "• 👤 Telegram (имя + фото)\n"
        "• 💬 WhatsApp, Viber, Signal\n"
        "• 🛡 Спам-проверка\n"
        "• ⚠️ Утечки данных\n"
        "• 🗺 Карта региона\n"
        "• 🔍 Поиск в Telegram\n"
        "• 🌍 Международные базы (РФ, UA, BY, KZ)\n\n"
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
    
    await update.message.reply_text("🔍 *Поиск...*", parse_mode="Markdown")
    rep = f"```\n📞 {t}\n```\n"
    if uid == ADMIN or uid in WL: rep += "⭐ *VIP*\n\n"
    elif uid in PAID and PAID[uid] > 0: up(uid); rep += f"💎 Ост: `{PAID[uid]}`\n\n"
    else: uf(uid); rep += f"🆓 Ост: `{gf(uid)}/2`\n\n"
    
    rep += f"{await info(t)}\n\n📱 *Мессенджеры:*\n{await messengers(t)}\n\n"
    n, ph = await tg(t)
    rep += f"👤 *TG:* `{n}`\n" if n else "👤 *TG:* ❌\n"
    if ph: await update.message.reply_photo(ph)
    STATS[t] = STATS.get(t, 0) + 1
    rep += f"\n{await extra_operator(t)}\n"
    rep += f"{await map_link(t)}\n"
    rep += f"\n{await ua_operator(t)}\n"
    rep += f"{await ua_links(t)}\n"
    rep += f"{await all_links(t)}\n"
    rep += f"\n{await spam_multi(t)}\n"
    rep += f"\n🛡 {await leak(t)}\n\n"
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
