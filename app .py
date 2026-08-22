"""
app.py — Berlin Tourist Mobility ABM Flask Web Application
Clean final version — no duplicate endpoints
Author: Suhas Akula | SRH Berlin 2026
"""
import sys, os, random, threading, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, render_template, request
from config import (ATTRACTIONS, RANDOM_SEED, SIM_START_HOUR, SIM_END_HOUR,
    STEP_MINUTES, CROWD_THRESHOLD, WEATHER_STATES, HOURLY_ACTIVITY_PROFILE,
    DAY_PHASES, PERSONA_HOTELS, NUDGE_RECEPTIVITY)
from network import load_network, get_travel_time
from weather import WeatherState, apply_weather_to_mode_choice
from personas import assign_personas
from interventions import get_intervention

app = Flask(__name__, template_folder='templates')

sim = {
    "running":False,"step":0,"hour":SIM_START_HOUR,"scenario":None,"weather":"Clear",
    "agents":[],"nodes":{},"stats":{},"alerts":[],"all_alerts":[],"day_count":0,
}

_tt_matrix     = None
_last_n_agents = 200
_last_scenario = None
_last_weather  = "Clear"
_last_reset    = time.time()
REAL_RESTART_SECONDS = 300
SIM_SPEED      = 0.35
_crowd_threshold = 0.25  # lower than config so alerts fire with many locations

PERSONA_COLORS = {
    "ShortWalker":"#15803d","ComfortMixed":"#1e40af",
    "LongDistanceCar":"#dc2626","LongDistanceRail":"#7c3aed",
}

def get_phase(h):
    for name,(s,e) in DAY_PHASES.items():
        if s<=h<e: return name
    return "Off-hours"

def get_receptivity_label(f):
    if f>=0.70: return "High"
    elif f>=0.40: return "Medium"
    elif f>=0.20: return "Low"
    return "Very Low"

def get_starting_hotel(persona,rng):
    hotels=PERSONA_HOTELS.get(persona,list(ATTRACTIONS.keys()))
    valid=[h for h in hotels if h in ATTRACTIONS]
    return rng.choice(valid) if valid else rng.choice(list(ATTRACTIONS.keys()))

class SimAgent:
    def __init__(self,aid,profile,wstate):
        self.id=aid; self.persona=profile.name; self.mode=profile.preferred_mode
        self.flexibility=profile.flexibility; self.time_budget=profile.time_budget
        self.time_elapsed=0.0; self.active=True; self.visited=set()
        self.rerouted=0; self.mode_shifted=0
        self.nudges_received=0; self.nudges_accepted=0
        self.satisfaction=100  # starts at 100%, drops when crowded
        self._rng=random.Random(aid*31+7)
        self._weather=wstate; self._profile=profile
        self.hotel=get_starting_hotel(profile.name,self._rng)
        self.current=self.hotel; self.visited.add(self.current)
        self.dest=self._next()
        lat,lon,_=ATTRACTIONS[self.current]
        self.lat=lat+self._rng.uniform(-0.0005,0.0005)
        self.lon=lon+self._rng.uniform(-0.0005,0.0005)

    def _next(self):
        unvisited=[a for a in ATTRACTIONS if a!=self.current and a not in self.visited and a!=self.hotel]
        if not unvisited: unvisited=[a for a in ATTRACTIONS if a!=self.current]
        return self._rng.choice(unvisited)

    @property
    def receptivity_label(self): return get_receptivity_label(self.flexibility)

    @property
    def acceptance_rate(self):
        return round(self.nudges_accepted/self.nudges_received*100,1) if self.nudges_received else 0.0

    def step(self,nodes,scenario,hour):
        if not self.active: return None
        h=int(hour)%24
        prob=min(1.0,HOURLY_ACTIVITY_PROFILE.get(h,0.4)*(1.3 if h in self._profile.peak_hours else 1.0))
        if self._rng.random()>prob: return None
        mode=apply_weather_to_mode_choice(self.mode,self._weather,self._rng)
        fn=get_intervention(scenario)
        new_dest,new_mode,alert=fn(self,nodes,hour)
        travel=get_travel_time(_tt_matrix,self.current,new_dest,new_mode)
        dwell=self._rng.uniform(self._profile.dwell_min,self._profile.dwell_max)
        nodes[self.current]["occupancy"]=max(0,nodes[self.current]["occupancy"]-1)
        self.current=new_dest; self.visited.add(new_dest)
        # Satisfaction drops when visiting crowded site
        nd=nodes.get(new_dest,{})
        ratio=nd.get("occupancy",0)/max(1,nd.get("capacity",1))
        if ratio>=_crowd_threshold:
            self.satisfaction=max(0,self.satisfaction-15)
        elif ratio<0.3:
            self.satisfaction=min(100,self.satisfaction+3)
        nodes[self.current]["occupancy"]+=1
        dlat,dlon,_=ATTRACTIONS[new_dest]
        self.lat+=(dlat-self.lat)*0.6+self._rng.uniform(-0.0003,0.0003)
        self.lon+=(dlon-self.lon)*0.6+self._rng.uniform(-0.0003,0.0003)
        self.dest=self._next()
        self.time_elapsed+=travel+dwell
        self.mode=new_mode
        return alert  # can be None or a dict

