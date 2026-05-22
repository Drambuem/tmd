import streamlit as st
from datetime import datetime, timedelta

# Ρύθμιση σελίδας
st.set_page_config(page_title="Logistics Planner PRO v1.3", layout="wide")

# --- ΔΕΔΟΜΕΝΑ ΔΡΟΜΟΛΟΓΙΩΝ ---
# 0:Δευ, 1:Τρι, 2:Τετ, 3:Πεμ, 4:Παρ, 5:Σαβ, 6:Κυρ

RAW_ROUTES = [
    # ΑΠΟ ΑΘΗΝΑ (Όλα αυθημερόν - Transit 0)
    {"from": "ΑΘΗΝΑ", "to": ["ΑΥΛΩΝΑΣ", "ΕΛΑΙΩΝΑΣ", "ΛΑΜΙΑ", "ΚΑΣΣΑΒΕΤΕΙΑ", "ΛΑΡΙΣΑ", "ΚΑΤΕΡΙΝΗ", "ΘΕΣΣΑΛΟΝΙΚΗ"], "days": [0, 3], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΤΡΙΚΑΛΑ", "ΓΡΕΒΕΝΑ"], "days": [0], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΧΑΛΚΙΔΑ"], "days": [1], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΚΟΡΙΝΘΟΣ", "ΝΑΥΠΛΙΟ", "ΤΥΡΙΝΘΑ", "ΤΡΙΠΟΛΗ", "ΚΑΛΑΜΑΤΑ"], "days": [2], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΝΗΣΙΑ"], "days": [4], "transit": 1}, # Τα νησιά παραμένουν +1 ημέρα για ασφάλεια
    
    # ΑΠΟ ΘΕΣΣΑΛΟΝΙΚΗ (Όλα αυθημερόν - Transit 0)
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": ["ΑΥΛΩΝΑΣ", "ΕΛΑΙΩΝΑΣ", "ΛΑΜΙΑ", "ΚΑΣΣΑΒΕΤΕΙΑ", "ΛΑΡΙΣΑ", "ΚΑΤΕΡΙΝΗ", "ΑΘΗΝΑ"], "days": [1, 4], "transit": 0},
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": ["ΒΕΡΟΙΑ", "ΚΟΖΑΝΗ", "ΓΡΕΒΕΝΑ", "ΙΩΑΝΝΙΝΑ"], "days": [0], "transit": 0},
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": ["ΣΕΡΡΕΣ", "ΔΡΑΜΑ", "ΚΑΒΑΛΑ", "ΞΑΝΘΗ", "ΚΟΜΟΤΗΝΗ", "ΑΛΕΞΑΝΔΡΟΥΠΟΛΗ"], "days": [1, 4], "transit": 0},
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": ["ΔΡΑΜΑ", "ΣΕΡΡΕΣ"], "days": [3], "transit": 0},
    
    # ΑΠΟ ΣΕΡΡΕΣ
    {"from": "ΣΕΡΡΕΣ", "to": ["ΘΕΣΣΑΛΟΝΙΚΗ"], "days": [0, 1], "transit": 0},
    
    # ΑΠΟ ΙΩΑΝΝΙΝΑ
    {"from": "ΙΩΑΝΝΙΝΑ", "to": ["ΑΡΤΑ", "ΑΓΡΙΝΙΟ", "ΠΑΤΡΑ", "ΑΙΓΙΟ", "ΚΟΡΙΝΘΟΣ", "ΑΘΗΝΑ"], "days": [1], "transit": 0},
    {"from": "ΙΩΑΝΝΙΝΑ", "to": ["ΓΡΕΒΕΝΑ", "ΚΟΖΑΝΗ", "ΒΕΡΟΙΑ", "ΘΕΣΣΑΛΟΝΙΚΗ"], "days": [2], "transit": 0},
    
    # ΑΠΟ ΑΜΦΙΣΣΑ
    {"from": "ΑΜΦΙΣΣΑ", "to": ["ΛΑΜΙΑ"], "days": [0, 1, 3, 4], "transit": 0},
    
    # ΑΠΟ ΠΑΤΡΑ
    {"from": "ΠΑΤΡΑ", "to": ["ΑΙΓΙΟ", "ΞΥΛΟΚΑΣΤΡΟ", "ΚΙΑΤΟ", "ΚΟΡΙΝΘΟΣ", "ΑΘΗΝΑ"], "days": [0], "transit": 0},
    {"from": "ΠΑΤΡΑ", "to": ["ΑΡΓΟΛΙΔΑ"], "days": [1], "transit": 0},
    {"from": "ΠΑΤΡΑ", "to": ["ΑΡΤΑ", "ΑΓΡΙΝΙΟ", "ΙΩΑΝΝΙΝΑ"], "days": [1], "transit": 0},
    
    # ΑΠΟ ΑΓΡΙΝΙΟ
    {"from": "ΑΓΡΙΝΙΟ", "to": ["ΠΑΤΡΑ", "ΑΜΦΙΣΣΑ"], "days": [2], "transit": 0},
    
    # ΑΠΟ ΛΑΡΙΣΑ
    {"from": "ΛΑΡΙΣΑ", "to": ["ΒΟΛΟΣ"], "days": [0, 3], "transit": 0},
    {"from": "ΛΑΡΙΣΑ", "to": ["ΚΑΣΣΑΒΕΤΕΙΑ", "ΛΑΜΙΑ", "ΕΛΑΙΩΝΑΣ", "ΑΥΛΩΝΑ", "ΑΘΗΝΑ"], "days": [3], "transit": 0},
    
    # ΑΠΟ ΓΡΕΒΕΝΑ
    {"from": "ΓΡΕΒΕΝΑ", "to": ["ΤΡΙΚΑΛΑ", "ΛΑΜΙΑ", "ΕΛΑΙΩΝΑΣ", "ΑΥΛΩΝΑ", "ΑΘΗΝΑ"], "days": [3], "transit": 0},
]

