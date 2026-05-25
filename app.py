import streamlit as st
from datetime import datetime, timedelta
import collections

# 1. Βασική Ρύθμιση
st.set_page_config(page_title="Μεταγωγές", page_icon="🚌", layout="wide")

# 2. CSS - Dark Mode & Styling
st.markdown("""
    <style>
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMainViewContainer"] {
        background-color: #121212 !important;
    }
    .main-title {
        color: #ffffff;
        text-align: center;
        font-family: 'Arial Black', sans-serif;
        font-size: 50px !important;
        font-weight: bold;
        margin-top: -40px;
        padding-bottom: 20px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    .manos-footer {
        position: fixed;
        bottom: 20px;
        left: 20px;
        font-size: 26px !important; 
        color: #ffffff !important;
        font-weight: 900 !important;
        font-family: sans-serif;
        z-index: 9999;
        text-shadow: 1px 1px 3px #000;
    }
    .route-card {
        background-color: #ffffff !important;
        padding: 20px !important;
        border-radius: 15px !important;
        border-left: 15px solid #007bff !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5) !important;
        margin-bottom: 15px !important;
        color: #000000 !important;
    }
    .return-card {
        background-color: #ffffff !important;
        padding: 20px !important;
        border-radius: 15px !important;
        border-left: 15px solid #ff8c00 !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5) !important;
        margin-bottom: 15px !important;
        color: #000000 !important;
    }
    .stSelectbox label, .stDateInput label {
        color: #ffffff !important;
        font-weight: bold !important;
    }
    .label-blue { color: #0056b3; font-weight: bold; }
    .date-red { color: #d32f2f; font-weight: bold; }
    [data-testid="stHeader"] { background-color: rgba(0,0,0,0) !important; }
    </style>
    <div class="main-title">Μεταγωγές</div>
    """, unsafe_allow_html=True)

# --- ΔΕΔΟΜΕΝΑ ΔΡΟΜΟΛΟΓΙΩΝ ---
RAW_ROUTES = [
    {"from": "ΑΘΗΝΑ", "to": ["ΑΥΛΩΝΑΣ", "ΕΛΑΙΩΝΑΣ", "ΛΑΜΙΑ", "ΚΑΣΣΑΒΕΤΕΙΑ", "ΛΑΡΙΣΑ", "ΚΑΤΕΡΙΝΗ", "ΘΕΣΣΑΛΟΝΙΚΗ"], "days": [0, 3], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΚΟΡΙΝΘΟΣ", "ΝΑΥΠΛΙΟ", "ΤΥΡΙΝΘΑ", "ΤΡΙΠΟΛΗ", "ΚΑΛΑΜΑΤΑ"], "days": [2], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΤΡΙΚΑΛΑ", "ΓΡΕΒΕΝΑ", "ΑΥΛΩΝΑΣ"], "days": [0], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΧΑΛΚΙΔΑ"], "days": [1], "transit": 0},
    {"from": "ΑΘΗΝΑ", "to": ["ΧΑΝΙΑ", "ΗΡΑΚΛΕΙΟ", "ΚΡΗΤΗ", "ΡΟΔΟΣ", "ΚΕΡΚΥΡΑ"], "days": [4], "transit": 1},
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": ["ΣΕΡΡΕΣ", "ΔΡΑΜΑ", "ΚΑΒΑΛΑ", "ΞΑΝΘΗ", "ΚΟΜΟΤΗΝΗ", "ΑΛΕΞΑΝΔΡΟΥΠΟΛΗ"], "days": [1, 4], "transit": 0},
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": ["ΒΕΡΟΙΑ", "ΚΟΖΑΝΗ", "ΓΡΕΒΕΝΑ", "ΙΩΑΝΝΙΝΑ", "ΑΥΛΩΝΑΣ"], "days": [0], "transit": 0},
    {"from": "ΘΕΣΣΑΛΟΝΙΚΗ", "to": ["ΑΥΛΩΝΑΣ", "ΛΑΡΙΣΑ", "ΛΑΜΙΑ", "ΑΘΗΝΑ"], "days": [1, 4], "transit": 0},
    {"from": "ΑΥΛΩΝΑΣ", "to": ["ΑΘΗΝΑ", "ΛΑΜΙΑ", "ΛΑΡΙΣΑ", "ΘΕΣΣΑΛΟΝΙΚΗ"], "days": [0, 1, 3, 4], "transit": 0},
    {"from": "ΣΕΡΡΕΣ", "to": ["ΘΕΣΣΑΛΟΝΙΚΗ"], "days": [0, 1], "transit": 0},
    {"from": "ΙΩΑΝΝΙΝΑ", "to": ["ΑΡΤΑ", "ΑΓΡΙΝΙΟ", "ΠΑΤΡΑ", "ΑΙΓΙΟ", "ΚΟΡΙΝΘΟΣ", "ΑΘΗΝΑ"], "days": [1], "transit": 0},
    {"from": "ΠΑΤΡΑ", "to": ["ΑΘΗΝΑ", "ΚΟΡΙΝΘΟΣ", "ΑΙΓΙΟ"], "days": [0], "transit": 0},
    {"from": "ΛΑΡΙΣΑ", "to": ["ΒΟΛΟΣ", "ΛΑΜΙΑ", "ΑΥΛΩΝΑΣ", "ΑΘΗΝΑ"], "days": [0, 3], "transit": 0},
    {"from": "ΑΜΦΙΣΣΑ", "to": ["ΛΑΜΙΑ"], "days": [0, 1, 3, 4], "transit": 0},
    {"from": "ΛΑΜΙΑ", "to": ["ΑΜΦΙΣΣΑ", "ΔΟΜΟΚΟΣ", "ΑΥΛΩΝΑΣ", "ΑΘΗΝΑ"], "days": [0, 1, 3, 4], "transit": 0},
    {"from": "ΓΡΕΒΕΝΑ", "to": ["ΤΡΙΚΑΛΑ", "ΛΑΜΙΑ", "ΑΥΛΩΝΑΣ", "ΑΘΗΝΑ"], "days": [3], "transit": 0},
    {"from": ["ΚΑΛΑΜΑΤΑ", "ΤΡΙΠΟΛΗ"], "to": ["ΑΘΗΝΑ"], "days": [3], "transit": 0},
    {"from": ["ΑΛΕΞΑΝΔΡΟΥΠΟΛΗ", "ΞΑΝΘΗ", "ΣΕΡΡΕΣ"], "to": ["ΘΕΣΣΑΛΟΝΙΚΗ"], "days": [2, 5], "transit": 0},
]

