import streamlit as st
from datetime import datetime, timedelta

# 1. Ρύθμιση Σελίδας
st.set_page_config(page_title="Μεταγωγές", page_icon="🚌", layout="wide")

# 2. CSS - Επιβολή Dark Mode & White Cards
st.markdown("""
    <style>
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMainViewContainer"] {
        background-color: #121212 !important;
    }
    .main-title {
        color: #ffffff;
        text-align: center;
        font-family: 'Arial Black', sans-serif;
        font-size: 50px !important;
        font-weight: bold;
        margin-top: -40px;
        padding-bottom: 20px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    .manos-footer {
        position: fixed;
        bottom: 20px;
        left: 20px;
        font-size: 22px !important; 
        color: #ffffff !important;
        font-weight: 800 !important;
        font-family: sans-serif;
        z-index: 9999;
    }
    .route-card {
        background-color: #ffffff !important;
        padding: 20px !important;
        border-radius: 15px !important;
        border-left: 15px solid #007bff !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5) !important;
        margin-bottom: 15px !important;
        color: #000000 !important;
    }
    .return-card {
        background-color: #ffffff !important;
        padding: 20px !important;
        border-radius: 15px !important;
        border-left: 15px solid #ff8c00 !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5) !important;
        margin-bottom: 15px !important;
        color: #000000 !important;
    }
    .stSelectbox label, .stDateInput label {
        color: #ffffff !important;
        font-weight: bold !important;
    }
    .label-blue { color: #0056b3; font-weight: bold; font-size: 1.1em; }
    .date-red { color: #d32f2f; font-weight: bold; font-size: 1.1em; }
    [data-testid="stHeader"] { background-color: rgba(0,0,0,0) !important; }
    </style>
    <div class="main-title">Μεταγωγές</div>
    """, unsafe_allow_html=True)

# --- ΔΕΔΟΜΕΝΑ ΔΡΟΜΟΛΟΓΙΩΝ ---
RAW_ROUTES = [
    {"from": "ΑΘΗΝΑ", "to": ["ΑΥΛΩΝΑΣ", "ΕΛΑΙΩΝΑΣ", "ΛΑΜΙΑ", "ΚΑΣΣΑΒΕΤΕΙΑ", "ΛΑΡΙΣΑ", "ΚΑΤΕΡΙΝΗ", "ΘΕΣΣΑΛΟΝΙΚΗ"], "days": [0, 3], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΚΟΡΙΝΘΟΣ", "ΝΑΥΠΛΙΟ", "ΤΥΡΙΝΘΑ", "ΤΡΙΠΟΛΗ", "ΚΑΛΑΜΑΤΑ"], "days": [2], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΤΡΙΚΑΛΑ", "ΓΡΕΒΕΝΑ", "ΑΥΛΩΝΑΣ"], "days": [0], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΧΑΛΚΙΔΑ"], "days": [1], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΚΡΗΤΗ", "ΡΟΔΟΣ", "ΚΕΡΚΥΡΑ", "ΜΥΤΙΛΗΝΗ"], "days": [4], "transit": 1},
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": ["ΣΕΡΡΕΣ", "ΔΡΑΜΑ", "ΚΑΒΑΛΑ", "ΞΑΝΘΗ", "ΚΟΜΟΤΗΝΗ", "ΑΛΕΞΑΝΔΡΟΥΠΟΛΗ"], "days": [1, 4], "transit": 0},
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": ["ΒΕΡΟΙΑ", "ΚΟΖΑΝΗ", "ΓΡΕΒΕΝΑ", "ΙΩΑΝΝΙΝΑ", "ΑΥΛΩΝΑΣ"], "days": [0], "transit": 0},
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": ["ΑΥΛΩΝΑΣ", "ΛΑΡΙΣΑ", "ΛΑΜΙΑ", "ΑΘΗΝΑ"], "days": [1, 4], "transit": 0},
    {"from": "ΑΥΛΩΝΑΣ", "to": ["ΑΘΗΝΑ", "ΛΑΜΙΑ", "ΛΑΡΙΣΑ", "ΘΕΣΣΑΛΟΝΙΚΗ"], "days": [0, 1, 3, 4], "transit": 0},
    {"from": "ΣΕΡΡΕΣ", "to": ["ΘΕΣΣΑΛΟΝΙΚΗ"], "days": [0, 1], "transit": 0},
    {"from": "ΙΩΑΝΝΙΝΑ", "to": ["ΑΡΤΑ", "ΑΓΡΙΝΙΟ", "ΠΑΤΡΑ", "ΑΘΗΝΑ"], "days": [1], "transit": 0},
    {"from": "ΠΑΤΡΑ", "to": ["ΑΘΗΝΑ", "ΚΟΡΙΝΘΟΣ"], "days": [0], "transit": 0},
    {"from": "ΛΑΡΙΣΑ", "to": ["ΒΟΛΟΣ", "ΛΑΜΙΑ", "ΑΥΛΩΝΑΣ", "ΑΘΗΝΑ"], "days": [0, 3], "transit": 0},
    {"from": "ΛΑΜΙΑ", "to": ["ΑΜΦΙΣΣΑ", "ΔΟΜΟΚΟΣ", "ΑΥΛΩΝΑΣ", "ΑΘΗΝΑ"], "days": [0, 1, 3, 4], "transit": 0},
    {"from": "ΓΡΕΒΕΝΑ", "to": ["ΤΡΙΚΑΛΑ", "ΛΑΜΙΑ", "ΑΥΛΩΝΑΣ", "ΑΘΗΝΑ"], "days": [3], "transit": 0},
    # ΕΠΙΣΤΡΟΦΕΣ HUB
    {"from": ["ΚΑΛΑΜΑΤΑ", "ΤΡΙΠΟΛΗ"], "to": ["ΑΘΗΝΑ"], "days": [3], "transit": 0},
    {"from": ["ΑΛΕΞΑΝΔΡΟΥΠΟΛΗ", "ΞΑΝΘΗ", "ΣΕΡΡΕΣ"], "to": ["ΘΕΣΣΑΛΟΝΙΚΗ"], "days": [2, 5], "transit": 0},
]

