# -*- coding: utf-8 -*-
from os import remove
from secrets import token_hex

from re import findall
from vkbottle import PhotoMessageUploader
from vkbottle.api import API
from vkbottle.bot import Bot, Message
from vkbottle.dispatch.rules.base import RegexRule

from college_api import CollegeAPI
from db import DB
from image import Img
from config import GROUP_TOKEN

api = API(token=GROUP_TOKEN)
bot = Bot(api=api)
db = DB()
college = CollegeAPI()
image_worker = Img()


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
        await msg.answer("Необходимо настроить текущую группу.\nИспользуйте комманду /группа ГРУППА")
        return
    timetable = college.get_timetable(chat.group_id)
    name = token_hex(16) + '.png'
    image_worker.from_timetable(name, timetable, chat.timetable_back, chat.timetable_fore)
    photo = await PhotoMessageUploader(api=api).upload(name)
    remove(name)
    await msg.answer(f"Расписание на текущую неделю:", attachment=photo)


@bot.on.message(RegexRule(r"/?(след неделя|next week)"))
async def get_next_week_timetable(msg: Message):
    """Sends actual timetable for the next week if available"""
    chat = db.get_or_add_chat(msg.peer_id)
    if chat.title == '':
        await msg.answer("Необходимо настроить текущую группу.\nИспользуйте комманду /группа ГРУППА")
        return
    timetable = college.get_timetable(chat.group_id)
    timetable = college.get_timetable(chat.group_id, int(timetable['week_number'])+1)
    name = token_hex(16) + '.png'
    image_worker.from_timetable(name, timetable, chat.timetable_back, chat.timetable_fore)
    photo = await PhotoMessageUploader(api=api).upload(name)
    remove(name)
    await msg.answer(f"Расписание на следующую неделю:", attachment=photo)


if __name__ == '__main__':
    bot.run_forever()
