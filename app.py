import streamlit as st
from datetime import datetime, timedelta

# Ρύθμιση σελίδας
st.set_page_config(page_title="Bus Route Planner", page_icon="🚌", layout="wide")

# --- ΕΠΙΒΟΛΗ CSS (FORCE BACKGROUND COLOR) ---
st.markdown("""
    <style>
    /* Επιβολή γκρι φόντου σε όλη την εφαρμογή */
    .stApp {
        background-color: #f0f2f6 !important;
    }
    
    /* Κεντρικό κοντέινερ για να μην "κολλάει" το κείμενο */
    .block-container {
        padding-top: 2rem !important;
    }

    /* Τίτλος */
    h1 {
        color: #003366 !important;
        text-align: center;
        font-weight: bold;
        padding-bottom: 20px;
    }

    /* Κάρτες Αποτελεσμάτων (Αναχώρηση) */
    .route-card {
        background-color: #ffffff !important;
        padding: 20px !important;
        border-radius: 15px !important;
        border-left: 12px solid #0056b3 !important;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1) !important;
        margin-bottom: 20px !important;
        color: #1a1a1a !important;
    }

    /* Κάρτες Αποτελεσμάτων (Επιστροφή) */
    .return-card {
        background-color: #ffffff !important;
        padding: 20px !important;
        border-radius: 15px !important;
        border-left: 12px solid #ff8c00 !important;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1) !important;
        margin-bottom: 20px !important;
        color: #1a1a1a !important;
    }

    .card-title {
        color: #003366 !important;
        font-size: 1.3rem !important;
        font-weight: bold !important;
        margin-bottom: 10px !important;
    }

    .card-detail {
        font-size: 1.1rem !important;
        line-height: 1.6 !important;
    }

    .highlight {
        color: #d32f2f !important;
        font-weight: bold !important;
        font-size: 1.2rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ΠΛΗΡΗ ΔΕΔΟΜΕΝΑ ΔΡΟΜΟΛΟΓΙΩΝ ΒΑΣΕΙ ΚΕΙΜΕΝΟΥ ---
RAW_ROUTES = [
    # ΑΘΗΝΑ (Άρθρο 10)
    {"from": "ΑΘΗΝΑ", "to": ["ΑΥΛΩΝΑΣ", "ΕΛΑΙΩΝΑΣ", "ΛΑΜΙΑ", "ΚΑΣΣΑΒΕΤΕΙΑ", "ΛΑΡΙΣΑ", "ΚΑΤΕΡΙΝΗ", "ΘΕΣΣΑΛΟΝΙΚΗ"], "days": [0, 3], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΚΟΡΙΝΘΟΣ", "ΝΑΥΠΛΙΟ", "ΤΥΡΙΝΘΑ", "ΤΡΙΠΟΛΗ", "ΚΑΛΑΜΑΤΑ"], "days": [2], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΧΑΛΚΙΔΑ"], "days": [1], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΑΥΛΩΝΑΣ", "ΕΛΑΙΩΝΑΣ", "ΛΑΜΙΑ", "ΤΡΙΚΑΛΑ", "ΓΡΕΒΕΝΑ"], "days": [0], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΧΑΝΙΑ", "ΗΡΑΚΛΕΙΟ", "ΡΕΘΥΜΝΟ", "ΛΑΣΙΘΙ", "ΝΗΣΙΑ"], "days": [4], "transit": 1},

    # ΘΕΣΣΑΛΟΝΙΚΗ (Άρθρο 11)
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": ["ΣΕΡΡΕΣ", "ΔΡΑΜΑ", "ΚΑΒΑΛΑ", "ΞΑΝΘΗ", "ΚΟΜΟΤΗΝΗ", "ΑΛΕΞΑΝΔΡΟΥΠΟΛΗ"], "days": [1, 4], "transit": 0},
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": ["ΒΕΡΟΙΑ", "ΚΟΖΑΝΗ", "ΓΡΕΒΕΝΑ", "ΙΩΑΝΝΙΝΑ"], "days": [0], "transit": 0},
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": ["ΔΡΑΜΑ", "ΣΕΡΡΕΣ"], "days": [3], "transit": 0},
    {"from": ["ΑΛΕΞΑΝΔΡΟΥΠΟΛΗ", "ΚΟΜΟΤΗΝΗ", "ΞΑΝΘΗ", "ΚΑΒΑΛΑ", "ΔΡΑΜΑ", "ΣΕΡΡΕΣ"], "to": ["ΘΕΣΣΑΛΟΝΙΚΗ"], "days": [2, 5], "transit": 0},

    # ΣΕΡΡΕΣ (Άρθρο 12)
    {"from": "ΣΕΡΡΕΣ", "to": ["ΘΕΣΣΑΛΟΝΙΚΗ"], "days": [0, 1], "transit": 0},
    
    # ΠΑΤΡΑ (Άρθρο 13)
    {"from": "ΠΑΤΡΑ", "to": ["ΑΙΓΙΟ", "ΞΥΛΟΚΑΣΤΡΟ", "ΚΙΑΤΟ", "ΚΟΡΙΝΘΟΣ", "ΑΘΗΝΑ"], "days": [0], "transit": 0},
    {"from": "ΠΑΤΡΑ", "to": ["ΑΡΓΟΛΙΔΑ", "ΜΕΣΣΗΝΙΑ"], "days": [1], "transit": 0},
    
    # ΑΓΡΙΝΙΟ (Άρθρο 14)
    {"from": "ΑΓΡΙΝΙΟ", "to": ["ΠΑΤΡΑ", "ΑΜΦΙΣΣΑ"], "days": [2], "transit": 0},
    {"from": "ΑΜΦΙΣΣΑ", "to": ["ΠΑΤΡΑ", "ΑΓΡΙΝΙΟ"], "days": [3], "transit": 0},

    # ΛΑΡΙΣΑ (Άρθρο 15)
    {"from": "ΛΑΡΙΣΑ", "to": ["ΚΑΣΣΑΒΕΤΕΙΑ", "ΛΑΜΙΑ", "ΕΛΑΙΩΝΑΣ", "ΑΥΛΩΝΑΣ", "ΑΘΗΝΑ"], "days": [3], "transit": 0},
    {"from": "ΛΑΡΙΣΑ", "to": ["ΒΟΛΟΣ"], "days": [0, 3], "transit": 0},
    {"from": "ΛΑΡΙΣΑ", "to": ["ΚΟΖΑΝΗ"], "days": [5], "transit": 0},

    # ΙΩΑΝΝΙΝΑ (Άρθρο 16)
    {"from": "ΙΩΑΝΝΙΝΑ", "to": ["ΑΡΤΑ", "ΑΓΡΙΝΙΟ", "ΠΑΤΡΑ", "ΑΙΓΙΟ", "ΚΟΡΙΝΘΟΣ", "ΑΘΗΝΑ"], "days": [1], "transit": 0},
    {"from": ["ΑΘΗΝΑ", "ΚΟΡΙΝΘΟΣ", "ΠΑΤΡΑ", "ΑΓΡΙΝΙΟ", "ΑΡΤΑ"], "to": ["ΙΩΑΝΝΙΝΑ"], "days": [2], "transit": 0},

    # ΓΡΕΒΕΝΑ (Άρθρο 17)
    {"from": "ΓΡΕΒΕΝΑ", "to": ["ΤΡΙΚΑΛΑ", "ΛΑΜΙΑ", "ΕΛΑΙΩΝΑΣ", "ΑΥΛΩΝΑΣ", "ΑΘΗΝΑ"], "days": [3], "transit": 0},

    # ΑΜΦΙΣΣΑ (Άρθρο 18)
    {"from": "ΑΜΦΙΣΣΑ", "to": ["ΛΑΜΙΑ"], "days": [0, 1, 3, 4], "transit": 0},
    {"from": "ΛΑΜΙΑ", "to": ["ΑΜΦΙΣΣΑ"], "days": [0, 1, 3, 4], "transit": 0},

    # ΕΠΙΣΤΡΟΦΕΣ / ΑΛΛΑ
    {"from": ["ΘΕΣΣΑΛΟΝΙΚΗ", "ΛΑΡΙΣΑ", "ΛΑΜΙΑ"], "to": ["ΑΘΗΝΑ"], "days": [1, 4], "transit": 0},
    {"from": "ΚΑΛΑΜΑΤΑ", "to": ["ΤΡΙΠΟΛΗ", "ΝΑΥΠΛΙΟ", "ΚΟΡΙΝΘΟΣ", "ΑΘΗΝΑ"], "days": [3], "transit": 0},
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
    return f"<b>{date.strftime('%d/%m/%Y')}</b> ({greek_day(date)})"

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
            if r["from"] == start:
                path = [current_leg]
            else:
                path_prefix = find_backward_path(start, r["from"], ship, depth + 1)
                path = path_prefix + [current_leg] if path_prefix else None
            if path:
                if best_path is None or path[0]["ship"] > best_path[0]["ship"]:
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
            if r["to"] == end:
                path = [current_leg]
            else:
                sub_path = find_forward_path(r["to"], end, arrive + timedelta(days=1), depth + 1)
                path = [current_leg] + sub_path if sub_path else None
            if path:
                if best_path is None or path[-1]["arrive"] < best_path[-1]["arrive"]:
                    best_path = path
    return best_path

# --- UI ---
st.title("🚌 Bus Route Planner")

with st.container():
    c1, c2, c3 = st.columns(3)
    with c1:
        origin = st.selectbox("📍 Αφετηρία:", ALL_CITIES, index=ALL_CITIES.index("ΣΕΡΡΕΣ"))
    with c2:
        dest = st.selectbox("🏁 Προορισμός:", ALL_CITIES, index=ALL_CITIES.index("ΑΘΗΝΑ"))
    with c3:
        d_date = st.date_input("📅 Παράδοση:", datetime.now() + timedelta(days=5))

st.markdown("<br>", unsafe_allow_html=True)

if st.button("🚀 Υπολογισμός"):
    res = find_backward_path(origin.upper(), dest.upper(), d_date)
    if res:
        st.session_state.update({'last_res': res, 'last_dest': dest, 'last_origin': origin, 'last_delivery': d_date})
        st.markdown(f"### 🗓️ Αναχώρηση: <span class='highlight'>{format_date_gr(res[0]['ship'])}</span>", unsafe_allow_html=True)
        for i, leg in enumerate(res):
            st.markdown(f"""<div class="route-card"><div class="card-title">🚌 Σκέλος {i+1}: {leg['from']} ➡️ {leg['to']}</div>
            <div class="card-detail">📅 Αναχώρηση: {format_date_gr(leg['ship'])} | 🏁 Άφιξη: {format_date_gr(leg['arrive'])}</div></div>""", unsafe_allow_html=True)
    else:
        st.error("Δεν βρέθηκε διαδρομή.")

if 'last_res' in st.session_state:
    st.markdown("<hr style='border-top: 2px solid #003366;'>", unsafe_allow_html=True)
    if st.button(f"🔄 Επιστροφή ({st.session_state['last_dest']} ➡️ {st.session_state['last_origin']})"):
        ret_res = find_forward_path(st.session_state['last_dest'].upper(), st.session_state['last_origin'].upper(), st.session_state['last_delivery'] + timedelta(days=1))
        if ret_res:
            st.markdown(f"### 🗓️ Επιστροφή: <span class='highlight'>{format_date_gr(ret_res[-1]['arrive'])}</span>", unsafe_allow_html=True)
            for i, leg in enumerate(ret_res):
                st.markdown(f"""<div class="return-card"><div class="card-title">🔄 Σκέλος {i+1}: {leg['from']} ➡️ {leg['to']}</div>
                <div class="card-detail">📅 Αναχώρηση: {format_date_gr(leg['ship'])} | 🏁 Άφιξη: {format_date_gr(leg['arrive'])}</div></div>""", unsafe_allow_html=True)
