import streamlit as st
from datetime import datetime, timedelta

# Ρύθμιση σελίδας
st.set_page_config(page_title="Bus Route Planner", page_icon="🚌", layout="wide")

# --- CSS ΓΙΑ ΕΠΙΒΟΛΗ ΧΡΩΜΑΤΩΝ (Targeting exact Streamlit elements) ---
st.markdown("""
    <style>
    /* 1. Φόντο όλης της σελίδας και των containers */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stMain"] {
        background-color: #dee2e6 !important;
    }

    /* 2. Κεντρικό πλαίσιο περιεχομένου */
    .block-container {
        background-color: #dee2e6 !important;
        padding: 3rem !important;
    }

    /* 3. Τίτλος */
    .main-title {
        color: #002b5c;
        text-align: center;
        font-family: 'Arial Black', sans-serif;
        font-size: 32px;
        padding-bottom: 30px;
    }

    /* 4. Κάρτες Αποτελεσμάτων (Αναχώρηση) - Λευκό κουτί με σκιά */
    .route-card {
        background-color: #ffffff !important;
        color: #000000 !important;
        padding: 25px !important;
        border-radius: 15px !important;
        border-left: 15px solid #004a99 !important;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.2) !important;
        margin-bottom: 25px !important;
    }

    /* 5. Κάρτες Επιστροφής - Λευκό κουτί με πορτοκαλί άκρη */
    .return-card {
        background-color: #ffffff !important;
        color: #000000 !important;
        padding: 25px !important;
        border-radius: 15px !important;
        border-left: 15px solid #ff7b00 !important;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.2) !important;
        margin-bottom: 25px !important;
    }

    /* 6. Bold κείμενο μέσα στις κάρτες */
    .card-text {
        font-size: 1.2rem !important;
        margin-bottom: 8px !important;
    }
    
    .day-name {
        color: #d32f2f;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ΔΕΔΟΜΕΝΑ ΔΡΟΜΟΛΟΓΙΩΝ ---
RAW_ROUTES = [
    {"from": "ΑΘΗΝΑ", "to": ["ΑΥΛΩΝΑΣ", "ΕΛΑΙΩΝΑΣ", "ΛΑΜΙΑ", "ΚΑΣΣΑΒΕΤΕΙΑ", "ΛΑΡΙΣΑ", "ΚΑΤΕΡΙΝΗ", "ΘΕΣΣΑΛΟΝΙΚΗ"], "days": [0, 3], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΤΡΙΚΑΛΑ", "ΓΡΕΒΕΝΑ"], "days": [0], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΧΑΛΚΙΔΑ"], "days": [1], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΚΟΡΙΝΘΟΣ", "ΝΑΥΠΛΙΟ", "ΤΥΡΙΝΘΑ", "ΤΡΙΠΟΛΗ", "ΚΑΛΑΜΑΤΑ"], "days": [2], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΧΑΝΙΑ", "ΗΡΑΚΛΕΙΟ", "ΝΗΣΙΑ"], "days": [4], "transit": 1},
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": ["ΣΕΡΡΕΣ", "ΔΡΑΜΑ", "ΚΑΒΑΛΑ", "ΞΑΝΘΗ", "ΚΟΜΟΤΗΝΗ", "ΑΛΕΞΑΝΔΡΟΥΠΟΛΗ"], "days": [1, 4], "transit": 0},
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": ["ΒΕΡΟΙΑ", "ΚΟΖΑΝΗ", "ΓΡΕΒΕΝΑ", "ΙΩΑΝΝΙΝΑ"], "days": [0], "transit": 0},
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": ["ΔΡΑΜΑ", "ΣΕΡΡΕΣ"], "days": [3], "transit": 0},
    {"from": "ΣΕΡΡΕΣ", "to": ["ΘΕΣΣΑΛΟΝΙΚΗ"], "days": [0, 1], "transit": 0},
    {"from": "ΙΩΑΝΝΙΝΑ", "to": ["ΑΡΤΑ", "ΑΓΡΙΝΙΟ", "ΠΑΤΡΑ", "ΑΙΓΙΟ", "ΚΟΡΙΝΘΟΣ", "ΑΘΗΝΑ"], "days": [1], "transit": 0},
    {"from": "ΠΑΤΡΑ", "to": ["ΑΙΓΙΟ", "ΚΟΡΙΝΘΟΣ", "ΑΘΗΝΑ"], "days": [0], "transit": 0},
    {"from": "ΠΑΤΡΑ", "to": ["ΑΡΓΟΛΙΔΑ", "ΜΕΣΣΗΝΙΑ"], "days": [1], "transit": 0},
    {"from": "ΑΓΡΙΝΙΟ", "to": ["ΠΑΤΡΑ", "ΑΜΦΙΣΣΑ"], "days": [2], "transit": 0},
    {"from": "ΛΑΡΙΣΑ", "to": ["ΒΟΛΟΣ"], "days": [0, 3], "transit": 0},
    {"from": "ΑΜΦΙΣΣΑ", "to": ["ΛΑΜΙΑ"], "days": [0, 1, 3, 4], "transit": 0},
    {"from": "ΛΑΜΙΑ", "to": ["ΑΜΦΙΣΣΑ", "ΔΟΜΟΚΟΣ"], "days": [0, 1, 3, 4], "transit": 0},
    {"from": "ΓΡΕΒΕΝΑ", "to": ["ΤΡΙΚΑΛΑ", "ΛΑΜΙΑ", "ΑΘΗΝΑ"], "days": [3], "transit": 0},
    # ΕΠΙΣΤΡΟΦΕΣ
    {"from": ["ΘΕΣΣΑΛΟΝΙΚΗ", "ΛΑΡΙΣΑ", "ΛΑΜΙΑ"], "to": ["ΑΘΗΝΑ"], "days": [1, 4], "transit": 0},
    {"from": ["ΚΑΛΑΜΑΤΑ", "ΤΡΙΠΟΛΗ", "ΝΑΥΠΛΙΟ"], "to": ["ΑΘΗΝΑ"], "days": [3], "transit": 0},
    {"from": ["ΑΛΕΞΑΝΔΡΟΥΠΟΛΗ", "ΞΑΝΘΗ", "ΣΕΡΡΕΣ"], "to": ["ΘΕΣΣΑΛΟΝΙΚΗ"], "days": [2, 5], "transit": 0},
]

# Hub Mapping
HUB_MAP = {"ΒΟΛΟΣ": "ΛΑΡΙΣΑ", "ΔΟΜΟΚΟΣ": "ΛΑΜΙΑ", "ΘΗΒΑ": "ΕΛΑΙΩΝΑΣ", "ΛΙΒΑΔΕΙΑ": "ΕΛΑΙΩΝΑΣ", "ΜΑΛΑΝΔΡΙΝΟ": "ΠΑΤΡΑ"}

ROUTES = []
for r in RAW_ROUTES:
    origins = [r["from"]] if isinstance(r["from"], str) else r["from"]
    destinations = r["to"] if isinstance(r["to"], list) else [r["to"]]
    for o in origins:
        for d in destinations:
            ROUTES.append({"from": o.upper(), "to": d.upper(), "days": r["days"], "transit": r["transit"]})

ALL_CITIES = sorted(list(set([r["from"] for r in ROUTES] + list(HUB_MAP.keys()))))

def greek_day(date):
    days = ["Δευτέρα", "Τρίτη", "Τετάρτη", "Πέμπτη", "Παρασκευή", "Σάββατο", "Κυριακή"]
    return days[date.weekday()]

def format_date_gr(date):
    return f"<b>{date.strftime('%d/%m/%Y')}</b> <span class='day-name'>({greek_day(date)})</span>"

# --- ΜΗΧΑΝΕΣ ΑΝΑΖΗΤΗΣΗΣ ---
def find_backward_path(start, end, deadline, depth=0):
    if depth > 4: return None
    target_arrival = deadline - timedelta(days=1)
    actual_end = HUB_MAP.get(end, end)
    best_path = None
    for r in ROUTES:
        if r["to"] == actual_end:
            ship = target_arrival - timedelta(days=r["transit"])
            tries = 0
            while ship.weekday() not in r["days"] and tries < 14:
                ship -= timedelta(days=1)
                tries += 1
            arrive = ship + timedelta(days=r["transit"])
            current_leg = {"from": r["from"], "to": r["to"], "ship": ship, "arrive": arrive}
            if r["from"] == start: path = [current_leg]
            else:
                prefix = find_backward_path(start, r["from"], ship, depth + 1)
                path = prefix + [current_leg] if prefix else None
            if path and (best_path is None or path[0]["ship"] > best_path[0]["ship"]):
                best_path = path
    if best_path and end in HUB_MAP:
        best_path.append({"from": HUB_MAP[end], "to": end, "ship": best_path[-1]["arrive"], "arrive": best_path[-1]["arrive"]})
    return best_path

def find_forward_path(start, end, start_date, depth=0):
    if depth > 4: return None
    best_path = None
    actual_start = HUB_MAP.get(start, start)
    for r in ROUTES:
        if r["from"] == actual_start:
            ship = start_date
            tries = 0
            while ship.weekday() not in r["days"] and tries < 14:
                ship += timedelta(days=1)
                tries += 1
            arrive = ship + timedelta(days=r["transit"])
            current_leg = {"from": r["from"], "to": r["to"], "ship": ship, "arrive": arrive}
            if r["to"] == end: path = [current_leg]
            else:
                suffix = find_forward_path(r["to"], end, arrive + timedelta(days=1), depth + 1)
                path = [current_leg] + suffix if suffix else None
            if path and (best_path is None or path[-1]["arrive"] < best_path[-1]["arrive"]):
                best_path = path
    return best_path

# --- UI ---
st.markdown('<div class="main-title">🚌 Bus Route Planner</div>', unsafe_allow_html=True)

with st.container():
    c1, c2, c3 = st.columns(3)
    with c1:
        origin = st.selectbox("📍 Αφετηρία:", ALL_CITIES, index=ALL_CITIES.index("ΣΕΡΡΕΣ"))
    with c2:
        dest = st.selectbox("🏁 Προορισμός:", ALL_CITIES, index=ALL_CITIES.index("ΑΘΗΝΑ"))
    with c3:
        d_date = st.date_input("📅 Παράδοση:", datetime.now() + timedelta(days=5))

if st.button("🚀 Υπολογισμός Δρομολογίου"):
    res = find_backward_path(origin.upper(), dest.upper(), d_date)
    if res:
        st.session_state.update({'res': res, 'd': dest, 'o': origin, 'dt': d_date})
        st.markdown(f"<h3>📅 Πρέπει να ξεκινήσει: {format_date_gr(res[0]['ship'])}</h3>", unsafe_allow_html=True)
        for i, leg in enumerate(res):
            st.markdown(f"""<div class="route-card"><div class="card-text"><b>🚌 Σκέλος {i+1}:</b> {leg['from']} ➡️ {leg['to']}</div>
            <div class="card-text">📦 <b>Αναχώρηση:</b> {format_date_gr(leg['ship'])} | 🏁 <b>Άφιξη:</b> {format_date_gr(leg['arrive'])}</div></div>""", unsafe_allow_html=True)

if 'res' in st.session_state:
    if st.button(f"🔄 Επιστροφή ({st.session_state['d']} ➡️ {st.session_state['o']})"):
        ret = find_forward_path(st.session_state['d'].upper(), st.session_state['o'].upper(), st.session_state['dt'] + timedelta(days=1))
        if ret:
            st.markdown(f"<h3>📅 Επιστροφή στην έδρα: {format_date_gr(ret[-1]['arrive'])}</h3>", unsafe_allow_html=True)
            for i, leg in enumerate(ret):
                st.markdown(f"""<div class="return-card"><div class="card-text"><b>🔄 Σκέλος {i+1}:</b> {leg['from']} ➡️ {leg['to']}</div>
                <div class="card-text">📦 <b>Αναχώρηση:</b> {format_date_gr(leg['ship'])} | 🏁 <b>Άφιξη:</b> {format_date_gr(leg['arrive'])}</div></div>""", unsafe_allow_html=True)
