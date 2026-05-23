import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(page_title="Logistics Planner PRO v1.7", layout="wide")

# --- ΔΕΔΟΜΕΝΑ ΔΡΟΜΟΛΟΓΙΩΝ ---
RAW_ROUTES = [
    # ΑΠΟ ΑΘΗΝΑ
    {"from": "ΑΘΗΝΑ", "to": ["ΑΥΛΩΝΑΣ", "ΕΛΑΙΩΝΑΣ", "ΛΑΜΙΑ", "ΚΑΣΣΑΒΕΤΕΙΑ", "ΛΑΡΙΣΑ", "ΚΑΤΕΡΙΝΗ", "ΘΕΣΣΑΛΟΝΙΚΗ"], "days": [0, 3], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΤΡΙΚΑΛΑ", "ΓΡΕΒΕΝΑ"], "days": [0], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΧΑΛΚΙΔΑ"], "days": [1], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΚΟΡΙΝΘΟΣ", "ΝΑΥΠΛΙΟ", "ΤΥΡΙΝΘΑ", "ΤΡΙΠΟΛΗ", "ΚΑΛΑΜΑΤΑ"], "days": [2], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΝΗΣΙΑ"], "days": [4], "transit": 1},

    # ΕΠΙΣΤΡΟΦΕΣ ΠΡΟΣ ΑΘΗΝΑ
    {"from": ["ΘΕΣΣΑΛΟΝΙΚΗ", "ΚΑΤΕΡΙΝΗ", "ΛΑΡΙΣΑ", "ΚΑΣΣΑΒΕΤΕΙΑ", "ΛΑΜΙΑ", "ΕΛΑΙΩΝΑΣ", "ΑΥΛΩΝΑΣ"], "to": ["ΑΘΗΝΑ"], "days": [1, 4], "transit": 0},
    {"from": ["ΓΡΕΒΕΝΑ", "ΤΡΙΚΑΛΑ"], "to": ["ΑΘΗΝΑ"], "days": [1], "transit": 0},
    {"from": ["ΚΑΛΑΜΑΤΑ", "ΤΡΙΠΟΛΗ", "ΤΥΡΙΝΘΑ", "ΝΑΥΠΛΙΟ", "ΚΟΡΙΝΘΟΣ"], "to": ["ΑΘΗΝΑ"], "days": [3], "transit": 0},
    {"from": ["ΧΑΛΚΙΔΑ"], "to": ["ΑΘΗΝΑ"], "days": [1], "transit": 0},

    # ΑΠΟ ΘΕΣΣΑΛΟΝΙΚΗ
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": ["ΒΕΡΟΙΑ", "ΚΟΖΑΝΗ", "ΓΡΕΒΕΝΑ", "ΙΩΑΝΝΙΝΑ"], "days": [0], "transit": 0},
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": ["ΣΕΡΡΕΣ", "ΔΡΑΜΑ", "ΚΑΒΑΛΑ", "ΞΑΝΘΗ", "ΚΟΜΟΤΗΝΗ", "ΑΛΕΞΑΝΔΡΟΥΠΟΛΗ"], "days": [1, 4], "transit": 0},
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": ["ΔΡΑΜΑ", "ΣΕΡΡΕΣ"], "days": [3], "transit": 0}, 
    
    # ΕΠΙΣΤΡΟΦΕΣ ΠΡΟΣ ΘΕΣΣΑΛΟΝΙΚΗ
    {"from": ["ΙΩΑΝΝΙΝΑ", "ΓΡΕΒΕΝΑ", "ΚΟΖΑΝΗ", "ΒΕΡΟΙΑ"], "to": ["ΘΕΣΣΑΛΟΝΙΚΗ"], "days": [1], "transit": 0},
    {"from": ["ΑΛΕΞΑΝΔΡΟΥΠΟΛΗ", "ΚΟΜΟΤΗΝΗ", "ΞΑΝΘΗ", "ΚΑΒΑΛΑ", "ΔΡΑΜΑ", "ΣΕΡΡΕΣ"], "to": ["ΘΕΣΣΑΛΟΝΙΚΗ"], "days": [2, 5], "transit": 0},
    {"from": ["ΔΡΑΜΑ", "ΣΕΡΡΕΣ"], "to": ["ΘΕΣΣΑΛΟΝΙΚΗ"], "days": [3], "transit": 0},

    # ΑΠΟ ΣΕΡΡΕΣ
    {"from": "ΣΕΡΡΕΣ", "to": ["ΘΕΣΣΑΛΟΝΙΚΗ"], "days": [0, 1], "transit": 0},
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": ["ΣΕΡΡΕΣ"], "days": [0, 1], "transit": 0},

    # ΑΠΟ ΙΩΑΝΝΙΝΑ / ΠΑΤΡΑ / ΑΛΛΑ
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

