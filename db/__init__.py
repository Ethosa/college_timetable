# -*- coding: utf-8 -*-
from sqlite3 import connect

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
                tt_fore TEXT NOT NULL  -- timetable foreground
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
                'INSERT INTO chat (id, title, group_id, tt_back, tt_fore) VALUES (?, ?, ?, ?, ?)',
                (chat_id, '', 0, '#212121', '#fefefe')
            )
            self.db.commit()
            chat = (chat_id, 0, '', '#212121', '#fefefe')
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