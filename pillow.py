from datetime import date
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFont


# ============================================================
# CONFIG
# ============================================================

IMAGE_WIDTH = 1000

# iOS / Apple Dark Mode
BG_COLOR = (14, 14, 16)
CARD_COLOR = (27, 27, 29)

TEXT_PRIMARY = (248, 248, 250)
TEXT_SECONDARY = (174, 174, 180)
TEXT_MUTED = (120, 120, 125)

BORDER = (48, 48, 52)

SIDE_PADDING = 32
CARD_PADDING = 26

HEADER_HEIGHT = 116
DAY_HEADER_HEIGHT = 70

LESSON_HEIGHT = 88
DAY_GAP = 18

CARD_RADIUS = 22


# ============================================================
# FONTS
# ============================================================

@lru_cache(maxsize=1)
def _get_fonts():
    """
    Шрифты загружаются один раз и кэшируются.
    """

    regular_path = (
        "/usr/share/fonts/truetype/dejavu/"
        "DejaVuSans.ttf"
    )

    bold_path = (
        "/usr/share/fonts/truetype/dejavu/"
        "DejaVuSans-Bold.ttf"
    )

    try:
        return {
            "title": ImageFont.truetype(
                bold_path,
                32,
            ),
            "subtitle": ImageFont.truetype(
                regular_path,
                16,
            ),
            "day": ImageFont.truetype(
                bold_path,
                23,
            ),
            "subject": ImageFont.truetype(
                bold_path,
                20,
            ),
            "time": ImageFont.truetype(
                bold_path,
                18,
            ),
            "detail": ImageFont.truetype(
                regular_path,
                15,
            ),
            "room": ImageFont.truetype(
                bold_path,
                18,
            ),
        }

    except OSError:
        default = ImageFont.load_default()

        return {
            "title": default,
            "subtitle": default,
            "day": default,
            "subject": default,
            "time": default,
            "detail": default,
            "room": default,
        }


# ============================================================
# TEXT HELPERS
# ============================================================

def _text_width(
    draw: ImageDraw.ImageDraw,
    text: str,
    font,
) -> int:
    """
    Возвращает ширину текста.
    """

    bbox = draw.textbbox(
        (0, 0),
        text,
        font=font,
    )

    return bbox[2] - bbox[0]


def _truncate_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font,
    max_width: int,
) -> str:
    """
    Обрезает слишком длинный текст,
    чтобы он не выходил за границы.
    """

    text = str(text or "")

    if not text:
        return ""

    if _text_width(
        draw,
        text,
        font,
    ) <= max_width:
        return text

    suffix = "..."

    while text:

        candidate = text + suffix

        if _text_width(
            draw,
            candidate,
            font,
        ) <= max_width:
            return candidate

        text = text[:-1]

    return suffix


# ============================================================
# DATE
# ============================================================

_MONTHS = (
    "января",
    "февраля",
    "марта",
    "апреля",
    "мая",
    "июня",
    "июля",
    "августа",
    "сентября",
    "октября",
    "ноября",
    "декабря",
)


def _format_date(value: date) -> str:
    return f"{value.day} {_MONTHS[value.month - 1]}"


# ============================================================
# LESSON STYLE
# ============================================================

def _get_lesson_style(lesson_type: str) -> tuple:
    """
    Возвращает основной цвет занятия.

    Цвет используется одновременно для:
    - индикатора;
    - времени;
    - аудитории.

    Остальной текст остаётся нейтральным.
    """

    lesson_type = str(
        lesson_type or ""
    ).lower()

    if "лекц" in lesson_type:
        return (10, 132, 255)

    if "практ" in lesson_type:
        return (48, 209, 88)

    if "лаборатор" in lesson_type:
        return (191, 90, 242)

    if "экзамен" in lesson_type:
        return (255, 69, 58)

    if "зачет" in lesson_type:
        return (255, 159, 10)

    if "семинар" in lesson_type:
        return (100, 210, 255)

    if "консультац" in lesson_type:
        return (142, 142, 147)

    return (10, 132, 255)


# ============================================================
# MAIN
# ============================================================