# --- ΜΗΧΑΝΗ BACKWARD (ΑΝΑΧΩΡΗΣΗ) ---
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

# --- ΜΗΧΑΝΗ FORWARD (ΕΠΙΣΤΡΟΦΗ) ---
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
st.title("🚛 Logistics Planner PRO v1.7")

col1, col2, col3 = st.columns(3)
with col1:
    def_origin = "ΣΕΡΡΕΣ" if "ΣΕΡΡΕΣ" in ALL_CITIES else ALL_CITIES[0]
    origin = st.selectbox("Από (Αφετηρία):", ALL_CITIES, index=ALL_CITIES.index(def_origin))
with col2:
    def_dest = "ΑΘΗΝΑ" if "ΑΘΗΝΑ" in ALL_CITIES else ALL_CITIES[0]
    dest = st.selectbox("Προς (Προορισμός):", ALL_CITIES, index=ALL_CITIES.index(def_dest))
with col3:
    d_date = st.date_input("Ημερομηνία Παράδοσης:", datetime.now() + timedelta(days=5))

if st.button("🔍 Υπολογισμός Διαδρομής"):
    res = find_backward_path(origin.upper(), dest.upper(), d_date)
    if res:
        st.session_state['last_res'] = res
        st.session_state['last_dest'] = dest
        st.session_state['last_origin'] = origin
        st.session_state['last_delivery'] = d_date
        
        st.success(f"### Αναχώρηση: {res[0]['ship'].strftime('%d/%m/%Y')} ({greek_day(res[0]['ship'])})")
        for i, leg in enumerate(res):
            with st.expander(f"Σκέλος {i+1}: {leg['from']} ➡️ {leg['to']}", expanded=True):
                c_a, c_b = st.columns(2)
                c_a.write(f"**Αναχώρηση:** {leg['ship'].strftime('%d/%m/%Y')}")
                c_b.write(f"**Άφιξη:** {leg['arrive'].strftime('%d/%m/%Y')}")
    else:
        st.error("Δεν βρέθηκε διαδρομή.")

if 'last_res' in st.session_state:
    st.write("---")
    if st.button(f"🔄 Υπολογισμός Επιστροφής ({st.session_state['last_dest']} ➡️ {st.session_state['last_origin']})"):
        ret_start = st.session_state['last_delivery'] + timedelta(days=1)
        ret_res = find_forward_path(st.session_state['last_dest'].upper(), st.session_state['last_origin'].upper(), ret_start)
        
        if ret_res:
            arr_date = ret_res[-1]['arrive'].strftime('%d/%m/%Y')
            st.success(f"### Επιστροφή στην έδρα: {arr_date}")
            for i, leg in enumerate(ret_res):
                st.info(f"Σκέλος {i+1}: {leg['from']} -> {leg['to']} | Αναχώρηση: {leg['ship'].strftime('%d/%m/%Y')} | Άφιξη: {leg['arrive'].strftime('%d/%m/%Y')}")
        else:
            st.error("Δεν βρέθηκε διαδρομή επιστροφής.")
