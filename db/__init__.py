# -*- coding: utf-8 -*-
from sqlite3 import connect

from .types import Chat


class DB:
    def __init__(self):
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
        chat = self.get_or_add_chat(chat_id)
        self.cursor.execute(
            'UPDATE chat SET title = ?, group_id = ? WHERE id = ?',
            (title, group_id, chat_id)
        )
        self.db.commit()