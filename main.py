import sys
import math
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar
import tcod


FILLED_TICK_MARK = "\u2593"
UNFILLED_TICK_MARK = "\u2591"
FILLED_COLOR = (0, 255, 0)
UNFILLED_COLOR = (255, 255, 255)


def days_into_year():
    today = datetime.today()
    year_start = datetime(today.year, 1, 1)
    return (today - year_start).days + 1


def days_to_end_of_year():
    today = datetime.today()
    year_end = datetime(today.year, 12, 31)
    return (year_end - today).days + 1


def days_in_year(year=datetime.now().year):
    return 365 + calendar.isleap(year)


def progress_display(percent,
                     percent_per_tick=5,
                     display_percent=True,
                     display_count=False,
                     current_value=-1,
                     max_value=-1):
    max_ticks = 100 // percent_per_tick
    filled_ticks = percent // percent_per_tick
    unfilled_ticks = max_ticks - filled_ticks
    display_str = f"[{FILLED_TICK_MARK * filled_ticks}{UNFILLED_TICK_MARK * unfilled_ticks}]"
    if display_percent:
        display_str += f" {percent}%"
    if display_count:
        display_str += f" ({current_value}/{max_value})"
    return display_str


def draw_progress_display(console,
                          x,
                          y,
                          percent,
                          percent_per_tick=5,
                          display_percent=True,
                          display_count=False,
                          current_value=-1,
                          max_value=-1,
                          fg_override=None):
    max_ticks = 100 // percent_per_tick
    filled_ticks = percent // percent_per_tick
    unfilled_ticks = max_ticks - filled_ticks

    full_bar_str = f"[{UNFILLED_TICK_MARK * max_ticks}]"
    if display_percent:
        full_bar_str += f" {percent}%"
    if display_count:
        full_bar_str += f" ({current_value}/{max_value})"

    fill_bar_str = FILLED_TICK_MARK * filled_ticks

    console.print(x=x, y=y, string=full_bar_str, fg=UNFILLED_COLOR)
    console.print(x=x + 1, y=y, string=fill_bar_str, fg=fg_override if fg_override else FILLED_COLOR)


def draw_year_progress(console, x, y):
    year_progress = days_into_year() / days_in_year()
    percent = math.floor(year_progress * 100.0)
    return draw_progress_display(console, x, y, percent, display_count=True, current_value=days_into_year(), max_value=days_in_year())


def draw_month_progress(console, x, y):
    today = datetime.today()
    month_end_day = calendar.monthrange(today.year, today.month)[1]
    percent = math.floor(today.day / month_end_day * 100.0)
    return draw_progress_display(console, x, y, percent, display_count=True, current_value=today.day, max_value=month_end_day)


def draw_day_progress(console, x, y):
    now = datetime.now()
    day_start = datetime(now.year, now.month, now.day, 0, 0, 0)
    minutes_since_start = (now - day_start).seconds // 60
    percent = math.floor(minutes_since_start / 1440.0 * 100.0)
    return draw_progress_display(console, x, y, percent, display_count=True, current_value=minutes_since_start, max_value=1440)


def draw_death_progress(console, x, y, life_expectancy):
    birthday = datetime(1995, 2, 14)
    expected_death = birthday + relativedelta(years=int(life_expectancy))
    now = datetime.now()
    days_in = (now - birthday).days
    days_left = (expected_death - now).days
    total_days = (expected_death - birthday).days
    percent = math.floor(days_in / total_days * 100.0)
    return draw_progress_display(console, x, y, percent, display_count=True, current_value=days_in, max_value=total_days, fg_override=(255, 0, 0))


def main():
    display_death = len(sys.argv) > 1 and sys.argv[1] == "death"
    life_expectancy = sys.argv[2] if len(sys.argv) > 2 else -1
    tileset = tcod.tileset.load_tilesheet("fonts/terminal16x16_gs_ro.png", 16, 16, tcod.tileset.CHARMAP_CP437)
    console = tcod.Console(40, 12 if display_death else 10, order="F")

    with tcod.context.new(columns=console.width, rows=console.height, tileset=tileset, title="Year Progress") as context:
        while True:
            console.clear()

            now = datetime.now()

            console.print(x=0, y=0, string="Year Progress: 2023 Edition")
            console.print(x=0, y=2, string="Today:")
            draw_day_progress(console, 0, 3)
            console.print(x=0, y=4, string=f"{now.strftime('%b')}:")
            draw_month_progress(console, 0, 5)
            console.print(x=0, y=6, string=f"{now.year}:")
            draw_year_progress(console, 0, 7)
            if display_death:
                console.print(x=0, y=9, string="Life:")
                draw_death_progress(console, 0, 10, life_expectancy)

            context.present(console)

            for event in tcod.event.wait():
                context.convert_event(event)
                if isinstance(event, tcod.event.Quit):
                    raise SystemExit()


if __name__ == '__main__':
    main()
