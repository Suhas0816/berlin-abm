"""
config.py — Berlin Tourist Mobility ABM
90+ locations covering ALL Berlin districts deeply
North, South, East, West, Centre — museums, parks, lakes, markets,
nightlife, galleries, universities, stadiums, churches, memorials
Author: Suhas Akula | SRH Berlin 2026 | Supervisor: Prof. Dr. Frank Wolter
"""
import os

N_AGENTS        = 500
SIM_START_HOUR  = 7.0
SIM_END_HOUR    = 22.0
STEP_MINUTES    = 5
N_STEPS         = int((SIM_END_HOUR - SIM_START_HOUR) * 60 / STEP_MINUTES)
RANDOM_SEED     = 42
CROWD_THRESHOLD = 0.25

HOURLY_ACTIVITY_PROFILE = {
    7:0.30, 8:0.45, 9:0.65, 10:0.85,
    11:1.00, 12:1.00, 13:1.00, 14:0.95,
    15:0.95, 16:0.80, 17:0.65, 18:0.55,
    19:0.45, 20:0.35, 21:0.20,
}

DAY_PHASES = {
    "Morning Rush": (7.0,  9.5),
    "Midday Peak":  (9.5,  15.0),
    "Afternoon":    (15.0, 18.0),
    "Evening":      (18.0, 22.0),
}

WEATHER_STATES = {
    "Clear":      {"probability":0.50,"walk_modifier":1.00,"bike_modifier":1.00},
    "Overcast":   {"probability":0.25,"walk_modifier":0.95,"bike_modifier":0.90},
    "Light Rain": {"probability":0.18,"walk_modifier":0.70,"bike_modifier":0.50},
    "Heavy Rain": {"probability":0.07,"walk_modifier":0.40,"bike_modifier":0.20},
}

