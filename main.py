# -*- coding: utf-8 -*-
import re
from random import randint, choice
from time import time
from os import remove
from secrets import token_hex

from re import findall, compile, IGNORECASE
from typing import Union, List, Pattern

import requests
from vkbottle import PhotoMessageUploader
from vkbottle.api import API
from vkbottle.bot import Bot, Message
from vkbottle.dispatch.rules.base import RegexRule
from ktc_api.aio import AKTCClient
from markovify.text import Text

from college_api import CollegeAPI
from db import DB, Chat
from image import Img
from config import GROUP_TOKEN, DM_DATA, VOTE_TIMEOUT, ADMINS, MESSAGE_STATES

api = API(token=GROUP_TOKEN)
bot = Bot(api=api)
bot.labeler.vbml_ignore_case = True
uploader = PhotoMessageUploader(api=api)
db = DB(api)
college = CollegeAPI()
client = AKTCClient()
image_worker = Img(dm_data=DM_DATA)


class IRegexRule(RegexRule):
    def __init__(self, regexp: Union[str, List[str], Pattern, List[Pattern]]):
        super().__init__(regexp)
        if isinstance(regexp, Pattern):
            regexp = [regexp]
        elif isinstance(regexp, str):
            regexp = [compile(regexp, IGNORECASE)]
        elif isinstance(regexp, list):
            regexp = [compile(exp, IGNORECASE) for exp in regexp]

        self.regexp = regexp


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


@bot.on.message(IRegexRule(r"/?(help|commands|команды|помощь)"))
async def help_message(msg: Message):
    """Sends help message"""
    user = await db.get_or_add_user_hate_niggers(msg.from_id)
    await msg.answer(
        "Вот, что я умею:\n"
        "◾ помощь - сообщение с доступными командами;\n"
        "◾ группа <Название группы> - установка группы для расписания;\n"
        "◾ расписание - расписание на текущую неделю;\n"
        "◾ след неделя - расписание на следующую неделю;\n"
        "◾ фронт/бэк/время/учитель <HEX цвет> - изменение цвета фона и текста для расписания;\n"
        "◾ дм <верхний текст><с новой строки нижний текст> - генерирует демотиватор;\n"
        "◾ топ/низ - показывает топ пользователей по карме;\n"
        "◾ +/- - проголосовать за пользователя;\n"
        "◾ сегодня/завтра/день недели - расписание на день.\n\n"
        "❗ вместо <ДАННЫЕ> пишите свои данные без <>\n"
        "❗ пример HEX цвета: #212121 #FEFEFE #DD75DD"
    )


@bot.on.message(IRegexRule(r"/?(группа|group)\s+\w{1,3}([\s\.\-]\d{2,3})+?"))
async def change_group(msg: Message):
    """Changes current chat group"""
    user = await db.get_or_add_user_hate_niggers(msg.from_id)
    chat = db.get_or_add_chat(msg.peer_id)
    group = college.to_group_name(findall(r'(\w{1,3}([\s.\-]\d{1,3})+)', msg.text)[0][0])
    group_data = college.get_group(group)
    if group_data is None:
        await msg.answer(f"Группа такой имя нет ❌")
        return
    db.change_chat_group(msg.peer_id, group_data['id'], group_data['title'])
    await msg.answer(f"Группа {group_data['title']} установить этот чат ✔")


@bot.on.message(IRegexRule(r"/?(fore|back|фронт|бек|бэк|teacher|time|учитель|время)\s+#[0-9a-fA-F]{6}"))
async def change_timetable_color(msg: Message):
    """Changes current chat timetable foreground or background"""
    user = await db.get_or_add_user_hate_niggers(msg.from_id)
    chat = db.get_or_add_chat(msg.peer_id)
    word, color = findall(
        r"/?(fore|back|фронт|бек|бэк|teacher|time|учитель|время)\s+(#[0-9a-fA-F]{6}|#[0-9a-fA-F]{8})",
        msg.text)[0]
    match word:
        case "fore" | "фронт":
            db.change_chat_tt_fore(chat.chat_id, color)
            await msg.answer(f"Цвет текст расписание готово ✔")
        case "back" | "бэк" | "бек":
            db.change_chat_tt_back(chat.chat_id, color)
            await msg.answer(f"Фон расписание готово ✔")
        case "teacher" | "учитель":
            db.change_chat_tt(chat.chat_id, 'tt_teacher', color)
            await msg.answer(f"Цвет учитель готово ✔")
        case "time" | "время":
            db.change_chat_tt(chat.chat_id, 'tt_time', color)
            await msg.answer(f"Цвет время готово ✔")


@bot.on.message(IRegexRule(r"/?(расписание|timetable)"))
async def get_timetable(msg: Message):
    """Sends actual timetable if available"""
    user = await db.get_or_add_user_hate_niggers(msg.from_id)
    chat = db.get_or_add_chat(msg.peer_id)
    if chat.title == '':
        await chat_not_installed(msg)
        return
    timetable = college.get_timetable(chat.group_id)
    name = token_hex(16) + '.png'
    image_worker.from_timetable(
        name, timetable,
        chat.timetable_back, chat.timetable_fore,
        chat.timetable_teacher, chat.timetable_time)
    photo = await PhotoMessageUploader(api=api).upload(name)
    remove(name)
    await msg.answer(f"Расписание текущий неделя:", attachment=photo)


