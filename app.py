import streamlit as st
from datetime import datetime, timedelta

# Ρύθμιση σελίδας
st.set_page_config(page_title="Μεταγωγές", page_icon="🚌", layout="wide")

# --- ΟΛΙΚΗ ΕΠΙΒΟΛΗ ΕΜΦΑΝΙΣΗΣ (FORCE THEME) ---
st.markdown("""
    <style>
    /* Επιβολή γκρι φόντου παντού */
    [data-testid="stAppViewContainer"], [data-testid="stMainViewContainer"], .main, .stApp {
        background-color: #e9ecef !important;
    }

    /* Τίτλος */
    .app-title {
        color: #002b5c;
        text-align: center;
        font-family: 'Arial Black', sans-serif;
        font-size: 45px;
        font-weight: bold;
        padding: 20px;
        margin-bottom: 20px;
    }

    /* Κάρτα Δρομολογίου (Λευκό κουτί με έντονο περίγραμμα) */
    .route-card {
        background-color: #ffffff !important;
        color: #000000 !important;
        padding: 25px !important;
        border-radius: 15px !important;
        border: 3px solid #004a99 !important;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2) !important;
        margin-bottom: 20px !important;
    }

    /* Κάρτα Επιστροφής */
    .return-card {
        background-color: #ffffff !important;
        color: #000000 !important;
        padding: 25px !important;
        border-radius: 15px !important;
        border: 3px solid #ff7b00 !important;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2) !important;
        margin-bottom: 20px !important;
    }

    .label { font-weight: bold; color: #004a99; font-size: 1.1rem; }
    .date-val { color: #d32f2f; font-weight: bold; font-size: 1.1rem; }
    </style>
    """, unsafe_allow_html=True)

