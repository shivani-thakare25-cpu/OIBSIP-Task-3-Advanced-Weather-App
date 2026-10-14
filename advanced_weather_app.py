
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timezone, timedelta
from io import BytesIO
import threading
import requests
from PIL import Image, ImageTk

import tkinter as tk
from tkinter import ttk
from datetime import datetime, timezone, timedelta
from io import BytesIO
import threading
import requests
from PIL import Image, ImageTk

API_KEY = "4cae878632e90651aa883e72b7763a56"

BG = "#071629"
CARD = "#102541"
INNER = "#142E4D"
BLUE = "#168BFF"
WHITE = "#F4F8FF"
MUTED = "#9BB8DE"
GREEN = "#35D6A0"
RED = "#FF7777"

unit = "C"
last_city = "Nagpur"
photos = []
icon_cache = {}
request_id = 0

root = tk.Tk()
root.title("Advanced Weather App")
root.geometry("1200x850")
root.minsize(900, 700)
root.configure(bg=BG)

container = tk.Frame(root, bg=BG)
container.pack(fill="both", expand=True)

canvas = tk.Canvas(container, bg=BG, highlightthickness=0)
scrollbar = ttk.Scrollbar(
    container, orient="vertical", command=canvas.yview
)
canvas.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)

dashboard = tk.Frame(canvas, bg=BG)
window_id = canvas.create_window(
    (0, 0), window=dashboard, anchor="nw"
)

dashboard.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)
canvas.bind(
    "<Configure>",
    lambda e: canvas.itemconfigure(window_id, width=e.width)
)

def label(parent, text, size=11, color=WHITE, bold=False, bg=CARD):
    return tk.Label(
        parent, text=text,
        font=("Segoe UI", size, "bold" if bold else "normal"),
        bg=bg, fg=color
    )

def card(parent, title):
    frame = tk.Frame(parent, bg=CARD, padx=16, pady=14)
    label(frame, title, 13, WHITE, True).pack(anchor="w", pady=(0, 12))
    return frame

def clear(frame):
    for child in frame.winfo_children():
        child.destroy()

def status(message, color=MUTED):
    status_label.config(text=message, fg=color)

def temperature(c):
    return f"{c:.0f}°{'F' if unit == 'F' else 'C'}" if unit == "C" \
        else f"{c * 9 / 5 + 32:.0f}°F"

def wind_speed(ms):
    return f"{ms:.1f} m/s" if unit == "C" else f"{ms * 2.23694:.1f} mph"

def get_icon(code, size=(64, 64)):
    key = (code, size)
    if key not in icon_cache:
        url = f"https://openweathermap.org/img/wn/{code}@2x.png"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        im = Image.open(BytesIO(response.content)).convert("RGBA")
        im = im.resize(size, Image.Resampling.LANCZOS)
        icon_cache[key] = ImageTk.PhotoImage(im)
    return icon_cache[key]

def icon_code(code, is_day=True):
    if code == 0:
        return "01d" if is_day else "01n"
    if code in (1, 2):
        return "02d" if is_day else "02n"
    if code == 3:
        return "03d" if is_day else "03n"
    if code in (45, 48):
        return "50d" if is_day else "50n"
    if code in (51, 53, 55, 56, 57):
        return "09d"
    if code in (61, 63, 65, 66, 67, 80, 81, 82):
        return "10d"
    if code in (71, 73, 75, 77, 85, 86):
        return "13d"
    if code in (95, 96, 99):
        return "11d"
    return "01d"

def condition(code):
    conditions = {
        0: "Clear Sky", 1: "Mainly Clear",
        2: "Partly Cloudy", 3: "Overcast",
        45: "Fog", 48: "Rime Fog",
        51: "Light Drizzle", 53: "Drizzle",
        55: "Heavy Drizzle", 61: "Light Rain",
        63: "Rain", 65: "Heavy Rain",
        71: "Light Snow", 73: "Snow",
        75: "Heavy Snow", 80: "Rain Showers",
        81: "Rain Showers", 82: "Heavy Showers",
        95: "Thunderstorm", 96: "Thunderstorm",
        99: "Thunderstorm"
    }
    return conditions.get(code, "Cloudy")

