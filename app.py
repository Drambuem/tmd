import streamlit as st
from datetime import datetime, timedelta

# Ρύθμιση σελίδας - Καθαρή εκκίνηση
st.set_page_config(page_title="Bus Route Planner", page_icon="🚌", layout="wide")

# --- ΚΑΘΑΡΟ CSS (ΜΟΝΟ ΓΙΑ ΤΙΣ ΚΑΡΤΕΣ) ---
st.markdown("""
    <style>
    /* Τίτλος */
    .title-text {
        color: #002b5c;
        text-align: center;
        font-size: 35px;
        font-weight: bold;
        padding-bottom: 20px;
    }

    /* Στυλ για τις κάρτες των δρομολογίων */
    .result-card {
        background-color: #f8f9fa; /* Ελαφρύ γκρι μέσα στο κουτί */
        color: #111111;
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #004a99; /* Έντονο μπλε περίγραμμα */
        margin-bottom: 20px;
        font-family: sans-serif;
    }

    /* Στυλ για τις κάρτες επιστροφής */
    .return-card {
        background-color: #fff9f0; /* Ελαφρύ πορτοκαλί μέσα στο κουτί */
        color: #111111;
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #ff8c00; /* Έντονο πορτοκαλί περίγραμμα */
        margin-bottom: 20px;
        font-family: sans-serif;
    }

    .label {
        font-weight: bold;
        color: #004a99;
    }

    .highlight-date {
        color: #d32f2f;
        font-weight: bold;
        font-size: 1.1em;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ΔΕΔΟΜΕΝΑ ΔΡΟΜΟΛΟΓΙΩΝ ---
RAW_ROUTES = [
    {"from": "ΑΘΗΝΑ", "to": ["ΑΥΛΩΝΑΣ", "ΕΛΑΙΩΝΑΣ", "ΛΑΜΙΑ", "ΚΑΣΣΑΒΕΤΕΙΑ", "ΛΑΡΙΣΑ", "ΚΑΤΕΡΙΝΗ", "ΘΕΣΣΑΛΟΝΙΚΗ"], "days": [0, 3], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΤΡΙΚΑΛΑ", "ΓΡΕΒΕΝΑ"], "days": [0], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΧΑΛΚΙΔΑ"], "days": [1], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΚΟΡΙΝΘΟΣ", "ΝΑΥΠΛΙΟ", "ΤΥΡΙΝΘΑ", "ΤΡΙΠΟΛΗ", "ΚΑΛΑΜΑΤΑ"], "days": [2], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΧΑΝΙΑ", "ΗΡΑΚΛΕΙΟ", "ΝΗΣΙΑ"], "days": [4], "transit": 1},
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": ["ΣΕΡΡΕΣ", "ΔΡΑΜΑ", "ΚΑΒΑΛΑ", "ΞΑΝΘΗ", "ΚΟΜΟΤΗΝΗ", "ΑΛΕΞΑΝΔΡΟΥΠΟΛΗ"], "days": [1, 4], "transit": 0},
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": ["ΒΕΡΟΙΑ", "ΚΟΖΑΝΗ", "ΓΡΕΒΕΝΑ", "ΙΩΑΝΝΙΝΑ"], "days": [0], "transit": 0},
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": ["ΔΡΑΜΑ", "ΣΕΡΡΕΣ"], "days": [3], "transit": 0},
    {"from": "ΣΕΡΡΕΣ", "to": ["ΘΕΣΣΑΛΟΝΙΚΗ"], "days": [0, 1], "transit": 0},
    {"from": "ΙΩΑΝΝΙΝΑ", "to": ["ΑΡΤΑ", "ΑΓΡΙΝΙΟ", "ΠΑΤΡΑ", "ΑΙΓΙΟ", "ΚΟΡΙΝΘΟΣ", "ΑΘΗΝΑ"], "days": [1], "transit": 0},
    {"from": "ΠΑΤΡΑ", "to": ["ΑΙΓΙΟ", "ΚΟΡΙΝΘΟΣ", "ΑΘΗΝΑ"], "days": [0], "transit": 0},
    {"from": "ΠΑΤΡΑ", "to": ["ΑΡΓΟΛΙΔΑ", "ΜΕΣΣΗΝΙΑ"], "days": [1], "transit": 0},
    {"from": "ΑΓΡΙΝΙΟ", "to": ["ΠΑΤΡΑ", "ΑΜΦΙΣΣΑ"], "days": [2], "transit": 0},
    {"from": "ΛΑΡΙΣΑ", "to": ["ΒΟΛΟΣ"], "days": [0, 3], "transit": 0},
    {"from": "ΑΜΦΙΣΣΑ", "to": ["ΛΑΜΙΑ"], "days": [0, 1, 3, 4], "transit": 0},
    {"from": "ΛΑΜΙΑ", "to": ["ΑΜΦΙΣΣΑ", "ΔΟΜΟΚΟΣ"], "days": [0, 1, 3, 4], "transit": 0},
    {"from": "ΓΡΕΒΕΝΑ", "to": ["ΤΡΙΚΑΛΑ", "ΛΑΜΙΑ", "ΑΘΗΝΑ"], "days": [3], "transit": 0},
    {"from": ["ΘΕΣΣΑΛΟΝΙΚΗ", "ΛΑΡΙΣΑ", "ΛΑΜΙΑ"], "to": ["ΑΘΗΝΑ"], "days": [1, 4], "transit": 0},
    {"from": ["ΚΑΛΑΜΑΤΑ", "ΤΡΙΠΟΛΗ", "ΝΑΥΠΛΙΟ"], "to": ["ΑΘΗΝΑ"], "days": [3], "transit": 0},
    {"from": ["ΑΛΕΞΑΝΔΡΟΥΠΟΛΗ", "ΞΑΝΘΗ", "ΣΕΡΡΕΣ"], "to": ["ΘΕΣΣΑΛΟΝΙΚΗ"], "days": [2, 5], "transit": 0},
]

HUB_MAP = {"ΒΟΛΟΣ": "ΛΑΡΙΣΑ", "ΔΟΜΟΚΟΣ": "ΛΑΜΙΑ", "ΘΗΒΑ": "ΕΛΑΙΩΝΑΣ", "ΛΙΒΑΔΕΙΑ": "ΕΛΑΙΩΝΑΣ", "ΜΑΛΑΝΔΡΙΝΟ": "ΠΑΤΡΑ"}

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
    if depth > 4: return None
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
            path_prefix = find_backward(start, r["from"], ship, depth + 1) if r["from"] != start else []
            if path_prefix is not None:
                path = path_prefix + [{"from": r["from"], "to": r["to"], "ship": ship, "arrive": ship + timedelta(days=r["transit"])}]
                if best is None or path[0]["ship"] > best[0]["ship"]: best = path
    if best and end in HUB_MAP:
        best.append({"from": HUB_MAP[end], "to": end, "ship": best[-1]["arrive"], "arrive": best[-1]["arrive"]})
    return best

def find_forward(start, end, s_date, depth=0):
    if depth > 4: return None
    act_start = HUB_MAP.get(start, start)
    best = None
    for r in ROUTES:
        if r["from"] == act_start:
            ship = s_date
            tries = 0
            while ship.weekday() not in r["days"] and tries < 14:
                ship += timedelta(days=1)
                tries += 1
            path_suffix = find_forward(r["to"], end, ship + timedelta(days=1 + r["transit"]), depth + 1) if r["to"] != end else []
            if path_suffix is not None:
                path = [{"from": r["from"], "to": r["to"], "ship": ship, "arrive": ship + timedelta(days=r["transit"])}] + path_suffix
                if best is None or path[-1]["arrive"] < best[-1]["arrive"]: best = path
    return best

# --- UI ---
st.markdown('<div class="title-text">🚌 Bus Route Planner</div>', unsafe_allow_html=True)

with st.container():
    c1, c2, c3 = st.columns(3)
    origin = c1.selectbox("📍 Αφετηρία:", ALL_CITIES, index=ALL_CITIES.index("ΣΕΡΡΕΣ"))
    dest = c2.selectbox("🏁 Προορισμός:", ALL_CITIES, index=ALL_CITIES.index("ΑΘΗΝΑ"))
    d_date = c3.date_input("📅 Ημερομηνία Παράδοσης:", datetime.now() + timedelta(days=5))

if st.button("🚀 Υπολογισμός Δρομολογίου"):
    res = find_backward(origin.upper(), dest.upper(), d_date)
    if res:
        st.session_state.update({'res': res, 'd': dest, 'o': origin, 'dt': d_date})
        st.markdown(f"<h3>📅 Πρέπει να ξεκινήσει: {format_dt(res[0]['ship'])}</h3>", unsafe_allow_html=True)
        for i, leg in enumerate(res):
            st.markdown(f"""<div class="result-card">
            <div style="font-weight:bold; font-size:1.2em;">🚌 Σκέλος {i+1}: {leg['from']} ➡️ {leg['to']}</div>
            <div><span class="label">Αναχώρηση:</span> {format_dt(leg['ship'])}</div>
            <div><span class="label">Άφιξη:</span> {format_dt(leg['arrive'])}</div>
            </div>""", unsafe_allow_html=True)
    else: st.error("Δεν βρέθηκε διαθέσιμη διαδρομή.")

if 'res' in st.session_state:
    st.write("---")
    if st.button(f"🔄 Επιστροφή ({st.session_state['d']} ➡️ {st.session_state['o']})"):
        ret = find_forward(st.session_state['d'].upper(), st.session_state['o'].upper(), st.session_state['dt'] + timedelta(days=1))
        if ret:
            st.markdown(f"<h3>📅 Επιστροφή στην έδρα: {format_dt(ret[-1]['arrive'])}</h3>", unsafe_allow_html=True)
            for i, leg in enumerate(ret):
                st.markdown(f"""<div class="return-card">
                <div style="font-weight:bold; font-size:1.2em;">🔄 Σκέλος {i+1}: {leg['from']} ➡️ {leg['to']}</div>
                <div><span class="label">Αναχώρηση:</span> {format_dt(leg['ship'])}</div>
                <div><span class="label">Άφιξη:</span> {format_dt(leg['arrive'])}</div>
                </div>""", unsafe_allow_html=True)