HUB_MAP = {
    "ΑΜΦΙΣΣΑ": "ΛΑΜΙΑ", "ΔΟΜΟΚΟΣ": "ΛΑΜΙΑ", "ΚΑΡΠΕΝΗΣΙ": "ΛΑΜΙΑ", "ΘΗΒΑ": "ΕΛΑΙΩΝΑΣ", 
    "ΛΙΒΑΔΕΙΑ": "ΕΛΑΙΩΝΑΣ", "ΧΑΛΚΙΔΑ": "ΕΛΑΙΩΝΑΣ", "ΣΠΑΡΤΗ": "ΤΡΙΠΟΛΗ", "ΠΥΡΓΟΣ": "ΠΑΤΡΑ", 
    "ΑΡΓΟΣ": "ΝΑΥΠΛΙΟ", "ΒΟΛΟΣ": "ΛΑΡΙΣΑ", "ΚΑΡΔΙΤΣΑ": "ΤΡΙΚΑΛΑ", "ΠΡΕΒΕΖΑ": "ΑΡΤΑ", 
    "ΗΓΟΥΜΕΝΙΤΣΑ": "ΙΩΑΝΝΙΝΑ", "ΜΕΣΟΛΟΓΓΙ": "ΑΓΡΙΝΙΟ", "ΕΔΕΣΣΑ": "ΒΕΡΟΙΑ", 
    "ΦΛΩΡΙΝΑ": "ΚΟΖΑΝΗ", "ΚΑΣΤΟΡΙΑ": "ΚΟΖΑΝΗ", "ΚΙΛΚΙΣ": "ΘΕΣΣΑΛΟΝΙΚΗ"
}

# Προετοιμασία λίστας δρομολογίων
ROUTES = []
for r in RAW_ROUTES:
    origins = [r["from"]] if isinstance(r["from"], str) else r["from"]
    destinations = r["to"] if isinstance(r["to"], list) else [r["to"]]
    for o in origins:
        for d in destinations:
            ROUTES.append({"from": o.upper(), "to": d.upper(), "days": r["days"], "transit": r["transit"]})

ALL_CITIES = sorted(list(set([r["from"] for r in ROUTES] + list(HUB_MAP.keys()))))

def greek_day(date):
    return ["Δευτέρα", "Τρίτη", "Τετάρτη", "Πέμπτη", "Παρασκευή", "Σάββατο", "Κυριακή"][date.weekday()]

def format_dt(date):
    return f"<b>{date.strftime('%d/%m/%Y')}</b> <span class='date-red'>({greek_day(date)})</span>"

