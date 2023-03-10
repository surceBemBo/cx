# Dev : https://t me/DEV_SAMIR
#@BA_BLOO
import requests
from strings.filters import command
from gpytranslate import Translator
from aiohttp import ClientSession
from pyrogram import filters, Client
import re
import config
from config import (YAFA_NAME, YAFA_CHANNEL, SUDO_USER,
                    START_IMG_URL, BOT_USERNAME)
from pyrogram.types import (InlineKeyboardButton,
                            InlineKeyboardMarkup, Message)
from telegraph import upload_file
from traceback import format_exc
from YukkiMusic import app
from typing import Union

@app.on_message(command(["ترجمة","ترجمه","/tr"]))
async def tr(_, message):
    trl = Translator()
    if message.reply_to_message and (message.reply_to_message.text or message.reply_to_message.caption):
        if len(message.text.split()) == 1:
            target_lang = "ar"
        else:
            target_lang = message.text.split()[1]
        if message.reply_to_message.text:
            text = message.reply_to_message.text
        else:
            text = message.reply_to_message.caption
    else:
        if len(message.text.split()) <= 2:
            return await message.reply_text("أرسل الامر على هذا الشكل :\n[Available options](https://telegra.ph/Lang-Codes-02-22).\n<b>Usage:</b> <code>/tr ar</code>",disable_web_page_preview=True)
        target_lang = message.text.split(None, 2)[1]
        text = message.text.split(None, 2)[2]
    detectlang = await trl.detect(text)
    try:
        data = requests.get(f"https://api.safone.tech/translate?text={text}&target={target_lang}").json()
        tekstr = await trl(text, targetlang=target_lang)
    except ValueError as err:
        return await message.reply_text(f"Error: <code>{str(err)}</code>")
    return await message.reply_text(f"<b>Translated:</b> from {data['origin']} to {data['target']} \n<code>{data['translated']}</code>")

def ReplyCheck(message: Message):
    reply_id = None
    if message.reply_to_message:
        reply_id = message.reply_to_message.message_id
    elif not message.from_user.is_self:
        reply_id = message.message_id
    return reply_id


session = ClientSession()
pattern = re.compile(r"^text/|json$|yaml$|xml$|toml$|x-sh$|x-shellscript$")
BASE = "https://batbin.me/"

async def post(url: str, *args, **kwargs):
    async with session.post(url, *args, **kwargs) as resp:
        try:
            data = await resp.json()
        except Exception:
            data = await resp.text()
    return data

async def paste(content: str):
    resp = await post(f"{BASE}api/v2/paste", data=content)
    if not resp["success"]:
        return
    return BASE + resp["message"]


