import streamlit as st
import mysql.connector
import pandas as pd
import datetime

st.set_page_config(
    page_title="Thread Suite Pro",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');
html, body, [class*="css"], .stApp {
    background-color: #FDFBF7 !important;
    color: #111111 !important;
    font-family: 'Outfit', sans-serif !important;
}
footer, #MainMenu, header[data-testid="stHeader"],
div[data-testid="stToolbar"], div[data-testid="stDecoration"],
div[data-testid="stStatusWidget"], .stDeployButton,
._profileContainer_gzau3_53, ._profilePreview_gzau3_63,
section[data-testid="stBottom"], a[href*="github.com"],
[data-testid="stActionButton"] {
    display: none !important;
}
h1, h2, h3 {
    font-family: 'Playfair Display', serif !important;
    color: #111111 !important;
}
label, div[data-testid="stWidgetLabel"] p {
    color: #333333 !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
}
.stTextInput>div>div>input,
.stNumberInput>div>div>input,
.stTextArea>div>div>textarea,
.stSelectbox>div>div>div {
    background-color: #ffffff !important;
    color: #111111 !important;
    border: 1.5px solid #E0D8CC !important;
    border-radius: 6px !important;
}
section[data-testid="stSidebar"] {
    background-color: #111111 !important;
}
section[data-testid="stSidebar"] * { color: #FDFBF7 !important; }
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] div[data-testid="stWidgetLabel"] p {
    color: #C4882A !important;
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
}
.stButton>button {
    background-color: #111111 !important;
    color: #FDFBF7 !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    font-size: 0.8rem !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    border: 1.5px solid #111111 !important;
}
.stButton>button:hover {
    background-color: #C4882A !important;
    border-color: #C4882A !important;
}
div[data-testid="stMetricContainer"] {
    background: #ffffff !important;
    border: 1.5px solid #E0D8CC !important;
    border-radius: 10px !important;
    padding: 18px !important;
}
div[data-testid="stMetricValue"] > div {
    font-family: 'Playfair Display', serif !important;
    font-size: 2rem !important;
    color: #C4882A !important;
}
div[data-testid="stMetricLabel"] > div {
    font-size: 0.7rem !important;
    text-transform: uppercase !important;
    letter-spacing: 2px !important;
    color: #888 !important;
}
.stForm {
    background: #ffffff !important;
    border: 1.5px solid #E0D8CC !important;
    border-radius: 10px !important;
    padding: 24px !important;
}
.stDataFrame {
    border-radius: 8px !important;
    border: 1.5px solid #E0D8CC !important;
}
.stTabs [data-baseweb="tab-list"] {
    background: #F0EBE3;
    border-radius: 8px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 6px !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    color: #666 !important;
}
.stTabs [aria-selected="true"] {
    background: #ffffff !important;
    color: #C4882A !important;
}
.result-card {
    background: #ffffff;
    border: 1.5px solid #E0D8CC;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 10px;
    border-left: 4px solid #C4882A;
}
</style>
""", unsafe_allow_html=True)

# ── DATABASE ──────────────────────────────────────────────────
@st.cache_resource(ttl=30)
def get_conn():
    try:
        if "mysql" not in st.secrets:
            return False, None
        c = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            port=int(st.secrets["mysql"]["port"]),
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"].get("database", "thread_business"),
            autocommit=True,
            connection_timeout=10,
        )
        return True, c
    except Exception:
        return False, None

db_ok, db_conn = get_conn()

def qry(sql, params=None, fetch=False):
    if not db_ok or db_conn is None:
        return pd.DataFrame() if fetch else None
    try:
        try:
            db_conn.ping(reconnect=True, attempts=3, delay=2)
        except Exception:
            get_conn.clear()
            return pd.DataFrame() if fetch else None
        cur = db_conn.cursor(dictionary=True)
        cur.execute(sql, params or ())
        if fetch:
            rows = cur.fetchall()
            cur.close()
            return pd.DataFrame(rows) if rows else pd.DataFrame()
        cur.close()
        return True
    except Exception:
        return pd.DataFrame() if fetch else None

def qry_one(sql, params=None):
    df = qry(sql, params, fetch=True)
    return df.iloc[0].to_dict() if df is not None and not df.empty else {}

def today():
    return datetime.date.today().isoformat()

# ── DEMO DATA ─────────────────────────────────────────────────
def init_demo():
    if "threads" not in st.session_state:
        st.session_state.threads = [
            {"thread_code": "T10", "thread_name": "Red Cotton 40/2",  "category": "Cotton",    "current_stock": 620, "unit": "Cone",  "low_stock_threshold": 50},
            {"thread_code": "T20", "thread_name": "White Silk 30D",   "category": "Silk",      "current_stock": 180, "unit": "Spool", "low_stock_threshold": 20},
            {"thread_code": "T30", "thread_name": "Black Poly 120D",  "category": "Polyester", "current_stock": 12,  "unit": "Cone",  "low_stock_threshold": 30},
        ]
    if "sellers" not in st.session_state:
        st.session_state.sellers = [
            {"id": 1, "name": "Rahim Traders",  "phone": "01711223344", "address": "Mirpur, Dhaka",  "thread_codes": "T10, T20"},
            {"id": 2, "name": "Karim Fabrics",  "phone": "01822334455", "address": "Gulshan, Dhaka", "thread_codes": "T30"},
        ]
    if "customers" not in st.session_state:
        st.session_state.customers = [
            {"id": 1, "name": "Apex Apparel",   "phone": "01933445566", "address": "Uttara, Dhaka",  "thread_codes": "T10, T30"},
            {"id": 2, "name": "Envoy Outlets",  "phone": "01644556677", "address": "Banani, Dhaka",  "thread_codes": "T20"},
        ]
    if "transactions" not in st.session_state:
        st.session_state.transactions = [
            {"id": 1, "transaction_date": today(), "transaction_type": "SELL", "thread_code": "T10", "party_name": "Apex Apparel", "quantity": 100, "notes": ""},
        ]
    if "store_name" not in st.session_state:
        st.session_state.store_name = "My Thread Business"

init_demo()

# ── SIDEBAR ───────────────────────────────────────────────────
if db_ok:
    row = qry_one("SELECT setting_value FROM store_settings WHERE setting_key='store_name'")
    store_name = row.get("setting_value", "Thread Suite Pro") if row else "Thread Suite Pro"
else:
    store_name = st.session_state.get("store_name", "Thread Suite Pro")

st.sidebar.markdown(f"""
<div style='padding:6px 0 20px'>
  <div style='font-family:"Playfair Display",serif;font-size:1.3rem;color:#E8A83A'>{store_name}</div>
  <div style='font-size:0.6rem;color:#C4882A;letter-spacing:3px;margin-top:4px;text-transform:uppercase'>Business Suite</div>
</div>
""", unsafe_allow_html=True)

if db_ok:
    st.sidebar.markdown("<div style='background:#1a2e1a;border:1px solid #2d5a2d;border-radius:6px;padding:7px 12px;font-size:0.7rem;color:#7ecf7e;margin-bottom:12px'>Connected to Database</div>", unsafe_allow_html=True)
else:
    st.sidebar.markdown("<div style='background:#2e1a1a;border:1px solid #5a2d2d;border-radius:6px;padding:7px 12px;font-size:0.7rem;color:#cf7e7e;margin-bottom:12px'>Demo Mode — No DB</div>", unsafe_allow_html=True)

PAGES = [
    "Dashboard",
    "Inventory and Stock",
    "Seller Directory",
    "Customer Directory",
    "Transactions",
    "Search",
    "Settings",
]
page = st.sidebar.radio("", PAGES, label_visibility="collapsed")
st.sidebar.markdown(f"<div style='font-size:0.65rem;color:#555;margin-top:12px'>{today()}</div>", unsafe_allow_html=True)

def page_title(label, title, sub=""):
    mb = "4px" if sub else "16px"
    st.markdown(f"<p style='text-transform:uppercase;letter-spacing:3px;color:#C4882A;font-size:0.7rem;margin-bottom:2px'>{label}</p>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='margin-top:0;font-size:2rem;margin-bottom:{mb}'>{title}</h1>", unsafe_allow_html=True)
    if sub:
        st.markdown(f"<p style='color:#888;font-size:0.82rem;margin-top:0;margin-bottom:16px'>{sub}</p>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════
if page == "Dashboard":
    page_title("Overview", "Dashboard", "Live business summary")

    if db_ok:
        t_count   = qry_one("SELECT COUNT(*) as c FROM threads").get("c", 0)
        s_count   = qry_one("SELECT COUNT(*) as c FROM sellers").get("c", 0)
        c_count   = qry_one("SELECT COUNT(*) as c FROM customers").get("c", 0)
        low_count = qry_one("SELECT COUNT(*) as c FROM threads WHERE current_stock <= low_stock_threshold").get("c", 0)
        today_qty = qry_one(f"SELECT COALESCE(SUM(quantity),0) as v FROM transactions WHERE transaction_type='SELL' AND transaction_date='{today()}'").get("v", 0)
        total_qty = qry_one("SELECT COALESCE(SUM(quantity),0) as v FROM transactions WHERE transaction_type='SELL'").get("v", 0)
    else:
        t_count   = len(st.session_state.threads)
        s_count   = len(st.session_state.sellers)
        c_count   = len(st.session_state.customers)
        low_count = sum(1 for t in st.session_state.threads if t["current_stock"] <= t["low_stock_threshold"])
        today_qty = sum(t["quantity"] for t in st.session_state.transactions if t["transaction_type"] == "SELL" and t["transaction_date"] == today())
        total_qty = sum(t["quantity"] for t in st.session_state.transactions if t["transaction_type"] == "SELL")

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Thread Types",  t_count)
    c2.metric("Sellers",       s_count)
    c3.metric("Customers",     c_count)
    c4.metric("Low Stock",     low_count)
    c5.metric("Sold Today",    today_qty)
    c6.metric("Total Sold",    total_qty)

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Recent Transactions")
        if db_ok:
            df = qry("SELECT transaction_date, transaction_type, thread_code, party_name, quantity FROM transactions ORDER BY id DESC LIMIT 10", fetch=True)
        else:
            df = pd.DataFrame(st.session_state.transactions).sort_values("id", ascending=False).head(10)
        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No transactions yet.")

    with col2:
        st.markdown("### Low Stock Alerts")
        if db_ok:
            ldf = qry("SELECT thread_code, thread_name, current_stock, unit, low_stock_threshold FROM threads WHERE current_stock <= low_stock_threshold ORDER BY current_stock ASC LIMIT 8", fetch=True)
        else:
            ldf = pd.DataFrame([t for t in st.session_state.threads if t["current_stock"] <= t["low_stock_threshold"]])
        if ldf is not None and not ldf.empty:
            st.dataframe(ldf, use_container_width=True, hide_index=True)
        else:
            st.success("All stock levels are OK.")

# ══════════════════════════════════════════════════════════════
# INVENTORY AND STOCK
# ══════════════════════════════════════════════════════════════
elif page == "Inventory and Stock":
    page_title("Inventory", "Inventory and Stock", "Manage your thread catalog and stock volumes")

    tab1, tab2, tab3 = st.tabs(["View Stock", "Add Thread", "Stock Movement"])

    with tab1:
        sq = st.text_input("", placeholder="Search by code, name, category...", label_visibility="collapsed", key="inv_search")
        if db_ok:
            sql = "SELECT thread_code, thread_name, category, current_stock, unit, low_stock_threshold FROM threads"
            params = []
            if sq:
                sql += " WHERE LOWER(thread_code) LIKE %s OR LOWER(thread_name) LIKE %s OR LOWER(category) LIKE %s"
                like = f"%{sq.lower()}%"
                params = [like, like, like]
            sql += " ORDER BY thread_name"
            df = qry(sql, params or None, fetch=True)
        else:
            df = pd.DataFrame(st.session_state.threads)
            if sq:
                df = df[df.apply(lambda r: any(sq.lower() in str(r[c]).lower() for c in ["thread_code", "thread_name", "category"]), axis=1)]

        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No products found.")

        if db_ok:
            all_df = qry("SELECT thread_code, thread_name, current_stock, unit, category, low_stock_threshold FROM threads ORDER BY thread_name", fetch=True)
        else:
            all_df = pd.DataFrame(st.session_state.threads)

        if all_df is not None and not all_df.empty:
            st.markdown("---")
            st.markdown("#### Edit or Delete a Thread")
            codes = list(all_df["thread_code"])
            chosen = st.selectbox("Select thread to edit or delete", ["-- Select --"] + codes, key="inv_edit_sel")
            if chosen != "-- Select --":
                row = all_df[all_df["thread_code"] == chosen].iloc[0]
                with st.form("edit_thread_form"):
                    c1, c2 = st.columns(2)
                    new_name = c1.text_input("Product Name", value=str(row.get("thread_name", "")))
                    new_cat  = c2.text_input("Category",     value=str(row.get("category", "")))
                    c3, c4  = st.columns(2)
                    new_stk  = c3.number_input("Current Stock", value=int(row.get("current_stock", 0)), min_value=0)
                    unit_opts = ["Cone", "Spool", "kg", "Box", "Bundle", "Piece", "Dozen"]
                    cur_unit  = str(row.get("unit", "Cone"))
                    unit_idx  = unit_opts.index(cur_unit) if cur_unit in unit_opts else 0
                    new_unit  = c4.selectbox("Unit", unit_opts, index=unit_idx)
                    new_low   = st.number_input("Low Stock Alert At", value=int(row.get("low_stock_threshold", 10)), min_value=1)
                    ce1, ce2  = st.columns(2)
                    if ce1.form_submit_button("Save Changes"):
                        if db_ok:
                            qry("UPDATE threads SET thread_name=%s, category=%s, current_stock=%s, unit=%s, low_stock_threshold=%s WHERE thread_code=%s",
                                (new_name, new_cat, new_stk, new_unit, new_low, chosen))
                        else:
                            for t in st.session_state.threads:
                                if t["thread_code"] == chosen:
                                    t.update({"thread_name": new_name, "current_stock": new_stk, "unit": new_unit})
                        st.success("Updated successfully.")
                        st.rerun()
                    if ce2.form_submit_button("Delete Thread"):
                        if db_ok:
                            qry("DELETE FROM threads WHERE thread_code=%s", (chosen,))
                        else:
                            st.session_state.threads = [t for t in st.session_state.threads if t["thread_code"] != chosen]
                        st.success("Deleted.")
                        st.rerun()

    with tab2:
        with st.form("add_thread_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            t_code = c1.text_input("SKU / Code  (e.g. T10)")
            t_name = c2.text_input("Product Name  (e.g. Red Cotton 40/2)")
            c3, c4, c5 = st.columns(3)
            t_cat  = c3.text_input("Category  (e.g. Cotton)")
            t_unit = c4.selectbox("Unit", ["Cone", "Spool", "kg", "Box", "Bundle", "Piece", "Dozen"])
            t_qty  = c5.number_input("Opening Stock", min_value=0, step=1)
            t_low  = st.number_input("Low Stock Alert At", min_value=1, value=10)
            if st.form_submit_button("Save Thread"):
                if not t_code or not t_name:
                    st.error("Code and Name are required.")
                else:
                    if db_ok:
                        qry("""INSERT INTO threads (thread_code, thread_name, category, current_stock, unit, low_stock_threshold)
                               VALUES (%s, %s, %s, %s, %s, %s)
                               ON DUPLICATE KEY UPDATE thread_name=%s, category=%s, unit=%s,
                               low_stock_threshold=%s, current_stock=current_stock+%s""",
                            (t_code.strip(), t_name.strip(), t_cat.strip(), t_qty, t_unit, t_low,
                             t_name.strip(), t_cat.strip(), t_unit, t_low, t_qty))
                    else:
                        existing = next((t for t in st.session_state.threads if t["thread_code"] == t_code.strip()), None)
                        if existing:
                            existing["current_stock"] += t_qty
                        else:
                            st.session_state.threads.append({
                                "thread_code": t_code.strip(), "thread_name": t_name.strip(),
                                "category": t_cat.strip(), "current_stock": t_qty,
                                "unit": t_unit, "low_stock_threshold": t_low
                            })
                    st.success(f"Thread '{t_name}' saved.")
                    st.rerun()

    with tab3:
        if db_ok:
            t_df = qry("SELECT thread_code, thread_name FROM threads ORDER BY thread_name", fetch=True)
            t_names = list(t_df["thread_name"]) if t_df is not None and not t_df.empty else []
            t_map   = dict(zip(t_df["thread_name"], t_df["thread_code"])) if t_df is not None and not t_df.empty else {}
        else:
            t_names = [t["thread_name"] for t in st.session_state.threads]
            t_map   = {t["thread_name"]: t["thread_code"] for t in st.session_state.threads}

        if not t_names:
            st.warning("Add threads first.")
        else:
            with st.form("stock_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                mv_prod = c1.selectbox("Thread", t_names)
                mv_type = c2.selectbox("Movement Type", ["BUY - Stock IN", "SELL - Stock OUT", "DAMAGED", "RETURN"])
                c3, c4  = st.columns(2)
                mv_qty  = c3.number_input("Quantity", min_value=1, step=1)
                mv_date = c4.date_input("Date", value=datetime.date.today())
                mv_party = st.text_input("Supplier or Customer Name")
                mv_note  = st.text_input("Notes (optional)")
                if st.form_submit_button("Save Movement"):
                    t_code2  = t_map.get(mv_prod, "")
                    tx_type  = "BUY" if "BUY" in mv_type else ("SELL" if "SELL" in mv_type else mv_type.split(" ")[0])
                    if db_ok:
                        qry("INSERT INTO transactions (transaction_date, transaction_type, thread_code, party_name, quantity, notes) VALUES (%s,%s,%s,%s,%s,%s)",
                            (mv_date.isoformat(), tx_type, t_code2, mv_party, mv_qty, mv_note))
                        if tx_type in ("BUY", "RETURN"):
                            qry("UPDATE threads SET current_stock=current_stock+%s WHERE thread_code=%s", (mv_qty, t_code2))
                        else:
                            qry("UPDATE threads SET current_stock=GREATEST(current_stock-%s,0) WHERE thread_code=%s", (mv_qty, t_code2))
                    else:
                        for t in st.session_state.threads:
                            if t["thread_code"] == t_code2:
                                if tx_type in ("BUY", "RETURN"):
                                    t["current_stock"] += mv_qty
                                else:
                                    t["current_stock"] = max(t["current_stock"] - mv_qty, 0)
                        nid = len(st.session_state.transactions) + 1
                        st.session_state.transactions.append({
                            "id": nid, "transaction_date": mv_date.isoformat(),
                            "transaction_type": tx_type, "thread_code": t_code2,
                            "party_name": mv_party, "quantity": mv_qty, "notes": mv_note
                        })
                    st.success(f"Movement saved. Type: {tx_type}, Qty: {mv_qty}")
                    st.rerun()

# ══════════════════════════════════════════════════════════════
# SELLER DIRECTORY
# ══════════════════════════════════════════════════════════════
elif page == "Seller Directory":
    page_title("Records", "Seller Directory", "Who sells which threads")

    tab1, tab2 = st.tabs(["View and Manage", "Add Seller"])

    with tab1:
        sq = st.text_input("", placeholder="Search by name, phone, address, or thread code...", label_visibility="collapsed", key="sell_search")
        if db_ok:
            sql = "SELECT id, name, phone, address, thread_codes FROM sellers"
            params = []
            if sq:
                like = f"%{sq.strip().lower()}%"
                sql += " WHERE LOWER(name) LIKE %s OR LOWER(phone) LIKE %s OR LOWER(address) LIKE %s OR LOWER(thread_codes) LIKE %s"
                params = [like, like, like, like]
            sql += " ORDER BY name"
            sdf = qry(sql, params or None, fetch=True)
        else:
            sdf = pd.DataFrame(st.session_state.sellers)
            if sq:
                sdf = sdf[sdf.apply(lambda r: any(sq.lower() in str(r[c]).lower() for c in ["name", "phone", "address", "thread_codes"]), axis=1)]

        if sdf is not None and not sdf.empty:
            st.markdown(f"{len(sdf)} seller(s) found")
            for _, row in sdf.iterrows():
                with st.expander(f"{row['name']}  |  {row.get('phone', '--')}  |  Threads: {row.get('thread_codes', '--')}"):
                    st.write(f"**Phone:** {row.get('phone', '--')}")
                    st.write(f"**Address:** {row.get('address', '--')}")
                    st.write(f"**Thread Codes:** {row.get('thread_codes', 'None assigned')}")
                    with st.form(f"edit_seller_{row['id']}"):
                        ef1, ef2 = st.columns(2)
                        en = ef1.text_input("Name",    value=str(row.get("name", "")),         key=f"sn_{row['id']}")
                        ep = ef2.text_input("Phone",   value=str(row.get("phone", "")),        key=f"sp_{row['id']}")
                        ea = ef1.text_input("Address", value=str(row.get("address", "")),      key=f"sa_{row['id']}")
                        et = ef2.text_input("Thread Codes (e.g. T10, T20, T30)", value=str(row.get("thread_codes", "")), key=f"st_{row['id']}")
                        sb1, sb2 = st.columns(2)
                        if sb1.form_submit_button("Save Changes"):
                            if db_ok:
                                qry("UPDATE sellers SET name=%s, phone=%s, address=%s, thread_codes=%s WHERE id=%s",
                                    (en.strip(), ep.strip(), ea.strip(), et.strip(), row["id"]))
                            else:
                                for s in st.session_state.sellers:
                                    if s["id"] == row["id"]:
                                        s.update({"name": en, "phone": ep, "address": ea, "thread_codes": et})
                            st.success("Updated.")
                            st.rerun()
                        if sb2.form_submit_button("Delete Seller"):
                            if db_ok:
                                qry("DELETE FROM sellers WHERE id=%s", (row["id"],))
                            else:
                                st.session_state.sellers = [s for s in st.session_state.sellers if s["id"] != row["id"]]
                            st.success(f"Deleted {row['name']}.")
                            st.rerun()
        else:
            st.info("No sellers found.")

    with tab2:
        with st.form("add_seller_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            s_name    = c1.text_input("Seller Name")
            s_phone   = c2.text_input("Phone Number")
            s_address = c1.text_input("Address")
            s_threads = c2.text_input("Thread Codes they sell  (e.g. T10, T20, T30)")
            s_notes   = st.text_area("Notes (optional)")
            if st.form_submit_button("Register Seller"):
                if not s_name or not s_phone:
                    st.error("Name and phone are required.")
                else:
                    if db_ok:
                        qry("INSERT INTO sellers (name, phone, address, thread_codes, notes) VALUES (%s,%s,%s,%s,%s)",
                            (s_name.strip(), s_phone.strip(), s_address.strip(), s_threads.strip(), s_notes.strip()))
                    else:
                        nid = max((s["id"] for s in st.session_state.sellers), default=0) + 1
                        st.session_state.sellers.append({
                            "id": nid, "name": s_name, "phone": s_phone,
                            "address": s_address, "thread_codes": s_threads
                        })
                    st.success(f"Seller '{s_name}' registered.")
                    st.rerun()

# ══════════════════════════════════════════════════════════════
# CUSTOMER DIRECTORY
# ══════════════════════════════════════════════════════════════
elif page == "Customer Directory":
    page_title("Records", "Customer Directory", "Who buys which threads")

    tab1, tab2 = st.tabs(["View and Manage", "Add Customer"])

    with tab1:
        cq = st.text_input("", placeholder="Search by name, phone, address, or thread code...", label_visibility="collapsed", key="cust_search")
        if db_ok:
            sql = "SELECT id, name, phone, address, thread_codes FROM customers"
            params = []
            if cq:
                like = f"%{cq.strip().lower()}%"
                sql += " WHERE LOWER(name) LIKE %s OR LOWER(phone) LIKE %s OR LOWER(address) LIKE %s OR LOWER(thread_codes) LIKE %s"
                params = [like, like, like, like]
            sql += " ORDER BY name"
            cdf = qry(sql, params or None, fetch=True)
        else:
            cdf = pd.DataFrame(st.session_state.customers)
            if cq:
                cdf = cdf[cdf.apply(lambda r: any(cq.lower() in str(r[c]).lower() for c in ["name", "phone", "address", "thread_codes"]), axis=1)]

        if cdf is not None and not cdf.empty:
            st.markdown(f"{len(cdf)} customer(s) found")
            for _, row in cdf.iterrows():
                with st.expander(f"{row['name']}  |  {row.get('phone', '--')}  |  Threads: {row.get('thread_codes', '--')}"):
                    st.write(f"**Phone:** {row.get('phone', '--')}")
                    st.write(f"**Address:** {row.get('address', '--')}")
                    st.write(f"**Thread Codes:** {row.get('thread_codes', 'None assigned')}")

                    if db_ok:
                        hist = qry(
                            "SELECT transaction_date, thread_code, quantity FROM transactions WHERE LOWER(party_name) LIKE %s AND transaction_type='SELL' ORDER BY transaction_date DESC LIMIT 10",
                            (f"%{str(row['name']).lower()}%",), fetch=True
                        )
                        if hist is not None and not hist.empty:
                            st.markdown("**Purchase History:**")
                            st.dataframe(hist, use_container_width=True, hide_index=True)

                    with st.form(f"edit_cust_{row['id']}"):
                        ef1, ef2 = st.columns(2)
                        en = ef1.text_input("Name",    value=str(row.get("name", "")),    key=f"cn_{row['id']}")
                        ep = ef2.text_input("Phone",   value=str(row.get("phone", "")),   key=f"cp_{row['id']}")
                        ea = ef1.text_input("Address", value=str(row.get("address", "")), key=f"ca_{row['id']}")
                        et = ef2.text_input("Thread Codes they buy (e.g. T10, T40)", value=str(row.get("thread_codes", "")), key=f"ct_{row['id']}")
                        cb1, cb2 = st.columns(2)
                        if cb1.form_submit_button("Save Changes"):
                            if db_ok:
                                qry("UPDATE customers SET name=%s, phone=%s, address=%s, thread_codes=%s WHERE id=%s",
                                    (en.strip(), ep.strip(), ea.strip(), et.strip(), row["id"]))
                            else:
                                for c in st.session_state.customers:
                                    if c["id"] == row["id"]:
                                        c.update({"name": en, "phone": ep, "address": ea, "thread_codes": et})
                            st.success("Updated.")
                            st.rerun()
                        if cb2.form_submit_button("Delete Customer"):
                            if db_ok:
                                qry("DELETE FROM customers WHERE id=%s", (row["id"],))
                            else:
                                st.session_state.customers = [c for c in st.session_state.customers if c["id"] != row["id"]]
                            st.success(f"Deleted {row['name']}.")
                            st.rerun()
        else:
            st.info("No customers found.")

    with tab2:
        with st.form("add_cust_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            cu_name    = c1.text_input("Customer Name")
            cu_phone   = c2.text_input("Phone Number")
            cu_address = c1.text_input("Address")
            cu_threads = c2.text_input("Thread Codes they buy  (e.g. T10, T40)")
            cu_notes   = st.text_area("Notes (optional)")
            if st.form_submit_button("Add Customer"):
                if not cu_name or not cu_phone:
                    st.error("Name and phone are required.")
                else:
                    if db_ok:
                        qry("INSERT INTO customers (name, phone, address, thread_codes, notes) VALUES (%s,%s,%s,%s,%s)",
                            (cu_name.strip(), cu_phone.strip(), cu_address.strip(), cu_threads.strip(), cu_notes.strip()))
                    else:
                        nid = max((c["id"] for c in st.session_state.customers), default=0) + 1
                        st.session_state.customers.append({
                            "id": nid, "name": cu_name, "phone": cu_phone,
                            "address": cu_address, "thread_codes": cu_threads
                        })
                    st.success(f"Customer '{cu_name}' added.")
                    st.rerun()

# ══════════════════════════════════════════════════════════════
# TRANSACTIONS
# ══════════════════════════════════════════════════════════════
elif page == "Transactions":
    page_title("Ledger", "Transaction History", "All buy and sell records")

    c1, c2, c3 = st.columns(3)
    f_type = c1.selectbox("Type", ["All", "BUY", "SELL", "DAMAGED", "RETURN"])
    f_from = c2.date_input("From", value=datetime.date.today() - datetime.timedelta(days=30))
    f_to   = c3.date_input("To",   value=datetime.date.today())
    f_q    = st.text_input("", placeholder="Filter by thread code or party name...", label_visibility="collapsed")

    if db_ok:
        sql = """SELECT t.id, t.transaction_date, t.transaction_type, t.thread_code,
                        th.thread_name, t.party_name, t.quantity, t.notes
                 FROM transactions t
                 LEFT JOIN threads th ON th.thread_code = t.thread_code
                 WHERE t.transaction_date BETWEEN %s AND %s"""
        params = [f_from.isoformat(), f_to.isoformat()]
        if f_type != "All":
            sql += " AND t.transaction_type=%s"
            params.append(f_type)
        if f_q:
            sql += " AND (LOWER(t.thread_code) LIKE %s OR LOWER(t.party_name) LIKE %s)"
            like = f"%{f_q.lower()}%"
            params += [like, like]
        sql += " ORDER BY t.id DESC LIMIT 300"
        df = qry(sql, params, fetch=True)
    else:
        df = pd.DataFrame(st.session_state.transactions)
        if f_type != "All" and not df.empty:
            df = df[df["transaction_type"] == f_type]
        if f_q and not df.empty:
            df = df[df.apply(lambda r: any(f_q.lower() in str(r[c]).lower() for c in ["thread_code", "party_name"]), axis=1)]

    if df is not None and not df.empty:
        st.markdown(f"{len(df)} record(s)")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No transactions found.")

# ══════════════════════════════════════════════════════════════
# SEARCH
# ══════════════════════════════════════════════════════════════
elif page == "Search":
    page_title("Tools", "Smart Search", "Search threads, sellers, and customers at once")

    q = st.text_input("", placeholder="Search anything — name, code, phone, address, category...", label_visibility="collapsed", key="smart_q")

    if q and len(q.strip()) >= 1:
        like = f"%{q.strip().lower()}%"
        st.markdown("---")
        found_any = False

        # Threads
        if db_ok:
            t_res = qry(
                "SELECT thread_code, thread_name, category, current_stock, unit FROM threads WHERE LOWER(thread_code) LIKE %s OR LOWER(thread_name) LIKE %s OR LOWER(category) LIKE %s",
                (like, like, like), fetch=True
            )
        else:
            td = pd.DataFrame(st.session_state.threads)
            t_res = td[td.apply(lambda r: any(q.lower() in str(r[c]).lower() for c in ["thread_code", "thread_name", "category"]), axis=1)] if not td.empty else pd.DataFrame()

        if t_res is not None and not t_res.empty:
            found_any = True
            st.markdown(f"#### Threads  —  {len(t_res)} found")
            st.dataframe(t_res, use_container_width=True, hide_index=True)

        # Sellers
        if db_ok:
            s_res = qry(
                "SELECT name, phone, address, thread_codes FROM sellers WHERE LOWER(name) LIKE %s OR LOWER(phone) LIKE %s OR LOWER(address) LIKE %s OR LOWER(thread_codes) LIKE %s",
                (like, like, like, like), fetch=True
            )
        else:
            sd = pd.DataFrame(st.session_state.sellers)
            s_res = sd[sd.apply(lambda r: any(q.lower() in str(r[c]).lower() for c in ["name", "phone", "address", "thread_codes"]), axis=1)] if not sd.empty else pd.DataFrame()

        if s_res is not None and not s_res.empty:
            found_any = True
            st.markdown(f"#### Sellers  —  {len(s_res)} found")
            for _, r in s_res.iterrows():
                st.markdown(f"""<div class='result-card'>
                <b style='font-size:1rem'>{r['name']}</b><br>
                Phone: {r.get('phone','--')} &nbsp;|&nbsp; Address: {r.get('address','--')}<br>
                Sells: <b>{r.get('thread_codes','--')}</b>
                </div>""", unsafe_allow_html=True)

        # Customers
        if db_ok:
            c_res = qry(
                "SELECT name, phone, address, thread_codes FROM customers WHERE LOWER(name) LIKE %s OR LOWER(phone) LIKE %s OR LOWER(address) LIKE %s OR LOWER(thread_codes) LIKE %s",
                (like, like, like, like), fetch=True
            )
        else:
            cd = pd.DataFrame(st.session_state.customers)
            c_res = cd[cd.apply(lambda r: any(q.lower() in str(r[c]).lower() for c in ["name", "phone", "address", "thread_codes"]), axis=1)] if not cd.empty else pd.DataFrame()

        if c_res is not None and not c_res.empty:
            found_any = True
            st.markdown(f"#### Customers  —  {len(c_res)} found")
            for _, r in c_res.iterrows():
                st.markdown(f"""<div class='result-card' style='border-left-color:#1a5f8a'>
                <b style='font-size:1rem'>{r['name']}</b><br>
                Phone: {r.get('phone','--')} &nbsp;|&nbsp; Address: {r.get('address','--')}<br>
                Buys: <b>{r.get('thread_codes','--')}</b>
                </div>""", unsafe_allow_html=True)

        if not found_any:
            st.warning(f"No results found for '{q}'. Try a different keyword.")
    else:
        st.markdown("""
        <div style='background:#fff;border:1.5px solid #E0D8CC;border-radius:12px;padding:32px;text-align:center;margin-top:20px'>
          <div style='font-family:"Playfair Display",serif;font-size:1.2rem;color:#333;margin-bottom:10px'>Search Everything</div>
          <div style='font-size:0.82rem;color:#888;line-height:2.2'>
            Thread code &nbsp;|&nbsp; Thread name &nbsp;|&nbsp; Category<br>
            Seller name &nbsp;|&nbsp; Seller phone &nbsp;|&nbsp; Seller area<br>
            Customer name &nbsp;|&nbsp; Customer phone &nbsp;|&nbsp; Thread codes
          </div>
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# SETTINGS
# ══════════════════════════════════════════════════════════════
elif page == "Settings":
    page_title("System", "Settings", "Customize your store name and preferences")

    if db_ok:
        raw = qry("SELECT setting_key, setting_value FROM store_settings", fetch=True)
        cfg = dict(zip(raw["setting_key"], raw["setting_value"])) if raw is not None and not raw.empty else {}
    else:
        cfg = {"store_name": st.session_state.get("store_name", "Thread Suite Pro"), "owner_name": "", "phone": "", "address": ""}

    with st.form("settings_form"):
        c1, c2 = st.columns(2)
        new_store = c1.text_input("Store / Business Name", value=cfg.get("store_name", ""))
        new_owner = c2.text_input("Owner Name",             value=cfg.get("owner_name", ""))
        new_phone = c1.text_input("Phone",                  value=cfg.get("phone", ""))
        new_addr  = c2.text_input("Address",                value=cfg.get("address", ""))
        if st.form_submit_button("Save Settings"):
            updates = {"store_name": new_store, "owner_name": new_owner, "phone": new_phone, "address": new_addr}
            for k, v in updates.items():
                if db_ok:
                    qry("INSERT INTO store_settings (setting_key, setting_value) VALUES (%s,%s) ON DUPLICATE KEY UPDATE setting_value=%s", (k, v, v))
                else:
                    st.session_state.store_settings = st.session_state.get("store_settings", {})
                    st.session_state.store_settings[k] = v
            st.session_state.store_name = new_store
            st.success("Settings saved. Refresh to see updated name in sidebar.")
            st.rerun()

    st.markdown("---")
    if db_ok:
        st.success("Connected to TiDB Cloud database.")
    else:
        st.error("Not connected to database. Running in demo mode.")
        st.markdown("""
        **To connect:**
        1. Go to tidbcloud.com and create a free Serverless cluster
        2. Run schema.sql in the SQL Editor
        3. Go to Streamlit Cloud, App Settings, Secrets, and paste your credentials
        ```toml
        [mysql]
        host     = "gateway01.ap-southeast-1.prod.aws.tidbcloud.com"
        port     = 4000
        user     = "your_user"
        password = "your_password"
        database = "thread_business"
        ```
        """)