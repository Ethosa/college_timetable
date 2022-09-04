# -*- coding: utf-8 -*-
"""Provides CollegeAPI class"""
from datetime import datetime
from re import match, sub, IGNORECASE
from typing import List, Dict, Any, Optional, NoReturn, Literal

from requests import Session


class CollegeAPI:
    """Provides working with KTC API"""
    URL = "http://mob.kansk-tc.ru/ktc-api/"

    def __init__(self):
        self.client = Session()
        self.courses = None
        self._init()

    def _init(self) -> NoReturn:
        self.courses = self.get_courses()

    def get_courses(self) -> List[Dict[str, Any]]:
        """Fetches courses

        :return: courses data
        """
        return self.client.get(f'{CollegeAPI.URL}courses/1').json()

    def get_timetable(self, group_id: int, week: Optional[int] = None) -> Dict[str, Any]:
        """Fetches timetable

        :param group_id: group unique ID
        :param week: week number
        :return: timetable data
        """
        if week is None:
            return self.client.get(f'{CollegeAPI.URL}timetable/{group_id}').json()
        return self.client.get(f'{CollegeAPI.URL}timetable/{group_id}/{week}').json()

    def get_day(
            self,
            group_id: int,
            day: Optional[Literal[0, 1, 2, 3, 4, 5]] = None,
            tomorrow: Optional[bool] = False
    ) -> Dict[str, Any]:
        """Fetches current day timetable

        :param group_id: group unique ID
        :param day: day number
        :param tomorrow: needs tomorrow day
        """
        timetable = self.get_timetable(group_id)
        if day is None:
            today = datetime.now().weekday()
            if tomorrow:
                # Get next date
                if today >= 5:
                    # Next week, because 6 is Sunday
                    today = 0
                    timetable = self.get_timetable(group_id, int(timetable['week_number']))
                else:
                    today += 1
                return timetable['days'][today]
            return timetable['days'][today]
        elif 0 <= day <= 6:
            return timetable['days'][day]

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
        """Replaces name with valid name"""
        return sub(r'([\.\s\-]+)', '.', name.upper())
