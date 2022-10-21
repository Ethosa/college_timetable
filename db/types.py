# -*- coding: utf-8 -*-
from typing import Tuple


class Chat:
    @staticmethod
    def from_tuple(data: Tuple[int, int, str]) -> 'Chat':
        return Chat(*data)

    def __init__(
            self,
            chat_id: int,
            group_id: int,
            title: str,
            timetable_back: str,
            timetable_fore: str,
            timetable_teacher: str,
            timetable_time: str
    ):
        self.chat_id = chat_id
        self.group_id = group_id
        self.title = title
        self.timetable_fore = timetable_fore
        self.timetable_back = timetable_back
        self.timetable_teacher = timetable_teacher
        self.timetable_time = timetable_time

    def __repr__(self) -> str:
        return (
            f"Chat[{self.chat_id}::{self.group_id}] '{self.title}' "
            f"({self.timetable_back}, {self.timetable_fore}, "
            f"{self.timetable_teacher}, {self.timetable_time})"
        )


class User:
    @staticmethod
    def from_tuple(data: Tuple[int, int, str]) -> 'User':
        return User(*data)

    def __init__(
            self,
            uid: int,
            nickname: str,
            count: int,
            last_vote: int
    ):
        self.uid = uid
        self.nickname = nickname
        self.count = count
        self.last_vote = last_vote

    def __repr__(self) -> str:
        return f"User[{self.uid}]::{self.count} {self.nickname}"


class ProCollege:
    @staticmethod
    def from_tuple(data: Tuple[int, str, str]) -> 'ProCollege':
        return ProCollege(*data)

    def __init__(
            self,
            uid: int,
            login: str,
            password: str
    ):
        self.uid = uid
        self.login = login
        self.password = password


class PhraseState:
    @staticmethod
    def from_tuple(data: Tuple[int, int, str]) -> 'PhraseState':
        return PhraseState(*data)

    def __init__(
            self,
            chat_id: int,
            state: int,
            text: str
    ):
        self.chat_id = chat_id
        self.state = state
        self.text = text
