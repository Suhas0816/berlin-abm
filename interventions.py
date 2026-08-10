"""
interventions.py — S1, S2, S3 nudge interventions
References: Thaler & Sunstein (2008), Pizarro et al. (2023), Franssens et al. (2021)
Author: Suhas Akula | SRH Berlin 2026
"""
from config import CROWD_THRESHOLD

def is_crowded(nodes,name):
    n=nodes.get(name,{})
    return n.get("occupancy",0)>=n.get("capacity",1)*CROWD_THRESHOLD

def occ_ratio(nodes,name):
    n=nodes.get(name,{})
    return n.get("occupancy",0)/max(1,n.get("capacity",1))

def capacity_weighted_alt(nodes,exclude,rng):
    scores={a:1.0-occ_ratio(nodes,a) for a in nodes if a!=exclude}
    total=sum(max(0.01,v) for v in scores.values())
    weights=[max(0.01,scores[a])/total for a in scores]
    return rng.choices(list(scores.keys()),weights=weights,k=1)[0]

def make_alert(atype,hour,title,msg,agent,frm,to):
    return {"type":atype,"time":f"{int(hour):02d}:{int((hour%1)*60):02d}",
            "title":title,"msg":msg,"persona":agent.persona,
            "receptivity":agent.receptivity_label,"hotel":agent.hotel,"from":frm,"to":to}

def apply_S1(agent,nodes,hour):
    if not is_crowded(nodes,agent.dest): return agent.dest,agent.mode,None
    agent.nudges_received+=1
    if agent._rng.random()<agent.flexibility:
        pool=([a for a in nodes if a!=agent.dest and a not in agent.visited]
              or [a for a in nodes if a!=agent.dest])
        new=agent._rng.choice(pool)
        agent.rerouted+=1; agent.nudges_accepted+=1
        return new,agent.mode,make_alert("crowding",hour,"Crowding Alert",f"Redirected to {new}",agent,agent.dest,new)
    return agent.dest,agent.mode,make_alert("nudge_rejected",hour,"Nudge Rejected",
        f"Ignored — receptivity: {agent.receptivity_label}",agent,agent.dest,agent.dest)

def apply_S2(agent,nodes,hour):
    if not is_crowded(nodes,agent.dest): return agent.dest,agent.mode,None
    agent.nudges_received+=1
    if agent._rng.random()<agent.flexibility:
        new=capacity_weighted_alt(nodes,agent.dest,agent._rng)
        agent.rerouted+=1; agent.nudges_accepted+=1
        return new,agent.mode,make_alert("alt",hour,"Alternative Suggested",f"Accepted — going to {new}",agent,agent.dest,new)
    return agent.dest,agent.mode,make_alert("nudge_rejected",hour,"Nudge Rejected",
        f"Declined — receptivity: {agent.receptivity_label}",agent,agent.dest,agent.dest)

def apply_S3(agent,nodes,hour):
    if agent.mode!="car": return agent.dest,agent.mode,None
    agent.nudges_received+=1
    if agent._rng.random()<agent.flexibility:
        agent.mode_shifted+=1; agent.nudges_accepted+=1
        return agent.dest,"subway",make_alert("mode_shift",hour,"Mode Shift Accepted",
            "Car to subway incentive accepted",agent,"car","subway")
    return agent.dest,agent.mode,make_alert("nudge_rejected",hour,"Mode Shift Rejected",
        f"Kept car — receptivity: {agent.receptivity_label}",agent,"car","car")

INTERVENTIONS={None:lambda a,n,h:(a.dest,a.mode,None),"S1":apply_S1,"S2":apply_S2,"S3":apply_S3}
def get_intervention(scenario): return INTERVENTIONS.get(scenario,INTERVENTIONS[None])
