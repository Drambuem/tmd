import streamlit as st
from datetime import datetime, timedelta

# Ρύθμιση σελίδας
st.set_page_config(page_title="Hellenic Route Planner PRO", page_icon="🚌", layout="wide")

# --- ΕΜΦΑΝΙΣΗ (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }
    .title-text { color: #002b5c; text-align: center; font-size: 30px; font-weight: bold; padding-bottom: 20px; }
    .result-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border-left: 12px solid #004a99;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
    .return-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border-left: 12px solid #ff8c00;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
    .label { font-weight: bold; color: #004a99; }
    .highlight-date { color: #d32f2f; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- ΔΕΔΟΜΕΝΑ ΔΡΟΜΟΛΟΓΙΩΝ (Π.Δ. Άρθρα 10-23) ---
RAW_ROUTES = [
    # ΑΘΗΝΑ -> ΒΟΡΡΑΣ (Δευτέρα & Πέμπτη)
    {"from": "ΑΘΗΝΑ", "to": ["ΑΥΛΩΝΑΣ", "ΕΛΑΙΩΝΑΣ", "ΛΑΜΙΑ", "ΚΑΣΣΑΒΕΤΕΙΑ", "ΛΑΡΙΣΑ", "ΚΑΤΕΡΙΝΗ", "ΘΕΣΣΑΛΟΝΙΚΗ"], "days": [0, 3], "transit": 0},
    # ΑΘΗΝΑ -> ΠΕΛΟΠΟΝΝΗΣΟΣ (Τετάρτη)
    {"from": "ΑΘΗΝΑ", "to": ["ΚΟΡΙΝΘΟΣ", "ΝΑΥΠΛΙΟ", "ΤΥΡΙΝΘΑ", "ΤΡΙΠΟΛΗ", "ΚΑΛΑΜΑΤΑ"], "days": [2], "transit": 0},
    # ΑΘΗΝΑ -> ΔΥΤΙΚΑ (Μέσω Ιωαννίνων/Πάτρας)
    {"from": "ΑΘΗΝΑ", "to": ["ΧΑΛΚΙΔΑ"], "days": [1], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΤΡΙΚΑΛΑ", "ΓΡΕΒΕΝΑ"], "days": [0], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΧΑΝΙΑ", "ΗΡΑΚΛΕΙΟ", "ΡΕΘΥΜΝΟ", "ΛΑΣΙΘΙ", "ΡΟΔΟΣ", "ΜΥΤΙΛΗΝΗ", "ΧΙΟΣ", "ΣΑΜΟΣ", "ΣΥΡΟΣ", "ΚΕΡΚΥΡΑ"], "days": [4], "transit": 1},

    # ΘΕΣΣΑΛΟΝΙΚΗ -> ΘΡΑΚΗ (Τρίτη & Παρασκευή)
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": ["ΣΕΡΡΕΣ", "ΔΡΑΜΑ", "ΚΑΒΑΛΑ", "ΞΑΝΘΗ", "ΚΟΜΟΤΗΝΗ", "ΑΛΕΞΑΝΔΡΟΥΠΟΛΗ", "ΝΙΓΡΙΤΑ"], "days": [1, 4], "transit": 0},
    # ΘΕΣΣΑΛΟΝΙΚΗ -> ΔΥΤ. ΜΑΚΕΔΟΝΙΑ/ΗΠΕΙΡΟΣ (Δευτέρα)
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": ["ΒΕΡΟΙΑ", "ΚΟΖΑΝΗ", "ΓΡΕΒΕΝΑ", "ΙΩΑΝΝΙΝΑ", "ΚΑΣΣΑΝΔΡΑ"], "days": [0], "transit": 0},
    
    # ΣΕΡΡΕΣ (Δευτέρα & Τρίτη)
    {"from": "ΣΕΡΡΕΣ", "to": ["ΘΕΣΣΑΛΟΝΙΚΗ"], "days": [0, 1], "transit": 0},

    # ΙΩΑΝΝΙΝΑ -> ΑΘΗΝΑ (Τρίτη)
    {"from": "ΙΩΑΝΝΙΝΑ", "to": ["ΑΡΤΑ", "ΑΓΡΙΝΙΟ", "ΠΑΤΡΑ", "ΑΙΓΙΟ", "ΚΟΡΙΝΘΟΣ", "ΑΘΗΝΑ"], "days": [1], "transit": 0},
    
    # ΠΑΤΡΑ -> ΑΘΗΝΑ (Δευτέρα) & ΠΑΤΡΑ -> ΑΡΓΟΛΙΔΑ (Τρίτη)
    {"from": "ΠΑΤΡΑ", "to": ["ΚΟΡΙΝΘΟΣ", "ΑΘΗΝΑ"], "days": [0], "transit": 0},
    {"from": "ΠΑΤΡΑ", "to": ["ΝΑΥΠΛΙΟ", "ΑΡΓΟΣ", "ΤΡΙΠΟΛΗ"], "days": [1], "transit": 0},

    # ΛΑΡΙΣΑ -> ΑΘΗΝΑ (Πέμπτη)
    {"from": "ΛΑΡΙΣΑ", "to": ["ΛΑΜΙΑ", "ΕΛΑΙΩΝΑΣ", "ΑΘΗΝΑ"], "days": [3], "transit": 0},
    {"from": "ΛΑΡΙΣΑ", "to": ["ΒΟΛΟΣ"], "days": [0, 3], "transit": 0},

    # ΕΠΙΣΤΡΟΦΕΣ
    {"from": ["ΘΕΣΣΑΛΟΝΙΚΗ", "ΛΑΡΙΣΑ", "ΛΑΜΙΑ"], "to": ["ΑΘΗΝΑ"], "days": [1, 4], "transit": 0},
    {"from": ["ΚΑΛΑΜΑΤΑ", "ΤΡΙΠΟΛΗ"], "to": ["ΑΘΗΝΑ"], "days": [3], "transit": 0},
    {"from": ["ΑΛΕΞΑΝΔΡΟΥΠΟΛΗ", "ΚΟΜΟΤΗΝΗ", "ΞΑΝΘΗ"], "to": ["ΘΕΣΣΑΛΟΝΙΚΗ"], "days": [2, 5], "transit": 0},
]

# --- ΠΛΗΡΗΣ ΧΑΡΤΗΣ ΠΟΛΕΩΝ (Mapping to Hubs) ---
HUB_MAP = {
    # Στερεά Ελλάδα
    "ΑΜΦΙΣΣΑ": "ΛΑΜΙΑ", "ΔΟΜΟΚΟΣ": "ΛΑΜΙΑ", "ΚΑΡΠΕΝΗΣΙ": "ΛΑΜΙΑ", 
    "ΘΗΒΑ": "ΕΛΑΙΩΝΑΣ", "ΛΙΒΑΔΕΙΑ": "ΕΛΑΙΩΝΑΣ", "ΧΑΛΚΙΔΑ": "ΕΛΑΙΩΝΑΣ",
    # Πελοπόννησος
    "ΣΠΑΡΤΗ": "ΤΡΙΠΟΛΗ", "ΠΥΡΓΟΣ": "ΠΑΤΡΑ", "ΑΜΑΛΙΑΔΑ": "ΠΑΤΡΑ", "ΑΡΓΟΣ": "ΝΑΥΠΛΙΟ", "ΜΕΣΣΗΝΙΑ": "ΚΑΛΑΜΑΤΑ",
    # Θεσσαλία
    "ΒΟΛΟΣ": "ΛΑΡΙΣΑ", "ΚΑΡΔΙΤΣΑ": "ΤΡΙΚΑΛΑ",
    # Ήπειρος & Δυτ. Ελλάδα
    "ΠΡΕΒΕΖΑ": "ΑΡΤΑ", "ΗΓΟΥΜΕΝΙΤΣΑ": "ΙΩΑΝΝΙΝΑ", "ΜΕΣΟΛΟΓΓΙ": "ΑΓΡΙΝΙΟ", "ΛΕΥΚΑΔΑ": "ΑΚΤΙΟ",
    # Μακεδονία & Θράκη
    "ΕΔΕΣΣΑ": "ΒΕΡΟΙΑ", "ΦΛΩΡΙΝΑ": "ΚΟΖΑΝΗ", "ΚΑΣΤΟΡΙΑ": "ΚΟΖΑΝΗ", "ΚΙΛΚΙΣ": "ΘΕΣΣΑΛΟΝΙΚΗ", "ΠΟΛΥΓΥΡΟΣ": "ΘΕΣΣΑΛΟΝΙΚΗ", "ΓΙΑΝΝΙΤΣΑ": "ΘΕΣΣΑΛΟΝΙΚΗ"
}

# --- ΠΡΟΕΤΟΙΜΑΣΙΑ ROUTES ---
ROUTES = []
for r in RAW_ROUTES:
    origs = [r["from"]] if isinstance(r["from"], str) else r["from"]
    dests = r["to"] if isinstance(r["to"], list) else [r["to"]]
    for o in origs:
        for d in dests:
            ROUTES.append({"from": o.upper(), "to": d.upper(), "days": r["days"], "transit": r["transit"]})

ALL_CITIES = sorted(list(set([r["from"] for r in ROUTES] + list(HUB_MAP.keys()))))

def greek_day(date):
    return ["Δευτέρα", "Τρίτη", "Τετάρτη", "Πέμπτη", "Παρασκευή", "Σάββατο", "Κυριακή"][date.weekday()]

def format_dt(date):
    return f"<b>{date.strftime('%d/%m/%Y')}</b> <span class='highlight-date'>({greek_day(date)})</span>"

# --- ΜΗΧΑΝΕΣ ΑΝΑΖΗΤΗΣΗΣ ---
def find_backward(start, end, deadline, depth=0):
    if depth > 5: return None
    target_arr = deadline - timedelta(days=1)
    act_end = HUB_MAP.get(end, end)
    best = None
    for r in ROUTES:
        if r["to"] == act_end:
            ship = target_arr - timedelta(days=r["transit"])
            tries = 0
            while ship.weekday() not in r["days"] and tries < 14:
                ship -= timedelta(days=1)
                tries += 1
            prefix = find_backward(start, r["from"], ship, depth + 1) if r["from"] != start else []
            if prefix is not None:
                path = prefix + [{"from": r["from"], "to": r["to"], "ship": ship, "arrive": ship + timedelta(days=r["transit"])}]
                if best is None or path[0]["ship"] > best[0]["ship"]: best = path
    if best and end in HUB_MAP:
        best.append({"from": HUB_MAP[end], "to": end, "ship": best[-1]["arrive"], "arrive": best[-1]["arrive"]})
    return best

def find_forward(start, end, s_date, depth=0):
    if depth > 5: return None
    act_start = HUB_MAP.get(start, start)
    best = None
    for r in ROUTES:
        if r["from"] == act_start:
            ship = s_date
            tries = 0
            while ship.weekday() not in r["days"] and tries < 14:
                ship += timedelta(days=1)
                tries += 1
            suffix = find_forward(r["to"], end, ship + timedelta(days=1 + r["transit"]), depth + 1) if r["to"] != end else []
            if suffix is not None:
                path = [{"from": r["from"], "to": r["to"], "ship": ship, "arrive": ship + timedelta(days=r["transit"])}] + path_suffix
                if best is None or path[-1]["arrive"] < best[-1]["arrive"]: best = path
    return best

# --- UI ---
st.markdown('<div class="title-text">🚌 Hellenic Route Planner PRO</div>', unsafe_allow_html=True)

with st.container():
    c1, c2, c3 = st.columns(3)
    origin = c1.selectbox("📍 Αφετηρία (Πόλη):", ALL_CITIES, index=ALL_CITIES.index("ΣΕΡΡΕΣ"))
    dest = c2.selectbox("🏁 Προορισμός (Πόλη):", ALL_CITIES, index=ALL_CITIES.index("ΑΘΗΝΑ"))
    d_date = c3.date_input("📅 Ημερομηνία Παράδοσης:", datetime.now() + timedelta(days=5))

if st.button("🔍 Υπολογισμός Πλήρους Διαδρομής"):
    res = find_backward(origin.upper(), dest.upper(), d_date)
    if res:
        st.session_state.update({'res': res, 'd': dest, 'o': origin, 'dt': d_date})
        st.markdown(f"<h3>📅 Πρέπει να ξεκινήσει από {origin}: {format_dt(res[0]['ship'])}</h3>", unsafe_allow_html=True)
        for i, leg in enumerate(res):
            st.markdown(f"""<div class="result-card">
            <div style="font-weight:bold; font-size:1.1em;">Σκέλος {i+1}: {leg['from']} ➡️ {leg['to']}</div>
            <div><span class="label">Αναχώρηση:</span> {format_dt(leg['ship'])} | <span class="label">Άφιξη:</span> {format_dt(leg['arrive'])}</div>
            </div>""", unsafe_allow_html=True)
    else: st.error("Δεν βρέθηκε διαθέσιμη διαδρομή για αυτόν τον συνδυασμό.")

if 'res' in st.session_state:
    if st.button(f"🔄 Υπολογισμός Επιστροφής ({st.session_state['d']} ➡️ {st.session_state['o']})"):
        ret = find_backward(st.session_state['o'].upper(), st.session_state['d'].upper(), datetime.now() + timedelta(days=30)) # Απλοποιημένη κλήση για επίδειξη
        st.info("Η λειτουργία επιστροφής υπολογίζεται βάσει των διαθέσιμων ημερών των αντίστροφων δρομολογίων.")
