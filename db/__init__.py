# -*- coding: utf-8 -*-
from time import time
from sqlite3 import connect
from typing import Literal, NoReturn, List

from vkbottle import API

from .types import Chat, User, ProCollege


class DB:
    """Provides convenient working with database"""
    def __init__(self, api: API):
        """Initializes class and create database if it not exists"""
        self.api = api
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
            );
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER NOT NULL,  -- user ID,
                nickname TEXT NOT NULL,  -- user nickname
                count INTEGER NOT NULL,  -- user count
                last_vote INTEGER NOT NULL  -- last user vote time
            );
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS procollege (
                id INTEGER NOT NULL,  -- user ID
                login TEXT NOT NULL,  -- user login
                password TEXT NOT NULL
            );
        ''')
        self.db.commit()

    async def get_or_add_user(self, uid: int) -> User:
        """Get user or create new if it not exists

        :param uid: user ID
        :return: user data
        """
        if uid <= 0 or uid >= 2e9:
            return
        user = self.cursor.execute('SELECT * FROM user WHERE id = ?', (uid,)).fetchone()
        if user is None:
            nickname = (await self.api.users.get(uid))[0].first_name
            self.cursor.execute(
                'INSERT INTO user (id, nickname, count, last_vote) VALUES (?, ?, ?, ?)',
                (uid, nickname, 0, 0))
            self.db.commit()
            user = (uid, nickname, 0, 0)
        return User.from_tuple(user)

    def get_users(self, limit: int, need_reverse: bool = False) -> List[User]:
        """Returns users top

        :param limit: users count limit
        :param need_reverse: need reverse users
        :return: users data
        """
        data = self.cursor.execute(
            f'SELECT * FROM user ORDER BY count {"ASC" if need_reverse else "DESC"} LIMIT ?', (limit,)
        ).fetchall()
        return [User.from_tuple(i) for i in data]

    async def inc_user_count(self, from_id: int, uid: int, by: int = 1) -> NoReturn:
        """Increases/decreases user's count

        :param from_id: user ID who voted
        :param uid: user ID
        :param by: count for inc/dec (1/-1)
        """
        user = await self.get_or_add_user(uid)
        self.cursor.execute('UPDATE user SET count = ? WHERE id = ?', (user.count + by, uid))
        user_voted = await self.get_or_add_user(from_id)
        self.cursor.execute('UPDATE user SET last_vote = ? WHERE id = ?', (int(time()), from_id))
        self.db.commit()

    def get_or_add_chat(self, chat_id: int) -> Chat:
        """Get chat or create new if it not exists

        :param chat_id: unique chat ID
        :return: Chat data
        """
        chat = self.cursor.execute('SELECT * FROM chat WHERE id = ?', (chat_id,)).fetchone()
        if chat is None:
            data = (chat_id, 0, '', '#212121', '#fefefe', '#cecece', '#98cd98')
            self.cursor.execute(
                'INSERT INTO chat (id, group_id, title, tt_back, tt_fore, tt_teacher, tt_time) '
                'VALUES (?, ?, ?, ?, ?, ?, ?)', data
            )
            self.db.commit()
            chat = data
        return Chat.from_tuple(chat)

    def get_or_add_pro(self, uid: int) -> ProCollege:
        pro = self.cursor.execute('SELECT * FROM procollege WHERE id = ?', (uid,)).fetchone()
        if pro is None:
            data = (uid, '', '')
            self.cursor.execute(
                'INSERT INTO procollege(id, login, password) VALUES(?, ?, ?)', data
            )
            self.db.commit()
            pro = data
        return ProCollege.from_tuple(pro)

    def auth(self, uid: int, login: str, password: str):
        pro = self.get_or_add_pro(uid)
        self.cursor.execute('UPDATE procollege SET login = ?, password = ? WHERE id = ?', (login, password, uid))
        self.db.commit()

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