def compute_stats():
    agents=sim["agents"]; nodes=sim["nodes"]
    modes=[a.mode for a in agents if a.active]
    occs=[n["occupancy"] for n in nodes.values()]
    sus={"walk","bicycle","subway","bus"}
    high=sum(1 for a in agents if a.active and a.flexibility>=0.70)
    medium=sum(1 for a in agents if a.active and 0.40<=a.flexibility<0.70)
    low=sum(1 for a in agents if a.active and 0.20<=a.flexibility<0.40)
    vlow=sum(1 for a in agents if a.active and a.flexibility<0.20)
    total_recv=sum(a.nudges_received for a in agents)
    total_acc=sum(a.nudges_accepted for a in agents)
    hotel_counts={}
    for a in agents:
        if a.active: hotel_counts[a.hotel]=hotel_counts.get(a.hotel,0)+1
    return {
        "hour":f"{int(sim['hour']):02d}:{int((sim['hour']%1)*60):02d}",
        "phase":get_phase(sim["hour"]),"weather":sim["weather"],
        "active_agents":sum(1 for a in agents if a.active),
        "crowded_nodes":sum(1 for n in nodes.values()
                            if n["occupancy"]>=n["capacity"]*_crowd_threshold),
        "total_nodes":len(nodes),
        "peak_occupancy":max(occs) if occs else 0,
        "walk_pct":round(modes.count("walk")/len(modes)*100,1) if modes else 0,
        "subway_pct":round(modes.count("subway")/len(modes)*100,1) if modes else 0,
        "car_pct":round(modes.count("car")/len(modes)*100,1) if modes else 0,
        "sustainable_pct":round(sum(1 for m in modes if m in sus)/len(modes)*100,1) if modes else 0,
        "total_reroutes":sum(a.rerouted for a in agents),
        "total_shifts":sum(a.mode_shifted for a in agents),
        "day_count":sim["day_count"],
        "receptivity_high":high,"receptivity_medium":medium,
        "receptivity_low":low,"receptivity_vlow":vlow,
        "nudges_received":total_recv,"nudges_accepted":total_acc,
        "nudge_acceptance_rate":round(total_acc/total_recv*100,1) if total_recv>0 else 0.0,
        "hotel_distribution":hotel_counts,
        "avg_satisfaction":round(sum(a.satisfaction for a in agents if a.active)/max(1,sum(1 for a in agents if a.active)),1),
    }

def make_nodes(n_agents):
    """Scale capacity so crowding builds realistically."""
    cap_scale = max(0.2, n_agents/500.0)
    return {name:{"lat":c[0],"lon":c[1],
                  "capacity":max(4,int(c[2]*cap_scale)),
                  "occupancy":0}
            for name,c in ATTRACTIONS.items()}

def do_step():
    agents=sim["agents"]; nodes=sim["nodes"]
    scenario=sim["scenario"]; hour=sim["hour"]
    alerts=[]
    random.shuffle(agents)
    for agent in agents:
        al=agent.step(nodes,scenario,hour)
        if al is not None:
            alerts.append(al)
    sim["step"]+=1
    sim["hour"]+=STEP_MINUTES/60.0
    sim["alerts"]=alerts[-10:]
    sim["all_alerts"]=(sim["all_alerts"]+alerts)[-100:]
    sim["stats"]=compute_stats()
    if sim["hour"]>=SIM_END_HOUR:
        reset_simulation()