# ── 90+ BERLIN LOCATIONS — ALL DISTRICTS ─────────────────────────────────────
ATTRACTIONS = {

    # ══ CENTRE / MITTE ════════════════════════════════════════════════════════
    "Brandenburg Gate":          (52.5163, 13.3777, 55),
    "Museum Island":             (52.5169, 13.3977, 45),
    "Reichstag":                 (52.5186, 13.3762, 40),
    "Holocaust Memorial":        (52.5138, 13.3786, 42),
    "Checkpoint Charlie":        (52.5076, 13.3904, 30),
    "Gendarmenmarkt":            (52.5138, 13.3925, 32),
    "Hackescher Markt":          (52.5230, 13.4023, 35),
    "Berlin Cathedral":          (52.5192, 13.4011, 38),
    "Humboldt Forum":            (52.5172, 13.4020, 40),
    "Unter den Linden":          (52.5170, 13.3888, 50),
    "Neue Wache Memorial":       (52.5177, 13.3939, 25),
    "Berlin State Opera":        (52.5166, 13.3951, 30),
    "Topography of Terror":      (52.5058, 13.3823, 35),
    "Jewish Museum Berlin":      (52.5026, 13.3944, 30),
    "Berliner Dom Museum":       (52.5196, 13.4014, 28),

    # ══ ALEXANDERPLATZ / TV TOWER AREA ═══════════════════════════════════════
    "Alexanderplatz":            (52.5219, 13.4132, 65),
    "TV Tower":                  (52.5208, 13.4094, 48),
    "Neptunbrunnen Fountain":    (52.5202, 13.4073, 30),
    "Rotes Rathaus":             (52.5198, 13.4093, 25),
    "Nikolaiviertel":            (52.5162, 13.4083, 35),

    # ══ POTSDAMER PLATZ / KULTURFORUM ════════════════════════════════════════
    "Potsdamer Platz":           (52.5096, 13.3762, 45),
    "Philharmonie Berlin":       (52.5097, 13.3697, 28),
    "Gemaldegalerie Museum":     (52.5084, 13.3680, 25),
    "Martin Gropius Bau":        (52.5060, 13.3814, 22),
    "Sony Center":               (52.5103, 13.3742, 40),

    # ══ WEST — CHARLOTTENBURG ════════════════════════════════════════════════
    "Charlottenburg Palace":     (52.5208, 13.2956, 30),
    "Victory Column":            (52.5145, 13.3501, 38),
    "Berlin Zoo":                (52.5080, 13.3371, 60),
    "Aquarium Berlin":           (52.5073, 13.3381, 35),
    "KaDeWe Department Store":   (52.5022, 13.3414, 40),
    "Kurfuerstendamm":           (52.5027, 13.3280, 55),
    "Savignyplatz":              (52.5066, 13.3225, 30),
    "Lietzenseepark":            (52.5063, 13.2910, 35),
    "Kaiser Wilhelm Church":     (52.5047, 13.3350, 45),
    "C A Berlinische Galerie W": (52.5005, 13.3310, 20),

    # ══ WEST — SPANDAU ═══════════════════════════════════════════════════════
    "Spandau Citadel":           (52.5353, 13.2078, 25),
    "Spandau Old Town":          (52.5369, 13.2002, 30),
    "Spandau Station":           (52.5343, 13.1973, 45),
    "Havel River Spandau":       (52.5289, 13.1950, 30),

    # ══ NORTH — WEDDING ══════════════════════════════════════════════════════
    "Tegel Lake":                (52.5892, 13.2456, 40),
    "Tegel Airport Park":        (52.5597, 13.2910, 35),
    "Ploetzensee Memorial":      (52.5424, 13.3219, 20),
    "Wedding Rathaus":           (52.5485, 13.3673, 25),
    "Volkspark Rehberge":        (52.5548, 13.3318, 35),
    "Schillerpark Wedding":      (52.5521, 13.3502, 30),

    # ══ NORTH — PANKOW / PRENZLAUER BERG ════════════════════════════════════
    "Prenzlauer Berg Park":      (52.5389, 13.4147, 40),
    "Mauerpark":                 (52.5416, 13.4019, 55),
    "Schoenhauser Allee":        (52.5477, 13.4141, 35),
    "Pankow Palace Park":        (52.5694, 13.4014, 30),
    "Weissensee Lake":           (52.5617, 13.4649, 40),
    "Kollwitzplatz":             (52.5366, 13.4205, 35),
    "Kulturbrauerei":            (52.5400, 13.4196, 30),
    "Zeiss Grossplanetarium":    (52.5441, 13.4653, 25),

    # ══ CENTRE — FRIEDRICHSHAIN ══════════════════════════════════════════════
    "East Side Gallery":         (52.5050, 13.4396, 35),
    "Volkspark Friedrichshain":  (52.5267, 13.4317, 60),
    "Boxhagener Platz":          (52.5130, 13.4558, 35),
    "RAW Gelaende":              (52.5097, 13.4551, 30),
    "Oberbaumbridge":            (52.5018, 13.4459, 30),
    "Computerspiele Museum":     (52.5138, 13.4499, 20),
    "Stralauer Allee":           (52.5002, 13.4504, 25),

    # ══ CENTRE — KREUZBERG ═══════════════════════════════════════════════════
    "Goerlitzer Park":           (52.4944, 13.4417, 50),
    "Kottbusser Tor":            (52.4993, 13.4185, 40),
    "Markthalle Neun":           (52.4996, 13.4337, 35),
    "Viktoriapark Kreuzberg":    (52.4877, 13.3811, 40),
    "Curry 36 Mehringdamm":      (52.4933, 13.3876, 25),
    "Bergmannstrasse Market":    (52.4916, 13.3926, 30),
    "Tempodrom Berlin":          (52.5021, 13.3818, 25),
    "Berlinische Galerie":       (52.5025, 13.3925, 22),

    # ══ SOUTH — SCHOENEBERG ══════════════════════════════════════════════════
    "Tempelhof Field":           (52.4733, 13.4037, 80),
    "Schoeneberg Town Hall":     (52.4979, 13.3432, 25),
    "Bayerischer Platz":         (52.4902, 13.3390, 30),
    "Rathaus Schoeneberg":       (52.4853, 13.3434, 22),
    "Rudolph Wilde Park":        (52.4836, 13.3313, 35),

    # ══ SOUTH — STEGLITZ / ZEHLENDORF ════════════════════════════════════════
    "Botanical Garden Berlin":   (52.4469, 13.3065, 45),
    "Wannsee Lake":              (52.4331, 13.1800, 60),
    "Pfaueninsel Island":        (52.4331, 13.1292, 20),
    "Grunewald Forest":          (52.4884, 13.2294, 50),
    "Brucke Museum":             (52.4611, 13.2512, 18),
    "Steglitz Town Hall":        (52.4586, 13.3228, 20),
    "Schlosspark Steglitz":      (52.4558, 13.3217, 30),

    # ══ SOUTH — NEUKOELLN ════════════════════════════════════════════════════
    "Tempelhof Park South":      (52.4668, 13.4194, 45),
    "Hermannplatz":              (52.4871, 13.4254, 40),
    "Britzer Garten":            (52.4452, 13.4217, 40),
    "Neukoelln Arcaden":         (52.4797, 13.4358, 35),
    "Rixdorf Village":           (52.4763, 13.4411, 20),

    # ══ EAST — LICHTENBERG / MARZAHN ═════════════════════════════════════════
    "Marzahn Gardens of World":  (52.5480, 13.5700, 40),
    "Tierpark Berlin":           (52.5031, 13.5238, 55),
    "Stasi Museum":              (52.5211, 13.5046, 25),
    "Treptower Park":            (52.4877, 13.4683, 45),
    "Molecule Man Sculpture":    (52.5014, 13.4474, 20),
    "Arena Berlin":              (52.4993, 13.4531, 30),

    # ══ EAST — KOEPENICK ═════════════════════════════════════════════════════
    "Koepenick Palace":          (52.4577, 13.5794, 25),
    "Mueggelsee Lake":           (52.4394, 13.6500, 50),
    "Koepenick Old Town":        (52.4559, 13.5797, 28),
    "Grosser Mueggelsee Trail":  (52.4279, 13.6376, 35),

    # ══ HOTELS ═══════════════════════════════════════════════════════════════
    "Hotel Adlon Kempinski":     (52.5163, 13.3806, 25),
    "Radisson Blu Berlin":       (52.5192, 13.4025, 20),
    "Park Inn Alexanderplatz":   (52.5220, 13.4110, 30),
    "Hilton Berlin Mitte":       (52.5138, 13.3906, 22),
    "25hours Hotel Bikini":      (52.5061, 13.3322, 18),
    "Estrel Hotel Neukoelln":    (52.4748, 13.4327, 25),
    "nhow Berlin Friedrichshain":(52.5016, 13.4467, 20),

    # ══ TRANSPORT HUBS ═══════════════════════════════════════════════════════
    "Berlin Hauptbahnhof":       (52.5251, 13.3694, 80),
    "Zoologischer Garten Stn":   (52.5069, 13.3325, 70),
    "Ostbahnhof":                (52.5106, 13.4346, 55),
    "Friedrichstrasse Stn":      (52.5200, 13.3879, 65),
    "Suedkreuz Station":         (52.4756, 13.3654, 50),
    "Gesundbrunnen Station":     (52.5487, 13.3884, 55),
    "Berlin Schoenefeld Airport":(52.3667, 13.5033, 45),
    "Berlin BER Terminal":       (52.3620, 13.5094, 60),
}

