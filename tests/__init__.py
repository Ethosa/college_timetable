from unittest import main, TestCase
from college_api import CollegeAPI


class CollegeAPITests(TestCase):
    api = CollegeAPI()

    def test_get_courses(self):
        print(self.api.get_courses())

    def test_get_timetable(self):
        print(self.api.get_timetable(264))

    def test_get_day_timetable(self):
        print(self.api.get_day(264))
        print(self.api.get_day(264, 5))


if __name__ == '__main__':
    main(verbosity=2)
