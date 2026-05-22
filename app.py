import streamlit as st
from datetime import datetime, timedelta

# Ρύθμιση σελίδας
st.set_page_config(page_title="Logistics Planner", layout="centered")

# --- ΔΕΔΟΜΕΝΑ ΔΡΟΜΟΛΟΓΙΩΝ ---
# 0:Δευτέρα, 1:Τρίτη, 2:Τετάρτη, 3:Πέμπτη, 4:Παρασκευή, 5:Σάββατο, 6:Κυριακή
ROUTES = {
    "ΑΘΗΝΑ": {
        "ΘΕΣΣΑΛΟΝΙΚΗ-ΒΟΡΕΙΑ (Λαμία, Λάρισα, Κατερίνη κλπ)": {"days": [0, 3], "transit": 1},
        "ΤΡΙΚΑΛΑ-ΓΡΕΒΕΝΑ": {"days": [0], "transit": 1},
        "ΧΑΛΚΙΔΑ": {"days": [1], "transit": 0},
        "ΠΕΛΟΠΟΝΝΗΣΟΣ (Κόρινθος, Ναύπλιο, Τρίπολη, Καλαμάτα)": {"days": [2], "transit": 1},
        "ΝΗΣΙΑ": {"days": [4], "transit": 2},
    },
    "ΘΕΣΣΑΛΟΝΙΚΗ": {
        "ΔΥΤ. ΜΑΚΕΔΟΝΙΑ-ΗΠΕΙΡΟΣ (Κοζάνη, Γρεβενά, Ιωάννινα)": {"days": [0], "transit": 1},
        "ΑΝΑΤ. ΜΑΚΕΔΟΝΙΑ-ΘΡΑΚΗ (Σέρρες, Δράμα, Ξάνθη, Έβρος)": {"days": [1, 4], "transit": 1},
        "ΣΕΡΡΕΣ-ΔΡΑΜΑ (Τοπικό)": {"days": [3], "transit": 0},
    },
    "ΣΕΡΡΕΣ": {
        "ΘΕΣΣΑΛΟΝΙΚΗ": {"days": [0, 1], "transit": 0},
    },
    "ΙΩΑΝΝΙΝΑ": {
        "ΔΥΤ. ΕΛΛΑΔΑ-ΑΘΗΝΑ (Άρτα, Αγρίνιο, Πάτρα, Κόρινθος)": {"days": [1], "transit": 1},
    },
    "ΑΜΦΙΣΣΑ": {
        "ΛΑΜΙΑ": {"days": [0, 1, 3, 4], "transit": 0},
    },
    "ΠΑΤΡΑ": {
        "ΑΘΗΝΑ (Μέσω Κορίνθου)": {"days": [0], "transit": 0},
        "ΑΡΓΟΛΙΔΑ": {"days": [1], "transit": 0},
    },
    "ΑΓΡΙΝΙΟ": {
        "ΠΑΤΡΑ-ΑΜΦΙΣΣΑ": {"days": [2], "transit": 1},
    },
    "ΛΑΡΙΣΑ": {
        "ΒΟΛΟΣ": {"days": [0, 3], "transit": 0},
        "ΑΘΗΝΑ (Νότια Διαδρομή)": {"days": [3], "transit": 1},
    },
    "ΓΡΕΒΕΝΑ": {
        "ΤΡΙΚΑΛΑ-ΛΑΜΙΑ-ΑΘΗΝΑ": {"days": [3], "transit": 1},
    }
}

# --- ΛΟΓΙΚΗ ΥΠΟΛΟΓΙΣΜΟΥ ---
def calculate_shipment(origin, route_key, delivery_date):
    route = ROUTES[origin][route_key]
    transit = route["transit"]
    available_days = route["days"]
    
    # Στόχος: Να είναι εκεί την προηγούμενη (delivery_date - 1)
    target_arrival = delivery_date - timedelta(days=1)
    
    # Ξεκινάμε από την ημέρα που "θα έπρεπε" να φτάσει και πάμε προς τα πίσω
    # μέχρι να βρούμε μέρα που έχει δρομολόγιο
    check_date = target_arrival - timedelta(days=transit)
    
    found = False
    # Ψάχνουμε στις τελευταίες 14 ημέρες για σιγουριά
    for _ in range(14):
        if check_date.weekday() in available_days:
            found = True
            break
        check_date -= timedelta(days=1)
    
    if found:
        actual_arrival = check_date + timedelta(days=transit)
        return check_date, actual_arrival
    return None, None

# --- INTERFACE ΕΦΑΡΜΟΓΗΣ ---
st.title("🚛 Προγραμματιστής Μεταφορών")
st.write("Υπολογίστε πότε πρέπει να ξεκινήσει ένα δέμα για να φτάσει στην ώρα του.")

# 1. Επιλογή Αφετηρίας
origin = st.selectbox("Από πού ξεκινάει το δέμα;", list(ROUTES.keys()))

# 2. Επιλογή Διαδρομής
available_routes = list(ROUTES[origin].keys())
route_selection = st.selectbox("Προς ποια κατεύθυνση/διαδρομή;", available_routes)

# 3. Επιλογή Ημερομηνίας Παράδοσης
delivery_date = st.date_input("Πότε πρέπει να γίνει η παράδοση στον τελικό προορισμό;", min_value=datetime.now())

# 4. Κουμπί Υπολογισμού
if st.button("Υπολογισμός Αναχώρησης"):
    ship_date, arrival_date = calculate_shipment(origin, route_selection, delivery_date)
    
    if ship_date:
        st.success(f"### Πρέπει να φύγει στις: **{ship_date.strftime('%d/%m/%Y')} ({greek_day(ship_date)})**")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Άφιξη στην Πόλη:**\n{arrival_date.strftime('%d/%m/%Y')}")
        with col2:
            st.warning(f"**Παράδοση στον Πελάτη:**\n{delivery_date.strftime('%d/%m/%Y')}")
        
        st.write("---")
        st.caption("Σημείωση: Αν ο προορισμός είναι απομακρυσμένος από την κεντρική στάση, υπολογίστε +1 ημέρα επιπλέον.")
    else:
        st.error("Δεν βρέθηκε διαθέσιμο δρομολόγιο.")

# Βοηθητική συνάρτηση για Ελληνικές μέρες
def greek_day(date):
    days = ["Δευτέρα", "Τρίτη", "Τετάρτη", "Πέμπτη", "Παρασκευή", "Σάββατο", "Κυριακή"]
    return days[date.weekday()]