# ============================================================
# THREAD SUITE PRO - Final Production Version
# ============================================================

import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
import base64
import os
import sys

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Thread Suite Pro", page_icon="🧵", layout="wide", initial_sidebar_state="expanded")

# Minimal CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .main-header { font-size: 2rem; font-weight: 700; color: #1E293B; margin-bottom: 0.5rem; }
    .metric-card { background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border: 1px solid #E2E8F0; }
    .metric-value { font-size: 2rem; font-weight: 700; color: #1E293B; }
    .metric-label { font-size: 0.85rem; color: #64748B; margin-top: 0.25rem; }
    .stButton > button { background: #2563EB; color: white; border: none; padding: 10px 24px; border-radius: 8px; font-weight: 600; width: 100%; }
    .stButton > button:hover { background: #1D4ED8; }
    .stTextInput > div > div > input, .stSelectbox > div > div > div, .stNumberInput > div > div > input { border-radius: 8px !important; border: 1px solid #CBD5E1 !important; }
    section[data-testid="stSidebar"] { background: #0F172A; }
    section[data-testid="stSidebar"] .stMarkdown { color: #F8FAFC; }
</style>
""", unsafe_allow_html=True)

# ---------- DATABASE PATH ----------
if getattr(sys, 'frozen', False):
    DB_PATH = os.path.join(os.path.dirname(sys.executable), 'thread_business.db')
else:
    DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'thread_business.db')

# ---------- DATABASE FUNCTIONS ----------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS store_settings (
        setting_key TEXT PRIMARY KEY, setting_value TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS threads (
        thread_code TEXT PRIMARY KEY, thread_name TEXT NOT NULL,
        category TEXT DEFAULT '', current_stock INTEGER DEFAULT 0,
        unit TEXT DEFAULT 'Cone', low_stock_threshold INTEGER DEFAULT 10,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS sellers (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
        phone TEXT, address TEXT, thread_codes TEXT, notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
        phone TEXT, address TEXT, thread_codes TEXT, notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transaction_date TEXT DEFAULT (date('now')),
        transaction_type TEXT DEFAULT 'SELL', thread_code TEXT,
        party_name TEXT, quantity INTEGER DEFAULT 0, notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
    c.execute("INSERT OR IGNORE INTO store_settings VALUES ('store_name','My Thread Business')")
    c.execute("INSERT OR IGNORE INTO store_settings VALUES ('owner_name','')")
    c.execute("INSERT OR IGNORE INTO store_settings VALUES ('phone','')")
    c.execute("INSERT OR IGNORE INTO store_settings VALUES ('address','')")
    conn.commit()
    conn.close()

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def execute_query(query, params=None, fetch=True):
    try:
        conn = get_conn()
        c = conn.cursor()
        if params:
            c.execute(query, params)
        else:
            c.execute(query)
        if fetch:
            result = c.fetchall()
            cols = [d[0] for d in c.description]
            conn.close()
            return pd.DataFrame(result, columns=cols) if result else pd.DataFrame()
        else:
            conn.commit()
            conn.close()
            return True
    except Exception as e:
        st.error(f"Query error: {e}")
        return pd.DataFrame() if fetch else False

def get_store_name():
    result = execute_query("SELECT setting_value FROM store_settings WHERE setting_key='store_name'")
    return result.iloc[0]['setting_value'] if not result.empty else "Thread Suite Pro"

def export_csv(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="export.csv"><button style="background:#2563EB;color:white;border:none;padding:6px 14px;border-radius:6px;">Download CSV</button></a>'

# ---------- MAIN APP ----------
def main():
    init_db()
    with st.sidebar:
        st.markdown(f"### {get_store_name()}")
        st.markdown("---")
        menu = st.radio("Navigation", [
            "Dashboard", "Thread Inventory", "Seller Directory",
            "Customer Directory", "Record Transaction", "Smart Search",
            "Transaction History", "Settings"
        ])
        st.markdown(f"*{date.today().strftime('%B %d, %Y')}*")

    if menu == "Dashboard": show_dashboard()
    elif menu == "Thread Inventory": show_inventory()
    elif menu == "Seller Directory": show_sellers()
    elif menu == "Customer Directory": show_customers()
    elif menu == "Record Transaction": show_transaction_form()
    elif menu == "Smart Search": show_smart_search()
    elif menu == "Transaction History": show_transaction_history()
    elif menu == "Settings": show_settings()

# ---------- DASHBOARD ----------
def show_dashboard():
    st.markdown('<p class="main-header">Business Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Real-time overview</p>', unsafe_allow_html=True)
    total_threads = execute_query("SELECT COUNT(*) as c FROM threads")['c'].iloc[0]
    total_sellers = execute_query("SELECT COUNT(*) as c FROM sellers")['c'].iloc[0]
    total_customers = execute_query("SELECT COUNT(*) as c FROM customers")['c'].iloc[0]
    low_stock = execute_query("SELECT COUNT(*) as c FROM threads WHERE current_stock <= low_stock_threshold")['c'].iloc[0]
    today_sales = execute_query(f"SELECT COALESCE(SUM(quantity),0) as v FROM transactions WHERE transaction_type='SELL' AND transaction_date='{date.today()}'")['v'].iloc[0]
    total_inventory = execute_query("SELECT COALESCE(SUM(current_stock),0) as v FROM threads")['v'].iloc[0]

    cols = st.columns(6)
    metrics = [
        (total_threads, "Thread Types"), (total_sellers, "Sellers"),
        (total_customers, "Customers"), (low_stock, "Low Stock"),
        (total_inventory, "Total Stock"), (today_sales, "Sold Today")
    ]
    for i, (val, label) in enumerate(metrics):
        with cols[i]:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{val}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Low Stock Alerts")
    low_df = execute_query("SELECT thread_code, thread_name, current_stock, low_stock_threshold FROM threads WHERE current_stock <= low_stock_threshold ORDER BY current_stock ASC LIMIT 10")
    if not low_df.empty:
        st.dataframe(low_df, use_container_width=True, hide_index=True)
    else:
        st.success("All products well stocked.")

    st.subheader("Recent Transactions")
    recent = execute_query("SELECT transaction_date, transaction_type, thread_code, party_name, quantity FROM transactions ORDER BY id DESC LIMIT 10")
    if not recent.empty:
        st.dataframe(recent, use_container_width=True, hide_index=True)
    else:
        st.info("No transactions yet.")

# ---------- INVENTORY ----------
def show_inventory():
    st.markdown('<p class="main-header">Thread Inventory</p>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["View Stock", "Add Thread", "Manage Thread"])
    with tab1:
        col1, col2, col3 = st.columns([3,1,1])
        search = col1.text_input("Search by code, name, or category", placeholder="Type to filter...")
        cats = execute_query("SELECT DISTINCT category FROM threads WHERE category != ''")
        cat_list = ['All'] + (cats['category'].tolist() if not cats.empty else [])
        sel_cat = col2.selectbox("Category", cat_list)
        stock_filter = col3.selectbox("Stock Status", ["All", "In Stock", "Low Stock", "Out of Stock"])
        query = "SELECT * FROM threads WHERE 1=1"
        params = []
        if search:
            like = f"%{search}%"
            query += " AND (LOWER(thread_code) LIKE LOWER(?) OR LOWER(thread_name) LIKE LOWER(?) OR LOWER(category) LIKE LOWER(?))"
            params.extend([like, like, like])
        if sel_cat != 'All':
            query += " AND LOWER(category) = LOWER(?)"
            params.append(sel_cat)
        if stock_filter == "In Stock":
            query += " AND current_stock > low_stock_threshold"
        elif stock_filter == "Low Stock":
            query += " AND current_stock <= low_stock_threshold AND current_stock > 0"
        elif stock_filter == "Out of Stock":
            query += " AND current_stock <= 0"
        query += " ORDER BY current_stock ASC"
        df = execute_query(query, tuple(params) if params else None)
        if not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.markdown(export_csv(df), unsafe_allow_html=True)
        else:
            st.info("No threads found.")
    with tab2:
        with st.form("add_thread"):
            st.subheader("Add New Thread")
            c1, c2 = st.columns(2)
            code = c1.text_input("Thread Code *"); name = c1.text_input("Thread Name *")
            cat = c1.text_input("Category")
            stock = c2.number_input("Opening Stock", min_value=0, value=0)
            unit = c2.selectbox("Unit", ["Cone","Spool","kg","Box","Bundle","Piece","Dozen"])
            threshold = c2.number_input("Low Stock Alert At", min_value=1, value=10)
            if st.form_submit_button("Save Thread"):
                if code and name:
                    execute_query("INSERT INTO threads (thread_code,thread_name,category,current_stock,unit,low_stock_threshold,created_at) VALUES (?,?,?,?,?,?,CURRENT_TIMESTAMP) ON CONFLICT(thread_code) DO UPDATE SET thread_name=excluded.thread_name, category=excluded.category, unit=excluded.unit, low_stock_threshold=excluded.low_stock_threshold, current_stock=current_stock+excluded.current_stock",
                                  (code.strip(), name.strip(), cat.strip(), stock, unit, threshold), fetch=False)
                    st.success(f"Thread '{name}' saved!"); st.rerun()
                else:
                    st.error("Code and Name are required.")
    with tab3:
        st.subheader("Edit or Delete Thread")
        all_threads = execute_query("SELECT * FROM threads")
        if not all_threads.empty:
            sel = st.selectbox("Select thread", all_threads['thread_name'])
            if sel:
                row = all_threads[all_threads['thread_name'] == sel].iloc[0]
                with st.form("edit_thread_form"):
                    c1, c2 = st.columns(2)
                    nname = c1.text_input("Name", value=row['thread_name'])
                    ncat = c1.text_input("Category", value=row['category'])
                    nstock = c2.number_input("Stock", value=int(row['current_stock']), min_value=0)
                    units = ["Cone","Spool","kg","Box","Bundle","Piece","Dozen"]
                    unit_idx = units.index(row['unit']) if row['unit'] in units else 0
                    nunit = c2.selectbox("Unit", units, index=unit_idx)
                    nthresh = st.number_input("Low Stock Threshold", value=int(row['low_stock_threshold']), min_value=1)
                    btn1, btn2 = st.columns(2)
                    if btn1.form_submit_button("Update"):
                        execute_query("UPDATE threads SET thread_name=?, category=?, current_stock=?, unit=?, low_stock_threshold=? WHERE thread_code=?",
                                      (nname, ncat, nstock, nunit, nthresh, row['thread_code']), fetch=False)
                        st.success("Updated!"); st.rerun()
                    if btn2.form_submit_button("Delete"):
                        execute_query("DELETE FROM threads WHERE thread_code=?", (row['thread_code'],), fetch=False)
                        st.success("Deleted!"); st.rerun()

# ---------- SELLERS ----------
def show_sellers():
    st.markdown('<p class="main-header">Seller Directory</p>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["View Sellers", "Add Seller"])
    with tab1:
        search = st.text_input("Search sellers", placeholder="Name, phone, thread codes...")
        query = "SELECT * FROM sellers WHERE 1=1"
        params = []
        if search:
            like = f"%{search}%"
            query += " AND (LOWER(name) LIKE LOWER(?) OR LOWER(phone) LIKE LOWER(?) OR LOWER(address) LIKE LOWER(?) OR LOWER(thread_codes) LIKE LOWER(?))"
            params.extend([like]*4)
        query += " ORDER BY name"
        sellers = execute_query(query, tuple(params) if params else None)
        if not sellers.empty:
            for _, s in sellers.iterrows():
                with st.expander(f"{s['name']} | {s.get('phone','N/A')} | Threads: {s.get('thread_codes','')}"):
                    st.write(f"Phone: {s.get('phone','')}")
                    st.write(f"Address: {s.get('address','')}")
                    st.write(f"Thread Codes: {s.get('thread_codes','')}")
                    if s.get('notes'): st.write(f"Notes: {s['notes']}")
                    col1, col2 = st.columns(2)
                    if col1.button("Edit", key=f"e_{s['id']}"):
                        st.session_state[f'edit_seller_{s["id"]}'] = True
                    if col2.button("Delete", key=f"d_{s['id']}"):
                        execute_query("DELETE FROM sellers WHERE id=?", (s['id'],), fetch=False)
                        st.success("Deleted!"); st.rerun()
                    if st.session_state.get(f'edit_seller_{s["id"]}'):
                        with st.form(f"form_{s['id']}"):
                            nname = st.text_input("Name", value=s['name'])
                            nphone = st.text_input("Phone", value=s.get('phone',''))
                            naddr = st.text_area("Address", value=s.get('address',''))
                            nthreads = st.text_input("Thread Codes", value=s.get('thread_codes',''))
                            nnotes = st.text_area("Notes", value=s.get('notes',''))
                            if st.form_submit_button("Save"):
                                execute_query("UPDATE sellers SET name=?, phone=?, address=?, thread_codes=?, notes=? WHERE id=?",
                                              (nname, nphone, naddr, nthreads, nnotes, s['id']), fetch=False)
                                st.session_state[f'edit_seller_{s["id"]}'] = False
                                st.success("Updated!"); st.rerun()
        else:
            st.info("No sellers found.")
    with tab2:
        with st.form("add_seller"):
            st.subheader("Register New Seller")
            c1, c2 = st.columns(2)
            name = c1.text_input("Seller Name *"); phone = c2.text_input("Phone")
            threads = c2.text_input("Thread Codes (e.g., T10, T20)")
            address = c1.text_area("Address"); notes = st.text_area("Notes")
            if st.form_submit_button("Register"):
                if name:
                    execute_query("INSERT INTO sellers (name,phone,address,thread_codes,notes) VALUES (?,?,?,?,?)",
                                  (name, phone, address, threads, notes), fetch=False)
                    st.success(f"Seller '{name}' added!"); st.rerun()
                else: st.error("Name required!")

# ---------- CUSTOMERS ----------
def show_customers():
    st.markdown('<p class="main-header">Customer Directory</p>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["View Customers", "Add Customer"])
    with tab1:
        search = st.text_input("Search customers", placeholder="Name, phone, thread codes...")
        query = "SELECT * FROM customers WHERE 1=1"
        params = []
        if search:
            like = f"%{search}%"
            query += " AND (LOWER(name) LIKE LOWER(?) OR LOWER(phone) LIKE LOWER(?) OR LOWER(address) LIKE LOWER(?) OR LOWER(thread_codes) LIKE LOWER(?))"
            params.extend([like]*4)
        query += " ORDER BY name"
        custs = execute_query(query, tuple(params) if params else None)
        if not custs.empty:
            for _, c in custs.iterrows():
                with st.expander(f"{c['name']} | {c.get('phone','N/A')} | Threads: {c.get('thread_codes','')}"):
                    st.write(f"Phone: {c.get('phone','')}")
                    st.write(f"Address: {c.get('address','')}")
                    st.write(f"Thread Codes: {c.get('thread_codes','')}")
                    if c.get('notes'): st.write(f"Notes: {c['notes']}")
                    hist = execute_query("SELECT transaction_date, thread_code, quantity FROM transactions WHERE LOWER(party_name) LIKE LOWER(?) AND transaction_type='SELL' ORDER BY transaction_date DESC LIMIT 10",
                                         (f"%{c['name']}%",))
                    if not hist.empty:
                        st.write("Purchase History:")
                        st.dataframe(hist, use_container_width=True, hide_index=True)
                    col1, col2 = st.columns(2)
                    if col1.button("Edit", key=f"ec_{c['id']}"): st.session_state[f'edit_cust_{c["id"]}'] = True
                    if col2.button("Delete", key=f"dc_{c['id']}"):
                        execute_query("DELETE FROM customers WHERE id=?", (c['id'],), fetch=False)
                        st.success("Deleted!"); st.rerun()
                    if st.session_state.get(f'edit_cust_{c["id"]}'):
                        with st.form(f"cform_{c['id']}"):
                            nname = st.text_input("Name", value=c['name'])
                            nphone = st.text_input("Phone", value=c.get('phone',''))
                            naddr = st.text_area("Address", value=c.get('address',''))
                            nthreads = st.text_input("Thread Codes", value=c.get('thread_codes',''))
                            nnotes = st.text_area("Notes", value=c.get('notes',''))
                            if st.form_submit_button("Save"):
                                execute_query("UPDATE customers SET name=?, phone=?, address=?, thread_codes=?, notes=? WHERE id=?",
                                              (nname, nphone, naddr, nthreads, nnotes, c['id']), fetch=False)
                                st.session_state[f'edit_cust_{c["id"]}'] = False
                                st.success("Updated!"); st.rerun()
        else: st.info("No customers found.")
    with tab2:
        with st.form("add_cust"):
            st.subheader("Add New Customer")
            c1, c2 = st.columns(2)
            name = c1.text_input("Customer Name *"); phone = c2.text_input("Phone")
            threads = c2.text_input("Thread Codes they buy")
            address = c1.text_area("Address"); notes = st.text_area("Notes")
            if st.form_submit_button("Register"):
                if name:
                    execute_query("INSERT INTO customers (name,phone,address,thread_codes,notes) VALUES (?,?,?,?,?)",
                                  (name, phone, address, threads, notes), fetch=False)
                    st.success(f"Customer '{name}' added!"); st.rerun()
                else: st.error("Name required!")

# ---------- RECORD TRANSACTION ----------
def show_transaction_form():
    st.markdown('<p class="main-header">Record Transaction</p>', unsafe_allow_html=True)
    threads = execute_query("SELECT * FROM threads ORDER BY thread_name")
    if threads.empty:
        st.warning("Add threads first."); return
    with st.form("trans_form"):
        c1, c2 = st.columns(2)
        opts = [f"{r['thread_code']} - {r['thread_name']} (Stock: {r['current_stock']})" for _, r in threads.iterrows()]
        sel = c1.selectbox("Thread *", opts)
        code = sel.split(' - ')[0]
        ttype = c1.selectbox("Type *", ["SELL","BUY","DAMAGED","RETURN"])
        qty = c2.number_input("Quantity *", min_value=1, value=1)
        party = c2.text_input("Party Name"); tdate = c2.date_input("Date", value=date.today())
        notes = st.text_area("Notes")
        if st.form_submit_button("Record Transaction"):
            if code and qty > 0:
                execute_query("INSERT INTO transactions (transaction_date,transaction_type,thread_code,party_name,quantity,notes) VALUES (?,?,?,?,?,?)",
                              (tdate.isoformat(), ttype, code, party, qty, notes), fetch=False)
                if ttype in ["BUY","RETURN"]:
                    execute_query("UPDATE threads SET current_stock = current_stock + ? WHERE thread_code = ?", (qty, code), fetch=False)
                else:
                    execute_query("UPDATE threads SET current_stock = MAX(current_stock - ?, 0) WHERE thread_code = ?", (qty, code), fetch=False)
                st.success("Transaction recorded!"); st.rerun()
            else: st.error("Thread and quantity required.")

# ---------- SMART SEARCH ----------
def show_smart_search():
    st.markdown('<p class="main-header">Smart Search</p>', unsafe_allow_html=True)
    search = st.text_input("", placeholder="Search thread code or name...")
    if search:
        st.markdown("---")
        like = f"%{search}%"
        threads_res = execute_query("SELECT * FROM threads WHERE LOWER(thread_code) LIKE LOWER(?) OR LOWER(thread_name) LIKE LOWER(?)", (like, like))
        if not threads_res.empty:
            st.subheader("Matching Threads")
            st.dataframe(threads_res, use_container_width=True, hide_index=True)
            for _, trow in threads_res.iterrows():
                code = trow['thread_code']
                with st.expander(f"Sellers & Customers for {code} - {trow['thread_name']}"):
                    ca, cb = st.columns(2)
                    with ca:
                        st.markdown("**Sellers who supply this thread**")
                        sell_df = execute_query("SELECT * FROM sellers WHERE LOWER(thread_codes) LIKE LOWER(?)", (f"%{code}%",))
                        if not sell_df.empty: st.dataframe(sell_df[['name','phone','address','thread_codes']], use_container_width=True, hide_index=True)
                        else: st.write("No sellers found.")
                    with cb:
                        st.markdown("**Customers who buy this thread**")
                        cust_df = execute_query("SELECT * FROM customers WHERE LOWER(thread_codes) LIKE LOWER(?)", (f"%{code}%",))
                        if not cust_df.empty: st.dataframe(cust_df[['name','phone','address','thread_codes']], use_container_width=True, hide_index=True)
                        else: st.write("No customers found.")
        else:
            sellers_res = execute_query("SELECT 'Seller' as Type, name, phone, thread_codes FROM sellers WHERE LOWER(name) LIKE LOWER(?) OR LOWER(thread_codes) LIKE LOWER(?)", (like, like))
            custs_res = execute_query("SELECT 'Customer' as Type, name, phone, thread_codes FROM customers WHERE LOWER(name) LIKE LOWER(?) OR LOWER(thread_codes) LIKE LOWER(?)", (like, like))
            if not sellers_res.empty: st.subheader("Sellers matching your search"); st.dataframe(sellers_res, use_container_width=True, hide_index=True)
            if not custs_res.empty: st.subheader("Customers matching your search"); st.dataframe(custs_res, use_container_width=True, hide_index=True)
            if sellers_res.empty and custs_res.empty: st.info("No results found.")

# ---------- TRANSACTION HISTORY ----------
def show_transaction_history():
    st.markdown('<p class="main-header">Transaction History</p>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    ftype = c1.selectbox("Type", ["All","SELL","BUY","DAMAGED","RETURN"])
    dr = c2.selectbox("Date Range", ["All Time","Today","Last 7 Days","Last 30 Days","This Month"])
    party_search = c3.text_input("Search party name")
    query = "SELECT * FROM transactions WHERE 1=1"
    params = []
    if ftype != "All":
        query += " AND transaction_type=?"; params.append(ftype)
    if dr == "Today": query += " AND date(transaction_date) = date('now')"
    elif dr == "Last 7 Days": query += " AND transaction_date >= date('now','-7 days')"
    elif dr == "Last 30 Days": query += " AND transaction_date >= date('now','-30 days')"
    elif dr == "This Month": query += " AND strftime('%Y-%m', transaction_date) = strftime('%Y-%m', 'now')"
    if party_search:
        query += " AND LOWER(party_name) LIKE LOWER(?)"; params.append(f"%{party_search}%")
    query += " ORDER BY transaction_date DESC, id DESC"
    df = execute_query(query, tuple(params) if params else None)
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown(export_csv(df), unsafe_allow_html=True)
    else: st.info("No transactions found.")

# ---------- SETTINGS ----------
def show_settings():
    st.markdown('<p class="main-header">Settings</p>', unsafe_allow_html=True)
    with st.form("settings_form"):
        settings = execute_query("SELECT * FROM store_settings")
        sdict = {r['setting_key']: r['setting_value'] for _, r in settings.iterrows()} if not settings.empty else {}
        store_name = st.text_input("Store Name", value=sdict.get('store_name','My Thread Business'))
        owner_name = st.text_input("Owner Name", value=sdict.get('owner_name',''))
        phone = st.text_input("Phone", value=sdict.get('phone',''))
        address = st.text_area("Address", value=sdict.get('address',''))
        if st.form_submit_button("Save Settings"):
            for k, v in {'store_name':store_name,'owner_name':owner_name,'phone':phone,'address':address}.items():
                execute_query("INSERT OR REPLACE INTO store_settings (setting_key, setting_value) VALUES (?,?)", (k, v), fetch=False)
            st.success("Settings saved!"); st.rerun()

if __name__ == "__main__":
    main()