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
            timetable_fore: str
    ):
        self.chat_id = chat_id
        self.group_id = group_id
        self.title = title
        self.timetable_fore = timetable_fore
        self.timetable_back = timetable_back

    def __repr__(self) -> str:
        return (
            f"Chat[{self.chat_id}::{self.group_id}] '{self.title}' "
            f"({self.timetable_back}, {self.timetable_fore})"
        )
