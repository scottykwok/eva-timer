from js import console
from js import URLSearchParams, window
import datetime

gui_timer = None
gui_parent = None
gui_settings = None
timer = None
config = None


class SELECTORS:
    def __init__(self):
        self.PANEL_TIMER = "#pan-clock"
        self.PANEL_POWER = "#pan-power"
        self.ALL_TEXT = "text"
        self.ALL_BORDERS = "path[id*=border], rect[id*=border]"
        self.ALL_DOT_GREEN = "#dot-green line"
        self.ALL_RECTS = "rect"
        self.ALL_LINES = "line"
        self.ALL_PATHS = "path"
        self.ALL_CLICKABLES = "[id^=clickable-]"
        self.ALL_HELP_TEXTS = "[id^=help-]"
        self.BORDER_STOP = "#border-stop"
        self.BORDER_SLOW = "#border-slow"
        self.BORDER_NORMAL = "#border-normal"
        self.BORDER_RACING = "#border-racing"
        self.BUTTON_POWER_INTERNAL = "#pan-internal"
        self.BUTTON_POWER_EXTERNAL = "#pan-external"
        self.BUTTON_POWER_SYSETM = "#pan-system"
        self.BUTTON_STOP = "#pan-stop"
        self.BUTTON_SLOW = "#pan-slow"
        self.BUTTON_NORMAL = "#pan-normal"
        self.BUTTON_RACING = "#pan-racing"
        self.BUTTON_EMERGENCY = "#pan-emergency"
        self.DOT_EMERGENCY = "#dot-emergency1, #dot-emergency2"
        self.BAR_STOP = "#bar-stop"
        self.BAR_SLOW = "#bar-slow"
        self.BAR_NORMAL = "#bar-normal"
        self.BAR_RACING = "#bar-racing"
        self.TEXT_STOP = "#text-stop"
        self.TEXT_SLOW = "#text-slow"
        self.TEXT_NORMAL = "#text-normal"
        self.TEXT_RACING = "#text-racing"
        self.TEXTGROUP_ACTIVE_TIME = "#textgroup-active-time"
        self.STRIP_INTERNAL = "#strip-internal"
        self.STRIP_EXTERNAL = "#strip-external"
        self.CLICKABLE_TOP = "#clickable-top"
        self.CLICKABLE_LEFT = "#clickable-left"
        self.CLICKABLE_BOTTOM = "#clickable-bottom"
        self.TEXTGROUP_TIMER = "#textgroup-clock"
        self.TEXTGROUP_SYSTEM_TIMER = "#textgroup-clock-sys"
        self.TEXT_SYSTEM_TIMER_MIN_SEC = "#text-min-sec-sys"
        self.TEXT_SYSTEM_TIMER_CENTISEC = "#text-millis-sys"
        self.TEXT_MIN_SEC = "#text-min-sec"
        self.TEXT_CENTISEC = "#text-millis"
        self.TEXT_TIMER = "#text-min-sec, #text-millis, #text-min-sec-sys, #text-millis-sys"


class STYLES:
    def __init__(self):
        self.CLICKABLE = "clickable"
        self.DARKEN = "darken"
        self.BLINK = "blink"
        self.BREATH = "breath"
        self.BLINK_FAST = "blink-fast"
        self.BLINK_SHOW = "blink-show"
        self.BLINK_HIDE = "blink-hide"
        self.VIEW_FLATTENED = "view-flattened"
        self.VIEW_TILTED = "view-tilted"


SEL = SELECTORS()
STY = STYLES()