@bot.on.message(IRegexRule(r"/?(след\s+неделя|следующая\s+неделя|next\s+week)"))
async def get_next_week_timetable(msg: Message):
    """Sends actual timetable for the next week if available"""
    user = await db.get_or_add_user_hate_niggers(msg.from_id)
    chat = db.get_or_add_chat(msg.peer_id)
    if chat.title == '':
        await chat_not_installed(msg)
        return
    timetable = college.get_timetable(chat.group_id)
    timetable = college.get_timetable(chat.group_id, int(timetable['week_number']) + 1)
    name = token_hex(16) + '.png'
    image_worker.from_timetable(
        name, timetable,
        chat.timetable_back, chat.timetable_fore,
        chat.timetable_teacher, chat.timetable_time)
    photo = await PhotoMessageUploader(api=api).upload(name)
    remove(name)
    await msg.answer(f"Расписание следующая неделя:", attachment=photo)


@bot.on.message(
    IRegexRule(
        r"\A\s*/?\s*(сегодня|today|завтра|tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|"
        r"понедельник|вторник|среда|четверг|пятница|суббота)\s*\Z")
)
async def get_day_timetable(msg: Message):
    """Sends actual timetable for day"""
    user = await db.get_or_add_user_hate_niggers(msg.from_id)
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
        chat.timetable_back, chat.timetable_fore,
        chat.timetable_teacher, chat.timetable_time
    )
    photo = await uploader.upload(name)
    remove(name)
    await msg.answer(f"Расписание {text}:", attachment=photo)


@bot.on.message(IRegexRule(r"/?(dm|дм)([\s\S]+)?"))
async def dm(msg: Message):
    """Sends demotivator"""
    # Get attachments from message
    user = await db.get_or_add_user_hate_niggers(msg.from_id)
    urls = get_attachments_photo(msg)
    if not urls and msg.reply_message:
        urls = get_attachments_photo(msg.reply_message)
    if not urls and msg.fwd_messages:
        for fwd in msg.fwd_messages:
            urls += get_attachments_photo(fwd)
    # Check urls
    if not urls:
        await msg.answer(f"Вы надо отправить чат картинка.")
        return
    # Download images
    images = []
    for url in urls:
        name = token_hex(24) + '.png'
        with open(name, 'wb') as f:
            f.write(requests.get(url).content)
        images.append(name)
    # Translate images to demotivators
    count = 1
    _, text = findall(r"/?(dm|дм)([\s\S]+)?", msg.text)[0]
    text = text.strip()
    if not text:
        image_worker.create_dm(images)
    elif text.isdigit():
        count = int(text)
        if count > 10:
            await msg.answer('Слишком большое количество повторений. Максимум 10.')
            return
        for i in range(count):
            image_worker.create_dm(images)
    else:
        data = text.strip().split('\n')
        if len(data) % 2 != 0:
            data.append('')
        for i, j in zip(data[0::2], data[1::2]):
            if not i and not j:
                image_worker.create_dm(images)
            else:
                image_worker.create_dm(images, i, j)
    # Upload and remove images
    photos = []
    for image in images:
        photos.append(await uploader.upload(image))
        remove(image)
    await msg.answer(attachment=','.join(photos))


@bot.on.message(IRegexRule(r'/?(top|топ|down|низ)'))
async def show_top(msg: Message):
    command = findall(r'/?(top|топ|down|низ)', msg.text, IGNORECASE)[0].lower()
    user = await db.get_or_add_user_hate_niggers(msg.from_id)
    users = []
    match command:
        case 'top' | 'топ':
            users = db.get_users(10)
        case 'down' | 'низ':
            users = db.get_users(10, True)
    await msg.answer(
        '\n'.join(f'{i + 1}. [id{v.uid}|{v.nickname}] ({v.count})'
                  for i, v in enumerate(users))
    )


@bot.on.message(IRegexRule(r'\A\s*/?карма\s*\Z'))
async def karma(msg: Message):
    if msg.from_id > 0:
        user = await db.get_or_add_user_hate_niggers(msg.from_id)
        await msg.answer(f'Ваш социальный кредит: {user.count}')