header = tk.Frame(dashboard, bg=BG)
header.pack(fill="x", padx=22, pady=18)

label(header, "⛅ ADVANCED WEATHER APP", 23, BLUE, True, BG).pack(side="left")

unit_button = tk.Button(
    header, text="°C  |  °F", command=lambda: toggle_unit(),
    bg=INNER, fg=WHITE, activebackground=BLUE,
    relief="flat", font=("Segoe UI", 11, "bold"), padx=15, pady=9
)
unit_button.pack(side="right")

search = tk.Frame(dashboard, bg=CARD, padx=14, pady=14)
search.pack(fill="x", padx=22, pady=4)

city_entry = tk.Entry(
    search, font=("Segoe UI", 13), bg=INNER,
    fg=WHITE, insertbackground=WHITE, relief="flat"
)
city_entry.insert(0, "Nagpur")
city_entry.pack(side="left", fill="x", expand=True, ipady=10, padx=(0, 10))

search_button = tk.Button(
    search, text="Get Weather", command=lambda: load_weather(),
    bg=BLUE, fg="white", activebackground=GREEN,
    relief="flat", font=("Segoe UI", 11, "bold"), padx=18, pady=8
)
search_button.pack(side="left", padx=4)

location_button = tk.Button(
    search, text="My Location", command=lambda: detect_location(),
    bg=INNER, fg=WHITE, activebackground=BLUE,
    relief="flat", font=("Segoe UI", 10), padx=12, pady=8
)
location_button.pack(side="left", padx=4)

status_label = label(
    dashboard, "Enter a city and click Get Weather.", 10, MUTED, bg=BG
)
status_label.pack(anchor="w", padx=25, pady=8)

current_card = card(dashboard, "CURRENT WEATHER")
current_card.pack(fill="x", padx=22, pady=8)

current_body = tk.Frame(current_card, bg=CARD)
current_body.pack(fill="x")

current_left = tk.Frame(current_body, bg=CARD)
current_left.pack(side="left", fill="both", expand=True)

city_label = label(current_left, "Your City", 23, WHITE, True)
city_label.pack(anchor="w")

date_label = label(current_left, "--", 10, MUTED)
date_label.pack(anchor="w", pady=5)

temp_label = label(current_left, "--°", 42, WHITE, True)
temp_label.pack(anchor="w", pady=4)

condition_label = label(current_left, "Weather Condition", 14, BLUE, True)
condition_label.pack(anchor="w")

feels_label = label(current_left, "Feels like: --", 11, MUTED)
feels_label.pack(anchor="w", pady=6)

current_icon_label = tk.Label(current_body, bg=CARD)
current_icon_label.pack(side="right", padx=25)

metrics = tk.Frame(current_card, bg=CARD)
metrics.pack(fill="x", pady=(18, 0))

metric_labels = {}
for i, title in enumerate(
    ["Humidity", "Wind Speed", "Pressure", "Visibility"]
):
    box = tk.Frame(metrics, bg=INNER, padx=12, pady=12)
    box.grid(row=0, column=i, sticky="nsew", padx=4)
    metrics.columnconfigure(i, weight=1)
    label(box, title, 10, MUTED, bg=INNER).pack(anchor="w")
    val = label(box, "--", 15, WHITE, True, INNER)
    val.pack(anchor="w", pady=(7, 0))
    metric_labels[title] = val

hour_card = card(dashboard, "HOURLY FORECAST — NEXT 6 HOURS")
hour_card.pack(fill="x", padx=22, pady=8)

hour_frame = tk.Frame(hour_card, bg=CARD)
hour_frame.pack(fill="x")

