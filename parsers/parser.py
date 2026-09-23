import requests
from datetime import datetime, date, timedelta


API_URL = (
    "https://api.ursei.su/public/schedule/rest/"
    "GetGsSched?grpid={}"
)


def get_schedule(group_id: int):
    url = API_URL.format(group_id)

    response = requests.get(
        url,
        timeout=8,
    )

    response.raise_for_status()

    return response.json()


def parse_schedule(data):
    schedule = []

    for month in data.get("Month", []):
        for day in month.get("Sched", []):

            lessons = []

            for lesson in day.get("mainSchedule", []):
                lessons.append({
                    "time": lesson.get("TimeStart", ""),
                    "subject": lesson.get("SubjName", ""),
                    "type": lesson.get("LoadKindSN", ""),
                    "teacher": lesson.get("FIO", ""),
                    "room": lesson.get("Aud", ""),
                })

            try:
                day_date = datetime.strptime(
                    day["datePair"],
                    "%d.%m.%Y"
                ).date()
            except (KeyError, ValueError):
                continue

            schedule.append({
                "date": day_date,
                "weekday": day.get("dayWeek", ""),
                "weekday_short": day.get("dayWeekShort", ""),
                "lessons": lessons,
            })

    return schedule


def get_week(schedule, target_date: date):

    monday = (
        target_date
        - timedelta(days=target_date.weekday())
    )

    sunday = monday + timedelta(days=6)

    return [
        day
        for day in schedule
        if monday <= day["date"] <= sunday
    ]


def get_weeks(group_id: int):

    data = get_schedule(group_id)

    schedule = parse_schedule(data)

    today = date.today()

    current_week = get_week(
        schedule,
        today,
    )

    next_week = get_week(
        schedule,
        today + timedelta(days=7),
    )

    return current_week, next_week