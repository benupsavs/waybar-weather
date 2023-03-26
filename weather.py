#!/usr/bin/env python

# credits to: https://gist.github.com/bjesus/f8db49e1434433f78e5200dc403d58a3
# credits to: https://github.com/khaneliman/dotfiles/blob/7d00ee4f66cdfcfce6fc3d11f0a7c6b3f00cc57f/dots/linux/hyprland/home/.config/waybar/scripts/weather.py
# credits to: https://github.com/chubin/wttr.in

import argparse
import json
import os
from datetime import datetime
from operator import itemgetter
from typing import Dict, NamedTuple

import platformdirs
import requests

class Config(NamedTuple):
    """Contains configuration for the forecast display."""
    temp_unit: str
    hourly_temp_unit: str
    feels_like_unit: str
    max_temp_unit: str
    min_temp_unit: str
    temp_indicator: str
    windspeed_unit: str
    windspeed_indicator: str
    lang: str = "en"

LOCALIZATION = {
    "en": {
        "feels_like": "Feels like",
        "wind": "Wind",
        "humidity": "Humidity",
        "today": "Today",
        "tomorrow": "Tomorrow",
        "weatherDesc": "weatherDesc",
        "chanceoffog": "Fog",
        "chanceoffrost": "Frost",
        "chanceofovercast": "Overcast",
        "chanceofrain": "Rain",
        "chanceofsnow": "Snow",
        "chanceofsunshine": "Sunshine",
        "chanceofthunder": "Thunder",
        "chanceofwindy": "Wind",
    }
}

WEATHER_CODES = {
    "113": "☀️",
    "116": "⛅️",
    "119": "☁️",
    "122": "☁️",
    "143": "🌫",
    "176": "🌦",
    "179": "🌧",
    "182": "🌧",
    "185": "🌧",
    "200": "⛈",
    "227": "🌨",
    "230": "❄️",
    "248": "🌫",
    "260": "🌫",
    "263": "🌦",
    "266": "🌦",
    "281": "🌧",
    "284": "🌧",
    "293": "🌦",
    "296": "🌦",
    "299": "🌧",
    "302": "🌧",
    "305": "🌧",
    "308": "🌧",
    "311": "🌧",
    "314": "🌧",
    "317": "🌧",
    "320": "🌨",
    "323": "🌨",
    "326": "🌨",
    "329": "❄️",
    "332": "❄️",
    "335": "❄️",
    "338": "❄️",
    "350": "🌧",
    "353": "🌦",
    "356": "🌧",
    "359": "🌧",
    "362": "🌧",
    "365": "🌧",
    "368": "🌨",
    "371": "❄️",
    "374": "🌧",
    "377": "🌧",
    "386": "⛈",
    "389": "🌩",
    "392": "⛈",
    "395": "❄️",
}

chances = [
    "chanceoffog",
    "chanceoffrost",
    "chanceofovercast",
    "chanceofrain",
    "chanceofsnow",
    "chanceofsunshine",
    "chanceofthunder",
    "chanceofwindy",
]

data = {}

def format_time(time: str):
    """Format the given time string."""
    return time.replace("00", "").zfill(2)

def format_temp(hour, cfg: Config):
    """Format temperature for the given hour."""
    return (hour[cfg.hourly_temp_unit] + "°").ljust(3)

def format_chances(hour, text: Dict[str, str]) -> str:
    """Format changes for the given hour."""
    probs = {
        text[e]: int(prob) for e, prob in hour.items() if e in chances and int(prob) > 0
    }
    key = itemgetter(0)
    val = itemgetter(1)
    sorted_probs = {e: probs[key(e)] for e in sorted(probs.items(), key=val, reverse=True)}
    conditions = [f"{event} {prob}%" for event, prob in sorted_probs.items()]
    return ", ".join(conditions)

