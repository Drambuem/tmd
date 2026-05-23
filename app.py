import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(page_title="Logistics Planner PRO v1.4", layout="wide")

# --- ΔΕΔΟΜΕΝΑ ΔΡΟΜΟΛΟΓΙΩΝ ---
# 0:Δευ, 1:Τρι, 2:Τετ, 3:Πεμ, 4:Παρ, 5:Σαβ, 6:Κυρ

RAW_ROUTES = [
    # --- ΑΠΟ ΑΘΗΝΑ ---
    {"from": "ΑΘΗΝΑ", "to": ["ΑΥΛΩΝΑΣ", "ΕΛΑΙΩΝΑΣ", "ΛΑΜΙΑ", "ΚΑΣΣΑΒΕΤΕΙΑ", "ΛΑΡΙΣΑ", "ΚΑΤΕΡΙΝΗ", "ΘΕΣΣΑΛΟΝΙΚΗ"], "days": [0, 3], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΤΡΙΚΑΛΑ", "ΓΡΕΒΕΝΑ"], "days": [0], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΧΑΛΚΙΔΑ"], "days": [1], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΚΟΡΙΝΘΟΣ", "ΝΑΥΠΛΙΟ", "ΤΥΡΙΝΘΑ", "ΤΡΙΠΟΛΗ", "ΚΑΛΑΜΑΤΑ"], "days": [2], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΝΗΣΙΑ"], "days": [4], "transit": 1},

    # --- ΕΠΙΣΤΡΟΦΕΣ ΠΡΟΣ ΑΘΗΝΑ (Αντίστροφα την επόμενη ημέρα) ---
    {"from": ["ΘΕΣΣΑΛΟΝΙΚΗ", "ΚΑΤΕΡΙΝΗ", "ΛΑΡΙΣΑ", "ΚΑΣΣΑΒΕΤΕΙΑ", "ΛΑΜΙΑ", "ΕΛΑΙΩΝΑΣ", "ΑΥΛΩΝΑΣ"], "to": ["ΑΘΗΝΑ"], "days": [1, 4], "transit": 0},
    {"from": ["ΓΡΕΒΕΝΑ", "ΤΡΙΚΑΛΑ"], "to": ["ΑΘΗΝΑ"], "days": [1], "transit": 0},
    {"from": ["ΚΑΛΑΜΑΤΑ", "ΤΡΙΠΟΛΗ", "ΤΥΡΙΝΘΑ", "ΝΑΥΠΛΙΟ", "ΚΟΡΙΝΘΟΣ"], "to": ["ΑΘΗΝΑ"], "days": [3], "transit": 0},
    {"from": ["ΧΑΛΚΙΔΑ"], "to": ["ΑΘΗΝΑ"], "days": [1], "transit": 0},

    # --- ΑΠΟ ΘΕΣΣΑΛΟΝΙΚΗ ---
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": ["ΒΕΡΟΙΑ", "ΚΟΖΑΝΗ", "ΓΡΕΒΕΝΑ", "ΙΩΑΝΝΙΝΑ"], "days": [0], "transit": 0},
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": ["ΣΕΡΡΕΣ", "ΔΡΑΜΑ", "ΚΑΒΑΛΑ", "ΞΑΝΘΗ", "ΚΟΜΟΤΗΝΗ", "ΑΛΕΞΑΝΔΡΟΥΠΟΛΗ"], "days": [1, 4], "transit": 0},
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": ["ΔΡΑΜΑ", "ΣΕΡΡΕΣ"], "days": [3], "transit": 0}, # Το δρομολόγιο της Πέμπτης
    
    # --- ΕΠΙΣΤΡΟΦΕΣ ΠΡΟΣ ΘΕΣΣΑΛΟΝΙΚΗ ---
    {"from": ["ΙΩΑΝΝΙΝΑ", "ΓΡΕΒΕΝΑ", "ΚΟΖΑΝΗ", "ΒΕΡΟΙΑ"], "to": ["ΘΕΣΣΑΛΟΝΙΚΗ"], "days": [1], "transit": 0},
    {"from": ["ΑΛΕΞΑΝΔΡΟΥΠΟΛΗ", "ΚΟΜΟΤΗΝΗ", "ΞΑΝΘΗ", "ΚΑΒΑΛΑ", "ΔΡΑΜΑ", "ΣΕΡΡΕΣ"], "to": ["ΘΕΣΣΑΛΟΝΙΚΗ"], "days": [2, 5], "transit": 0},
    {"from": ["ΔΡΑΜΑ", "ΣΕΡΡΕΣ"], "to": ["ΘΕΣΣΑΛΟΝΙΚΗ"], "days": [3], "transit": 0}, # Επιστροφή Πέμπτης αυθημερόν

    # --- ΑΠΟ ΣΕΡΡΕΣ ---
    {"from": "ΣΕΡΡΕΣ", "to": ["ΘΕΣΣΑΛΟΝΙΚΗ"], "days": [0, 1], "transit": 0},
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": ["ΣΕΡΡΕΣ"], "days": [0, 1], "transit": 0}, # Σέρρες-Θεσ-Σέρρες

    # --- ΑΠΟ ΙΩΑΝΝΙΝΑ ΠΡΟΣ ΑΘΗΝΑ ---
    {"from": "ΙΩΑΝΝΙΝΑ", "to": ["ΑΡΤΑ", "ΑΓΡΙΝΙΟ", "ΠΑΤΡΑ", "ΑΙΓΙΟ", "ΚΟΡΙΝΘΟΣ", "ΑΘΗΝΑ"], "days": [1], "transit": 0},
    {"from": ["ΑΘΗΝΑ", "ΚΟΡΙΝΘΟΣ", "ΠΑΤΡΑ", "ΑΓΡΙΝΙΟ", "ΑΡΤΑ"], "to": ["ΙΩΑΝΝΙΝΑ"], "days": [2], "transit": 0},

    # --- ΑΠΟ ΠΑΤΡΑ ---
    {"from": "ΠΑΤΡΑ", "to": ["ΑΙΓΙΟ", "ΞΥΛΟΚΑΣΤΡΟ", "ΚΙΑΤΟ", "ΚΟΡΙΝΘΟΣ", "ΑΘΗΝΑ"], "days": [0], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΚΟΡΙΝΘΟΣ", "ΚΙΑΤΟ", "ΞΥΛΟΚΑΣΤΡΟ", "ΑΙΓΙΟ", "ΠΑΤΡΑ"], "days": [0], "transit": 0}, # Επιστροφή ίδια μέρα
    {"from": "ΠΑΤΡΑ", "to": ["ΑΡΓΟΛΙΔΑ"], "days": [1], "transit": 0},
    {"from": "ΑΡΓΟΛΙΔΑ", "to": ["ΠΑΤΡΑ"], "days": [1], "transit": 0},

    # --- ΛΟΙΠΑ ΤΟΠΙΚΑ ---
    {"from": "ΑΓΡΙΝΙΟ", "to": ["ΠΑΤΡΑ", "ΑΜΦΙΣΣΑ"], "days": [2], "transit": 0},
    {"from": ["ΠΑΤΡΑ", "ΑΜΦΙΣΣΑ"], "to": ["ΑΓΡΙΝΙΟ"], "days": [3], "transit": 0},
    {"from": "ΛΑΡΙΣΑ", "to": ["ΒΟΛΟΣ"], "days": [0, 3], "transit": 0},
    {"from": "ΒΟΛΟΣ", "to": ["ΛΑΡΙΣΑ"], "days": [0, 3], "transit": 0},
    {"from": "ΑΜΦΙΣΣΑ", "to": ["ΛΑΜΙΑ"], "days": [0, 1, 3, 4], "transit": 0},
    {"from": "ΛΑΜΙΑ", "to": ["ΑΜΦΙΣΣΑ"], "days": [0, 1, 3, 4], "transit": 0},
]

