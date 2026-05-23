import streamlit as st
from datetime import datetime, timedelta

# Ρύθμιση σελίδας και Εικονιδίου
st.set_page_config(page_title="Bus Logistics Planner", page_icon="🚌", layout="wide")

# --- CUSTOM CSS ΓΙΑ ΕΜΦΑΝΙΣΗ ---
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #004a99;
        color: white;
        font-weight: bold;
    }
    .stExpander {
        background-color: white;
        border: 1px solid #ddd;
        border-radius: 10px;
    }
    .reportview-container .main .block-container {
        padding-top: 2rem;
    }
    h1 {
        color: #004a99;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ΔΕΔΟΜΕΝΑ ΔΡΟΜΟΛΟΓΙΩΝ ---
RAW_ROUTES = [
    {"from": "ΑΘΗΝΑ", "to": ["ΑΥΛΩΝΑΣ", "ΕΛΑΙΩΝΑΣ", "ΛΑΜΙΑ", "ΚΑΣΣΑΒΕΤΕΙΑ", "ΛΑΡΙΣΑ", "ΚΑΤΕΡΙΝΗ", "ΘΕΣΣΑΛΟΝΙΚΗ"], "days": [0, 3], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΤΡΙΚΑΛΑ", "ΓΡΕΒΕΝΑ"], "days": [0], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΧΑΛΚΙΔΑ"], "days": [1], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΚΟΡΙΝΘΟΣ", "ΝΑΥΠΛΙΟ", "ΤΥΡΙΝΘΑ", "ΤΡΙΠΟΛΗ", "ΚΑΛΑΜΑΤΑ"], "days": [2], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΝΗΣΙΑ"], "days": [4], "transit": 1},
    {"from": ["ΘΕΣΣΑΛΟΝΙΚΗ", "ΚΑΤΕΡΙΝΗ", "ΛΑΡΙΣΑ", "ΚΑΣΣΑΒΕΤΕΙΑ", "ΛΑΜΙΑ", "ΕΛΑΙΩΝΑΣ", "ΑΥΛΩΝΑΣ"], "to": ["ΑΘΗΝΑ"], "days": [1, 4], "transit": 0},
    {"from": ["ΓΡΕΒΕΝΑ", "ΤΡΙΚΑΛΑ"], "to": ["ΑΘΗΝΑ"], "days": [1], "transit": 0},
    {"from": ["ΚΑΛΑΜΑΤΑ", "ΤΡΙΠΟΛΗ", "ΤΥΡΙΝΘΑ", "ΝΑΥΠΛΙΟ", "ΚΟΡΙΝΘΟΣ"], "to": ["ΑΘΗΝΑ"], "days": [3], "transit": 0},
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": ["ΒΕΡΟΙΑ", "ΚΟΖΑΝΗ", "ΓΡΕΒΕΝΑ", "ΙΩΑΝΝΙΝΑ"], "days": [0], "transit": 0},
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": ["ΣΕΡΡΕΣ", "ΔΡΑΜΑ", "ΚΑΒΑΛΑ", "ΞΑΝΘΗ", "ΚΟΜΟΤΗΝΗ", "ΑΛΕΞΑΝΔΡΟΥΠΟΛΗ"], "days": [1, 4], "transit": 0},
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": ["ΔΡΑΜΑ", "ΣΕΡΡΕΣ"], "days": [3], "transit": 0},
    {"from": ["ΑΛΕΞΑΝΔΡΟΥΠΟΛΗ", "ΚΟΜΟΤΗΝΗ", "ΞΑΝΘΗ", "ΚΑΒΑΛΑ", "ΔΡΑΜΑ", "ΣΕΡΡΕΣ"], "to": ["ΘΕΣΣΑΛΟΝΙΚΗ"], "days": [2, 5], "transit": 0},
    {"from": "ΣΕΡΡΕΣ", "to": ["ΘΕΣΣΑΛΟΝΙΚΗ"], "days": [0, 1], "transit": 0},
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": ["ΣΕΡΡΕΣ"], "days": [0, 1], "transit": 0},
    {"from": "ΙΩΑΝΝΙΝΑ", "to": ["ΑΡΤΑ", "ΑΓΡΙΝΙΟ", "ΠΑΤΡΑ", "ΑΙΓΙΟ", "ΚΟΡΙΝΘΟΣ", "ΑΘΗΝΑ"], "days": [1], "transit": 0},
    {"from": "ΠΑΤΡΑ", "to": ["ΑΙΓΙΟ", "ΞΥΛΟΚΑΣΤΡΟ", "ΚΙΑΤΟ", "ΚΟΡΙΝΘΟΣ", "ΑΘΗΝΑ"], "days": [0], "transit": 0},
    {"from": "ΠΑΤΡΑ", "to": ["ΑΡΓΟΛΙΔΑ"], "days": [1], "transit": 0},
    {"from": "ΑΓΡΙΝΙΟ", "to": ["ΠΑΤΡΑ", "ΑΜΦΙΣΣΑ"], "days": [2], "transit": 0},
    {"from": ["ΠΑΤΡΑ", "ΑΜΦΙΣΣΑ"], "to": ["ΑΓΡΙΝΙΟ"], "days": [3], "transit": 0},
    {"from": "ΛΑΡΙΣΑ", "to": ["ΒΟΛΟΣ"], "days": [0, 3], "transit": 0},
    {"from": "ΑΜΦΙΣΣΑ", "to": ["ΛΑΜΙΑ"], "days": [0, 1, 3, 4], "transit": 0},
    {"from": "ΛΑΜΙΑ", "to": ["ΑΜΦΙΣΣΑ"], "days": [0, 1, 3, 4], "transit": 0},
    {"from": "ΓΡΕΒΕΝΑ", "to": ["ΤΡΙΚΑΛΑ", "ΛΑΜΙΑ", "ΑΥΛΩΝΑΣ", "ΑΘΗΝΑ"], "days": [3], "transit": 0},
]