def create_schedule_image(
    schedule: list[dict],
    title: str = "Расписание",
) -> Image.Image:
    """
    Создаёт изображение расписания в стиле iOS.

    Принимает результат get_week() из parsers/parser.py.

    Формат:

        [
            {
                "date": date(...),
                "weekday": "Среда",
                "weekday_short": "Ср",
                "lessons": [
                    {
                        "time": "08:30",
                        "subject": "Программирование",
                        "type": "Лекция",
                        "teacher": "Иванов И.И.",
                        "room": "301",
                    }
                ],
            }
        ]

    Возвращает PIL.Image.
    """

    fonts = _get_fonts()

    # --------------------------------------------------------
    # CALCULATE HEIGHT
    # --------------------------------------------------------

    total_height = HEADER_HEIGHT

    for day in schedule:

        lessons = day.get(
            "lessons",
            [],
        )

        lesson_count = max(
            len(lessons),
            1,
        )

        day_height = (
            DAY_HEADER_HEIGHT
            + lesson_count * LESSON_HEIGHT
            + CARD_PADDING
        )

        total_height += (
            day_height
            + DAY_GAP
        )

    total_height += 26

    # --------------------------------------------------------
    # CREATE IMAGE
    # --------------------------------------------------------

    image = Image.new(
        "RGB",
        (
            IMAGE_WIDTH,
            total_height,
        ),
        BG_COLOR,
    )

    draw = ImageDraw.Draw(image)

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    header_x = SIDE_PADDING
    header_y = 24

    # Системный iOS blue accent
    draw.rounded_rectangle(
        (
            header_x,
            header_y + 5,
            header_x + 6,
            header_y + 61,
        ),
        radius=3,
        fill=(10, 132, 255),
    )

    # Заголовок
    draw.text(
        (
            header_x + 22,
            header_y,
        ),
        title,
        font=fonts["title"],
        fill=TEXT_PRIMARY,
    )

    # Подзаголовок
    draw.text(
        (
            header_x + 22,
            header_y + 47,
        ),
        "Расписание занятий",
        font=fonts["subtitle"],
        fill=TEXT_SECONDARY,
    )

    # Тонкая линия
    draw.line(
        (
            SIDE_PADDING,
            HEADER_HEIGHT - 1,
            IMAGE_WIDTH - SIDE_PADDING,
            HEADER_HEIGHT - 1,
        ),
        fill=BORDER,
        width=1,
    )

    # --------------------------------------------------------
    # DAYS
    # --------------------------------------------------------

    y = HEADER_HEIGHT + 16

    for day in schedule:

        lessons = day.get(
            "lessons",
            [],
        )

        lesson_count = max(
            len(lessons),
            1,
        )

        day_height = (
            DAY_HEADER_HEIGHT
            + lesson_count * LESSON_HEIGHT
            + CARD_PADDING
        )

        x1 = SIDE_PADDING
        x2 = IMAGE_WIDTH - SIDE_PADDING

        y1 = y
        y2 = y + day_height

        # ----------------------------------------------------
        # DAY CARD
        # ----------------------------------------------------

        draw.rounded_rectangle(
            (
                x1,
                y1,
                x2,
                y2,
            ),
            radius=CARD_RADIUS,
            fill=CARD_COLOR,
            outline=BORDER,
            width=1,
        )

        # ----------------------------------------------------
        # DAY HEADER
        # ----------------------------------------------------

        current_date = day.get("date")

        if current_date:
            date_text = _format_date(
                current_date
            )
        else:
            date_text = ""

        weekday = str(
            day.get("weekday", "")
        )

        if date_text and weekday:
            day_title = (
                f"{date_text} · {weekday}"
            )
        else:
            day_title = (
                date_text
                or weekday
            )

        draw.text(
            (
                x1 + CARD_PADDING,
                y1 + 19,
            ),
            day_title,
            font=fonts["day"],
            fill=TEXT_PRIMARY,
        )

        # ----------------------------------------------------
        # LESSON COUNT
        # ----------------------------------------------------

        count = len(lessons)

        if count == 1:
            lesson_word = "пара"
        elif 2 <= count <= 4:
            lesson_word = "пары"
        else:
            lesson_word = "пар"

        count_text = (
            f"{count} {lesson_word}"
        )

        count_width = _text_width(
            draw,
            count_text,
            fonts["detail"],
        )

        draw.text(
            (
                x2
                - CARD_PADDING
                - count_width,
                y1 + 25,
            ),
            count_text,
            font=fonts["detail"],
            fill=TEXT_MUTED,
        )

        # ----------------------------------------------------
        # LESSONS
        # ----------------------------------------------------

        lesson_y = (
            y1
            + DAY_HEADER_HEIGHT
        )

        if not lessons:

            draw.text(
                (
                    x1 + CARD_PADDING,
                    lesson_y + 18,
                ),
                "Нет занятий",
                font=fonts["detail"],
                fill=TEXT_MUTED,
            )

        for index, lesson in enumerate(
            lessons
        ):

            # ------------------------------------------------
            # DIVIDER
            # ------------------------------------------------

            if index > 0:

                draw.line(
                    (
                        x1 + CARD_PADDING,
                        lesson_y,
                        x2 - CARD_PADDING,
                        lesson_y,
                    ),
                    fill=BORDER,
                    width=1,
                )

            content_y = (
                lesson_y + 15
            )

            # ------------------------------------------------
            # LESSON COLOR
            # ------------------------------------------------

            lesson_color = (
                _get_lesson_style(
                    lesson.get("type")
                )
            )

            # ------------------------------------------------
            # LEFT INDICATOR
            # ------------------------------------------------

            draw.rounded_rectangle(
                (
                    x1 + CARD_PADDING,
                    content_y + 1,
                    x1 + CARD_PADDING + 5,
                    content_y + 54,
                ),
                radius=3,
                fill=lesson_color,
            )

            # ------------------------------------------------
            # TIME
            # ------------------------------------------------

            time_x = (
                x1
                + CARD_PADDING
                + 18
            )

            time_text = str(
                lesson.get(
                    "time",
                    "",
                )
            )

            draw.text(
                (
                    time_x,
                    content_y + 1,
                ),
                time_text,
                font=fonts["time"],
                fill=lesson_color,
            )

            # ------------------------------------------------
            # SUBJECT
            # ------------------------------------------------

            subject_x = (
                time_x + 78
            )

            room = str(
                lesson.get(
                    "room",
                    "",
                )
                or ""
            )

            # Немного больше места под аудиторию,
            # потому что шрифт теперь крупнее.
            room_reserved_width = (
                115
                if room
                else 0
            )

            subject_max_width = (
                x2
                - subject_x
                - CARD_PADDING
                - room_reserved_width
            )

            subject = _truncate_text(
                draw,
                lesson.get(
                    "subject",
                    "",
                ),
                fonts["subject"],
                subject_max_width,
            )

            draw.text(
                (
                    subject_x,
                    content_y,
                ),
                subject,
                font=fonts["subject"],
                fill=TEXT_PRIMARY,
            )

            # ------------------------------------------------
            # ROOM
            # ------------------------------------------------

            if room:

                room_text = _truncate_text(
                    draw,
                    room,
                    fonts["room"],
                    90,
                )

                room_text_width = (
                    _text_width(
                        draw,
                        room_text,
                        fonts["room"],
                    )
                )

                room_x = (
                    x2
                    - CARD_PADDING
                    - room_text_width
                )

                draw.text(
                    (
                        room_x,
                        content_y + 1,
                    ),
                    room_text,
                    font=fonts["room"],
                    fill=lesson_color,
                )

            # ------------------------------------------------
            # TYPE + TEACHER
            # ------------------------------------------------

            details = []

            lesson_type = lesson.get(
                "type"
            )

            if lesson_type:
                details.append(
                    str(lesson_type)
                )

            teacher = lesson.get(
                "teacher"
            )

            if teacher:
                details.append(
                    str(teacher)
                )

            detail_text = "  ·  ".join(
                details
            )

            if detail_text:

                detail_max_width = (
                    x2
                    - subject_x
                    - CARD_PADDING
                )

                detail_text = _truncate_text(
                    draw,
                    detail_text,
                    fonts["detail"],
                    detail_max_width,
                )

                draw.text(
                    (
                        subject_x,
                        content_y + 38,
                    ),
                    detail_text,
                    font=fonts["detail"],
                    fill=TEXT_SECONDARY,
                )

            lesson_y += LESSON_HEIGHT

        y += (
            day_height
            + DAY_GAP
        )

    return image