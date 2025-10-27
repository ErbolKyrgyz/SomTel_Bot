import os 
import asyncio
import aiohttp
import time
from keep_alive import keep_alive
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

# --- TOKEN ---
TOKEN_API = os.getenv("7583391474:AAF2dsZQCkizbVDuZzRMVEXzkIkExTeWY9w")

bot = Bot(token=TOKEN_API)
dp = Dispatcher()

# --- CACHE için ---
latest_rate = {"value": None, "last_update": 0}

# --- DİL VERİLERİ ---
LANGS = {
    "kg": {
        "welcome": "Салам! 💰 Мен SOMTEL. Бул бот аркылуу акча жөнөтүү, комиссия жана курс тууралуу маалымат ала аласыз.",
        "menu": "🏠 Башкы меню\nЭмне кылгыңыз келет:",
        "options": [
            "1️⃣ SOMTEL жөнүндө маалымат",
            "2️⃣ Комиссия эсептөө",
            "3️⃣ Валюта курсу",
            "4️⃣ Байланыш / Жардам"
        ],
        "back": "🔙 Артка кайтуу",
        "select_country": "🌍 Акчаны жөнөтүүчү өлкөнү тандаңыз:",
        "send_country": "🇹🇷 Түркия",
        "recv_country": "🇰🇬 Кыргызстан",
        "amount_info": "💡 Комиссия төмөнкүдөй эсептелет:\n\n🇹🇷 **Түркиядан жиберүү (TL)**:\n1-19999 = 2%\n20000-34999 = 1.7%\n35000+ = 1.5%\n\n🇰🇬 **Кыргызстандан жиберүү (SOM)**:\n1-49999 = 2.2%\n50000-99999 = 1.8%\n100000+ = 1.5%\n\n💰 **Жөнөтүү суммасын киргизиңиз:**",
        "enter_amount": "💰 Сумманы киргизиңиз:",
        "result": "Комиссия: {fee:.2f} {currency}",
        "rate_error": "❌ Валюта курсу алынган жок. Кийинчерээк аракет кылыңыз.",
        "contact": "📞 Байланыш маалыматтары:\n🇹🇷 WhatsApp: +905059389919\n📧 Email: janyshov04@gmail.com\n🇰🇬 Телефон: +996700200406"
    },
    "tr": {
        "welcome": "Hoş geldiniz! 💰 Ben SOMTEL. Bu bot ile para transferi hakkında bilgi alabilir, komisyon ücretlerini öğrenebilir ve döviz kurlarını görebilirsiniz.",
        "menu": "🏠 Ana Menü\nLütfen yapmak istediğiniz işlemi seçiniz:",
        "options": [
            "1️⃣ SOMTEL hakkında bilgi",
            "2️⃣ Ücret hesapla",
            "3️⃣ Döviz kurları",
            "4️⃣ Yardım / İletişim"
        ],
        "back": "🔙 Geri dön",
        "select_country": "🌍 Gönderen ülkeyi seçiniz:",
        "send_country": "🇹🇷 Türkiye",
        "recv_country": "🇰🇬 Kırgızistan",
        "amount_info": "💡 Komisyon oranları aşağıdaki gibidir:\n\n🇹🇷 **Türkiye'den gönderim (TL)**:\n1-19999 = 2%\n20000-34999 = 1.7%\n35000+ = 1.5%\n\n🇰🇬 **Kırgızistan'dan gönderim (SOM)**:\n1-49999 = 2.2%\n50000-99999 = 1.8%\n100000+ = 1.5%\n\n💰 **Lütfen göndermek istediğiniz miktarı yazınız:**",
        "enter_amount": "💰 Lütfen miktarı giriniz:",
        "result": "Komisyon: {fee:.2f} {currency}",
        "rate_error": "❌ Döviz kurları alınamadı. Lütfen tekrar deneyin.",
        "contact": "📞 İletişim Bilgileri:\n🇹🇷 WhatsApp: +905059389919\n📧 Email: janyshov04@gmail.com\n🇰🇬 Telefon: +996700200406"
    },
    "ru": {
    "welcome": "Добро пожаловать! 💰 Я — SOMTEL. С помощью этого бота вы можете узнать о денежных переводах, комиссиях и обменных курсах.",
    "menu": "🏠 Главное меню\nПожалуйста, выберите, что вы хотите сделать:",
    "options": [
        "1️⃣ О компании SOMTEL",
        "2️⃣ Рассчитать комиссию",
        "3️⃣ Курсы валют",
        "4️⃣ Помощь / Контакты"
    ],
    "back": "🔙 Назад",
    "select_country": "🌍 Выберите страну отправления:",
    "send_country": "🇹🇷 Турция",
    "recv_country": "🇰🇬 Кыргызстан",
    "amount_info": "💡 Тарифы комиссии:\n\n🇹🇷 **Из Турции (TRY)**:\n1-19999 = 2%\n20000-34999 = 1.7%\n35000+ = 1.5%\n\n🇰🇬 **Из Кыргызстана (SOM)**:\n1-49999 = 2.2%\n50000-99999 = 1.8%\n100000+ = 1.5%\n\n💰 **Введите сумму для перевода:**",
    "enter_amount": "💰 Введите сумму:",
    "result": "Комиссия: {fee:.2f} {currency}",
    "rate_error": "❌ Не удалось получить курсы валют. Попробуйте позже.",
    "contact": "📞 Контактная информация:\n🇹🇷 WhatsApp: +905059389919\n📧 Email: janyshov04@gmail.com\n🇰🇬 Телефон: +996700200406"
}
}

