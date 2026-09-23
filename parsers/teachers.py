import logging
import requests

from datetime import date, datetime, timedelta


logger = logging.getLogger(__name__)


TEACHERS = {
    # Математика / информатика
    "шевыряева с.н": (1265, 56),
    "вихорев м.с": (1314, 56),
    "голенищев а.б": (1315, 56),
    "гончарова е.и": (1269, 56),
    "горшенина е.и": (1247, 56),
    "кондрашкин в.и": (405, 56),
    "корогод н.а": (1306, 56),
    "маскайкин е.п": (554, 56),
    "олейников а.а": (1232, 56),
    "солович в.о": (1293, 56),
    "суздалев а.с": (967, 56),
    "шафикова г.а": (1241, 56),

    # Технические / управленческие
    "голышев и.д": (1160, 48),
    "давыдов д.в": (1319, 48),
    "дерябичева м.о": (549, 48),
    "жигарь о.в": (1267, 48),
    "здунов в.и": (1263, 48),
    "зубков м.с": (1284, 48),
    "ионова ю.в": (1295, 48),
    "камдина л.в": (1261, 48),
    "костенок п.и": (1322, 48),
    "кулаков а.б": (171, 48),
    "кулакова ю.н": (187, 48),
    "макаренко е.в": (1304, 48),
    "маскайкина е.в": (347, 48),
    "осташевский с.м": (957, 48),
    "репникова л.н": (92, 48),
    "сотников а.с": (1318, 48),
    "чивильский а.в": (492, 48),
    "шагеев д.а": (1258, 48),
    "ярушина": (1176, 48),

    # Общие / гуманитарные
    "артишевский": (1288, 55),
    "балынская": (1273, 55),
    "болдырева": (1242, 55),
    "власова": (823, 55),
    "гресь": (1296, 55),
    "добрынина": (1280, 55),
    "казаченок": (1289, 55),
    "киуру": (997, 55),
    "коваль": (1285, 55),
    "колесников": (482, 55),
    "колесникова": (1312, 55),
    "курочкина": (1305, 55),
    "лаптев": (1300, 55),
    "линьков": (1302, 55),
    "лукашевич": (1221, 55),
    "миниханов": (1317, 55),
    "мудряков": (1310, 55),
    "оринина": (1311, 55),
    "погудина": (1264, 55),
    "приходько": (1290, 55),
    "пушкарева": (1248, 55),
    "рогозина": (723, 55),
    "сивкова": (1309, 55),
    "спирина": (142, 55),
    "стукалов": (1294, 55),
    "тифанюк": (1308, 55),
    "ульянова": (1106, 55),
    "фефелова": (992, 55),
    "шахматов": (1236, 55),

    # Экономика
    "бардин": (438, 47),
    "галкина": (629, 47),
    "голованова": (1125, 47),
    "долгих": (547, 47),
    "жилина": (292, 47),
    "зубкова": (367, 47),
    "кабытова": (1303, 47),
    "киреева": (12, 47),
    "лобанов": (1307, 47),
    "моторин": (1321, 47),
    "нестеренко": (110, 47),
    "пастернак": (524, 47),
    "пряхин": (1320, 47),
    "романова": (434, 47),
    "сельницына": (6, 47),
    "сергеичева": (416, 47),
    "стародубова": (490, 47),
    "степанова": (1210, 47),
    "худяков": (1301, 47),
    "ческидова": (590, 47),
}


def get_teacher_id(name: str):
    """
    Возвращает:
        teacher_id, department_id
    """

    name = name.strip().lower()

    teacher = TEACHERS.get(name)

    if not teacher:
        return None

    return teacher


def get_week_dates(target_date: date):
    """
    Возвращает понедельник и воскресенье недели.
    """

    monday = (
        target_date
        - timedelta(days=target_date.weekday())
    )

    sunday = monday + timedelta(days=6)

    return monday, sunday


def get_teacher_schedule(
    name: str,
    target_date: date | None = None,
):
    """
    Получает расписание преподавателя
    на неделю target_date.
    """

    teacher = get_teacher_id(name)

    if not teacher:
        raise ValueError(
            f"Преподаватель не найден: {name}"
        )

    teacher_id, department_id = teacher

    if target_date is None:
        target_date = date.today()

    monday, sunday = get_week_dates(
        target_date
    )

    date_start = monday.strftime(
        "%d.%m.%Y"
    )

    date_end = sunday.strftime(
        "%d.%m.%Y"
    )

    url = (
        "https://old.ursei.su/Services/"
        "GetTeacherSched"
        f"?departid={department_id}"
        f"&empid={teacher_id}"
        f"&dstart={date_start}"
        f"&dend={date_end}"
    )

    logger.info(
        "Запрос расписания преподавателя | "
        "teacher=%s | teacher_id=%s | "
        "department=%s | %s - %s",
        name,
        teacher_id,
        department_id,
        date_start,
        date_end,
    )

    response = requests.get(
        url,
        timeout=10,
    )

    response.raise_for_status()

    data = response.json()

    logger.info(
        "Получено расписание преподавателя | teacher=%s",
        name,
    )

    return data

def parse_teacher_schedule(data):
    schedule = []

    for month in data:

        for day in month.get("DateDay", []):

            lessons = []

            for lesson in day.get(
                "Schedule",
                []
            ):
                lessons.append({
                    "time": lesson.get(
                        "TimeStart",
                        ""
                    ),
                    "subject": lesson.get(
                        "SubjName",
                        ""
                    ),
                    "type": lesson.get(
                        "LoadKindSN",
                        ""
                    ),
                    "teacher": "",
                    "room": lesson.get(
                        "Aud",
                        ""
                    ),
                    "group": lesson.get(
                        "GSName",
                        ""
                    ),
                })

            current_date = datetime.strptime(
                day["DatePair"],
                "%d.%m.%Y"
            ).date()

            schedule.append({
                "date": current_date,
                "weekday": day.get(
                    "DayWeek",
                    ""
                ),
                "weekday_short": "",
                "lessons": lessons,
            })

    return schedule

if __name__ == "__main__":
    teacher_name = "олейников а.а"

    data = get_teacher_schedule(teacher_name)

    schedule = parse_teacher_schedule(data)

    print(f"Найдено дней: {len(schedule)}")

    for day in schedule:
        print(day)