day_card = card(dashboard, "5-DAY FORECAST")
day_card.pack(fill="x", padx=22, pady=8)

day_frame = tk.Frame(day_card, bg=CARD)
day_frame.pack(fill="x")

def get_json(url, params=None):
    response = requests.get(url, params=params, timeout=15)
    if response.status_code == 401:
        raise ValueError("Invalid API key. Check your OpenWeatherMap key.")
    if response.status_code == 404:
        raise ValueError("City not found. Please enter a valid city.")
    if response.status_code == 429:
        raise ValueError("API limit reached. Please try again later.")
    response.raise_for_status()
    return response.json()

def fetch_data(city):
    if not API_KEY or API_KEY == "YOUR_OPENWEATHERMAP_API_KEY":
        raise ValueError("Add your OpenWeatherMap API key in the code.")

    current = get_json(
        "https://api.openweathermap.org/data/2.5/weather",
        {"q": city, "appid": API_KEY, "units": "metric"}
    )

    lat = current["coord"]["lat"]
    lon = current["coord"]["lon"]

    forecast = get_json(
        "https://api.open-meteo.com/v1/forecast",
        {
            "latitude": lat,
            "longitude": lon,
            "current": (
                "temperature_2m,relative_humidity_2m,"
                "apparent_temperature,is_day,weather_code,"
                "wind_speed_10m,surface_pressure"
            ),
            "hourly": "temperature_2m,weather_code",
            "daily": (
                "weather_code,temperature_2m_max,"
                "temperature_2m_min"
            ),
            "forecast_days": 6,
            "timezone": "auto"
        }
    )
    return current, forecast

def render_hourly(data):
    clear(hour_frame)
    hourly = data["hourly"]
    times = hourly["time"]
    now = data["current"]["time"]

    start = 0
    for i, time in enumerate(times):
        if time >= now:
            start = i
            break

    indexes = list(range(start, min(start + 6, len(times))))
    for col, i in enumerate(indexes):
        box = tk.Frame(hour_frame, bg=INNER, padx=5, pady=10)
        box.grid(row=0, column=col, sticky="nsew", padx=3)
        hour_frame.columnconfigure(col, weight=1)

        time_text = datetime.fromisoformat(times[i]).strftime("%I %p").lstrip("0")
        code = hourly["weather_code"][i]
        temp = hourly["temperature_2m"][i]

        label(box, time_text, 10, MUTED, bg=INNER).pack()
        try:
            photo = get_icon(icon_code(code), (48, 48))
            photos.append(photo)
            tk.Label(box, image=photo, bg=INNER).pack(pady=5)
        except (requests.RequestException, OSError, ValueError):
            label(box, "☁", 20, BLUE, bg=INNER).pack(pady=5)

        label(box, temperature(temp), 13, WHITE, True, INNER).pack()
        label(box, condition(code), 8, MUTED, bg=INNER).pack(pady=(5, 0))

def render_daily(data):
    clear(day_frame)
    daily = data["daily"]

    for i in range(min(5, len(daily["time"]))):
        row = tk.Frame(day_frame, bg=INNER, padx=12, pady=8)
        row.pack(fill="x", pady=3)

        day = datetime.fromisoformat(daily["time"][i]).strftime("%a, %d %b")
        code = daily["weather_code"][i]
        high = daily["temperature_2m_max"][i]
        low = daily["temperature_2m_min"][i]

        label(row, day, 11, WHITE, True, INNER).pack(side="left")

        try:
            photo = get_icon(icon_code(code), (44, 44))
            photos.append(photo)
            tk.Label(row, image=photo, bg=INNER).pack(side="left", padx=15)
        except (requests.RequestException, OSError, ValueError):
            label(row, "☁", 20, BLUE, bg=INNER).pack(side="left", padx=15)

        label(row, condition(code), 10, MUTED, bg=INNER).pack(side="left")
        label(
            row, f"{temperature(high)} / {temperature(low)}",
            11, WHITE, True, INNER
        ).pack(side="right")

