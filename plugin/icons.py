account = 'F0004'
alert = 'F0026'
calendar = 'F00ED'
calendar_clock = 'F00F0'
cctv = 'F07AE'
checkbox_blank_circle_outline = 'F0130'
checkbox_blank_circle_outline = 'F0130'
checkbox_marked = 'F0132'
checkbox_marked_circle = 'F0133'
checkbox_multiple_blank = 'F0136'
checkbox_multiple_blank_outline = 'F0137'
checkbox_multiple_marked = 'F0138'
clock = 'F0954'
counter = 'F0199'
crosshairs_gps = 'F01A4'
fan = 'F0210'
file_code = 'F022E'
form_select = 'F1401'
form_textbox = 'F060E'
gauge = 'F029A'
home_assistant = 'F07D0'
lightbulb = 'F0335'
lock = 'F033E'
lock_open = 'F033F'
map_marker_radius = 'F0352'
message = 'F0361'
music_note = 'F0387'
music_note_off = 'F038A'
order_bool_ascending_variant = 'F098F'
playlist_check = 'F05C7'
playlist_remove = 'F0413'
remote = 'F0454'
remote_off = 'F0EC4'
thermostat = 'F0393'
toggle_switch = 'F0521'
toggle_switch_off = 'F0522'
view_dashboard_outline = 'F0A1D'
weather_fog = 'F0591'
weather_night = 'F0594'
weather_partly_cloudy = 'F0595'
weather_sunny = 'F0599'
window_shutter = 'F111C'
window_shutter_open = 'F111E'
information = 'F02FC'
palette = 'F03D8'
star_circle_outline = 'F09A4'
image_broken = 'F02ED'
swap_horizontal_bold = 'F0BCD'


DEFAULT_ICONS = {
    "person": account,
    "lock": lock,
    "lock_open": lock_open,
    "light": lightbulb,
    "switch": toggle_switch,
    "switch_off": toggle_switch_off,
    "binary_sensor": checkbox_marked_circle,
    "binary_sensor_off": checkbox_blank_circle_outline,
    "sensor": gauge,
    "climate": thermostat,
    "cover": window_shutter,
    "cover_open": window_shutter_open,
    "scene": view_dashboard_outline,
    "group": checkbox_multiple_blank,
    "group_on": checkbox_multiple_marked,
    "group_off": checkbox_multiple_blank_outline,
    "input_boolean": checkbox_blank_circle_outline,
    "input_boolean_on": checkbox_marked,
    "input_select": form_select,
    "input_number": counter,
    "input_text": form_textbox,
    "input_datetime": calendar_clock,
    "timer": clock,
    "calendar": calendar,
    "select": order_bool_ascending_variant,
    "sun": weather_sunny,
    "moon": weather_night,
    "weather": weather_partly_cloudy,
    "homeassistant": home_assistant,
    "zone": map_marker_radius,
    "script": file_code,
    "fan": fan,
    "camera": cctv,
    "automation": playlist_check,
    "automation_off": playlist_remove,
    "media_player": music_note,
    "media_player_off": music_note_off,
    "remote": remote,
    "remote_off": remote_off,
    "device_tracker": crosshairs_gps,
    "persistent_notification": message,
    "air_quality": weather_fog,
    "unavailable": alert,
    "information": information,
    "palette": palette,
    "star-circle-outline": star_circle_outline,
    "image_broken": image_broken,
    "swap_horizontal_bold": swap_horizontal_bold,
}