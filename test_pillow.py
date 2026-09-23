from parsers.groups import GROUPS
from parsers.parser import get_weeks
from pillow import create_schedule_image


GROUP_NAME = "ИСПД-302"


def main():
    group_id = GROUPS[GROUP_NAME]

    print(
        f"Группа: {GROUP_NAME}"
    )

    _, next_week = get_weeks(group_id)

    image = create_schedule_image(
        next_week,
        title=f"{GROUP_NAME} · следующая неделя",
    )

    image.save(
        "schedule_next_week.png",
        format="PNG",
        optimize=True,
    )

    print("Изображение сохранено: schedule_next_week.png")


if __name__ == "__main__":
    main()