def render_current(current, forecast):
    global photos
    photos = []

    data = forecast["current"]
    city = current.get("name", "Unknown")
    country = current.get("sys", {}).get("country", "")

    city_label.config(text=f"{city}, {country}")
    date_label.config(
        text=datetime.fromisoformat(data["time"]).strftime("%A, %d %B %Y  |  %I:%M %p")
    )

    temp_label.config(text=temperature(data["temperature_2m"]))
    feels_label.config(text=f"Feels like: {temperature(data['apparent_temperature'])}")
    condition_label.config(text=condition(data["weather_code"]))

    metric_labels["Humidity"].config(
        text=f"{data['relative_humidity_2m']}%"
    )
    metric_labels["Wind Speed"].config(
        text=wind_speed(data["wind_speed_10m"] / 3.6)
    )
    metric_labels["Pressure"].config(
        text=f"{data['surface_pressure']:.0f} hPa"
    )

    visibility = current.get("visibility")
    metric_labels["Visibility"].config(
        text=f"{visibility / 1000:.1f} km" if visibility is not None else "N/A"
    )

    try:
        photo = get_icon(
            current["weather"][0]["icon"], (125, 125)
        )
        photos.append(photo)
        current_icon_label.config(image=photo, text="")
    except (requests.RequestException, OSError, ValueError):
        current_icon_label.config(image="", text="☁", fg=BLUE,
                                  font=("Segoe UI", 55))

    render_hourly(forecast)
    render_daily(forecast)

def show_error(message, number):
    if number == request_id:
        status(message, RED)
        search_button.config(state="normal")


def load_weather(city=None):
    global request_id, last_city
    city = (city or city_entry.get()).strip()

    if not city:
        status("Please enter a city name.", RED)
        return

    last_city = city
    request_id += 1
    number = request_id
    selected_unit = unit

    status("Loading weather dashboard...", BLUE)
    search_button.config(state="disabled")

    def worker():
        try:
            current, forecast = fetch_data(city)

            def update():
                if number != request_id or selected_unit != unit:
                    return
                render_current(current, forecast)
                status(f"Weather dashboard updated: {city}", GREEN)
                search_button.config(state="normal")

            root.after(0, update)

        except requests.RequestException:
            root.after(
                0, lambda: show_error(
                    "Network error. Check your internet connection.", number
                )
            )
        except (ValueError, KeyError, TypeError) as exc:
            root.after(0, lambda: show_error(str(exc), number))
        except Exception:
            root.after(
                0, lambda: show_error(
                    "Unable to load weather data. Try again.", number
                )
            )

    threading.Thread(target=worker, daemon=True).start()

def toggle_unit():
    global unit
    unit = "F" if unit == "C" else "C"
    unit_button.config(text="°F  |  °C" if unit == "F" else "°C  |  °F")
    load_weather(last_city)

def detect_location():
    status("Detecting approximate location using IP...", BLUE)
    location_button.config(state="disabled")

    def worker():
        try:
            info = get_json("https://ipinfo.io/json")
            city = info.get("city")
            if not city:
                raise ValueError("Location not found. Enter your city manually.")

            def update():
                city_entry.delete(0, tk.END)
                city_entry.insert(0, city)
                location_button.config(state="normal")
                load_weather(city)

            root.after(0, update)

        except (requests.RequestException, ValueError) as exc:
            root.after(0, lambda: status(str(exc), RED))
            root.after(0, lambda: location_button.config(state="normal"))

    threading.Thread(target=worker, daemon=True).start()

city_entry.bind("<Return>", lambda event: load_weather())
footer = label(
    dashboard,
    "Weather data: OpenWeatherMap + Open-Meteo | IP location: ipinfo.io",
    9, MUTED, bg=BG
)
footer.pack(pady=18)
root.after(500, load_weather)
root.mainloop()