user_language = {}
user_transfer = {}

# --- KURLAR (her dakika güncellenir) ---
async def get_exchange_rate():
    """TRY -> KGS döviz kurunu alır (her dakika bir kez güncellenir)."""
    now = time.time()
    # 60 saniyeden eskiyse güncelle
    if now - latest_rate["last_update"] > 60 or latest_rate["value"] is None:
        url = "https://open.er-api.com/v6/latest/TRY"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    data = await response.json()
                    rate = data.get("rates", {}).get("KGS")
                    if rate:
                        latest_rate["value"] = rate
                        latest_rate["last_update"] = now
        except Exception as e:
            print("Kur çekme hatası:", e)

    return latest_rate["value"]

# --- /start ---
@dp.message(CommandStart())
async def start(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇰🇬 Кыргызча", callback_data="lang_kg")],
        [InlineKeyboardButton(text="🇹🇷 Türkçe", callback_data="lang_tr")],
        [InlineKeyboardButton(text="ru Русский", callback_data="lang_ru")],
    ])
    await message.answer("🌍 Dil seçiniz / Выберите язык / Тилди тандаңыз:", reply_markup=keyboard)

# --- Dil seçimi ---
@dp.callback_query(lambda c: c.data.startswith("lang_"))
async def set_language(callback_query: CallbackQuery):
    lang = callback_query.data.split("_")[1]
    user_language[callback_query.from_user.id] = lang
    text = LANGS[lang]["welcome"]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=opt, callback_data=f"menu_{i+1}")] for i, opt in enumerate(LANGS[lang]["options"])
    ])
    await callback_query.message.edit_text(text + "\n\n" + LANGS[lang]["menu"], reply_markup=keyboard)

