"""
network.py — Berlin street network
Author: Suhas Akula | SRH Berlin 2026
Reference: Boeing (2017) OSMnx
"""
import os, pickle, logging, warnings
from math import radians, sin, cos, sqrt, atan2
from config import ATTRACTIONS, MODE_SPEEDS

logging.basicConfig(level=logging.INFO,format="%(asctime)s %(levelname)-8s %(message)s",datefmt="%H:%M:%S")
logger=logging.getLogger(__name__)
warnings.filterwarnings("ignore")

CACHE_DIR=os.path.join(os.path.dirname(os.path.abspath(__file__)),"cache")
MATRIX_CACHE=os.path.join(CACHE_DIR,"distance_matrix.pkl")
os.makedirs(CACHE_DIR,exist_ok=True)

def haversine_km(lat1,lon1,lat2,lon2):
    R=6371.0
    p1,p2=radians(lat1),radians(lat2)
    dp,dl=radians(lat2-lat1),radians(lon2-lon1)
    a=sin(dp/2)**2+cos(p1)*cos(p2)*sin(dl/2)**2
    return R*2*atan2(sqrt(a),sqrt(1-a))

def build_haversine_matrix():
    logger.warning("osmnx not installed — using haversine fallback.")
    names=list(ATTRACTIONS.keys())
    matrix={}
    for n1 in names:
        la1,lo1,_=ATTRACTIONS[n1]
        for n2 in names:
            la2,lo2,_=ATTRACTIONS[n2]
            matrix[(n1,n2)]=0.0 if n1==n2 else haversine_km(la1,lo1,la2,lo2)*1.3
    return matrix

def build_travel_time_matrix(dist_matrix):
    tt={}
    for mode,speed in MODE_SPEEDS.items():
        overhead=1.25 if mode in ("subway","bus","train") else 1.05
        tt[mode]={pair:max(2.0,(d/speed)*60*overhead) for pair,d in dist_matrix.items()}
    return tt

def load_network():
    try:
        import osmnx as ox, networkx as nx
        if os.path.exists(MATRIX_CACHE):
            with open(MATRIX_CACHE,"rb") as f: dist_matrix=pickle.load(f)
        else:
            lats=[v[0] for v in ATTRACTIONS.values()]
            lons=[v[1] for v in ATTRACTIONS.values()]
            G=ox.graph_from_bbox(bbox=(max(lats)+0.015,min(lats)-0.015,max(lons)+0.015,min(lons)-0.015),network_type="walk",simplify=True)
            node_map={name:ox.distance.nearest_nodes(G,X=c[1],Y=c[0]) for name,c in ATTRACTIONS.items()}
            names=list(node_map.keys()); dist_matrix={}
            for n1 in names:
                try: lengths=dict(nx.single_source_dijkstra_path_length(G,node_map[n1],weight="length"))
                except: lengths={}
                for n2 in names:
                    if n1==n2: dist_matrix[(n1,n2)]=0.0
                    elif node_map[n2] in lengths: dist_matrix[(n1,n2)]=lengths[node_map[n2]]/1000.0
                    else:
                        la1,lo1,_=ATTRACTIONS[n1]; la2,lo2,_=ATTRACTIONS[n2]
                        dist_matrix[(n1,n2)]=haversine_km(la1,lo1,la2,lo2)*1.3
            with open(MATRIX_CACHE,"wb") as f: pickle.dump(dist_matrix,f)
    except ImportError:
        dist_matrix=build_haversine_matrix()
    return dist_matrix,build_travel_time_matrix(dist_matrix)

def get_travel_time(tt_matrix,origin,dest,mode):
    if origin==dest: return 0.0
    return tt_matrix.get(mode,tt_matrix.get("walk",{})).get((origin,dest),10.0)