@bot.on.message(IRegexRule(r'/?([\+\-])'))
async def incdec_count(msg: Message):
    if msg.reply_message is None:
        return
    if msg.reply_message.from_id == msg.from_id:
        await msg.answer('❌ Нельзя менять социальный кредит сам себя.')
        return
    command = findall(r'/?([+\-])', msg.text, IGNORECASE)[0]
    user = await db.get_or_add_user_hate_niggers(msg.from_id)
    timeout = time() - user.last_vote
    if timeout < VOTE_TIMEOUT:
        timeout = VOTE_TIMEOUT - timeout
        hours = str(int(timeout // 60 // 60)).zfill(2)
        mins = str(int((timeout // 60) - (timeout // 60 // 60))).zfill(2)
        seconds = str(int(timeout - timeout // 60 * 60)).zfill(2)
        await msg.answer(f'❌ Извинение ты пока не может голосовать. ⌛ Ждать {hours}:{mins}:{seconds}')
        return
    other = await db.get_or_add_user_hate_niggers(msg.reply_message.from_id)
    result = other.count
    if command == '+':
        await db.inc_user_count(msg.from_id, msg.reply_message.from_id)
        result += 1
    else:
        await db.inc_user_count(msg.from_id, msg.reply_message.from_id, -1)
        result -= 1
    await msg.answer(f'Социальный кредит [id{other.uid}|{other.nickname}] изменять: {other.count} → {result}')


@bot.on.message(IRegexRule(r'/?рассылка ([\s\S]+)'))
async def send_all(msg: Message):
    if msg.from_id not in ADMINS:
        await msg.answer('❌ Извенять. Вы нет права.')
        return
    chats = db.cursor.execute('SELECT * FROM chat').fetchall()
    chats = [Chat.from_tuple(i) for i in chats]
    text = findall(r'/?рассылка ([\s\S]+)', msg.text)[0]
    chats = [chats[i:i + 99] for i in range(0, len(chats), 99)]
    for c in chats:
        await api.messages.send(
            peer_ids=','.join([str(chat.chat_id) for chat in c]),
            message=text, random_id=randint(0, 2e3))


@bot.on.message(IRegexRule(r'/?(жмых|seam carve)(\s+\d{1,2})?'))
async def seam_carve_img(msg: Message):
    percent = 25
    command = findall(r'/?(жмых|seam carve)(\s+\d{1,3})?', msg.text)[0][1].strip()
    if command:
        percent = int(command)
        if percent > 99:
            await msg.answer('Процент не быть больше 100')
            return
    user = await db.get_or_add_user_hate_niggers(msg.from_id)
    urls = get_attachments_photo(msg)
    if not urls and msg.reply_message:
        urls = get_attachments_photo(msg.reply_message)
    if not urls and msg.fwd_messages:
        for fwd in msg.fwd_messages:
            urls += get_attachments_photo(fwd)
    # Check urls
    if not urls:
        await msg.answer(f"Вы надо отправить чат картинка.")
        return
    # Download images
    images = []
    for url in urls:
        name = token_hex(24) + '.png'
        with open(name, 'wb') as f:
            f.write(requests.get(url).content)
        images.append(name)
    await msg.answer('Начинать работать ...')
    await image_worker.seam_carve(images, percent, msg, GROUP_TOKEN)


@bot.on.message(IRegexRule(r'/?(login|логин|вход|auth)\s+(\S+)\s+(\S+)'))
async def auth(msg: Message):
    if msg.peer_id > 2e9:
        await msg.answer('❌ Входить проколедж только личный сообщение')
        return
    command, login, password = findall(r'/?(login|логин|вход|auth)\s+(\S+)\s+(\S+)', msg.text)[0]
    pro = db.auth(msg.from_id, login, password)
    await msg.answer('✅ Данный вход сохранить. Теперь разрешать смотреть оценка.')


@bot.on.message(IRegexRule(r"/?(оценки|grades)"))
async def get_next_week_timetable(msg: Message):
    """Sends actual timetable for the next week if available"""
    pro = db.get_or_add_pro(msg.from_id)
    chat = db.get_or_add_chat(msg.peer_id)
    name = token_hex(16) + '.png'
    try:
        image_worker.create_grades(
            name, await client.grades(pro.login, pro.password),
            chat.timetable_back, chat.timetable_fore,
            chat.timetable_teacher, chat.timetable_time
        )
    except Exception:
        await msg.answer("Случился ошибка. Caught system_error with code 9")
        return
    photo = await PhotoMessageUploader(api=api).upload(name)
    remove(name)
    await msg.answer(f"Ваши оценки:\nЧтобы войти в ProCollege, напишите /логин ЛОГИН ПАРОЛЬ", attachment=photo)


@bot.on.chat_message()
async def on_chat_message(msg: Message):
    state = db.inc_state(msg.peer_id, re.sub(r"{[^}]+}", "", msg.text))
    if state.state == 0:
        text = choice(MESSAGE_STATES)
        model = Text(state.text, well_formed=False)
        for i in re.findall(r"{markov(\d+)}", text):
            try:
                sentence = model.make_sentence_with_start(msg.text.split()[-1], strict=False, tries=25)
            except Exception:
                sentence = None
            if sentence is None:
                sentence = model.make_short_sentence(int(i), tries=25)
            if sentence is None:
                sentence = model.make_sentence(tries=25)
            if sentence is None:
                sentence = ""
            text = text.replace("{markov" + i + "}", sentence)
        await msg.answer(text)


if __name__ == '__main__':
    bot.run_forever()