HUB_MAP = {
    "ΑΜΦΙΣΣΑ": "ΛΑΜΙΑ", "ΔΟΜΟΚΟΣ": "ΛΑΜΙΑ", "ΚΑΡΠΕΝΗΣΙ": "ΛΑΜΙΑ", "ΘΗΒΑ": "ΕΛΑΙΩΝΑΣ", 
    "ΛΙΒΑΔΕΙΑ": "ΕΛΑΙΩΝΑΣ", "ΧΑΛΚΙΔΑ": "ΕΛΑΙΩΝΑΣ", "ΣΠΑΡΤΗ": "ΤΡΙΠΟΛΗ", "ΠΥΡΓΟΣ": "ΠΑΤΡΑ", 
    "ΑΡΓΟΣ": "ΝΑΥΠΛΙΟ", "ΒΟΛΟΣ": "ΛΑΡΙΣΑ", "ΚΑΡΔΙΤΣΑ": "ΤΡΙΚΑΛΑ", "ΠΡΕΒΕΖΑ": "ΑΡΤΑ", 
    "ΗΓΟΥΜΕΝΙΤΣΑ": "ΙΩΑΝΝΙΝΑ", "ΜΕΣΟΛΟΓΓΙ": "ΑΓΡΙΝΙΟ", "ΕΔΕΣΣΑ": "ΒΕΡΟΙΑ", "ΚΙΛΚΙΣ": "ΘΕΣΣΑΛΟΝΙΚΗ"
}

ROUTES = []
for r in RAW_ROUTES:
    origins = [r["from"]] if isinstance(r["from"], str) else r["from"]
    destinations = r["to"] if isinstance(r["to"], list) else [r["to"]]
    for o in origins:
        for d in destinations:
            ROUTES.append({"from": o.upper(), "to": d.upper(), "days": r["days"], "transit": r["transit"]})

ALL_CITIES = sorted(list(set([r["from"] for r in ROUTES] + list(HUB_MAP.keys()))))

def greek_day(date):
    return ["Δευτέρα", "Τρίτη", "Τετάρτη", "Πέμπτη", "Παρασκευή", "Σάββατο", "Κυριακή"][date.weekday()]

def format_dt(date):
    return f"<b>{date.strftime('%d/%m/%Y')}</b> <span class='date-red'>({greek_day(date)})</span>"