# Προετοιμασία λίστας ROUTES
ROUTES = []
for r in RAW_ROUTES:
    for target in r["to"]:
        ROUTES.append({
            "from": r["from"],
            "to": target,
            "days": r["days"],
            "transit": r["transit"]
        })

ALL_CITIES = sorted(list(set([r["from"] for r in ROUTES] + [r["to"] for r in ROUTES])))

def greek_day(date):
    days = ["Δευτέρα", "Τρίτη", "Τετάρτη", "Πέμπτη", "Παρασκευή", "Σάββατο", "Κυριακή"]
    return days[date.weekday()]

# --- ΜΗΧΑΝΗ ΑΝΑΖΗΤΗΣΗΣ ---
def find_best_path(current_city, target_city, deadline_date, depth=0):
    if depth > 3: 
        return None
    
    best_full_path = None
    
    # Στόχος: Το δέμα να είναι στον προορισμό 1 μέρα πριν την παράδοση
    latest_arrival = deadline_date - timedelta(days=1)
    
    for r in ROUTES:
        if r["to"] == target_city:
            ship_date = latest_arrival - timedelta(days=r["transit"])
            while ship_date.weekday() not in r["days"]:
                ship_date -= timedelta(days=1)
            
            arrival_date = ship_date + timedelta(days=r["transit"])
            
            current_leg = {
                "from": r["from"],
                "to": r["to"],
                "ship": ship_date,
                "arrive": arrival_date
            }
            
            if r["from"] == current_city:
                return [current_leg]
            else:
                # Για ανταπόκριση: Πρέπει να έχει φτάσει στον κόμβο
                # τουλάχιστον 1 ημέρα ΠΡΙΝ φύγει το επόμενο φορτηγό.
                sub_path = find_best_path(current_city, r["from"], ship_date, depth + 1)
                
                if sub_path:
                    full_path = sub_path + [current_leg]
                    if best_full_path is None or full_path[0]["ship"] > best_full_path[0]["ship"]:
                        best_full_path = full_path
                        
    return best_full_path

# --- UI ---
st.title("🚛 Logistics Planner PRO v1.3")
st.info("Όλα τα δρομολόγια εκτελούνται αυθημερόν. Οι ανταποκρίσεις απαιτούν 1 ημέρα παραμονή στον κόμβο.")

c1, c2, c3 = st.columns(3)
with c1:
    start_city = st.selectbox("Αφετηρία:", ALL_CITIES, index=ALL_CITIES.index("ΣΕΡΡΕΣ"))
with c2:
    end_city = st.selectbox("Προορισμός:", ALL_CITIES, index=ALL_CITIES.index("ΑΘΗΝΑ"))
with c3:
    target_date = st.date_input("Ημερομηνία Παράδοσης:", datetime.now() + timedelta(days=5))

if st.button("🔍 Υπολογισμός"):
    result_path = find_best_path(start_city, end_city, target_date)
    
    if result_path:
        st.success(f"### Αναχώρηση: {result_path[0]['ship'].strftime('%d/%m/%Y')} ({greek_day(result_path[0]['ship'])})")
        
        for i, leg in enumerate(result_path):
            with st.expander(f"Σκέλος {i+1}: {leg['from']} ➡️ {leg['to']}", expanded=True):
                col_a, col_b = st.columns(2)
                col_a.metric("Φορτώνει", leg['ship'].strftime('%d/%m/%Y'), greek_day(leg['ship']))
                col_b.metric("Φτάνει", leg['arrive'].strftime('%d/%m/%Y'), greek_day(leg['arrive']))
        
        st.warning(f"📦 **Τελική Παράδοση στον Πελάτη:** {target_date.strftime('%d/%m/%Y')}")
    else:
        st.error("Δεν βρέθηκε διαδρομή.")