# Αναδομή των ROUTES για τον αλγόριθμο
ROUTES = []
for r in RAW_ROUTES:
    origins = [r["from"]] if isinstance(r["from"], str) else r["from"]
    destinations = r["to"] if isinstance(r["to"], list) else [r["to"]]
    for o in origins:
        for d in destinations:
            ROUTES.append({"from": o, "to": d, "days": r["days"], "transit": r["transit"]})

ALL_CITIES = sorted(list(set([r["from"] for r in ROUTES] + [r["to"] for r in ROUTES])))

def greek_day(date):
    days = ["Δευτέρα", "Τρίτη", "Τετάρτη", "Πέμπτη", "Παρασκευή", "Σάββατο", "Κυριακή"]
    return days[date.weekday()]

def find_best_path(current_city, target_city, deadline_date, depth=0):
    if depth > 3: return None
    best_full_path = None
    latest_arrival = deadline_date - timedelta(days=1)
    
    for r in ROUTES:
        if r["to"] == target_city:
            ship_date = latest_arrival - timedelta(days=r["transit"])
            while ship_date.weekday() not in r["days"]:
                ship_date -= timedelta(days=1)
            
            arrival_date = ship_date + timedelta(days=r["transit"])
            current_leg = {"from": r["from"], "to": r["to"], "ship": ship_date, "arrive": arrival_date}
            
            if r["from"] == current_city:
                return [current_leg]
            else:
                # Κανόνας ανταπόκρισης: Άφιξη τουλάχιστον 1 μέρα πριν την επόμενη αναχώρηση
                sub_path = find_best_path(current_city, r["from"], ship_date, depth + 1)
                if sub_path:
                    full_path = sub_path + [current_leg]
                    if best_full_path is None or full_path[0]["ship"] > best_full_path[0]["ship"]:
                        best_full_path = full_path
    return best_full_path

