import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(page_title="Logistics Planner PRO v1.6", layout="wide")

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

# --- ΜΗΧΑΝΗ BACKWARD (ΓΙΑ ΑΝΑΧΩΡΗΣΗ) ---
def find_backward_path(start, end, deadline, depth=0):
    if depth > 4: return None
    target_arrival = deadline - timedelta(days=1)
    best_path = None

    for r in ROUTES:
        if r["to"] == end:
            ship = target_arrival - timedelta(days=r["transit"])
            # Πηγαίνουμε πίσω μέχρι να βρούμε μέρα δρομολογίου
            tries = 0
            while ship.weekday() not in r["days"] and tries < 14:
                ship -= timedelta(days=1)
                tries += 1
            
            arrive = ship + timedelta(days=r["transit"])
            current_leg = {"from": r["from"], "to": r["to"], "ship": ship, "arrive": arrive}
            
            if r["from"] == start:
                path = [current_leg]
            else:
                # Ανταπόκριση: Πρέπει να έχει φτάσει τουλάχιστον 1 μέρα ΠΡΙΝ το ship
                path_prefix = find_backward_path(start, r["from"], ship, depth + 1)
                path = path_prefix + [current_leg] if path_prefix else None
            
            if path:
                # Επιλέγουμε τη διαδρομή που ξεκινάει όσο το δυνατόν αργότερα
                if best_path is None or path[0]["ship"] > best_path[0]["ship"]:
                    best_path = path
    return best_path

# --- ΜΗΧΑΝΗ FORWARD (ΓΙΑ ΕΠΙΣΤΡΟΦΗ) ---
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
                # Ανταπόκριση: Φεύγει τουλάχιστον 1 μέρα ΜΕΤΑ την άφιξη
                path_suffix = find_forward_path(r["to"], end, arrive + timedelta(days=1), depth + 1)
                path = [current_leg] + path_suffix if path_suffix else None
            
            if path:
                if best_path is None or path[-1]["arrive"] < best_path[-1]["arrive"]:
                    best_path = path
    return best_path

# --- UI ---
st.title("🚛 Logistics Planner PRO v1.6")

col1, col2, col3 = st.columns(3)
with col1:
    # ΠΡΟΕΠΙΛΟΓΗ: ΣΕΡΡΕΣ
    default_origin = "ΣΕΡΡΕΣ" if "ΣΕΡΡΕΣ" in ALL_CITIES else ALL_CITIES[0]
    origin = st.selectbox("Από (Αφετηρία):", ALL
