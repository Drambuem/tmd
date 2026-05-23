import streamlit as st
from datetime import datetime, timedelta

# Ρύθμιση σελίδας
st.set_page_config(page_title="Prisoner Transfer Planner", page_icon="🚌", layout="wide")

# --- CSS ΓΙΑ ΕΠΑΓΓΕΛΜΑΤΙΚΗ ΕΜΦΑΝΙΣΗ ---
st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; }
    h1 { color: #003366; text-align: center; }
    .route-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        border-left: 8px solid #0056b3;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 10px;
    }
    .return-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        border-left: 8px solid #ff8c00;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 10px;
    }
    .highlight { color: #d32f2f; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- ΔΕΔΟΜΕΝΑ ΒΑΣΕΙ ΑΡΘΡΩΝ 10-23 ---
RAW_ROUTES = [
    # ΑΡΘΡΟ 10: ΔΙΕΥΘΥΝΣΗ ΜΕΤΑΓΩΓΩΝ ΑΤΤΙΚΗΣ (ΑΘΗΝΑ)
    {"from": "ΑΘΗΝΑ", "to": ["ΑΥΛΩΝΑΣ", "ΕΛΑΙΩΝΑΣ", "ΛΑΜΙΑ", "ΚΑΣΣΑΒΕΤΕΙΑ", "ΛΑΡΙΣΑ", "ΚΑΤΕΡΙΝΗ", "ΘΕΣΣΑΛΟΝΙΚΗ"], "days": [0, 3], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΚΟΡΙΝΘΟΣ", "ΝΑΥΠΛΙΟ", "ΤΥΡΙΝΘΑ", "ΤΡΙΠΟΛΗ", "ΚΑΛΑΜΑΤΑ"], "days": [2], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΧΑΛΚΙΔΑ"], "days": [1], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΑΥΛΩΝΑΣ", "ΕΛΑΙΩΝΑΣ", "ΛΑΜΙΑ", "ΤΡΙΚΑΛΑ", "ΓΡΕΒΕΝΑ"], "days": [0], "transit": 0},
    
    # ΑΡΘΡΟ 11: ΘΕΣΣΑΛΟΝΙΚΗ
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": ["ΝΙΓΡΙΤΑ", "ΣΕΡΡΕΣ", "ΔΡΑΜΑ", "ΕΛΕΥΘΕΡΟΥΠΟΛΗ", "ΚΑΒΑΛΑ", "ΞΑΝΘΗ", "ΚΟΜΟΤΗΝΗ", "ΑΛΕΞΑΝΔΡΟΥΠΟΛΗ"], "days": [1, 4], "transit": 0},
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": ["ΒΕΡΟΙΑ", "ΚΟΖΑΝΗ", "ΓΡΕΒΕΝΑ", "ΙΩΑΝΝΙΝΑ"], "days": [0], "transit": 0},
    
    # ΑΡΘΡΟ 12: ΣΕΡΡΕΣ
    {"from": "ΣΕΡΡΕΣ", "to": ["ΘΕΣΣΑΛΟΝΙΚΗ"], "days": [0, 1], "transit": 0},
    {"from": "ΣΕΡΡΕΣ", "to": ["ΝΙΓΡΙΤΑ"], "days": [0, 1, 2, 3, 4, 5], "transit": 0},
    
    # ΑΡΘΡΟ 13: ΠΑΤΡΑ
    {"from": "ΠΑΤΡΑ", "to": ["ΑΙΓΙΟ", "ΞΥΛΟΚΑΣΤΡΟ", "ΚΙΑΤΟ", "ΚΟΡΙΝΘΟΣ", "ΑΘΗΝΑ"], "days": [0], "transit": 0},
    {"from": "ΠΑΤΡΑ", "to": ["ΑΡΓΟΛΙΔΑ", "ΜΕΣΣΗΝΙΑ"], "days": [1], "transit": 0},
    {"from": "ΠΑΤΡΑ", "to": ["ΙΩΑΝΝΙΝΑ"], "days": [1], "transit": 0}, # Ανταπόκριση από Αργολίδα
    
    # ΑΡΘΡΟ 14: ΑΓΡΙΝΙΟ
    {"from": "ΑΓΡΙΝΙΟ", "to": ["ΠΑΤΡΑ", "ΑΜΦΙΣΣΑ"], "days": [2], "transit": 0},
    {"from": "ΑΜΦΙΣΣΑ", "to": ["ΠΑΤΡΑ", "ΑΓΡΙΝΙΟ"], "days": [3], "transit": 0}, # Επιστροφή
    
    # ΑΡΘΡΟ 15: ΛΑΡΙΣΑ
    {"from": "ΛΑΡΙΣΑ", "to": ["ΚΑΣΣΑΒΕΤΕΙΑ", "ΛΑΜΙΑ", "ΕΛΑΙΩΝΑΣ", "ΑΥΛΩΝΑΣ", "ΑΘΗΝΑ"], "days": [3], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΑΥΛΩΝΑΣ", "ΕΛΑΙΩΝΑΣ", "ΛΑΜΙΑ", "ΚΑΣΣΑΒΕΤΕΙΑ", "ΛΑΡΙΣΑ"], "days": [4], "transit": 0}, # Επιστροφή
    {"from": "ΛΑΡΙΣΑ", "to": ["ΒΟΛΟΣ"], "days": [0, 3], "transit": 0},
    {"from": "ΛΑΡΙΣΑ", "to": ["ΚΟΖΑΝΗ"], "days": [5], "transit": 0},
    
    # ΑΡΘΡΟ 16: ΙΩΑΝΝΙΝΑ
    {"from": "ΙΩΑΝΝΙΝΑ", "to": ["ΑΡΤΑ", "ΑΓΡΙΝΙΟ", "ΠΑΤΡΑ", "ΑΙΓΙΟ", "ΚΟΡΙΝΘΟΣ", "ΑΘΗΝΑ"], "days": [1], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΚΟΡΙΝΘΟΣ", "ΑΙΓΙΟ", "ΠΑΤΡΑ", "ΑΓΡΙΝΙΟ", "ΑΡΤΑ", "ΙΩΑΝΝΙΝΑ"], "days": [2], "transit": 0}, # Επιστροφή
    
    # ΑΡΘΡΟ 17: ΓΡΕΒΕΝΑ
    {"from": "ΓΡΕΒΕΝΑ", "to": ["ΤΡΙΚΑΛΑ", "ΛΑΜΙΑ", "ΕΛΑΙΩΝΑΣ", "ΑΥΛΩΝΑΣ", "ΑΘΗΝΑ"], "days": [3], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΑΥΛΩΝΑΣ", "ΕΛΑΙΩΝΑΣ", "ΛΑΜΙΑ", "ΤΡΙΚΑΛΑ", "ΓΡΕΒΕΝΑ"], "days": [4], "transit": 0}, # Επιστροφή
    
    # ΑΡΘΡΟ 18: ΑΜΦΙΣΣΑ
    {"from": "ΑΜΦΙΣΣΑ", "to": ["ΛΑΜΙΑ"], "days": [0, 1, 3, 4], "transit": 0},
    {"from": "ΛΑΜΙΑ", "to": ["ΑΜΦΙΣΣΑ"], "days": [0, 1, 3, 4], "transit": 0},
    
    # ΑΡΘΡΟ 19: ΛΑΜΙΑ
    {"from": "ΛΑΜΙΑ", "to": ["ΔΟΜΟΚΟΣ"], "days": [0, 1, 2, 3, 4], "transit": 0},
    
    # ΑΡΘΡΟ 20: ΚΡΗΤΗ & ΝΗΣΙΑ (Αναχώρηση Παρασκευή)
    {"from": "ΑΘΗΝΑ", "to": ["ΧΑΝΙΑ", "ΡΕΘΥΜΝΟ", "ΗΡΑΚΛΕΙΟ", "ΛΑΣΙΘΙ", "ΝΗΣΙΑ"], "days": [4], "transit": 1},
    {"from": ["ΧΑΝΙΑ", "ΗΡΑΚΛΕΙΟ"], "to": ["ΑΘΗΝΑ"], "days": [5], "transit": 1},
]

# Hubs & Ειδικές Ανταποκρίσεις βάσει κειμένου
HUB_DELIVERIES = {
    "ΒΟΛΟΣ": "ΛΑΡΙΣΑ",
    "ΑΜΦΙΣΣΑ": "ΛΑΜΙΑ",
    "ΔΟΜΟΚΟΣ": "ΛΑΜΙΑ",
    "ΛΙΒΑΔΕΙΑ": "ΕΛΑΙΩΝΑΣ",
    "ΘΗΒΑ": "ΕΛΑΙΩΝΑΣ",
    "ΜΑΛΑΝΔΡΙΝΟ": "ΠΑΤΡΑ"
}

ROUTES = []
for r in RAW_ROUTES:
    origins = [r["from"]] if isinstance(r["from"], str) else r["from"]
    destinations = r["to"] if isinstance(r["to"], list) else [r["to"]]
    for o in origins:
        for d in destinations:
            ROUTES.append({"from": o.upper(), "to": d.upper(), "days": r["days"], "transit": r["transit"]})

ALL_CITIES = sorted(list(set([r["from"] for r in ROUTES] + list(HUB_DELIVERIES.keys()))))

def greek_day(date):
    days = ["Δευτέρα", "Τρίτη", "Τετάρτη", "Πέμπτη", "Παρασκευή", "Σάββατο", "Κυριακή"]
    return days[date.weekday()]

def format_date_gr(date):
    return f"<b>{date.strftime('%d/%m/%Y')}</b> ({greek_day(date)})"

# --- ΜΗΧΑΝΕΣ ΑΝΑΖΗΤΗΣΗΣ ---
def find_backward_path(start, end, deadline, depth=0):
    if depth > 4: return None
    target_arrival = deadline - timedelta(days=1)
    
    # Αν ο προορισμός είναι Hub delivery, άλλαξε τον προορισμό στο Hub
    search_end = HUB_DELIVERIES.get(end, end)
    best_path = None

    for r in ROUTES:
        if r["to"] == search_end:
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
    
    # Πρόσθεσε το τελικό σκέλος αν είναι Hub delivery
    if best_path and end in HUB_DELIVERIES:
        hub_city = HUB_DELIVERIES[end]
        # Βρες το δρομολόγιο από το Hub στον τελικό προορισμό
        for r in ROUTES:
            if r["from"] == hub_city and r["to"] == end:
                # Υπολόγισε πότε φεύγει από το Hub (τουλάχιστον 1 μέρα μετά την άφιξη στο hub)
                h_ship = best_path[-1]["arrive"] + timedelta(days=1)
                while h_ship.weekday() not in r["days"]:
                    h_ship += timedelta(days=1)
                h_arrive = h_ship + timedelta(days=r["transit"])
                best_path.append({"from": hub_city, "to": end, "ship": h_ship, "arrive": h_arrive})
                break
                
    return best_path

def find_forward_path(start, end, start_date, depth=0):
    if depth > 4: return None
    best_path = None
    search_start = HUB_DELIVERIES.get(start, start)

    for r in ROUTES:
        if r["from"] == search_start:
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
st.title("🚌 Prisoner Route Planner v2.0")
st.markdown("<p style='text-align: center;'>Βάσει του Προεδρικού Διατάγματος (Άρθρα 10-23)</p>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    origin = st.selectbox("📍 Αφετηρία:", ALL_CITIES, index=ALL_CITIES.index("ΣΕΡΡΕΣ"))
with c2:
    dest = st.selectbox("🏁 Προορισμός:", ALL_CITIES, index=ALL_CITIES.index("ΑΘΗΝΑ"))
with c3:
    d_date = st.date_input("📅 Ημερομηνία Παράδοσης:", datetime.now() + timedelta(days=5))

if st.button("🚀 Υπολογισμός Διαδρομής"):
    res = find_backward_path(origin.upper(), dest.upper(), d_date)
    if res:
        st.session_state['last_res'] = res
        st.session_state['last_dest'] = dest
        st.session_state['last_origin'] = origin
        st.session_state['last_delivery'] = d_date
        
        st.markdown(f"### 🗓️ Αναχώρηση από {origin}: <span class='highlight'>{format_date_gr(res[0]['ship'])}</span>", unsafe_allow_html=True)
        for i, leg in enumerate(res):
            st.markdown(f"""
            <div class="route-card">
                <div style="font-weight:bold; color:#003366;">🚌 Σκέλος {i+1}: {leg['from']} ➡️ {leg['to']}</div>
                <div>📅 Αναχώρηση: {format_date_gr(leg['ship'])} | 🏁 Άφιξη: {format_date_gr(leg['arrive'])}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.error("Δεν βρέθηκε διαθέσιμη διαδρομή.")

if 'last_res' in st.session_state:
    st.markdown("<hr>", unsafe_allow_html=True)
    if st.button(f"🔄 Υπολογισμός Επιστροφής"):
        ret_start = st.session_state['last_delivery'] + timedelta(days=1)
        ret_res = find_forward_path(st.session_state['last_dest'].upper(), st.session_state['last_origin'].upper(), ret_start)
        if ret_res:
            st.markdown(f"### 🗓️ Επιστροφή στην έδρα: <span class='highlight'>{format_date_gr(ret_res[-1]['arrive'])}</span>", unsafe_allow_html=True)
            for i, leg in enumerate(ret_res):
                st.markdown(f"""
                <div class="return-card">
                    <div style="font-weight:bold; color:#cc5500;">🔄 Σκέλος {i+1}: {leg['from']} ➡️ {leg['to']}</div>
                    <div>📅 Αναχώρηση: {format_date_gr(leg['ship'])} | 🏁 Άφιξη: {format_date_gr(leg['arrive'])}</div>
                </div>
                """, unsafe_allow_html=True)
