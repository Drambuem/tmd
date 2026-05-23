import streamlit as st
from datetime import datetime, timedelta

# 1. Βασική Ρύθμιση
st.set_page_config(page_title="Μεταγωγές", page_icon="🚌", layout="wide")

# 2. ΕΠΙΒΟΛΗ ΓΚΡΙ ΦΟΝΤΟΥ (ΜΕ ΤΗΝ ΠΙΟ ΙΣΧΥΡΗ ΜΕΘΟΔΟ)
st.markdown("""
    <style>
    /* Αλλαγή των εσωτερικών μεταβλητών του Streamlit (Root Variables) */
    :root {
        --background-color: #f0f2f6;
        --secondary-background-color: #e5e7eb;
    }

    /* Επιβολή σε όλα τα επίπεδα */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMainViewContainer"], [data-testid="stHeader"] {
        background-color: #f0f2f6 !important;
    }

    /* Κατάργηση της λευκής γραμμής στην κορυφή */
    [data-testid="stHeader"] {
        display: none !important;
    }
    .main .block-container {
        padding-top: 1rem !important;
    }

    /* Τίτλος */
    .app-title {
        color: #003366;
        text-align: center;
        font-family: 'Arial Black', sans-serif;
        font-size: 50px;
        font-weight: bold;
        padding-bottom: 20px;
    }

    /* Κάρτα Δρομολογίου */
    .route-card {
        background-color: #ffffff !important;
        color: #000000 !important;
        padding: 20px !important;
        border-radius: 15px !important;
        border-left: 12px solid #0056b3 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
        margin-bottom: 20px !important;
    }

    .return-card {
        background-color: #ffffff !important;
        color: #000000 !important;
        padding: 20px !important;
        border-radius: 15px !important;
        border-left: 12px solid #ff7b00 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
        margin-bottom: 20px !important;
    }

    /* by Manos - Διακριτικά κάτω αριστερά */
    .manos-footer {
        position: fixed;
        bottom: 10px;
        left: 15px;
        font-size: 12px;
        color: #9ca3af;
        font-style: italic;
    }

    .label { font-weight: bold; color: #003366; }
    .val { color: #d32f2f; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- ΔΕΔΟΜΕΝΑ ΔΡΟΜΟΛΟΓΙΩΝ (ΒΑΣΕΙ Π.Δ.) ---
RAW_ROUTES = [
    {"from": "ΑΘΗΝΑ", "to": ["ΑΥΛΩΝΑΣ", "ΕΛΑΙΩΝΑΣ", "ΛΑΜΙΑ", "ΚΑΣΣΑΒΕΤΕΙΑ", "ΛΑΡΙΣΑ", "ΚΑΤΕΡΙΝΗ", "ΘΕΣΣΑΛΟΝΙΚΗ"], "days": [0, 3], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΚΟΡΙΝΘΟΣ", "ΝΑΥΠΛΙΟ", "ΤΥΡΙΝΘΑ", "ΤΡΙΠΟΛΗ", "ΚΑΛΑΜΑΤΑ"], "days": [2], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΤΡΙΚΑΛΑ", "ΓΡΕΒΕΝΑ"], "days": [0], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΚΡΗΤΗ", "ΡΟΔΟΣ", "ΜΥΤΙΛΗΝΗ", "ΧΙΟΣ", "ΣΑΜΟΣ", "ΚΕΡΚΥΡΑ"], "days": [4], "transit": 1},
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": ["ΣΕΡΡΕΣ", "ΔΡΑΜΑ", "ΚΑΒΑΛΑ", "ΞΑΝΘΗ", "ΚΟΜΟΤΗΝΗ", "ΑΛΕΞΑΝΔΡΟΥΠΟΛΗ"], "days": [1, 4], "transit": 0},
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": ["ΒΕΡΟΙΑ", "ΚΟΖΑΝΗ", "ΓΡΕΒΕΝΑ", "ΙΩΑΝΝΙΝΑ"], "days": [0], "transit": 0},
    {"from": "ΣΕΡΡΕΣ", "to": ["ΘΕΣΣΑΛΟΝΙΚΗ"], "days": [0, 1], "transit": 0},
    {"from": "ΙΩΑΝΝΙΝΑ", "to": ["ΑΡΤΑ", "ΑΓΡΙΝΙΟ", "ΠΑΤΡΑ", "ΑΘΗΝΑ"], "days": [1], "transit": 0},
    {"from": "ΠΑΤΡΑ", "to": ["ΚΟΡΙΝΘΟΣ", "ΑΘΗΝΑ"], "days": [0], "transit": 0},
    {"from": "ΛΑΡΙΣΑ", "to": ["ΒΟΛΟΣ", "ΛΑΜΙΑ", "ΑΘΗΝΑ"], "days": [3, 0], "transit": 0},
    {"from": "ΑΜΦΙΣΣΑ", "to": ["ΛΑΜΙΑ"], "days": [0, 1, 3, 4], "transit": 0},
    {"from": "ΛΑΜΙΑ", "to": ["ΑΜΦΙΣΣΑ", "ΔΟΜΟΚΟΣ"], "days": [0, 1, 2, 3, 4], "transit": 0},
    {"from": ["ΘΕΣΣΑΛΟΝΙΚΗ", "ΛΑΡΙΣΑ", "ΛΑΜΙΑ"], "to": ["ΑΘΗΝΑ"], "days": [1, 4], "transit": 0},
    {"from": ["ΚΑΛΑΜΑΤΑ", "ΤΡΙΠΟΛΗ", "ΝΑΥΠΛΙΟ"], "to": ["ΑΘΗΝΑ"], "days": [3], "transit": 0},
]

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

# Μηχανή Αναζήτησης (με έλεγχο κύκλων)
def find_path(start, end, deadline, mode='backward', visited=None):
    if visited is None: visited = set()
    if end in visited: return None
    new_visited = visited.copy()
    new_visited.add(end)

    if mode == 'backward':
        target_arr = deadline - timedelta(days=1)
        act_end = HUB_MAP.get(end, end)
        best = None
        for r in ROUTES:
            if r["to"] == act_end:
                ship = target_arr - timedelta(days=r["transit"])
                while ship.weekday() not in r["days"]: ship -= timedelta(days=1)
                prefix = find_path(start, r["from"], ship, 'backward', new_visited) if r["from"] != start else []
                if prefix is not None:
                    path = prefix + [{"from": r["from"], "to": r["to"], "ship": ship, "arrive": ship + timedelta(days=r["transit"])}]
                    if best is None or path[0]["ship"] > best[0]["ship"]: best = path
        if best and end in HUB_MAP:
            best.append({"from": HUB_MAP[end], "to": end, "ship": best[-1]["arrive"], "arrive": best[-1]["arrive"]})
        return best
    else: # forward for return
        act_start = HUB_MAP.get(start, start)
        best = None
        for r in ROUTES:
            if r["from"] == act_start:
                ship = deadline
                while ship.weekday() not in r["days"]: ship += timedelta(days=1)
                suffix = find_path(r["to"], end, ship + timedelta(days=1), 'forward', new_visited) if r["to"] != end else []
                if suffix is not None:
                    path = [{"from": r["from"], "to": r["to"], "ship": ship, "arrive": ship + timedelta(days=r["transit"])}] + suffix
                    if best is None or path[-1]["arrive"] < best[-1]["arrive"]: best = path
        return best

# --- UI ---
st.markdown('<div class="app-title">Μεταγωγές</div>', unsafe_allow_html=True)

with st.container():
    c1, c2, c3 = st.columns(3)
    origin = c1.selectbox("📍 Αφετηρία:", ALL_CITIES, index=ALL_CITIES.index("ΣΕΡΡΕΣ"))
    dest = c2.selectbox("🏁 Προορισμός:", ALL_CITIES, index=ALL_CITIES.index("ΑΘΗΝΑ"))
    d_date = c3.date_input("📅 Παράδοση:", datetime.now() + timedelta(days=5))

if st.button("🚀 Υπολογισμός"):
    res = find_path(origin.upper(), dest.upper(), d_date, 'backward')
    if res:
        st.session_state.update({'res': res, 'd': dest, 'o': origin, 'dt': d_date})
        st.success(f"### 🗓️ Αναχώρηση: {res[0]['ship'].strftime('%d/%m/%Y')} ({greek_day(res[0]['ship'])})")
        for i, leg in enumerate(res):
            st.markdown(f"""<div class="route-card"><div style="font-weight:bold; font-size:1.2em; color:#003366;">🚌 Σκέλος {i+1}: {leg['from']} ➡️ {leg['to']}</div>
            <div><span class="label">Αναχώρηση:</span> {leg['ship'].strftime('%d/%m/%Y')} ({greek_day(leg['ship'])}) | <span class="label">Άφιξη:</span> {leg['arrive'].strftime('%d/%m/%Y')}</div></div>""", unsafe_allow_html=True)
    else: st.error("Δεν βρέθηκε διαδρομή.")

if 'res' in st.session_state:
    if st.button(f"🔄 Επιστροφή"):
        ret = find_path(st.session_state['d'].upper(), st.session_state['o'].upper(), st.session_state['dt'] + timedelta(days=1), 'forward')
        if ret:
            st.warning(f"### 🗓️ Επιστροφή στην έδρα: {ret[-1]['arrive'].strftime('%d/%m/%Y')} ({greek_day(ret[-1]['arrive'])})")
            for i, leg in enumerate(ret):
                st.markdown(f"""<div class="return-card"><div style="font-weight:bold; font-size:1.2em; color:#cc5500;">🔄 Σκέλος {i+1}: {leg['from']} ➡️ {leg['to']}</div>
                <div><span class="label">Αναχώρηση:</span> {leg['ship'].strftime('%d/%m/%Y')} | <span class="label">Άφιξη:</span> {leg['arrive'].strftime('%d/%m/%Y')}</div></div>""", unsafe_allow_html=True)

# Footer by Manos
st.markdown('<div class="manos-footer">by Manos</div>', unsafe_allow_html=True)
