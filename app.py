import streamlit as st
from datetime import datetime, timedelta

# 1. Ρύθμιση Σελίδας
st.set_page_config(page_title="Μεταγωγές", page_icon="🚌", layout="wide")

# 2. CSS για Εσωτερικό Γκρι Φόντο και Κάρτες
st.markdown("""
    <style>
    /* Δημιουργούμε ένα γκρίζο πλαίσιο για όλο το περιεχόμενο */
    .main-container {
        background-color: #f0f2f6;
        padding: 30px;
        border-radius: 15px;
        color: #111;
    }
    
    .app-title {
        color: #002b5c;
        text-align: center;
        font-family: sans-serif;
        font-size: 40px;
        font-weight: bold;
        margin-bottom: 20px;
    }

    .route-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border-left: 10px solid #0056b3;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }

    .return-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border-left: 10px solid #ff8c00;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }

    .footer {
        text-align: left;
        font-size: 12px;
        color: #666;
        font-style: italic;
        margin-top: 50px;
    }

    .label { font-weight: bold; color: #0056b3; }
    .val { color: #d32f2f; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- ΔΕΔΟΜΕΝΑ ΠΟΛΕΩΝ & ΔΡΟΜΟΛΟΓΙΩΝ ---
# Όλες οι πόλεις που υπάγονται σε Hubs βάσει Π.Δ.
HUB_MAP = {
    "ΑΜΦΙΣΣΑ": "ΛΑΜΙΑ", "ΔΟΜΟΚΟΣ": "ΛΑΜΙΑ", "ΚΑΡΠΕΝΗΣΙ": "ΛΑΜΙΑ", 
    "ΘΗΒΑ": "ΕΛΑΙΩΝΑΣ", "ΛΙΒΑΔΕΙΑ": "ΕΛΑΙΩΝΑΣ", "ΧΑΛΚΙΔΑ": "ΕΛΑΙΩΝΑΣ",
    "ΣΠΑΡΤΗ": "ΤΡΙΠΟΛΗ", "ΠΥΡΓΟΣ": "ΠΑΤΡΑ", "ΑΜΑΛΙΑΔΑ": "ΠΑΤΡΑ", "ΑΡΓΟΣ": "ΝΑΥΠΛΙΟ",
    "ΒΟΛΟΣ": "ΛΑΡΙΣΑ", "ΚΑΡΔΙΤΣΑ": "ΤΡΙΚΑΛΑ", "ΠΡΕΒΕΖΑ": "ΑΡΤΑ", "ΗΓΟΥΜΕΝΙΤΣΑ": "ΙΩΑΝΝΙΝΑ",
    "ΜΕΣΟΛΟΓΓΙ": "ΑΓΡΙΝΙΟ", "ΕΔΕΣΣΑ": "ΒΕΡΟΙΑ", "ΦΛΩΡΙΝΑ": "ΚΟΖΑΝΗ", "ΚΑΣΤΟΡΙΑ": "ΚΟΖΑΝΗ",
    "ΚΙΛΚΙΣ": "ΘΕΣΣΑΛΟΝΙΚΗ", "ΠΟΛΥΓΥΡΟΣ": "ΘΕΣΣΑΛΟΝΙΚΗ", "ΓΙΑΝΝΙΤΣΑ": "ΘΕΣΣΑΛΟΝΙΚΗ",
    "ΣΑΜΟΣ": "ΑΘΗΝΑ", "ΡΟΔΟΣ": "ΑΘΗΝΑ", "ΜΥΤΙΛΗΝΗ": "ΑΘΗΝΑ", "ΚΕΡΚΥΡΑ": "ΙΩΑΝΝΙΝΑ",
    "ΗΡΑΚΛΕΙΟ": "ΚΡΗΤΗ", "ΧΑΝΙΑ": "ΚΡΗΤΗ", "ΡΕΘΥΜΝΟ": "ΚΡΗΤΗ", "ΑΓΙΟΣ ΝΙΚΟΛΑΟΣ": "ΚΡΗΤΗ"
}

RAW_ROUTES = [
    {"from": "ΑΘΗΝΑ", "to": ["ΑΥΛΩΝΑΣ", "ΕΛΑΙΩΝΑΣ", "ΛΑΜΙΑ", "ΚΑΣΣΑΒΕΤΕΙΑ", "ΛΑΡΙΣΑ", "ΚΑΤΕΡΙΝΗ", "ΘΕΣΣΑΛΟΝΙΚΗ"], "days": [0, 3], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΚΟΡΙΝΘΟΣ", "ΝΑΥΠΛΙΟ", "ΤΡΙΠΟΛΗ", "ΚΑΛΑΜΑΤΑ"], "days": [2], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΤΡΙΚΑΛΑ", "ΓΡΕΒΕΝΑ"], "days": [0], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΚΡΗΤΗ"], "days": [4], "transit": 1},
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": ["ΣΕΡΡΕΣ", "ΔΡΑΜΑ", "ΚΑΒΑΛΑ", "ΞΑΝΘΗ", "ΚΟΜΟΤΗΝΗ", "ΑΛΕΞΑΝΔΡΟΥΠΟΛΗ"], "days": [1, 4], "transit": 0},
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": ["ΒΕΡΟΙΑ", "ΚΟΖΑΝΗ", "ΓΡΕΒΕΝΑ", "ΙΩΑΝΝΙΝΑ"], "days": [0], "transit": 0},
    {"from": "ΣΕΡΡΕΣ", "to": ["ΘΕΣΣΑΛΟΝΙΚΗ"], "days": [0, 1], "transit": 0},
    {"from": "ΙΩΑΝΝΙΝΑ", "to": ["ΑΡΤΑ", "ΑΓΡΙΝΙΟ", "ΠΑΤΡΑ", "ΑΘΗΝΑ"], "days": [1], "transit": 0},
    {"from": "ΠΑΤΡΑ", "to": ["ΚΟΡΙΝΘΟΣ", "ΑΘΗΝΑ"], "days": [0], "transit": 0},
    {"from": "ΛΑΡΙΣΑ", "to": ["ΒΟΛΟΣ", "ΛΑΜΙΑ", "ΑΘΗΝΑ"], "days": [3, 0], "transit": 0},
    {"from": "ΑΜΦΙΣΣΑ", "to": ["ΛΑΜΙΑ"], "days": [0, 1, 3, 4], "transit": 0},
    {"from": "ΛΑΜΙΑ", "to": ["ΑΜΦΙΣΣΑ", "ΔΟΜΟΚΟΣ"], "days": [0, 1, 2, 3, 4], "transit": 0},
    {"from": ["ΘΕΣΣΑΛΟΝΙΚΗ", "ΛΑΡΙΣΑ", "ΛΑΜΙΑ"], "to": ["ΑΘΗΝΑ"], "days": [1, 4], "transit": 0},
    {"from": ["ΚΑΛΑΜΑΤΑ", "ΤΡΙΠΟΛΗ"], "to": ["ΑΘΗΝΑ"], "days": [3], "transit": 0},
    {"from": "ΚΡΗΤΗ", "to": ["ΑΘΗΝΑ"], "days": [5], "transit": 1},
]

# Προετοιμασία
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
    return f"<b>{date.strftime('%d/%m/%Y')}</b> <span class='val'>({greek_day(date)})</span>"

# --- ΜΗΧΑΝΕΣ ΑΝΑΖΗΤΗΣΗΣ ---
def find_path(start, end, deadline, mode='backward'):
    if mode == 'backward':
        target_arr = deadline - timedelta(days=1)
        act_end = HUB_MAP.get(end, end)
        best = None
        for r in ROUTES:
            if r["to"] == act_end:
                ship = target_arr - timedelta(days=r["transit"])
                while ship.weekday() not in r["days"]: ship -= timedelta(days=1)
                prefix = find_path(start, r["from"], ship, 'backward') if r["from"] != start else []
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
                suffix = find_path(r["to"], end, ship + timedelta(days=1), 'forward') if r["to"] != end else []
                if suffix is not None:
                    path = [{"from": r["from"], "to": r["to"], "ship": ship, "arrive": ship + timedelta(days=r["transit"])}] + suffix
                    if best is None or path[-1]["arrive"] < best[-1]["arrive"]: best = path
        return best

# --- UI (WRAP EVERYTHING IN A DIV) ---
st.markdown('<div class="main-container">', unsafe_allow_html=True)
st.markdown('<div class="app-title">Μεταγωγές</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
origin = c1.selectbox("📍 Αφετηρία:", ALL_CITIES, index=ALL_CITIES.index("ΣΕΡΡΕΣ"))
dest = c2.selectbox("🏁 Προορισμός:", ALL_CITIES, index=ALL_CITIES.index("ΑΘΗΝΑ"))
d_date = c3.date_input("📅 Παράδοση:", datetime.now() + timedelta(days=5))

if st.button("🚀 Υπολογισμός"):
    res = find_path(origin.upper(), dest.upper(), d_date, 'backward')
    if res:
        st.session_state.update({'res': res, 'd': dest, 'o': origin, 'dt': d_date})
        st.markdown(f"### 🗓️ Πρέπει να ξεκινήσει: {format_dt(res[0]['ship'])}", unsafe_allow_html=True)
        for i, leg in enumerate(res):
            st.markdown(f"""<div class="route-card">
            <div style="font-weight:bold; font-size:1.2em; color:#0056b3;">🚌 Σκέλος {i+1}: {leg['from']} ➡️ {leg['to']}</div>
            <div><span class="label">Αναχώρηση:</span> {format_dt(leg['ship'])} | <span class="label">Άφιξη:</span> {format_dt(leg['arrive'])}</div>
            </div>""", unsafe_allow_html=True)
    else: st.error("Δεν βρέθηκε διαδρομή.")

if 'res' in st.session_state:
    if st.button(f"🔄 Επιστροφή ({st.session_state['d']} ➡️ {st.session_state['o']})"):
        ret = find_path(st.session_state['d'].upper(), st.session_state['o'].upper(), st.session_state['dt'] + timedelta(days=1), 'forward')
        if ret:
            st.markdown(f"### 🗓️ Επιστροφή στην έδρα: {format_dt(ret[-1]['arrive'])}", unsafe_allow_html=True)
            for i, leg in enumerate(ret):
                st.markdown(f"""<div class="return-card">
                <div style="font-weight:bold; font-size:1.2em; color:#ff8c00;">🔄 Σκέλος {i+1}: {leg['from']} ➡️ {leg['to']}</div>
                <div><span class="label">Αναχώρηση:</span> {format_dt(leg['ship'])} | <span class="label">Άφιξη:</span> {format_dt(leg['arrive'])}</div>
                </div>""", unsafe_allow_html=True)

st.markdown('<div class="footer">by Manos</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True) # Κλείσιμο main-container
