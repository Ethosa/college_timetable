# -*- coding: utf-8 -*-
from typing import Dict, Any, List
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont


class Img:
    def __init__(self):
        self.title_font = ImageFont.truetype('Symbola.ttf', 32, encoding='UTF-8')
        self.font = ImageFont.truetype('Symbola.ttf', 24, encoding='UTF-8')
        self.small_font = ImageFont.truetype('Symbola.ttf', 16, encoding='UTF-8')

    def _draw_days(
            self,
            days: List[Dict[str, Any]],
            draw: ImageDraw,
            w: int,
            y_offset: int,
            foreground: str
    ) -> int:
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
                draw.text((offset + 4, y + 8), lesson['time'][0], foreground, self.title_font)
                draw.multiline_text(
                    (offset + 36, y), lesson['time'][1] + '\n' + lesson['time'][2],
                    foreground,
                    self.font
                )
                # Draw lesson title
                lesson_title = '\n'.join(wrap(lesson['title'], 30))
                box = draw.multiline_textbbox((0, 0), lesson_title, self.font)
                h = box[3] if box[3] > 0 else 32
                # Draw lesson teacher and classroom
                draw.multiline_text((offset + 96, y), lesson_title, foreground, self.font)
                teacher_classroom = lesson['teacher'] + ', ' + lesson['classroom']
                length = draw.textlength(teacher_classroom, self.small_font)
                draw.text(
                    ((w3 - 96) / 2 - length / 2 + offset + 96, y + h),
                    teacher_classroom,
                    foreground,
                    self.small_font
                )
                y += 64
                if max_y < y:
                    max_y = y
            offset += w3
        return max_y

    def from_timetable(
            self,
            name: str,
            timetable: Dict[str, Any],
            background: str,
            foreground: str
    ):
        w, h = 1024, 900
        img = Image.new('RGBA', (w, h), background)
        draw = ImageDraw.Draw(img, 'RGBA')
        week_title = f'{timetable["week_number"]} неделя'
        length = draw.textlength(week_title, self.title_font)
        draw.text((w / 2 - length / 2, 32), week_title, foreground, self.title_font)

        y_offset = 128  # offset from week title
        max_y = self._draw_days(timetable['days'][:3], draw, w, y_offset, foreground)
        y_offset = max_y + 64
        self._draw_days(timetable['days'][3:], draw, w, y_offset, foreground)

        img.save(name)