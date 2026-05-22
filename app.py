import streamlit as st
from datetime import datetime, timedelta

# Ρύθμιση σελίδας
st.set_page_config(page_title="Logistics Planner PRO", layout="wide")

# --- ΒΑΣΙΚΑ ΔΕΔΟΜΕΝΑ ΔΡΟΜΟΛΟΓΙΩΝ ---
# 0:Δευ, 1:Τρι, 2:Τετ, 3:Πεμ, 4:Παρ, 5:Σαβ, 6:Κυρ
DIRECT_ROUTES = [
    {"from": "ΑΘΗΝΑ", "to": "ΘΕΣΣΑΛΟΝΙΚΗ", "days": [0, 3], "transit": 1},
    {"from": "ΑΘΗΝΑ", "to": "ΛΑΡΙΣΑ", "days": [0, 3], "transit": 1},
    {"from": "ΑΘΗΝΑ", "to": "ΛΑΜΙΑ", "days": [0, 3], "transit": 1},
    {"from": "ΑΘΗΝΑ", "to": "ΤΡΙΚΑΛΑ", "days": [0], "transit": 1},
    {"from": "ΑΘΗΝΑ", "to": "ΓΡΕΒΕΝΑ", "days": [0], "transit": 1},
    {"from": "ΑΘΗΝΑ", "to": "ΧΑΛΚΙΔΑ", "days": [1], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": "ΚΟΡΙΝΘΟΣ", "days": [2], "transit": 1},
    {"from": "ΑΘΗΝΑ", "to": "ΚΑΛΑΜΑΤΑ", "days": [2], "transit": 1},
    {"from": "ΑΘΗΝΑ", "to": "ΤΡΙΠΟΛΗ", "days": [2], "transit": 1},
    {"from": "ΑΘΗΝΑ", "to": "ΝΗΣΙΑ", "days": [4], "transit": 2},
    
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": "ΙΩΑΝΝΙΝΑ", "days": [0], "transit": 1},
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": "ΚΟΖΑΝΗ", "days": [0], "transit": 1},
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": "ΑΛΕΞΑΝΔΡΟΥΠΟΛΗ", "days": [1, 4], "transit": 1},
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": "ΞΑΝΘΗ", "days": [1, 4], "transit": 1},
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": "ΣΕΡΡΕΣ", "days": [1, 3, 4], "transit": 0},
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": "ΑΘΗΝΑ", "days": [1, 4], "transit": 1}, # Επιστροφή από Αθήνα-Θεσ/νικη
    
    {"from": "ΣΕΡΡΕΣ", "to": "ΘΕΣΣΑΛΟΝΙΚΗ", "days": [0, 1], "transit": 0},
    
    {"from": "ΙΩΑΝΝΙΝΑ", "to": "ΑΘΗΝΑ", "days": [1], "transit": 1},
    {"from": "ΙΩΑΝΝΙΝΑ", "to": "ΠΑΤΡΑ", "days": [1], "transit": 1},
    
    {"from": "ΑΜΦΙΣΣΑ", "to": "ΛΑΜΙΑ", "days": [0, 1, 3, 4], "transit": 0},
    
    {"from": "ΠΑΤΡΑ", "to": "ΑΘΗΝΑ", "days": [0], "transit": 0},
    {"from": "ΠΑΤΡΑ", "to": "ΑΡΓΟΛΙΔΑ", "days": [1], "transit": 0},
    
    {"from": "ΑΓΡΙΝΙΟ", "to": "ΠΑΤΡΑ", "days": [2], "transit": 1},
    {"from": "ΑΓΡΙΝΙΟ", "to": "ΑΜΦΙΣΣΑ", "days": [2], "transit": 1},
    
    {"from": "ΛΑΡΙΣΑ", "to": "ΒΟΛΟΣ", "days": [0, 3], "transit": 0},
    {"from": "ΛΑΡΙΣΑ", "to": "ΑΘΗΝΑ", "days": [3], "transit": 1},
    
    {"from": "ΓΡΕΒΕΝΑ", "to": "ΑΘΗΝΑ", "days": [3], "transit": 1},
]

# Λίστα όλων των πόλεων για το μενού
ALL_CITIES = sorted(list(set([r["from"] for r in DIRECT_ROUTES] + [r["to"] for r in DIRECT_ROUTES])))

def greek_day(date):
    days = ["Δευτέρα", "Τρίτη", "Τετάρτη", "Πέμπτη", "Παρασκευή", "Σάββατο", "Κυριακή"]
    return days[date.weekday()]

# --- ΜΗΧΑΝΗ ΥΠΟΛΟΓΙΣΜΟΥ ---
def find_route(origin, destination, target_delivery_date):
    # 1. Επιθυμητή άφιξη στον προορισμό (1 μέρα πριν την παράδοση)
    target_arrival = target_delivery_date - timedelta(days=1)
    
    # 2. Έλεγχος για Απευθείας Δρομολόγιο
    for r in DIRECT_ROUTES:
        if r["from"] == origin and r["to"] == destination:
            # Πότε πρέπει να φύγει
            ship_date = target_arrival - timedelta(days=r["transit"])
            # Βρες την κοντινότερη προηγούμενη μέρα δρομολογίου
            while ship_date.weekday() not in r["days"]:
                ship_date -= timedelta(days=1)
            actual_arrival = ship_date + timedelta(days=r["transit"])
            return [{"from": origin, "to": destination, "ship": ship_date, "arrive": actual_arrival}]

    # 3. Έλεγχος για Δρομολόγιο μέσω Hub (Αθήνα ή Θεσσαλονίκη)
    # Δοκιμάζουμε αν η πόλη μπορεί να πάει Αθήνα/Θεσσαλονίκη και μετά στον προορισμό
    for hub in ["ΑΘΗΝΑ", "ΘΕΣΣΑΛΟΝΙΚΗ"]:
        leg2 = None
        leg1 = None
        
        # Ψάχνουμε το 2ο σκέλος: Hub -> Προορισμός
        for r in DIRECT_ROUTES:
            if r["from"] == hub and r["to"] == destination:
                leg2_ship = target_arrival - timedelta(days=r["transit"])
                while leg2_ship.weekday() not in r["days"]:
                    leg2_ship -= timedelta(days=1)
                leg2_arrive = leg2_ship + timedelta(days=r["transit"])
                leg2 = {"from": hub, "to": destination, "ship": leg2_ship, "arrive": leg2_arrive}
                break
        
        if leg2:
            # Ψάχνουμε το 1ο σκέλος: Αφετηρία -> Hub
            # Πρέπει να φτάσει στο Hub τουλάχιστον την ίδια μέρα που φεύγει το 2ο (πρωί)
            for r in DIRECT_ROUTES:
                if r["from"] == origin and r["to"] == hub:
                    leg1_ship = leg2["ship"] - timedelta(days=r["transit"])
                    while leg1_ship.weekday() not in r["days"]:
                        leg1_ship -= timedelta(days=1)
                    leg1_arrive = leg1_ship + timedelta(days=r["transit"])
                    leg1 = {"from": origin, "to": hub, "ship": leg1_ship, "arrive": leg1_arrive}
                    break
            
            if leg1 and leg2:
                return [leg1, leg2]

    return None

# --- UI ΕΦΑΡΜΟΓΗΣ ---
st.title("🚛 Σύστημα Προγραμματισμού Μεταφορών")
st.markdown("### Υπολογισμός Διαδρομής & Ανταποκρίσεων")

col1, col2, col3 = st.columns(3)

with col1:
    origin = st.selectbox("Από (Αφετηρία):", ALL_CITIES, index=ALL_CITIES.index("ΑΘΗΝΑ"))
with col2:
    dest = st.selectbox("Προς (Τελικός Προορισμός):", ALL_CITIES, index=ALL_CITIES.index("ΘΕΣΣΑΛΟΝΙΚΗ"))
with col3:
    delivery_date = st.date_input("Ημερομηνία Παράδοσης στον Πελάτη:", datetime.now() + timedelta(days=3))

if st.button("Υπολογισμός Δρομολογίου"):
    if origin == dest:
        st.error("Η αφετηρία και ο προορισμός είναι η ίδια πόλη!")
    else:
        path = find_route(origin, dest, delivery_date)
        
        if path:
            st.success(f"### Πρέπει να ξεκινήσει: {path[0]['ship'].strftime('%d/%m/%Y')} ({greek_day(path[0]['ship'])})")
            
            # Εμφάνιση Διαδρομής
            st.write("#### Αναλυτική Διαδρομή:")
            for i, leg in enumerate(path):
                st.info(f"**Σκέλος {i+1}:** {leg['from']} ➡️ {leg['to']}")
                st.write(f"📅 Αναχώρηση: {leg['ship'].strftime('%d/%m/%Y')} | 🏁 Άφιξη: {leg['arrive'].strftime('%d/%m/%Y')}")
            
            st.warning(f"📦 **Τελική Παράδοση στον προορισμό {dest}:** {delivery_date.strftime('%d/%m/%Y')} ({greek_day(delivery_date)})")
        else:
            st.error("Δεν βρέθηκε διαθέσιμη διαδρομή για αυτόν τον συνδυασμό πόλεων. Δοκιμάστε άλλη ημερομηνία ή επικοινωνήστε με το γραφείο κίνησης.")

st.sidebar.markdown("""
### Οδηγίες
1. Επιλέξτε την πόλη που έχετε το δέμα.
2. Επιλέξτε τον τελικό προορισμό.
3. Η εφαρμογή θα βρει αν υπάρχει απευθείας δρομολόγιο ή αν πρέπει να πάει μέσω **Αθήνας/Θεσσαλονίκης**.
4. Αν χρειάζεται ανταπόκριση, υπολογίζει αυτόματα τις ημέρες αναμονής στον κόμβο.
""")