def reset_simulation():
    global _last_n_agents,_last_weather
    wconf=WEATHER_STATES.get(_last_weather,WEATHER_STATES["Clear"])
    wstate=WeatherState(_last_weather,wconf["walk_modifier"],wconf["bike_modifier"])
    rng=random.Random(random.randint(0,9999))
    profiles=assign_personas(_last_n_agents,rng)
    agents=[SimAgent(i,p,wstate) for i,p in enumerate(profiles)]
    nodes=make_nodes(_last_n_agents)
    for a in agents: nodes[a.current]["occupancy"]+=1
    sim["step"]=0; sim["hour"]=SIM_START_HOUR
    sim["agents"]=agents; sim["nodes"]=nodes
    sim["alerts"]=[]; sim["day_count"]+=1
    sim["stats"]=compute_stats()

def background_runner():
    global _last_reset
    while True:
        if sim["running"]:
            do_step()
            now=time.time()
            if now-_last_reset>=REAL_RESTART_SECONDS:
                _last_reset=now; reset_simulation()
            time.sleep(SIM_SPEED)
        else:
            time.sleep(0.05)

# ── ROUTES ────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html",attractions=ATTRACTIONS)

@app.route("/api/init",methods=["POST"])
def api_init():
    global _tt_matrix,_last_n_agents,_last_scenario,_last_weather,_last_reset
    data=request.json or {}
    scenario=data.get("scenario") or None
    weather=data.get("weather","Clear")
    n_agents=int(data.get("n_agents",200))
    seed=int(data.get("seed",RANDOM_SEED))
    if _tt_matrix is None: _,_tt_matrix=load_network()
    _last_n_agents=n_agents; _last_scenario=scenario
    _last_weather=weather; _last_reset=time.time()
    wconf=WEATHER_STATES.get(weather,WEATHER_STATES["Clear"])
    wstate=WeatherState(weather,wconf["walk_modifier"],wconf["bike_modifier"])
    rng=random.Random(seed)
    profiles=assign_personas(n_agents,rng)
    agents=[SimAgent(i,p,wstate) for i,p in enumerate(profiles)]
    nodes=make_nodes(n_agents)
    for a in agents: nodes[a.current]["occupancy"]+=1
    sim.update({"running":False,"step":0,"hour":SIM_START_HOUR,
                "scenario":scenario,"weather":weather,
                "agents":agents,"nodes":nodes,
                "alerts":[],"all_alerts":[],"day_count":0})
    sim["stats"]=compute_stats()
    return jsonify({"status":"ok",
                    "message":f"Ready: {n_agents} agents | {scenario or 'Baseline'} | {weather} | Starting from hotels"})

@app.route("/api/start",methods=["POST"])
def api_start():
    sim["running"]=True; return jsonify({"status":"running"})

@app.route("/api/pause",methods=["POST"])
def api_pause():
    sim["running"]=False; return jsonify({"status":"paused"})

@app.route("/api/step",methods=["POST"])
def api_step():
    sim["running"]=False; do_step(); return jsonify({"status":"stepped"})

@app.route("/api/state")
def api_state():
    agents=sim["agents"]; nodes=sim["nodes"]
    return jsonify({
        "running":sim["running"],"step":sim["step"],
        "stats":sim["stats"],"alerts":sim["alerts"],
        "hour":sim["hour"],"day_count":sim["day_count"],
        "agents":[{
            "id":a.id,"lat":round(a.lat,6),"lon":round(a.lon,6),
            "persona":a.persona,"mode":a.mode,
            "color":PERSONA_COLORS.get(a.persona,"#64748b"),
            "active":a.active,"current":a.current,"hotel":a.hotel,
            "dest":a.dest,
            "flexibility":round(a.flexibility,2),
            "receptivity":a.receptivity_label,
            "nudges_recv":a.nudges_received,
            "nudges_acc":a.nudges_accepted,
            "accept_rate":a.acceptance_rate,
            "visits":len(a.visited),
        } for a in agents if a.active],
        "nodes":{name:{
            "lat":d["lat"],"lon":d["lon"],
            "occupancy":d["occupancy"],"capacity":d["capacity"],
            "ratio":round(d["occupancy"]/max(1,d["capacity"]),3),
            "crowded":d["occupancy"]>=d["capacity"]*_crowd_threshold,
        } for name,d in nodes.items()},
        "nudge_receptivity":NUDGE_RECEPTIVITY,
        "persona_hotels":PERSONA_HOTELS,
    })