# --- Menü işlemleri ---
@dp.callback_query(lambda c: c.data.startswith("menu_"))
async def handle_menu(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    lang = user_language.get(user_id, "tr")
    data = callback_query.data

    if data == "menu_1":  # SOMTEL hakkında bilgi
        info = {
            "tr": "SomTel, Kırgızistan ile Türkiye arasında hızlı, güvenli ve uygun maliyetli para transferi hizmeti sunmak amacıyla kurulmuş uluslararası bir şirkettir."
                "Misyonumuz, her müşterimize güvenilir, şeffaf ve kolay bir transfer deneyimi yaşatmaktır."
                ""
                "Biz biliyoruz ki, memlekete para göndermek sadece finansal bir işlem değil — aileye duyulan sevginin ve sorumluluğun bir göstergesidir."
                "Bu yüzden SomTel, her transferi kendi parasıymış gibi korur ve her müşterisini bir dost gibi görür."
                ""
                "SomTel ile:"
                "✅ Paranız birkaç dakika içinde güvenle ulaşır."
                "✅ Tüm bilgileriniz şifreli ve korunur."
                "✅ Komisyon oranlarımız her zaman adil ve şeffaftır."
                "✅ Destek ekibimiz her zaman size yardımcı olmaya hazırdır."
                ""
                "SomTel, Kırgızistan ile Türkiye arasındaki güven köprüsüdür."
                "Bizim için her işlem bir sayı değil, bir insan hikayesidir — sevdiklerine destek olmak isteyen insanların hikayesi."
                "SomTel ile sadece para değil, sevgi ve güven gönderirsiniz.",
            "kg": "📘 SomTel — бул Кыргызстан менен Түркиянын ортосундагы акча которууларды жеңилдеткен ишенимдүү эл аралык кызмат."
                        "Биз ар бир кардардын ишенимине татыктуу болууну, ар бир которуунун коопсуздугун жана ылдамдыгын камсыздоону эң башкы максат катары коёбуз."
                        ""
                        "Биз билебиз — чет өлкөдө жүрүп, үй-бүлөңө акча жөнөтүү бул жөн гана каржылык маселе эмес, бул сүйүү жана жоопкерчилик белгиси. Ошондуктан SomTel сиздин ар бир которууңузду өз акчасындай коргойт."
                        ""
                        "SomTel аркылуу акча жөнөтүү:"
                        "✅ Ылдам — которуу бир нече мүнөттө иштетилет."
                        "✅ Коопсуз — бардык маалыматтар корголгон жана шифрленген."
                        "✅ Төмөн комиссия — ар бир кардар үчүн эң пайдалуу тарифтер."
                        "✅ Колоо кызматы — биздин команда ар дайым жардам берүүгө даяр."

                        "Биз Кыргызстан менен Түркиянын ортосундагы көпүрө болууну каалайбыз — ишеним, боордоштук жана чыныгы кызмат аркылуу."
                        "SomTel — бул жөн гана акча которуу эмес, бул жакындарыңыз менен байланышты сактоонун эң оңой жолу.",
            "ru": "SomTel — это международный сервис, созданный для надежных и быстрых денежных переводов между Кыргызстаном и Турцией."
                    "Наша миссия — обеспечить каждому клиенту удобный, безопасный и выгодный способ отправки денег своим близким."
                    "   "
                    "Мы понимаем, что перевод денег домой — это не просто финансовая операция. Это акт заботы, любви и доверия. Поэтому SomTel гарантирует полную безопасность каждой транзакции и конфиденциальность всех данных."
                        "   "
                    "С SomTel вы получаете:"
                    "✅ Быструю обработку переводов — деньги доходят за считанные минуты."
                    "✅ Полную безопасность — защита данных на всех этапах."
                    "✅ Низкие комиссии — прозрачные и честные условия."
                    "✅ Поддержку клиентов — мы всегда рядом, чтобы помочь."
                        "   "
                    "Мы строим мост между Кыргызстаном и Турцией, основанный на доверии, уважении и взаимопомощи."
                    "SomTel — это не просто переводы. Это связь с родными, где бы вы ни находились."
        }
        text = info[lang]
    elif data == "menu_2":  # Ücret hesapla
        text = LANGS[lang]["select_country"]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=LANGS[lang]["send_country"], callback_data="send_TR")],
            [InlineKeyboardButton(text=LANGS[lang]["recv_country"], callback_data="send_KG")]
        ])
        await callback_query.message.edit_text(text, reply_markup=keyboard)
        return
    elif data == "menu_3":  # Döviz kurları
        rate = await get_exchange_rate()
        if rate:
            text = f"💱 1 TRY = {round(rate, 2)} KGS 🇰🇬\n🕒 Son güncelleme: {time.strftime('%H:%M:%S')}"
        else:
            text = LANGS[lang]["rate_error"]
    elif data == "menu_4":  # İletişim
        text = LANGS[lang]["contact"]
    else:
        text = "❌ Geçersiz seçim."

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=LANGS[lang]["back"], callback_data="main_menu")]])
    await callback_query.message.edit_text(text, reply_markup=keyboard)

# --- Ana Menüye dön ---
@dp.callback_query(lambda c: c.data == "main_menu")
async def main_menu(callback_query: CallbackQuery):
    lang = user_language.get(callback_query.from_user.id, "tr")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=opt, callback_data=f"menu_{i+1}")] for i, opt in enumerate(LANGS[lang]["options"])
    ])
    await callback_query.message.edit_text(LANGS[lang]["menu"], reply_markup=keyboard)

# --- Ücret Hesaplama ---
@dp.callback_query(lambda c: c.data.startswith("send_"))
async def select_country(callback_query: CallbackQuery):
    lang = user_language.get(callback_query.from_user.id, "tr")
    sender_country = callback_query.data.split("_")[1]
    user_transfer[callback_query.from_user.id] = {"sender": sender_country}
    await callback_query.message.edit_text(LANGS[lang]["amount_info"])

@dp.message()
async def calculate_fee(message: Message):
    user_id = message.from_user.id
    if user_id not in user_transfer:
        return

    lang = user_language.get(user_id, "tr")
    sender = user_transfer[user_id]["sender"]

    try:
        amount = float(message.text)
    except ValueError:
        await message.answer("❌ Geçersiz miktar. Lütfen sayısal bir değer girin.")
        return

    if sender == "TR":
        if amount <= 9999:
            rate = 0.025
        elif amount <= 19999:
            rate = 0.02
        elif amount <= 34999:
            rate = 0.018
        else:
            rate = 0.016
        currency = "TL"
    else:
        if amount <= 49999:
            rate = 0.019
        elif amount <= 99999:
            rate = 0.017
        else:
            rate = 0.015
        currency = "SOM"

    fee = amount * rate
    await message.answer(LANGS[lang]["result"].format(fee=fee, currency=currency))

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔁 Tekrar Hesapla", callback_data="menu_2")],
        [InlineKeyboardButton(text=LANGS[lang]["back"], callback_data="main_menu")]
    ])
    await message.answer("Ne yapmak istersiniz?", reply_markup=keyboard)

# --- Başlat ---
async def main():
    print("🚀 SOMTEL Bot başlatıldı.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    keep_alive()
    asyncio.run(main())