# --- ΜΗΧΑΝΗ ΑΝΑΖΗΤΗΣΗΣ ---
def find_path(start, end, current_date, mode='backward', visited=None):
    if visited is None: visited = set()
    if end in visited: return None
    new_v = visited.copy()
    new_v.add(end if mode == 'backward' else start)

    if mode == 'backward':
        target_arrival = current_date - timedelta(days=1)
        actual_end = HUB_MAP.get(end, end)
        best_path = None
        for r in ROUTES:
            if r["to"] == actual_end:
                ship = target_arrival - timedelta(days=r["transit"])
                while ship.weekday() not in r["days"]: ship -= timedelta(days=1)
                prefix = find_path(start, r["from"], ship, 'backward', new_v) if r["from"] != start else []
                if prefix is not None:
                    path = prefix + [{"from": r["from"], "to": r["to"], "ship": ship, "arrive": ship + timedelta(days=r["transit"])}]
                    if best_path is None or path[0]["ship"] > best_path[0]["ship"]: best_path = path
        if best_path and end in HUB_MAP:
            best_path.append({"from": actual_end, "to": end, "ship": best_path[-1]["arrive"], "arrive": best_path[-1]["arrive"]})
        return best_path
    
    else: # FORWARD (ΕΠΙΣΤΡΟΦΗ)
        actual_start = HUB_MAP.get(start, start)
        best_path = None
        for r in ROUTES:
            if r["from"] == actual_start:
                ship = current_date
                while ship.weekday() not in r["days"]: ship += timedelta(days=1)
                arrive = ship + timedelta(days=r["transit"])
                if r["to"] == end:
                    path = [{"from": r["from"], "to": r["to"], "ship": ship, "arrive": arrive}]
                else:
                    suffix = find_path(r["to"], end, arrive + timedelta(days=1), 'forward', new_v)
                    path = [{"from": r["from"], "to": r["to"], "ship": ship, "arrive": arrive}] + suffix if suffix else None
                if path and (best_path is None or path[-1]["arrive"] < best_path[-1]["arrive"]): best_path = path
        return best_path

# --- UI ---
with st.container():
    c1, c2, c3 = st.columns(3)
    origin = c1.selectbox("📍 Αφετηρία:", ALL_CITIES, index=ALL_CITIES.index("ΣΕΡΡΕΣ"))
    dest = c2.selectbox("🏁 Προορισμός:", ALL_CITIES, index=ALL_CITIES.index("ΑΘΗΝΑ"))
    d_date = c3.date_input("📅 Παράδοση:", datetime.now() + timedelta(days=5))

if st.button("🚀 Υπολογισμός Δρομολογίου"):
    res = find_path(origin.upper(), dest.upper(), d_date, 'backward')
    if res:
        st.session_state['res'] = res
        st.session_state['o'] = origin
        st.session_state['d'] = dest
        st.session_state['dt'] = d_date
        st.session_state['ret'] = None # Καθαρισμός προηγούμενης επιστροφής
    else:
        st.error("Δεν βρέθηκε διαδρομή.")

if 'res' in st.session_state and st.session_state['res']:
    st.markdown(f"<h3 style='color:white;'>🗓️ Πρέπει να ξεκινήσει: {format_dt(st.session_state['res'][0]['ship'])}</h3>", unsafe_allow_html=True)
    for i, leg in enumerate(st.session_state['res']):
        st.markdown(f"""<div class="route-card"><div style="font-weight:bold; font-size:1.3em; color:#0056b3;">🚌 Σκέλος {i+1}: {leg['from']} ➡️ {leg['to']}</div>
        <div><span class="label-blue">Αναχώρηση:</span> {format_dt(leg['ship'])} | <span class="label-blue">Άφιξη:</span> {format_dt(leg['arrive'])}</div></div>""", unsafe_allow_html=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    if st.button(f"🔄 Υπολογισμός Επιστροφής"):
        ret_path = find_path(st.session_state['d'].upper(), st.session_state['o'].upper(), st.session_state['dt'] + timedelta(days=1), 'forward')
        if ret_path:
            st.session_state['ret'] = ret_path
        else:
            st.error("Δεν βρέθηκε διαδρομή επιστροφής.")

if 'ret' in st.session_state and st.session_state['ret']:
    st.markdown(f"<h3 style='color:white;'>🗓️ Επιστροφή στην έδρα: {format_dt(st.session_state['ret'][-1]['arrive'])}</h3>", unsafe_allow_html=True)
    for i, leg in enumerate(st.session_state['ret']):
        st.markdown(f"""<div class="return-card"><div style="font-weight:bold; font-size:1.3em; color:#cc5500;">🔄 Σκέλος {i+1}: {leg['from']} ➡️ {leg['to']}</div>
        <div><span class="label-blue">Αναχώρηση:</span> {format_dt(leg['ship'])} | <span class="label-blue">Άφιξη:</span> {format_dt(leg['arrive'])}</div></div>""", unsafe_allow_html=True)

# by Manos
st.markdown('<div class="manos-footer">by Manos</div>', unsafe_allow_html=True)
