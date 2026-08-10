"""
weather.py — Weather states affecting transport mode choice
Author: Suhas Akula | SRH Berlin 2026
"""
from dataclasses import dataclass
from config import WEATHER_STATES

@dataclass
class WeatherState:
    name:str; walk_modifier:float; bike_modifier:float

def sample_weather(rng):
    names=list(WEATHER_STATES.keys())
    weights=[WEATHER_STATES[n]["probability"] for n in names]
    chosen=rng.choices(names,weights=weights,k=1)[0]
    cfg=WEATHER_STATES[chosen]
    return WeatherState(chosen,cfg["walk_modifier"],cfg["bike_modifier"])

def apply_weather_to_mode_choice(mode,weather,rng):
    if mode=="walk":    return "walk" if rng.random()<=weather.walk_modifier else "subway"
    if mode=="bicycle": return "bicycle" if rng.random()<=weather.bike_modifier else "subway"
    return mode
