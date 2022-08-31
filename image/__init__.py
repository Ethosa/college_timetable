# -*- coding: utf-8 -*-
from random import choice
from typing import Dict, Any, List, NoReturn, Optional, Union, Tuple
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont


class Img:
    """Provides working with pillow"""
    def __init__(
            self,
            font_path: str = 'NotoSans-Regular.ttf',
            encoding: str = 'utf-8',
            xl_size: int = 32,
            lg_size: int = 22,
            sm_size: int = 16,
            xxxl_size: int = 64,
            xxl_size: int = 42,
            dm_data: Optional[List[Union[str, Tuple[str, str]]]] = None
    ):
        """Initializes class and creates fonts

        :param font_path: path to font file
        :param encoding: font encoding
        :param xl_size: title text size
        :param lg_size: text size
        :param sm_size: small text size
        :param xxxl_size: extra large text size
        :param xxl_size: large text size
        :param dm_data: data for dm
        """
        ttf = lambda size: ImageFont.truetype(font_path, size, encoding=encoding)
        self.title_font = ttf(xl_size)
        self.font_mini = ttf(int(xl_size * 0.75))
        self.font = ttf(lg_size)
        self.small_font = ttf(sm_size)
        self.dm_title_font = ttf(xxxl_size)
        self.dm_font = ttf(xxl_size)
        self.dm_data = dm_data

    def _draw_days(
            self,
            days: List[Dict[str, Any]],
            draw: ImageDraw,
            w: int,
            y_offset: int,
            foreground: str
    ) -> int:
        """Draws list of days

        :param days: days data
        :param draw: ImageDraw instance
        :param w: day width
        :param y_offset: y offset
        :param foreground: foreground color
        :return: maximum y from days
        """
        offset = 0
        w3 = w / 3
        max_y = y_offset

        for day in days:
            y = y_offset
            # Draw day title
            length = draw.textlength(day['title'], self.font)
            draw.text((w3 / 2 - length / 2 + offset, y), day['title'], foreground, self.font)

            y += 32
            for lesson in day['lessons']:
                # Draw lesson <hr>
                draw.line([(offset + 8, y), (offset + w3 - 8, y)], foreground, 1)
                y += 4
                # Draw lesson time
                # Lesson number
                x = offset + draw.textlength(lesson['time'][0], self.title_font)
                draw.text((offset + 4, y + 8), lesson['time'][0], foreground, self.title_font)
                # Lesson time from and time to
                x += 16
                draw.multiline_text(
                    (x, y), lesson['time'][1] + '\n' + lesson['time'][2],
                    foreground,
                    self.font_mini
                )
                # Draw lesson title
                lesson_title = '\n'.join(wrap(lesson['title'], 22))
                title_font = self.font_mini
                _, _, _w, _h = draw.multiline_textbbox((0, 0), lesson['time'][1], self.font_mini)
                x += _w
                _, _, _w, _h = draw.multiline_textbbox((0, 0), lesson_title, self.font_mini)
                if _h == 0:
                    _h = 32
                draw.multiline_text(
                    ((x + ((w3 - (x - offset)) / 2 - _w / 2)), y),
                    lesson_title, foreground, title_font, align='center')
                # Draw lesson teacher and classroom
                teacher_classroom = lesson['teacher'] + ', ' + lesson['classroom']
                length = draw.textlength(teacher_classroom, self.small_font)
                draw.text(
                    ((w3 - length + offset - 8), y + _h),
                    teacher_classroom, foreground, self.small_font
                )
                y += _h + 36
                if max_y < y:
                    max_y = y
            offset += w3
        return max_y

    def from_day(
            self,
            name: str,
            day: Dict[str, Any],
            background: str,
            foreground: str
    ) -> NoReturn:
        """Creates an image from day

        :param name: file name
        :param day: day data
        :param background: background color
        :param foreground: foreground color
        :return:
        """
        w, h = 512, 600
        y = 16
        img = Image.new('RGBA', (w, h), background)
        draw = ImageDraw.Draw(img, 'RGBA')

        # Draw day title
        _, _, width, height = draw.textbbox((0, 0), day['title'], self.title_font)
        draw.text((w/2 - width/2, y), day['title'], foreground, self.title_font)
        y += height + 32

        # Draw lessons
        for lesson in day['lessons']:
            # Draw lesson <hr>
            draw.line([(8, y), (w - 8, y)], foreground, 1)
            y += 4
            # Draw lesson time
            # Lesson number
            x = draw.textlength(lesson['time'][0], self.title_font)
            draw.text((4, y + 8), lesson['time'][0], foreground, self.title_font)
            # Lesson time from and time to
            x += 16
            draw.multiline_text(
                (x, y), lesson['time'][1] + '\n' + lesson['time'][2],
                foreground,
                self.font_mini
            )
            # Draw lesson title
            lesson_title = '\n'.join(wrap(lesson['title'], 22))
            title_font = self.font_mini
            _, _, _w, _h = draw.multiline_textbbox((0, 0), lesson['time'][1], self.font_mini)
            x += _w
            _, _, _w, _h = draw.multiline_textbbox((0, 0), lesson_title, self.font_mini)
            if _h == 0:
                _h = 32
            draw.multiline_text(
                ((x + ((w - x) / 2 - _w / 2)), y),
                lesson_title, foreground, title_font, align='center')
            # Draw lesson teacher and classroom
            teacher_classroom = lesson['teacher'] + ', ' + lesson['classroom']
            length = draw.textlength(teacher_classroom, self.small_font)
            draw.text(
                ((w - length - 8), y + _h),
                teacher_classroom, foreground, self.small_font
            )
            y += _h + 36

        # Save and clear
        img.save(name)
        del img
        del draw

    def from_timetable(
            self,
            name: str,
            timetable: Dict[str, Any],
            background: str,
            foreground: str
    ) -> NoReturn:
        """Creates an image from timetable

        :param name: file name
        :param timetable: timetable data
        :param background: background color
        :param foreground: foreground color
        """
        w, h = 1280, 900
        y = 32
        img = Image.new('RGBA', (w, h), background)
        draw = ImageDraw.Draw(img, 'RGBA')

        # Draw week title
        week_title = f'{timetable["week_number"]} неделя'
        length = draw.textlength(week_title, self.title_font)
        draw.text((w / 2 - length / 2, y), week_title, foreground, self.title_font)

        # Draw week days
        y += 96  # offset from week title
        max_y = self._draw_days(timetable['days'][:3], draw, w, y, foreground)
        y = max_y + 32
        self._draw_days(timetable['days'][3:], draw, w, y, foreground)

        # Save and clear
        img.save(name)
        del img
        del draw

    def create_dm(
            self,
            images: List[str],
            title: Optional[str] = '',
            text: Optional[str] = ''
    ) -> NoReturn:
        """Creates dm image

        :param images: list of image paths
        :param title: title text
        :param text: subtitle text
        """
        is_random = False
        if not title and not text:
            is_random = True
            if not self.dm_data:
                return
        w, h = 1024, 1150
        for file in images:
            if is_random:
                result = choice(self.dm_data)
                if isinstance(result, str):
                    title, text = result, ''
                else:
                    title, text = result
            src = Image.open(file)
            dst = Image.new('RGBA', (w, h), "black")
            draw = ImageDraw.Draw(dst, 'RGBA')

            # Draw box
            draw.rectangle((62, 62, 961, 961), "white")

            # Paste source to destination
            src = src.resize((896, 896))
            dst.paste(src, (64, 64))

            # Draw first line
            _, _, width, height = draw.textbbox((0, 0), title, self.dm_title_font)
            draw.text((w/2 - width/2, 968), title, "white", self.dm_title_font)

            # Draw second line
            _, _, width, height = draw.textbbox((0, 0), text, self.dm_font)
            draw.text((w/2 - width/2, 1048), text, "white", self.dm_font)

            # Clear
            dst.save(file)
            del src
            del dst
            del draw