@app.route("/api/set_speed",methods=["POST"])
def api_set_speed():
    global SIM_SPEED
    data=request.json or {}
    SIM_SPEED=max(0.02,min(2.0,float(data.get("speed",0.35))))
    return jsonify({"status":"ok","speed":SIM_SPEED})

@app.route("/api/set_capacity",methods=["POST"])
def api_set_capacity():
    data=request.json or {}
    name=data.get("name"); capacity=int(data.get("capacity",30))
    nodes=sim["nodes"]
    if name and name in nodes:
        nodes[name]["capacity"]=capacity
        return jsonify({"status":"ok","name":name,"capacity":capacity})
    return jsonify({"status":"error","message":"Not found"}),404

@app.route("/api/set_nudge",methods=["POST"])
def api_set_nudge():
    global _crowd_threshold
    data=request.json or {}
    if "crowd_threshold" in data:
        _crowd_threshold=float(data["crowd_threshold"])
    agents=sim["agents"]
    if "s1_receptivity" in data:
        val=float(data["s1_receptivity"])
        for a in agents:
            if a.persona=="ShortWalker": a.flexibility=val
    if "s2_receptivity" in data:
        val=float(data["s2_receptivity"])
        for a in agents:
            if a.persona=="ComfortMixed": a.flexibility=val
    if "s3_receptivity" in data:
        val=float(data["s3_receptivity"])
        for a in agents:
            if a.persona in ("LongDistanceCar","LongDistanceRail"): a.flexibility=val
    return jsonify({"status":"ok"})

@app.route("/api/compare")
def api_compare():
    global _tt_matrix
    if _tt_matrix is None: _,_tt_matrix=load_network()
    results={}
    for scenario,label in [(None,"Baseline"),("S1","S1"),("S2","S2"),("S3","S3")]:
        wconf=WEATHER_STATES["Clear"]
        wstate=WeatherState("Clear",wconf["walk_modifier"],wconf["bike_modifier"])
        rng=random.Random(42)
        profiles=assign_personas(200,rng)
        agents=[SimAgent(i,p,wstate) for i,p in enumerate(profiles)]
        nodes=make_nodes(200)
        for a in agents: nodes[a.current]["occupancy"]+=1
        hour=SIM_START_HOUR
        for _ in range(120):
            random.shuffle(agents)
            for agent in agents: agent.step(nodes,scenario,hour)
            hour+=STEP_MINUTES/60.0
            if hour>=SIM_END_HOUR: break
        modes=[a.mode for a in agents if a.active]
        occs=[n["occupancy"] for n in nodes.values()]
        sus={"walk","bicycle","subway","bus"}
        total_recv=sum(a.nudges_received for a in agents)
        total_acc=sum(a.nudges_accepted for a in agents)
        results[label]={
            "crowded_nodes":sum(1 for n in nodes.values() if n["occupancy"]>=n["capacity"]*_crowd_threshold),
            "total_reroutes":sum(a.rerouted for a in agents),
            "total_shifts":sum(a.mode_shifted for a in agents),
            "walk_pct":round(modes.count("walk")/len(modes)*100,1) if modes else 0,
            "car_pct":round(modes.count("car")/len(modes)*100,1) if modes else 0,
            "sustainable_pct":round(sum(1 for m in modes if m in sus)/len(modes)*100,1) if modes else 0,
            "peak_occupancy":max(occs) if occs else 0,
            "nudge_acceptance_rate":round(total_acc/total_recv*100,1) if total_recv>0 else 0.0,
        }
    return jsonify(results)

if __name__=="__main__":
    print("="*55)
    print("  Berlin Tourist Mobility ABM")
    print("  Author: Suhas Akula | SRH Berlin 2026")
    print("="*55)
    print("\nLoading Berlin network...")
    _,_tt_matrix=load_network()
    print("Network ready.\n")
    threading.Thread(target=background_runner,daemon=True).start()
    print("Open: http://localhost:5000")
    app.run(debug=False,host="0.0.0.0",port=5000,use_reloader=False,threaded=True)