def render_callback(time):
    if time is None:  # timer in systemtime mode
        now = datetime.datetime.now()
        minutes = now.hour
        seconds = now.minute
        centiseconds = now.second
    else:  # timer in countdown/up mode
        minutes = int((time % 3600) / 60)
        seconds = int(time % 60)
        centiseconds = int((time % 1) * 100)
    if minutes < 10:
        gui_timer.select(SEL.TEXTGROUP_TIMER).show()
        gui_timer.select(SEL.TEXTGROUP_SYSTEM_TIMER).hide()
        gui_timer.select(SEL.TEXT_MIN_SEC).text_content(f"{minutes:01d}:{seconds:02d}")
        gui_timer.select(SEL.TEXT_CENTISEC).text_content(f":{centiseconds:02d}")
    else:
        gui_timer.select(SEL.TEXTGROUP_TIMER).hide()
        gui_timer.select(SEL.TEXTGROUP_SYSTEM_TIMER).show()
        gui_timer.select(SEL.TEXT_SYSTEM_TIMER_MIN_SEC).text_content(f"{minutes:02d}:{seconds:02d}")
        gui_timer.select(SEL.TEXT_SYSTEM_TIMER_CENTISEC).text_content(f":{centiseconds:02d}")


# For status rendering
def status_callback(from_status, to_status, from_running, to_running):
    # print(f"Debug: {from_status} -> {to_status}. Running: {from_running} -> {to_running}")
    match to_status:
        case timer.STANDBY:
            show_standby()
        case timer.RACING:
            show_racing()
        case timer.EMERGENCY:
            show_emergency()
        case timer.ENDED:
            show_ended()
        case timer.SYSTEMTIME:
            show_system_time()
        case _:
            console.log(f"Error: {from_status} -> {to_status}. Running: {from_running} -> {to_running}")
    # Blink the STOP button
    if not to_running and to_status != timer.ENDED:
        gui_timer.select(SEL.BAR_STOP).add_class(STY.BREATH).show()
        gui_timer.select(SEL.TEXTGROUP_TIMER).add_class(STY.BREATH)
    else:
        gui_timer.select(SEL.BAR_STOP).remove_class(STY.BREATH).hide()
        gui_timer.select(SEL.TEXTGROUP_TIMER).remove_class(STY.BREATH)


def config_callback():
    gui_settings.select("#countdown").set_checked(timer.mode == timer.MODE_COUNT_DOWN)
    gui_settings.select("#countup").set_checked(timer.mode == timer.MODE_COUNT_UP)
    gui_settings.select("#systemtime").set_checked(timer.mode == timer.MODE_SYSTEM_TIME)

    gui_settings.select("#autoplay").set_checked(config["autoplay"] == 1)
    gui_settings.select("#tilted").set_checked(config["tilted"] == 1)
    gui_settings.select("#fullscreen").set_checked(config["fullscreen"] == 1)
    gui_settings.select("#wireframe").set_checked(config["theme"] == "wireframe")
    gui_settings.select("#greyscale").set_checked(config["theme"] == "greyscale")


def register_event_listeners_timer():
    # Play/Pause/Reset when click on the timer
    gui_timer.select(SEL.PANEL_TIMER).clickable().on_click(lambda e: (timer.reset() if timer.time_is_up() else timer.toggle_play_pause(),))

    # Settings
    gui_timer.select(SEL.PANEL_POWER).clickable().on_click(
        lambda e: gui_settings.toggle_visibility(),
    )

    # Tilt View
    gui_timer.select(SEL.CLICKABLE_TOP).clickable().on_click(
        lambda e: gui_timer.toggle_class(STY.VIEW_FLATTENED),
    )

    # Fullscreen
    gui_timer.select(SEL.CLICKABLE_LEFT).clickable().on_click(
        lambda e: gui_parent.toggle_fullscreen(),
    )

    # To System Clock
    gui_timer.select(SEL.BUTTON_NORMAL).clickable().on_click(
        lambda e: (
            timer.reset(),
            timer.set_mode(timer.MODE_SYSTEM_TIME),
        )
    )

    # To Count Up / Down
    gui_timer.select(SEL.BUTTON_RACING).clickable().on_click(lambda e: (timer.reset() or timer.toggle_mode_count_updown()))

    # Stop
    gui_timer.select(SEL.BUTTON_STOP).clickable().on_click(lambda e: timer.reset())

    # TBC
    # gui_timer.select("#clickable-bottom").clickable().on_click(
    #     lambda e: True,
    # )


