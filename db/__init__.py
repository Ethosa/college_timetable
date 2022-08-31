# -*- coding: utf-8 -*-
from sqlite3 import connect
from typing import Literal

from .types import Chat


class DB:
    """Provides convenient working with database"""
    def __init__(self):
        """Initializes class and create database if it not exists"""
        self.db = connect('chats.db')
        self.cursor = self.db.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat (
                id INTEGER NOT NULL,  -- chat unique ID
                group_id INTEGER NOT NULL,  -- group unique ID
                title TEXT NOT NULL,  -- group title
                tt_back TEXT NOT NULL,  -- timetable background
                tt_fore TEXT NOT NULL,  -- timetable foreground
                tt_teacher TEXT NOT NULL, -- timetable teacher foreground
                tt_time TEXT NOT NULL  -- timetable time foreground
            )
        ''')
        self.db.commit()

    def get_or_add_chat(self, chat_id: int) -> Chat:
        """Get chat or create new if it not exists

        :param chat_id: unique chat ID
        :return: Chat data
        """
        chat = self.cursor.execute('SELECT * FROM chat WHERE id = ?', (chat_id,)).fetchone()
        if chat is None:
            self.cursor.execute(
                'INSERT INTO chat (id, title, group_id, tt_back, tt_fore, tt_teacher, tt_time) '
                'VALUES (?, ?, ?, ?, ?, ?, ?)',
                (chat_id, '', 0, '#212121', '#fefefe', '#cecece', '#98cd98')
            )
            self.db.commit()
            chat = (chat_id, 0, '', '#212121', '#fefefe', '#cecece', '#98cd98')
        return Chat.from_tuple(chat)

    def change_chat_group(self, chat_id: int, group_id: int, title: str):
        """Changes chat group

        :param chat_id: unique chat ID
        :param group_id: unique group ID
        :param title: group title
        """
        chat = self.get_or_add_chat(chat_id)
        self.cursor.execute(
            'UPDATE chat SET title = ?, group_id = ? WHERE id = ?',
            (title, group_id, chat_id)
        )
        self.db.commit()

    def change_chat_tt(
            self,
            chat_id: int,
            color_name: Literal['tt_fore', 'tt_back', 'tt_teacher', 'tt_time'],
            color: str
    ):
        """Changes chat timetable color

        :param chat_id: unique chat ID
        :param color_name: color name
        :param color: HEX color
        """
        chat = self.get_or_add_chat(chat_id)
        self.cursor.execute(
            f'UPDATE chat SET {color_name} = ? WHERE id = ?',
            (color, chat_id)
        )
        self.db.commit()

    def change_chat_tt_fore(self, chat_id: int, color: str):
        """Changes chat timetable foreground

        :param chat_id: unique chat ID
        :param color: foreground color
        """
        chat = self.get_or_add_chat(chat_id)
        self.cursor.execute(
            'UPDATE chat SET tt_fore = ? WHERE id = ?',
            (color, chat_id)
        )
        self.db.commit()

    def change_chat_tt_back(self, chat_id: int, color: str):
        """Changes chat timetable background

        :param chat_id: unique chat ID
        :param color: background color
        """
        chat = self.get_or_add_chat(chat_id)
        self.cursor.execute(
            'UPDATE chat SET tt_back = ? WHERE id = ?',
            (color, chat_id)
        )
        self.db.commit()