ROUTES = []
for r in RAW_ROUTES:
    origins = [r["from"]] if isinstance(r["from"], str) else r["from"]
    destinations = r["to"] if isinstance(r["to"], list) else [r["to"]]
    for o in origins:
        for d in destinations:
            ROUTES.append({"from": o.upper(), "to": d.upper(), "days": r["days"], "transit": r["transit"]})

ALL_CITIES = sorted(list(set([r["from"] for r in ROUTES] + [r["to"] for r in ROUTES])))

def greek_day(date):
    days = ["Δευτέρα", "Τρίτη", "Τετάρτη", "Πέμπτη", "Παρασκευή", "Σάββατο", "Κυριακή"]
    return days[date.weekday()]

def format_date_gr(date):
    return f"{date.strftime('%d/%m/%Y')} ({greek_day(date)})"

# --- ΜΗΧΑΝΕΣ ΑΝΑΖΗΤΗΣΗΣ ---
def find_backward_path(start, end, deadline, depth=0):
    if depth > 4: return None
    target_arrival = deadline - timedelta(days=1)
    best_path = None
    for r in ROUTES:
        if r["to"] == end:
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
                sub_path = find_backward_path(start, r["from"], ship, depth + 1)
                path = sub_path + [current_leg] if sub_path else None
            if path:
                if best_path is None or path[0]["ship"] > best_path[0]["ship"]:
                    best_path = path
    return best_path

def find_forward_path(start, end, start_date, depth=0):
    if depth > 4: return None
    best_path = None
    for r in ROUTES:
        if r["from"] == start:
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
st.markdown("---")

c1, c2, c3 = st.columns(3)
with c1:
    origin = st.selectbox("📍 Αφετηρία:", ALL_CITIES, index=ALL_CITIES.index("ΣΕΡΡΕΣ"))
with c2:
    dest = st.selectbox("🏁 Προορισμός:", ALL_CITIES, index=ALL_CITIES.index("ΑΘΗΝΑ"))
with c3:
    d_date = st.date_input("📅 Ημερομηνία Παράδοσης:", datetime.now() + timedelta(days=5))

if st.button("🔍 Υπολογισμός Δρομολογίου"):
    res = find_backward_path(origin.upper(), dest.upper(), d_date)
    if res:
        st.session_state['last_res'] = res
        st.session_state['last_dest'] = dest
        st.session_state['last_origin'] = origin
        st.session_state['last_delivery'] = d_date
        
        st.markdown(f"### 🗓️ Πρέπει να ξεκινήσει: **{format_date_gr(res[0]['ship'])}**")
        
        for i, leg in enumerate(res):
            with st.container():
                st.markdown(f"""
                <div style="background-color: white; padding: 15px; border-radius: 10px; border-left: 5px solid #004a99; margin-bottom: 10px;">
                    <h4 style="margin:0;">Σκέλος {i+1}: {leg['from']} ➡️ {leg['to']}</h4>
                    <p style="margin:0;">📅 Αναχώρηση: {format_date_gr(leg['ship'])}</p>
                    <p style="margin:0;">🏁 Άφιξη: {format_date_gr(leg['arrive'])}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.error("Δεν βρέθηκε διαθέσιμη διαδρομή.")

if 'last_res' in st.session_state:
    st.markdown("---")
    if st.button(f"🔄 Υπολογισμός Επιστροφής ({st.session_state['last_dest']} ➡️ {st.session_state['last_origin']})"):
        ret_start = st.session_state['last_delivery'] + timedelta(days=1)
        ret_res = find_forward_path(st.session_state['last_dest'].upper(), st.session_state['last_origin'].upper(), ret_start)
        
        if ret_res:
            st.markdown(f"### 🗓️ Επιστροφή στην έδρα: **{format_date_gr(ret_res[-1]['arrive'])}**")
            for i, leg in enumerate(ret_res):
                st.markdown(f"""
                <div style="background-color: #fff4e6; padding: 15px; border-radius: 10px; border-left: 5px solid #ff9900; margin-bottom: 10px;">
                    <h4 style="margin:0;">Σκέλος {i+1}: {leg['from']} ➡️ {leg['to']}</h4>
                    <p style="margin:0;">📅 Αναχώρηση: {format_date_gr(leg['ship'])}</p>
                    <p style="margin:0;">🏁 Άφιξη: {format_date_gr(leg['arrive'])}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error("Δεν βρέθηκε διαδρομή επιστροφής.")