def register_event_listeners_settings():
    # For settings.html
    gui_settings.select("#countdown").on_click(
        lambda e: timer.set_mode(0),
    )
    gui_settings.select("#countup").on_click(
        lambda e: timer.set_mode(1),
    )
    gui_settings.select("#systemtime").on_click(
        lambda e: timer.set_mode(2),
    )
    gui_settings.select("#tiltedview").on_click(
        lambda e: gui_timer.toggle_class(STY.VIEW_FLATTENED),
    )
    gui_settings.select("#fullscreen").on_click(
        lambda e: gui_parent.toggle_fullscreen(),
    )
    gui_settings.select("#wireframe").on_click(
        lambda e: toggle_wireframe(),
    )
    gui_settings.select("#greyscale").on_click(
        lambda e: toggle_greyscale(),
    )
    gui_settings.select("#ok").on_click(
        lambda e: gui_settings.hide(),
    )

    # maximum duration
    gui_settings.select("#duration").on_input(
        lambda element, e: timer.parse_duration(element.value),
    ).on_focusout(
        lambda element, e: gui_settings.select("#duration").set_value(timer.format_duration()),
    )

    # emergency duration
    gui_settings.select("#emergency_duration").on_input(
        lambda element, e: timer.parse_emergency_duration(element.value),
    ).on_focusout(
        lambda element, e: gui_settings.select("#emergency_duration").set_value(timer.format_emergency_duration()),
    )


def register_keyboard_listeners():
    def on_keydown(event):
        match event.code:
            case "Space":
                event.preventDefault()
                timer.toggle_play_pause()
            case "KeyR":
                _ = timer.reset() or timer.toggle_mode()
            case "KeyP":
                gui_timer.toggle_class(STY.VIEW_FLATTENED)
            case "KeyF":
                gui_parent.toggle_fullscreen()
            case "KeyS":
                gui_settings.toggle_visibility()
            case "KeyW":
                toggle_wireframe()
            case "KeyG":
                toggle_greyscale()
            case "ArrowUp":
                event.preventDefault()
                timer.adjust_elapsed_time(-1)
            case "ArrowDown":
                event.preventDefault()
                timer.adjust_elapsed_time(+1)
            case "Escape":
                gui_settings.hide()
            case "KeyD":
                pass
            case "+":
                pass
            case "-":
                pass
            case _:
                pass

    gui_timer.select_document().add_event_listener("keydown", on_keydown)


def show_standby():
    gui_timer.select(SEL.TEXTGROUP_TIMER).add_class(STY.BREATH)
    gui_timer.select(
        [
            SEL.ALL_TEXT,
            SEL.ALL_DOT_GREEN,
            SEL.DOT_EMERGENCY,
            SEL.ALL_BORDERS,
        ]
    ).reset_all_color()
    gui_timer.select([SEL.STRIP_INTERNAL, SEL.BAR_RACING]).remove_class(STY.BLINK_FAST)
    gui_timer.select([SEL.BUTTON_EMERGENCY, SEL.TEXTGROUP_ACTIVE_TIME]).remove_class(STY.BLINK)
    gui_timer.select(
        [
            SEL.BUTTON_EMERGENCY,
            SEL.BUTTON_POWER_EXTERNAL,
            SEL.BUTTON_POWER_INTERNAL,
            SEL.BAR_STOP,
            SEL.BAR_SLOW,
            SEL.BAR_NORMAL,
            SEL.BAR_RACING,
            SEL.TEXT_STOP,
            SEL.TEXT_SLOW,
            SEL.TEXT_NORMAL,
            SEL.TEXT_RACING,
            SEL.BORDER_STOP,
            SEL.BORDER_SLOW,
            SEL.BORDER_NORMAL,
            SEL.BORDER_RACING,
            SEL.BUTTON_EMERGENCY,
            SEL.STRIP_EXTERNAL,
            SEL.STRIP_INTERNAL,
        ]
    ).show()


