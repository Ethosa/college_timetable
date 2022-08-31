# -*- coding: utf-8 -*-
from os import remove
from secrets import token_hex

from re import findall

import requests
from vkbottle import PhotoMessageUploader
from vkbottle.api import API
from vkbottle.bot import Bot, Message
from vkbottle.dispatch.rules.base import RegexRule

from college_api import CollegeAPI
from db import DB
from image import Img
from config import GROUP_TOKEN, DM_DATA

api = API(token=GROUP_TOKEN)
bot = Bot(api=api)
bot.labeler.vbml_ignore_case = True
uploader = PhotoMessageUploader(api=api)
db = DB()
college = CollegeAPI()
image_worker = Img(dm_data=DM_DATA)


async def chat_not_installed(msg: Message):
    await msg.answer("Необходимо настроить текущую группу.\nИспользуйте комманду /группа ГРУППА")


def get_attachments_photo(msg: Message):
    """Gets attachments from message

    :param msg: message object
    :return: list of photo URLs
    """
    urls = []
    for attachment in msg.attachments:
        if attachment.type.value == "photo":
            w, url = 0, None
            for size in attachment.photo.sizes:
                if size.width > w:
                    w, url = size.width, size.url
            if url is not None:
                urls.append(url)
    return urls


@bot.on.message(RegexRule(r"/?(help|commands|команды|помощь)"))
async def help_message(msg: Message):
    """Sends help message"""
    await msg.answer(
        "Вот, что я умею:\n"
        "◾ помощь - сообщение с доступными командами;\n"
        "◾ группа <Название группы> - установка группы для расписания;\n"
        "◾ расписание - расписание на текущую неделю;\n"
        "◾ след неделя - расписание на следующую неделю;\n"
        "◾ фронт/бэк <HEX цвет> - изменение цвета фона и текста для расписания;\n"
        "◾ дм <верхний текст><с новой строки нижний текст> - генерирует демотиватор;\n"
        "◾ сегодня/завтра/день недели - расписание на день.\n\n"
        "❗ вместо <ДАННЫЕ> пишите свои данные без <>\n"
        "❗ пример HEX цвета: #212121 #FEFEFE #DD75DD"
    )


@bot.on.message(RegexRule(r"/?(группа|group)\s+\w{1,3}([\s\.\-]\d{2,3})+?"))
async def change_group(msg: Message):
    """Changes current chat group"""
    chat = db.get_or_add_chat(msg.peer_id)
    group = college.to_group_name(findall(r'(\w{1,3}([\s\.\-]\d{1,3})+)', msg.text)[0][0])
    group_data = college.get_group(group)
    if group_data is None:
        await msg.answer(f"Увы, но такой группы нет❌")
        return
    db.change_chat_group(msg.peer_id, group_data['id'], group_data['title'])
    await msg.answer(f"Группа {group_data['title']} успешно установлена в этом чате✔")


@bot.on.message(RegexRule(r"/?(fore|back|фронт|бек|бэк)\s+#[0-9a-fA-F]{6}"))
async def change_timetable_color(msg: Message):
    """Changes current chat timetable foreground or background"""
    chat = db.get_or_add_chat(msg.peer_id)
    word, color = findall(r"/?(fore|back|фронт|бек|бэк)\s+(#[0-9a-fA-F]{6})", msg.text)[0]
    match word:
        case "fore" | "фронт":
            db.change_chat_tt_fore(chat.chat_id, color)
            await msg.answer(f"Цвет текста в расписании успешно изменен✔")
        case "back" | "бэк" | "бек":
            db.change_chat_tt_back(chat.chat_id, color)
            await msg.answer(f"Фон расписания успешно изменен✔")


@bot.on.message(RegexRule(r"/?(расписание|timetable)"))
async def get_timetable(msg: Message):
    """Sends actual timetable if available"""
    chat = db.get_or_add_chat(msg.peer_id)
    if chat.title == '':
        await chat_not_installed(msg)
        return
    timetable = college.get_timetable(chat.group_id)
    name = token_hex(16) + '.png'
    image_worker.from_timetable(name, timetable, chat.timetable_back, chat.timetable_fore)
    photo = await PhotoMessageUploader(api=api).upload(name)
    remove(name)
    await msg.answer(f"Расписание на текущую неделю:", attachment=photo)


@bot.on.message(RegexRule(r"/?(след\s+неделя|следующая\s+неделя|next\s+week)"))
async def get_next_week_timetable(msg: Message):
    """Sends actual timetable for the next week if available"""
    chat = db.get_or_add_chat(msg.peer_id)
    if chat.title == '':
        await chat_not_installed(msg)
        return
    timetable = college.get_timetable(chat.group_id)
    timetable = college.get_timetable(chat.group_id, int(timetable['week_number'])+1)
    name = token_hex(16) + '.png'
    image_worker.from_timetable(name, timetable, chat.timetable_back, chat.timetable_fore)
    photo = await PhotoMessageUploader(api=api).upload(name)
    remove(name)
    await msg.answer(f"Расписание на следующую неделю:", attachment=photo)


@bot.on.message(
    RegexRule(
        r"/?(сегодня|today|завтра|tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|"
        r"понедельник|вторник|среда|четверг|пятница|суббота)")
)
async def get_day_timetable(msg: Message):
    """Sends actual timetable for day"""
    text = msg.text.lstrip('/').lower()
    chat = db.get_or_add_chat(msg.peer_id)
    if chat.title == '':
        await chat_not_installed(msg)
        return
    # Generate random file name
    name = token_hex(16) + '.png'
    # if day is None - day is current
    day = None
    # works when day is None
    tomorrow = False
    match text:
        case 'tomorrow' | 'завтра':
            tomorrow = True
        case 'monday' | 'понедельник':
            day = 0
        case 'tuesday' | 'вторник':
            day = 1
        case 'wednesday' | 'среда':
            day = 2
        case 'thursday' | 'четверг':
            day = 3
        case 'friday' | 'пятница':
            day = 4
        case 'saturday' | 'суббота':
            day = 5
    image_worker.from_day(
        name, college.get_day(chat.group_id, day, tomorrow),
        chat.timetable_back,
        chat.timetable_fore
    )
    photo = await uploader.upload(name)
    remove(name)
    await msg.answer(f"Расписание на {text}:", attachment=photo)


@bot.on.message(RegexRule(r"/?(dm|дм)(\s+([^\n]+)\s+([^\n]+))?"))
async def dm(msg: Message):
    """Sends demotivator"""
    # Get attachments from message
    urls = get_attachments_photo(msg)
    if not urls and msg.reply_message:
        urls = get_attachments_photo(msg.reply_message)
    if not urls and msg.fwd_messages:
        for fwd in msg.fwd_messages:
            urls += get_attachments_photo(fwd)
    # Check urls
    if not urls:
        await msg.answer(f"Вы должны отправить картинку.")
        return
    # Download images
    images = []
    for url in urls:
        name = token_hex(24) + '.png'
        with open(name, 'wb') as f:
            f.write(requests.get(url).content)
        images.append(name)
    # Translate images to demotivators
    _, _, title, text = findall(r"/?(dm|дм)(\s+([^\n]+)\s+([^\n]+))?", msg.text)[0]
    if not title and not text:
        image_worker.create_dm(images)
    else:
        image_worker.create_dm(images, title, text)
    # Upload and remove images
    photos = []
    for image in images:
        photos.append(await uploader.upload(image))
        remove(image)
    await msg.answer(attachment=','.join(photos))


if __name__ == '__main__':
    bot.run_forever()
