# -*- coding: utf-8 -*-
from re import match, sub, IGNORECASE
from typing import List, Dict, Any, Optional

from requests import Session


class CollegeAPI:
    URL = "http://mob.kansk-tc.ru/ktc-api/"

    def __init__(self):
        self.client = Session()
        self.courses = None
        self._init()

    def _init(self):
        self.courses = self.get_courses()

    def get_courses(self) -> List[Dict[str, Any]]:
        return self.client.get(f'{CollegeAPI.URL}courses/1').json()

    def get_timetable(self, group_id: int, week: Optional[int] = None) -> Dict[str, Any]:
        if week is None:
            return self.client.get(f'{CollegeAPI.URL}timetable/{group_id}').json()
        return self.client.get(f'{CollegeAPI.URL}timetable/{group_id}/{week}').json()

    def get_group(self, pattern: str) -> Dict[str, Any]:
        """Returns True, if group exists

        :param pattern: group title regex pattern
        """
        if self.courses is not None:
            for course in self.courses:
                for group in course['groups']:
                    if match(pattern, group['title'], IGNORECASE):
                        return group

    def has_group(self, pattern: str) -> bool:
        """Returns True, if group exists

        :param pattern: group title regex pattern
        """
        if self.courses is not None:
            for course in self.courses:
                for group in course['groups']:
                    if match(pattern, group['title'], IGNORECASE):
                        return True

    @staticmethod
    def to_group_name(name: str) -> str:
        return sub(r'([\.\s\-]+)', '.', name.upper())
