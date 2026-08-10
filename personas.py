"""
personas.py — Tourist personas from k-means clustering (Chapter 4)
Author: Suhas Akula | SRH Berlin 2026
Reference: Dolnicar (2002)
"""
from dataclasses import dataclass
from typing import List
from config import PERSONAS

@dataclass
class PersonaProfile:
    name:str; label:str; preferred_mode:str; fallback_modes:List[str]
    flexibility:float; time_budget:float; dwell_min:int; dwell_max:int
    peak_hours:List[int]; max_visits:int

def sample_persona(persona_name,rng):
    cfg=PERSONAS[persona_name]
    flex=max(0.05,min(0.95,cfg["flexibility"]+rng.uniform(-0.10,0.10)))
    return PersonaProfile(
        name=persona_name,label=cfg["label"],
        preferred_mode=cfg["preferred_mode"],fallback_modes=cfg["fallback_modes"],
        flexibility=round(flex,3),time_budget=cfg["time_budget_min"],
        dwell_min=cfg["dwell_min"],dwell_max=cfg["dwell_max"],
        peak_hours=cfg["peak_hours"],max_visits=cfg["max_visits"],
    )

def assign_personas(n_agents,rng):
    profiles=[]
    for pname,cfg in PERSONAS.items():
        count=max(1,round(n_agents*cfg["proportion"]))
        for _ in range(count): profiles.append(sample_persona(pname,rng))
    while len(profiles)<n_agents: profiles.append(sample_persona("ShortWalker",rng))
    profiles=profiles[:n_agents]; rng.shuffle(profiles)
    return profiles