@app.on_message(command(["طباعة","طباعه","/pr"]))
async def paste_func(_, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("الرد على رسالة ب  `/pr`")
    r = message.reply_to_message
    if not r.text and not r.document:
        return await message.reply_text("يتم دعم النصوص والمستندات فقط ")
    m = await message.reply_text("لصق ...")
    if r.text:
        content = str(r.text)
    elif r.document:
        if r.document.file_size > 40000:
            return await m.edit("يمكنك فقط لصق ملفات أصغر من 40 كيلوبايت .")
        if not pattern.search(r.document.mime_type):
            return await m.edit("يمكن لصق الملفات النصية فقط .")
        doc = await message.reply_to_message.download()
        async with aiofiles.open(doc, mode="r") as f:
            content = await f.read()
        os.remove(doc)
    link = await paste(content)
    kb = [[InlineKeyboardButton(text="رابط اللصق", url=link)]]
    try:
        if m.from_user.is_bot:
            await message.reply_photo(photo=link,quote=False,caption="تم نسخ النص",reply_markup=InlineKeyboardMarkup(kb),)
        else:
            await message.reply_photo(photo=link,quote=False,caption="تم نسخ النص",reply_markup=InlineKeyboardMarkup(kb),)
        await m.delete()
    except Exception:
        await m.edit("فتح الرابط", reply_markup=InlineKeyboardMarkup(kb))


@app.on_message(command(["ميديا", "/tm", "tgm"]))
async def telegraph(client, message):
    replied = message.reply_to_message
    if not replied:
        return await message.reply("الرد على ملف وسائط مدعوم ")
    if not (
        (replied.photo and replied.photo.file_size <= 5242880)
        or (replied.animation and replied.animation.file_size <= 5242880)
        or (replied.video and replied.video.file_name.endswith(".mp4") and replied.video.file_size <= 5242880)
        or (replied.document and replied.document.file_name.endswith((".jpg", ".jpeg", ".png", ".gif", ".mp4")) and replied.document.file_size <= 5242880)):
        return await message.reply("غير مدعوم !")
    download_location = await client.download_media(message=message.reply_to_message,file_name="root/downloads/")
    try:
        response = upload_file(download_location)
    except Exception as document:
        await message.reply(message, text=document)
    else:
        button_s = InlineKeyboardMarkup([[InlineKeyboardButton("فتح الرابط 🔗", url=f"https://telegra.ph{response[0]}")]])
        await message.reply(f"**الرابط »**\n`https://telegra.ph{response[0]}`",disable_web_page_preview=True,reply_markup=button_s)
    finally:
        os.remove(download_location)

 
@app.on_message(command(["رابط","الرابط","/link"]) & ~filters.bot & ~filters.private)
async def invitelink(client, message):
    chid = message.chat.id
    try:
        invitelink = await client.export_chat_invite_link(chid)
    except:
        return await message.reply_text("قم برفعي مسؤول في المجموعة أولا ؟")
    await message.reply_text(f"تم إنشاء رابط الدعوة بنجاح :\n {invitelink}")

 
@app.on_message(command(["قول"])
    & filters.group
    & ~filters.channel
    & ~filters.edited
)
def echo(client, msg):
    text = msg.text.split(None, 1)[1]
    msg.reply(text)
    
    
@app.on_message(command(["الاوامر"])
    & filters.group
    & ~filters.edited
)
@app.on_message(command(["الاوامر"])
    & filters.channel
    & ~filters.edited
)
async def ahmad(client: Client, message: Message): 
  await message.reply_photo(
    photo=config.START_IMG_URL,
    caption=f"""• أهلا عزيزي اليك اوامر بوت الميوزك •

⌔︙تشغيل او شغل: لبدء تشغيل الاغاني

⌔︙بنك : لقياس سرعة النت في البوت

⌔︙أوامر القناة : تشغيل + أسم الأغنية 

⌔︙كتم : لكتم الأغنية الحالية

⌔︙كمل : لألغاء كتم الأغنبة الحالية

⌔︙تخطي : لتخطي الأغنية الحالية

⌔︙أمر التحميل : تحميل + اسم الاغنية 

⌔︙انهاء او اسكت : لايقاف تشغيل الأغنية الحالية

⌔︙طباعة : بالرد على نص لطباعته

⌔︙ترجمة : بالرد على نص + en او ar

⌔︙ميديا : بالرد على صورة او ملصق

⌔︙ملاحظة : أمر التشغيل في القنوات 👇:

⌔︙اضف البوت الى قناتك ثم أرسل 👇:

⌔︙قناة أو تشغيل او قناه + أسم الاغنية التي تريدها

━━━⊶⛧•[𝚂𝙾𝚄𝚁𝙲𝙴 𝚂𝙴𝙼𝙾](https://t.me/FTTUTY)•⛧⊷━━""",
        reply_markup=InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(f"{YAFA_NAME} ›", url=f"{YAFA_CHANNEL}"),
                ],[
                InlineKeyboardButton(f"• إضـغـط لاضـافـتـيـﮯ لـقـنـاتـڪ ✅ •", url=f"https://t.me/{BOT_USERNAME}?startchannel=true"),
                ],[
                InlineKeyboardButton("• إضـغـط لاضـافـتـيـﮯ لـمـجـمـوعـتـڪ ✅ •", url=f"https://t.me/{BOT_USERNAME}?startgroup=true"),
                ]
            ]
        ),
    )
    
@app.on_message(command(["المبرمج سمير","سمير","سورس","مصنع","مبرمج السورس","السورس","المطور","المبرمج"])
    & filters.group
    & ~filters.edited
)
@app.on_message(command(["المبرمج سمير","سمير","سورس","مصنع","مبرمج السورس","مطور السورس","السورس","المطور","المبرمج"])
    & filters.channel
    & ~filters.edited
)
async def ahmad(client: Client, message: Message):
    await message.reply_photo(
        photo=config.START_IMG_URL,
        caption=f"""• مـرحـبـا بـڪ فـي سـورس سيمو 🔻

[• قناة السورس 🎖](https://t.me/FTTUTY)

[• مـبـرمـجہ آلـسـورس 🎖](https://t.me/DEV_SAMIR)

[• لـتـنـصـيـب بـوتـڪ 🎖](https://t.me/DEV_SAMIR)

[• جـروب الدعـم 🎖](https://t.me/T_S_T99)""",
        reply_markup=InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(" 𝐒 𝐀 𝐌 𝐈 𝐑 ", url=f"{SUDO_USER}",
                ),
                InlineKeyboardButton(f" 𝐒 𝐎 𝐔 𝐑 𝐂 𝐄 ", url=f"{YAFA_CHANNEL}",
                ),
            ],
            [
                InlineKeyboardButton("✅- اضغط لاضفتي لمجموعتك - ✅", url=f"https://t.me/{BOT_USERNAME}?startgroup=true",
                ),
                #InlineKeyboardButton("•لتنصيب بـوتڪ•", url=f"https://t.me/DEV_SAMIR",),
                ]
            ]
        ),
    )