# --- ΔΕΔΟΜΕΝΑ ΔΡΟΜΟΛΟΓΙΩΝ (Π.Δ.) ---
RAW_ROUTES = [
    # ΑΘΗΝΑ
    {"from": "ΑΘΗΝΑ", "to": ["ΑΥΛΩΝΑΣ", "ΕΛΑΙΩΝΑΣ", "ΛΑΜΙΑ", "ΚΑΣΣΑΒΕΤΕΙΑ", "ΛΑΡΙΣΑ", "ΚΑΤΕΡΙΝΗ", "ΘΕΣΣΑΛΟΝΙΚΗ"], "days": [0, 3], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΤΡΙΚΑΛΑ", "ΓΡΕΒΕΝΑ"], "days": [0], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΧΑΛΚΙΔΑ"], "days": [1], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΚΟΡΙΝΘΟΣ", "ΝΑΥΠΛΙΟ", "ΤΥΡΙΝΘΑ", "ΤΡΙΠΟΛΗ", "ΚΑΛΑΜΑΤΑ"], "days": [2], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΧΑΝΙΑ", "ΗΡΑΚΛΕΙΟ", "ΡΕΘΥΜΝΟ", "ΛΑΣΙΘΙ", "ΡΟΔΟΣ", "ΜΥΤΙΛΗΝΗ", "ΧΙΟΣ", "ΣΑΜΟΣ", "ΣΥΡΟΣ", "ΚΕΡΚΥΡΑ"], "days": [4], "transit": 1},
    # ΘΕΣΣΑΛΟΝΙΚΗ
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": ["ΣΕΡΡΕΣ", "ΔΡΑΜΑ", "ΚΑΒΑΛΑ", "ΞΑΝΘΗ", "ΚΟΜΟΤΗΝΗ", "ΑΛΕΞΑΝΔΡΟΥΠΟΛΗ"], "days": [1, 4], "transit": 0},
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": ["ΒΕΡΟΙΑ", "ΚΟΖΑΝΗ", "ΓΡΕΒΕΝΑ", "ΙΩΑΝΝΙΝΑ"], "days": [0], "transit": 0},
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": ["ΔΡΑΜΑ", "ΣΕΡΡΕΣ"], "days": [3], "transit": 0},
    # ΛΟΙΠΑ ΤΜΗΜΑΤΑ
    {"from": "ΣΕΡΡΕΣ", "to": ["ΘΕΣΣΑΛΟΝΙΚΗ"], "days": [0, 1], "transit": 0},
    {"from": "ΙΩΑΝΝΙΝΑ", "to": ["ΑΡΤΑ", "ΑΓΡΙΝΙΟ", "ΠΑΤΡΑ", "ΑΙΓΙΟ", "ΚΟΡΙΝΘΟΣ", "ΑΘΗΝΑ"], "days": [1], "transit": 0},
    {"from": "ΠΑΤΡΑ", "to": ["ΑΙΓΙΟ", "ΚΟΡΙΝΘΟΣ", "ΑΘΗΝΑ"], "days": [0], "transit": 0},
    {"from": "ΠΑΤΡΑ", "to": ["ΝΑΥΠΛΙΟ", "ΑΡΓΟΣ", "ΤΡΙΠΟΛΗ"], "days": [1], "transit": 0},
    {"from": "ΑΓΡΙΝΙΟ", "to": ["ΠΑΤΡΑ", "ΑΜΦΙΣΣΑ"], "days": [2], "transit": 0},
    {"from": "ΛΑΡΙΣΑ", "to": ["ΒΟΛΟΣ"], "days": [0, 3], "transit": 0},
    {"from": "ΑΜΦΙΣΣΑ", "to": ["ΛΑΜΙΑ"], "days": [0, 1, 3, 4], "transit": 0},
    {"from": "ΛΑΜΙΑ", "to": ["ΑΜΦΙΣΣΑ", "ΔΟΜΟΚΟΣ"], "days": [0, 1, 3, 4], "transit": 0},
    {"from": "ΓΡΕΒΕΝΑ", "to": ["ΤΡΙΚΑΛΑ", "ΛΑΜΙΑ", "ΑΘΗΝΑ"], "days": [3], "transit": 0},
    # ΕΠΙΣΤΡΟΦΕΣ
    {"from": ["ΘΕΣΣΑΛΟΝΙΚΗ", "ΛΑΡΙΣΑ", "ΛΑΜΙΑ"], "to": ["ΑΘΗΝΑ"], "days": [1, 4], "transit": 0},
    {"from": ["ΚΑΛΑΜΑΤΑ", "ΤΡΙΠΟΛΗ"], "to": ["ΑΘΗΝΑ"], "days": [3], "transit": 0},
    {"from": ["ΑΛΕΞΑΝΔΡΟΥΠΟΛΗ", "ΚΟΜΟΤΗΝΗ", "ΞΑΝΘΗ", "ΣΕΡΡΕΣ"], "to": ["ΘΕΣΣΑΛΟΝΙΚΗ"], "days": [2, 5], "transit": 0},
]