def get_output(json_input: str, cfg: Config) -> str:
    """Get the json output."""
    text = LOCALIZATION[cfg.lang]
    weather = json.loads(json_input)
    data["text"] = WEATHER_CODES[weather["current_condition"][0]["weatherCode"]] + " "
    data["text"] += weather["current_condition"][0][cfg.temp_unit] + cfg.temp_indicator

    weather_desc = text["weatherDesc"]
    data[
        "tooltip"
    ] = f"<b>{weather['current_condition'][0][weather_desc][0]['value']} {weather['current_condition'][0][cfg.temp_unit]}°</b>\n"
    data[
        "tooltip"
    ] += f"{text['feels_like']}: {weather['current_condition'][0][cfg.feels_like_unit]}°\n"
    data[
        "tooltip"
    ] += f"{text['wind']}: {weather['current_condition'][0]['windspeed' + cfg.windspeed_unit]}{cfg.windspeed_indicator}\n"
    data[
        "tooltip"
    ] += f"{text['humidity']}: {weather['current_condition'][0]['humidity']}%\n"
    for i, day in enumerate(weather["weather"]):
        data["tooltip"] += "\n<b>"
        if i == 0:
            data["tooltip"] += f"{text['today']}, "
        if i == 1:
            data["tooltip"] += f"{text['tomorrow']}, "
        if i == 2 and "day_after_tomorrow" in text:
            data["tooltip"] += f"{text['day_after_tomorrow']}, "
        data["tooltip"] += f"{day['date']}</b>\n"
        data["tooltip"] += f"⬆️ {day[cfg.max_temp_unit]}° ⬇️ {day[cfg.min_temp_unit]}° "
        data[
            "tooltip"
        ] += f"🌅 {day['astronomy'][0]['sunrise']} 🌇 {day['astronomy'][0]['sunset']}\n"
        for hour in day["hourly"]:
            if i == 0:
                if int(format_time(hour["time"])) < datetime.now().hour - 2:
                    continue
            data[
                "tooltip"
            ] += f"{format_time(hour['time'])} {WEATHER_CODES[hour['weatherCode']]} {format_temp(hour, cfg)} {hour[weather_desc][0]['value']}, {format_chances(hour, text)}\n"


    return json.dumps(data)

def main():
    """"The main function."""
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-l", "--location", help="Your wttr location", type=str)
    arg_parser.add_argument("-u", "--unit", help="Your unit of temperature measurement (C or F)", type=str)
    arg_parser.add_argument("-w", "--windspeed-unit", help="Your unit of wind speed measurement (K or M)", type=str)
    args = arg_parser.parse_args()

    if args.windspeed_unit == "K":
        windspeed_unit = "Kmph"
        windspeed_indicator = "Km/h"
    else:
        windspeed_unit = "Miles"
        windspeed_indicator = "Mi/h"

    if args.unit == "C":
        config = Config(
            temp_unit = "temp_C",
            hourly_temp_unit = "tempC",
            feels_like_unit = "FeelsLikeC",
            max_temp_unit = "maxtempC",
            min_temp_unit = "mintempC",
            temp_indicator = "°C",
            windspeed_unit=windspeed_unit,
            windspeed_indicator=windspeed_indicator,
        )
    else:
        config = Config(
            temp_unit = "temp_F",
            hourly_temp_unit = "tempF",
            feels_like_unit = "FeelsLikeF",
            max_temp_unit = "maxtempF",
            min_temp_unit = "mintempF",
            temp_indicator = "°F",
            windspeed_unit=windspeed_unit,
            windspeed_indicator=windspeed_indicator,
        )

    cache_dir = ""
    cache_filename = ""
    output = ""
    try:
        cache_dir = platformdirs.user_cache_dir("waybar-weather")
        os.makedirs(cache_dir, exist_ok=True)
        cache_filename = os.path.join(cache_dir, "cache.json")
        with open(cache_filename, "r", encoding="utf8") as f:
            weather_json = f.read()
        output = get_output(weather_json, config)
    except:
        pass

    try:
        weather_json = requests.get(
            f"https://{config.lang}.wttr.in/{args.location}?format=j1", timeout=10,
        ).text

        output = get_output(weather_json, config)

        try:
            if cache_dir and cache_filename:
                with open(cache_filename, "w", encoding="utf8") as f:
                    f.write(weather_json)
        except:
            pass
    except:
        pass

    if output:
        print(output)

if __name__ == "__main__":
    main()
