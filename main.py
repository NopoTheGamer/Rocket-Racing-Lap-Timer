# import required libraries
import time
import cv2
import screeninfo
from vidgear.gears import ScreenGear
from sendWebhook import send_webhook
import PIL
import dxcam

# define dimensions of screen w.r.t to given monitor to be captured
monitors = screeninfo.get_monitors()
primary_monitor = monitors[0]
monitor_width, monitor_height = primary_monitor.width, primary_monitor.height
options = {'top': 0, 'left': 0, 'width': monitor_width, 'height': monitor_height}

# open video stream with defined parameters
stream = ScreenGear(logging=True, **options).start()

monitor_str = "1080p"
if monitor_height == 1440:
    monitor_str = "1440p"

def current_milli_time():
    return round(time.time() * 1000)


def match_image(template, screenshot):
    # Convert images to grayscale if they have multiple channels
    if len(template.shape) == 3:
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    else:
        template_gray = template

    if len(screenshot.shape) == 3:
        screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    else:
        screenshot_gray = screenshot

    # Perform template matching
    result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)

    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    return max_val, max_loc


should_screenshot = False


def scan_image(image, screen_frame, threshold, name):
    match_value, match_location = match_image(image, screen_frame)
    if match_value > threshold:
        print(f"{name} found at location: {match_location}")
        print(match_value)
        if should_screenshot: cv2.imwrite(f'screenshots/{name}-{current_milli_time()}.png', screen_frame)
        return True
    else:
        return False


racestart = cv2.imread(f'{monitor_str}/racestart.png', cv2.IMREAD_UNCHANGED)
lap2 = cv2.imread(f'{monitor_str}/lap2.png', cv2.IMREAD_UNCHANGED)
lap3 = cv2.imread(f'{monitor_str}/lap3.png', cv2.IMREAD_UNCHANGED)
place = cv2.imread(f'{monitor_str}/place.png', cv2.IMREAD_UNCHANGED)
game_mode = cv2.imread(f'{monitor_str}/gamemode.png', cv2.IMREAD_UNCHANGED)


def convert_to_minutes_seconds(big_time, small_time):
    total_seconds = (big_time - small_time) / 1000
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{int(minutes) if minutes.is_integer() else minutes}m:{round(seconds, 2)}s"


racetimer = -1
lap1_time = -1
lap2_time = -1
lap3_time = -1
last_sent_racetimer = -1
last_sent_lap1_time = -1
last_sent_lap2_time = -1
last_sent_lap3_time = -1
has_race_started = False
has_lap2_started = False
has_lap3_started = False
has_race_finish = False


# loop over

def reset_laps():
    global racetimer, lap1_time, lap2_time, lap3_time, has_lap2_started, has_lap3_started, has_race_finish
    global last_sent_racetimer, last_sent_lap1_time, last_sent_lap2_time, last_sent_lap3_time
    racetimer = -1
    lap1_time = -1
    lap2_time = -1
    lap3_time = -1
    last_sent_racetimer = -1
    last_sent_lap1_time = -1
    last_sent_lap2_time = -1
    last_sent_lap3_time = -1
    has_lap2_started = False
    has_lap3_started = False
    has_race_finish = False


while True:
    # print(current_milli_time())
    frame = stream.read()

    # check for frame if Nonetype
    if frame is None:
        break

    if scan_image(racestart, frame, 0.65, "racestart"):
        if not has_race_started:
            reset_laps()
            racetimer = current_milli_time()
            has_race_started = True
    elif scan_image(lap2, frame, 0.9, "lap2"):
        if not has_lap2_started:
            lap1_time = current_milli_time()
            has_lap2_started = True
    elif scan_image(lap3, frame, 0.9, "lap3"):
        if not has_lap3_started:
            lap2_time = current_milli_time()
            has_lap3_started = True
    elif scan_image(place, frame, 0.8, "place"):
        if not has_race_finish:
            lap3_time = current_milli_time()
            print(f"Race Time: {convert_to_minutes_seconds(lap3_time, racetimer)}")
            print(f"Lap 1 Time: {convert_to_minutes_seconds(lap1_time, racetimer)}")
            print(f"Lap 2 Time: {convert_to_minutes_seconds(lap2_time, lap1_time)}")
            print(f"Lap 3 Time: {convert_to_minutes_seconds(lap3_time, lap2_time)}")
            has_race_finish = True
            has_race_started = False
    if last_sent_racetimer != racetimer or last_sent_lap1_time != lap1_time or \
            last_sent_lap2_time != lap2_time or last_sent_lap3_time != lap3_time:
        send_webhook({"start": racetimer, "lap1": lap1_time, "lap2": lap2_time, "lap3": lap3_time})
        last_sent_racetimer = racetimer
        last_sent_lap1_time = lap1_time
        last_sent_lap2_time = lap2_time
        last_sent_lap3_time = lap3_time

    if scan_image(game_mode, frame, 0.9, "game_mode"):
        send_webhook({"start": -1, "lap1": -1, "lap2": -1, "lap3": -1})
        reset_laps()

    # Show output window
    # cv2.imshow("Output Frame", frame)

    # check for 'q' key if pressed
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

# close output window
cv2.destroyAllWindows()

# safely close video stream
stream.stop()