# --- ΠΛΗΡΗΣ ΧΑΡΤΗΣ ΠΟΛΕΩΝ (Mapping to Hubs) ---
HUB_MAP = {
    "ΑΜΦΙΣΣΑ": "ΛΑΜΙΑ", "ΔΟΜΟΚΟΣ": "ΛΑΜΙΑ", "ΚΑΡΠΕΝΗΣΙ": "ΛΑΜΙΑ", 
    "ΘΗΒΑ": "ΕΛΑΙΩΝΑΣ", "ΛΙΒΑΔΕΙΑ": "ΕΛΑΙΩΝΑΣ", "ΧΑΛΚΙΔΑ": "ΕΛΑΙΩΝΑΣ",
    "ΣΠΑΡΤΗ": "ΤΡΙΠΟΛΗ", "ΠΥΡΓΟΣ": "ΠΑΤΡΑ", "ΑΜΑΛΙΑΔΑ": "ΠΑΤΡΑ", "ΑΡΓΟΣ": "ΝΑΥΠΛΙΟ",
    "ΒΟΛΟΣ": "ΛΑΡΙΣΑ", "ΚΑΡΔΙΤΣΑ": "ΤΡΙΚΑΛΑ", "ΠΡΕΒΕΖΑ": "ΑΡΤΑ", "ΗΓΟΥΜΕΝΙΤΣΑ": "ΙΩΑΝΝΙΝΑ",
    "ΜΕΣΟΛΟΓΓΙ": "ΑΓΡΙΝΙΟ", "ΕΔΕΣΣΑ": "ΒΕΡΟΙΑ", "ΦΛΩΡΙΝΑ": "ΚΟΖΑΝΗ", "ΚΑΣΤΟΡΙΑ": "ΚΟΖΑΝΗ",
    "ΚΙΛΚΙΣ": "ΘΕΣΣΑΛΟΝΙΚΗ", "ΠΟΛΥΓΥΡΟΣ": "ΘΕΣΣΑΛΟΝΙΚΗ", "ΓΙΑΝΝΙΤΣΑ": "ΘΕΣΣΑΛΟΝΙΚΗ"
}

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
    return f"<b>{date.strftime('%d/%m/%Y')}</b> <span class='date-val'>({greek_day(date)})</span>"

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
            if r["from"] == start: path = [{"from": r["from"], "to": r["to"], "ship": ship, "arrive": ship + timedelta(days=r["transit"])}]
            else:
                prefix = find_backward(start, r["from"], ship, depth + 1)
                path = prefix + [{"from": r["from"], "to": r["to"], "ship": ship, "arrive": ship + timedelta(days=r["transit"])}] if prefix else None
            if path and (best is None or path[0]["ship"] > best[0]["ship"]): best = path
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
            if r["to"] == end: path = [{"from": r["from"], "to": r["to"], "ship": ship, "arrive": ship + timedelta(days=r["transit"])}]
            else:
                suffix = find_forward(r["to"], end, ship + timedelta(days=1 + r["transit"]), depth + 1)
                path = [{"from": r["from"], "to": r["to"], "ship": ship, "arrive": ship + timedelta(days=r["transit"])}] + suffix if suffix else None
            if path and (best is None or path[-1]["arrive"] < best[-1]["arrive"]): best = path
    return best

# --- UI ---
st.markdown('<div class="app-title">🚌 Μεταγωγές</div>', unsafe_allow_html=True)

with st.container():
    c1, c2, c3 = st.columns(3)
    origin = c1.selectbox("📍 Από (Αφετηρία):", ALL_CITIES, index=ALL_CITIES.index("ΣΕΡΡΕΣ"))
    dest = c2.selectbox("🏁 Προς (Προορισμός):", ALL_CITIES, index=ALL_CITIES.index("ΑΘΗΝΑ"))
    d_date = c3.date_input("📅 Παράδοση:", datetime.now() + timedelta(days=5))

if st.button("🔍 Υπολογισμός Διαδρομής"):
    res = find_backward(origin.upper(), dest.upper(), d_date)
    if res:
        st.session_state.update({'res': res, 'd': dest, 'o': origin, 'dt': d_date})
        st.markdown(f"### 🗓️ Πρέπει να ξεκινήσει: {format_dt(res[0]['ship'])}", unsafe_allow_html=True)
        for i, leg in enumerate(res):
            st.markdown(f"""<div class="route-card">
            <div style="font-weight:bold; font-size:1.2em; color:#002b5c;">🚌 Σκέλος {i+1}: {leg['from']} ➡️ {leg['to']}</div>
            <div><span class="label">Αναχώρηση:</span> {format_dt(leg['ship'])} | <span class="label">Άφιξη:</span> {format_dt(leg['arrive'])}</div>
            </div>""", unsafe_allow_html=True)
    else: st.error("Δεν βρέθηκε διαδρομή.")

if 'res' in st.session_state:
    if st.button(f"🔄 Επιστροφή ({st.session_state['d']} ➡️ {st.session_state['o']})"):
        ret = find_forward(st.session_state['d'].upper(), st.session_state['o'].upper(), st.session_state['dt'] + timedelta(days=1))
        if ret:
            st.markdown(f"### 🗓️ Επιστροφή στην έδρα: {format_dt(ret[-1]['arrive'])}", unsafe_allow_html=True)
            for i, leg in enumerate(ret):
                st.markdown(f"""<div class="return-card">
                <div style="font-weight:bold; font-size:1.2em; color:#cc5500;">🔄 Σκέλος {i+1}: {leg['from']} ➡️ {leg['to']}</div>
                <div><span class="label">Αναχώρηση:</span> {format_dt(leg['ship'])} | <span class="label">Άφιξη:</span> {format_dt(leg['arrive'])}</div>
                </div>""", unsafe_allow_html=True)