# --- ΜΗΧΑΝΗ ΑΝΑΖΗΤΗΣΗΣ (BFS - ΟΧΙ ΑΝΑΔΡΟΜΗ) ---
def iterative_find_path(start, end, start_date, mode='backward'):
    # Στο backward το start_date είναι το deadline. Στο forward είναι η ημερομηνία έναρξης.
    queue = collections.deque([(start, start_date, [])])
    visited = {}
    best_path = None

    while queue:
        curr_city, curr_date, path = queue.popleft()
        
        # Αν φτάσαμε στον προορισμό
        if curr_city == end:
            if mode == 'backward':
                if best_path is None or path[0]['ship'] > best_path[0]['ship']:
                    best_path = path
            else:
                if best_path is None or path[-1]['arrive'] < best_path[-1]['arrive']:
                    best_path = path
            continue

        # Αποφυγή ατέρμονων βρόχων (μέγιστο 5 στάσεις)
        if len(path) > 5: continue

        actual_end = HUB_MAP.get(curr_city, curr_city) if mode == 'forward' else curr_city
        
        for r in ROUTES:
            # Στο backward ψάχνουμε ποιος πάει στην curr_city
            if mode == 'backward' and r["to"] == (HUB_MAP.get(curr_city, curr_city)):
                ship = (curr_date - timedelta(days=1)) - timedelta(days=r["transit"])
                while ship.weekday() not in r["days"]: ship -= timedelta(days=1)
                arrive = ship + timedelta(days=r["transit"])
                
                # Έλεγχος αν έχουμε ήδη βρει καλύτερη ημερομηνία για αυτή την πόλη
                if r["from"] not in visited or ship > visited[r["from"]]:
                    visited[r["from"]] = ship
                    queue.append((r["from"], ship, [{"from": r["from"], "to": r["to"], "ship": ship, "arrive": arrive}] + path))
            
            # Στο forward ψάχνουμε πού πάει η curr_city
            elif mode == 'forward' and r["from"] == actual_end:
                ship = curr_date
                while ship.weekday() not in r["days"]: ship += timedelta(days=1)
                arrive = ship + timedelta(days=r["transit"])
                
                if r["to"] not in visited or arrive < visited[r["to"]]:
                    visited[r["to"]] = arrive
                    queue.append((r["to"], arrive + timedelta(days=1), path + [{"from": r["from"], "to": r["to"], "ship": ship, "arrive": arrive}]))

    return best_path

# --- UI ---
c1, c2, c3 = st.columns(3)
origin = c1.selectbox("📍 Αφετηρία:", ALL_CITIES, index=ALL_CITIES.index("ΣΕΡΡΕΣ"))
dest = c2.selectbox("🏁 Προορισμός:", ALL_CITIES, index=ALL_CITIES.index("ΑΘΗΝΑ"))
d_date = c3.date_input("📅 Παράδοση:", datetime.now() + timedelta(days=5))

if st.button("🚀 Υπολογισμός Δρομολογίου"):
    res = iterative_find_path(origin.upper(), dest.upper(), d_date, 'backward')
    if res:
        st.session_state['res'] = res
        st.session_state['o'] = origin
        st.session_state['d'] = dest
        st.session_state['dt'] = d_date
        st.session_state['ret'] = None
    else: st.error("Δεν βρέθηκε διαδρομή.")

if 'res' in st.session_state and st.session_state['res']:
    st.markdown(f"<h3 style='color:white;'>🗓️ Πρέπει να ξεκινήσει: {format_dt(st.session_state['res'][0]['ship'])}</h3>", unsafe_allow_html=True)
    for i, leg in enumerate(st.session_state['res']):
        st.markdown(f"""<div class="route-card"><div style="font-weight:bold; font-size:1.2em; color:#0056b3;">🚌 Σκέλος {i+1}: {leg['from']} ➡️ {leg['to']}</div>
        <div><span class="label-blue">Αναχώρηση:</span> {format_dt(leg['ship'])} | <span class="label-blue">Άφιξη:</span> {format_dt(leg['arrive'])}</div></div>""", unsafe_allow_html=True)
    
    if st.button(f"🔄 Υπολογισμός Επιστροφής"):
        with st.spinner('Υπολογισμός...'):
            ret_path = iterative_find_path(st.session_state['d'].upper(), st.session_state['o'].upper(), st.session_state['dt'] + timedelta(days=1), 'forward')
            st.session_state['ret'] = ret_path
            if not ret_path: st.error("Δεν βρέθηκε διαδρομή επιστροφής.")

if 'ret' in st.session_state and st.session_state['ret']:
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color:white;'>🗓️ Επιστροφή στην έδρα: {format_dt(st.session_state['ret'][-1]['arrive'])}</h3>", unsafe_allow_html=True)
    for i, leg in enumerate(st.session_state['ret']):
        st.markdown(f"""<div class="return-card"><div style="font-weight:bold; font-size:1.2em; color:#cc5500;">🔄 Σκέλος {i+1}: {leg['from']} ➡️ {leg['to']}</div>
        <div><span class="label-blue">Αναχώρηση:</span> {format_dt(leg['ship'])} | <span class="label-blue">Άφιξη:</span> {format_dt(leg['arrive'])}</div></div>""", unsafe_allow_html=True)

# by Manos
st.markdown('<div class="manos-footer">by Manos</div>', unsafe_allow_html=True)