MODE_SPEEDS = {
    "walk":5.0,"bicycle":15.0,"subway":30.0,
    "bus":20.0,"car":25.0,"train":60.0,
}

PERSONAS = {
    "ShortWalker": {
        "label":"Short-Range Walker","proportion":0.72,
        "preferred_mode":"walk","fallback_modes":["walk","bicycle"],
        "peak_hours":[11,12,13],"flexibility":0.75,
        "time_budget_min":9999,"dwell_min":5,"dwell_max":15,"max_visits":50,
    },
    "ComfortMixed": {
        "label":"Comfort / Mixed-Mode","proportion":0.22,
        "preferred_mode":"subway","fallback_modes":["subway","bus","car"],
        "peak_hours":[14,15,16],"flexibility":0.45,
        "time_budget_min":9999,"dwell_min":5,"dwell_max":15,"max_visits":50,
    },
    "LongDistanceCar": {
        "label":"Long-Distance Car/Train","proportion":0.04,
        "preferred_mode":"car","fallback_modes":["car","train"],
        "peak_hours":[7,8,9],"flexibility":0.20,
        "time_budget_min":9999,"dwell_min":5,"dwell_max":15,"max_visits":50,
    },
    "LongDistanceRail": {
        "label":"Long-Distance Rail","proportion":0.02,
        "preferred_mode":"train","fallback_modes":["train","subway"],
        "peak_hours":[7,8],"flexibility":0.15,
        "time_budget_min":9999,"dwell_min":5,"dwell_max":15,"max_visits":50,
    },
}

PERSONA_HOTELS = {
    "ShortWalker":     ["Hotel Adlon Kempinski","Hilton Berlin Mitte","Radisson Blu Berlin"],
    "ComfortMixed":    ["Park Inn Alexanderplatz","Hilton Berlin Mitte","25hours Hotel Bikini"],
    "LongDistanceCar": ["25hours Hotel Bikini","Berlin Hauptbahnhof","Zoologischer Garten Stn"],
    "LongDistanceRail":["Berlin Hauptbahnhof","Ostbahnhof","Friedrichstrasse Stn"],
}

NUDGE_RECEPTIVITY = {
    "ShortWalker":     {"label":"High",     "score":0.75,"color":"#15803d"},
    "ComfortMixed":    {"label":"Medium",   "score":0.45,"color":"#d97706"},
    "LongDistanceCar": {"label":"Low",      "score":0.20,"color":"#dc2626"},
    "LongDistanceRail":{"label":"Very Low", "score":0.15,"color":"#7c3aed"},
}

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR,"output")
CACHE_DIR  = os.path.join(BASE_DIR,"cache")
os.makedirs(OUTPUT_DIR,exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)
OSM_NETWORK_TYPE = "walk"