def show_racing():
    gui_timer.select(
        [
            SEL.BAR_STOP,
            SEL.BAR_SLOW,
            SEL.BAR_NORMAL,
            SEL.BUTTON_EMERGENCY,
            SEL.BUTTON_POWER_EXTERNAL,
        ]
    ).hide()
    gui_timer.blink_show_hide(
        [SEL.BUTTON_POWER_INTERNAL, SEL.STRIP_INTERNAL, SEL.BAR_RACING],
        [SEL.BUTTON_POWER_EXTERNAL, SEL.STRIP_EXTERNAL, SEL.BAR_NORMAL, SEL.BUTTON_EMERGENCY],
    )


def show_emergency():
    gui_timer.select([SEL.ALL_TEXT, SEL.ALL_DOT_GREEN, SEL.DOT_EMERGENCY]).all_color("red")
    gui_timer.select(SEL.ALL_BORDERS).stroke_color("red")
    gui_timer.select(SEL.BUTTON_EMERGENCY).show()
    gui_timer.select(
        [
            SEL.BUTTON_POWER_EXTERNAL,
            SEL.BAR_STOP,
            SEL.BAR_SLOW,
            SEL.BAR_NORMAL,
            SEL.BAR_RACING,
        ]
    ).hide()
    gui_timer.blink_show_hide([SEL.BUTTON_EMERGENCY], [SEL.BAR_RACING])


def show_ended():
    gui_timer.select([SEL.STRIP_INTERNAL, SEL.BAR_RACING]).toggle_class(STY.BLINK_FAST)
    gui_timer.select([SEL.BUTTON_EMERGENCY, SEL.TEXTGROUP_ACTIVE_TIME]).toggle_class(STY.BLINK)
    gui_timer.select(SEL.BAR_RACING).show()
    gui_timer.select(
        [
            SEL.BUTTON_POWER_EXTERNAL,
            SEL.BAR_STOP,
            SEL.BAR_SLOW,
            SEL.BAR_NORMAL,
            SEL.TEXT_SLOW,
            SEL.TEXT_NORMAL,
            SEL.TEXT_RACING,
            SEL.BORDER_SLOW,
            SEL.BORDER_NORMAL,
            SEL.BORDER_RACING,
        ]
    ).hide()


def show_system_time():
    console.log("show_system_time")
    gui_timer.select(SEL.TEXTGROUP_TIMER).remove_class(STY.BREATH)
    gui_timer.blink_show_hide(
        [SEL.BUTTON_POWER_EXTERNAL, SEL.STRIP_EXTERNAL, SEL.BAR_NORMAL, SEL.BUTTON_EMERGENCY],
        [SEL.BUTTON_POWER_INTERNAL, SEL.STRIP_INTERNAL, SEL.BAR_RACING, SEL.BAR_STOP, SEL.BAR_SLOW],
    )


def toggle_wireframe():
    # Shapes
    gui_timer.select(
        [
            SEL.ALL_LINES,
            SEL.ALL_RECTS,
            SEL.ALL_PATHS,
        ]
    ).toggle_class("wireframe")

    # Keep the clickable areas filled
    gui_timer.select(SEL.ALL_CLICKABLES).toggle_class("wireframe")

    # Text
    gui_timer.select(SEL.ALL_TEXT).toggle_class("opacity70").toggle_class("wireframe")

    # Timer Text
    gui_timer.select(SEL.TEXT_TIMER).toggle_class("wireframe-bold")

    # Set Help text visible
    gui_timer.select(SEL.ALL_HELP_TEXTS).hide()


def toggle_greyscale():
    toggle_wireframe()
    gui_timer.select(SEL.TEXT_TIMER).toggle_class("greyscale")
    gui_timer.select(SEL.TEXT_TIMER).toggle_class("wireframe-bold")