# --- UI ---
st.title("🚛 Logistics Planner PRO v1.4")
st.markdown(f"**Ενημέρωση:** Προστέθηκε το κυκλικό δρομολόγιο Θεσσαλονίκη-Δράμα-Σέρρες της Πέμπτης.")

c1, c2, c3 = st.columns(3)
with c1:
    start_city = st.selectbox("Από (Αφετηρία):", ALL_CITIES, index=ALL_CITIES.index("ΑΘΗΝΑ"))
with c2:
    end_city = st.selectbox("Προς (Προορισμός):", ALL_CITIES, index=ALL_CITIES.index("ΣΕΡΡΕΣ"))
with c3:
    target_date = st.date_input("Παράδοση στον Πελάτη:", datetime.now() + timedelta(days=5))

if st.button("🔍 Υπολογισμός"):
    if start_city == end_city:
        st.error("Η αφετηρία και ο προορισμός συμπίπτουν.")
    else:
        result_path = find_best_path(start_city, end_city, target_date)
        if result_path:
            st.success(f"### Αναχώρηση: {result_path[0]['ship'].strftime('%d/%m/%Y')} ({greek_day(result_path[0]['ship'])})")
            for i, leg in enumerate(result_path):
                with st.expander(f"Σκέλος {i+1}: {leg['from']} ➡️ {leg['to']}", expanded=True):
                    col_a, col_b = st.columns(2)
                    col_a.metric("Φορτώνει", leg['ship'].strftime('%d/%m/%Y'), greek_day(leg['ship']))
                    col_b.metric("Φτάνει", leg['arrive'].strftime('%d/%m/%Y'), greek_day(leg['arrive']))
            st.info(f"📦 **Τελική Παράδοση:** {target_date.strftime('%d/%m/%Y')}")
        else:
            st.error("Δεν βρέθηκε διαδρομή. Το σύστημα επιτρέπει μόνο δρομολόγια που συνδέονται μέσω Αθήνας/Θεσσαλονίκης ή απευθείας.")
