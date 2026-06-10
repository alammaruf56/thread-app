# ============================================================
# THREAD SUITE PRO - Final Version (supports env vars)
# ============================================================

import streamlit as st
import mysql.connector
import pandas as pd
from datetime import date
import base64
import os

# Page configuration
st.set_page_config(
    page_title="Thread Suite Pro",
    page_icon="🧵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Minimal CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .main-header { font-size: 2rem; font-weight: 700; color: #1E293B; margin-bottom: 0.5rem; }
    .sub-header { font-size: 1rem; color: #64748B; margin-bottom: 2rem; }
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

# ------------------ DATABASE CONNECTION (secrets or env) ------------------
def get_db_config():
    """Get DB config from st.secrets first, else from environment variables."""
    if "tidb" in st.secrets:
        return {
            "host": st.secrets["tidb"]["host"],
            "port": st.secrets["tidb"]["port"],
            "user": st.secrets["tidb"]["user"],
            "password": st.secrets["tidb"]["password"],
            "database": st.secrets["tidb"]["database"]
        }
    else:
        # Fallback to environment variables (for Render, Hugging Face, etc.)
        return {
            "host": os.getenv("TIDB_HOST", "localhost"),
            "port": int(os.getenv("TIDB_PORT", "4000")),
            "user": os.getenv("TIDB_USER", ""),
            "password": os.getenv("TIDB_PASSWORD", ""),
            "database": os.getenv("TIDB_DATABASE", "thread_business")
        }

@st.cache_resource(ttl=3600)
def get_db_connection():
    try:
        cfg = get_db_config()
        conn = mysql.connector.connect(
            host=cfg["host"],
            port=cfg["port"],
            user=cfg["user"],
            password=cfg["password"],
            database=cfg["database"],
            autocommit=True,
            connect_timeout=10
        )
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

def execute_query(query, params=None, fetch=True):
    conn = get_db_connection()
    if conn is None:
        return pd.DataFrame() if fetch else False
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        if fetch:
            result = cursor.fetchall()
            cursor.close()
            return pd.DataFrame(result) if result else pd.DataFrame()
        else:
            conn.commit()
            cursor.close()
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
    return f'<a href="data:file/csv;base64,{b64}" download="export.csv"><button style="background:#2563EB;color:white;border:none;padding:8px 16px;border-radius:6px;">Download CSV</button></a>'

# ------------------ MAIN APP ------------------
def main():
    with st.sidebar:
        store_name = get_store_name()
        st.markdown(f"### {store_name}")
        st.markdown("---")
        menu = st.radio("Navigation", [
            "Dashboard",
            "Thread Inventory",
            "Seller Directory",
            "Customer Directory",
            "Record Transaction",
            "Smart Search",
            "Transaction History",
            "Settings"
        ])
        st.markdown(f"*{date.today().strftime('%B %d, %Y')}*")

    if menu == "Dashboard":
        show_dashboard()
    elif menu == "Thread Inventory":
        show_inventory()
    elif menu == "Seller Directory":
        show_sellers()
    elif menu == "Customer Directory":
        show_customers()
    elif menu == "Record Transaction":
        show_transaction_form()
    elif menu == "Smart Search":
        show_smart_search()
    elif menu == "Transaction History":
        show_transaction_history()
    elif menu == "Settings":
        show_settings()

# ------------------ DASHBOARD ------------------
def show_dashboard():
    st.markdown('<p class="main-header">Business Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Real-time overview</p>', unsafe_allow_html=True)
    
    total_threads = execute_query("SELECT COUNT(*) as c FROM threads")
    total_sellers = execute_query("SELECT COUNT(*) as c FROM sellers")
    total_customers = execute_query("SELECT COUNT(*) as c FROM customers")
    low_stock = execute_query("SELECT COUNT(*) as c FROM threads WHERE current_stock <= low_stock_threshold")
    today_sales = execute_query(f"SELECT COALESCE(SUM(quantity),0) as v FROM transactions WHERE transaction_type='SELL' AND transaction_date='{date.today()}'")
    total_inventory = execute_query("SELECT SUM(current_stock) as v FROM threads")

    if total_threads.empty:
        st.error("Unable to load dashboard. Check database connection.")
        return

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{total_threads["c"].iloc[0]}</div><div class="metric-label">Thread Types</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{total_sellers["c"].iloc[0]}</div><div class="metric-label">Sellers</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{total_customers["c"].iloc[0]}</div><div class="metric-label">Customers</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{low_stock["c"].iloc[0]}</div><div class="metric-label">Low Stock</div></div>', unsafe_allow_html=True)
    with col5:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{int(total_inventory["v"].iloc[0]) if not total_inventory.empty else 0}</div><div class="metric-label">Total Stock</div></div>', unsafe_allow_html=True)
    with col6:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{int(today_sales["v"].iloc[0]) if not today_sales.empty else 0}</div><div class="metric-label">Sold Today</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Low Stock Alerts")
    low_df = execute_query("""
        SELECT thread_code, thread_name, current_stock, low_stock_threshold
        FROM threads WHERE current_stock <= low_stock_threshold
        ORDER BY current_stock ASC LIMIT 10
    """)
    if not low_df.empty:
        st.dataframe(low_df, use_container_width=True, hide_index=True)
    else:
        st.success("All products are well stocked.")

    st.subheader("Recent Transactions")
    recent = execute_query("""
        SELECT transaction_date, transaction_type, thread_code, party_name, quantity
        FROM transactions ORDER BY id DESC LIMIT 10
    """)
    if not recent.empty:
        st.dataframe(recent, use_container_width=True, hide_index=True)
    else:
        st.info("No transactions yet.")

# ------------------ INVENTORY ------------------
def show_inventory():
    st.markdown('<p class="main-header">Thread Inventory</p>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["View Stock", "Add Thread", "Manage Thread"])
    
    with tab1:
        col1, col2, col3 = st.columns([3,1,1])
        with col1:
            search = st.text_input("Search by code, name, or category", placeholder="Type to filter...")
        with col2:
            cats = execute_query("SELECT DISTINCT category FROM threads WHERE category != ''")
            cat_list = ['All'] + (cats['category'].tolist() if not cats.empty else [])
            sel_cat = st.selectbox("Category", cat_list)
        with col3:
            stock_filter = st.selectbox("Stock Status", ["All", "In Stock", "Low Stock", "Out of Stock"])
        
        query = "SELECT thread_code, thread_name, category, current_stock, unit, low_stock_threshold FROM threads WHERE 1=1"
        if search:
            query += f" AND (thread_code LIKE '%{search}%' OR thread_name LIKE '%{search}%' OR category LIKE '%{search}%')"
        if sel_cat != 'All':
            query += f" AND category = '{sel_cat}'"
        if stock_filter == "In Stock":
            query += " AND current_stock > low_stock_threshold"
        elif stock_filter == "Low Stock":
            query += " AND current_stock <= low_stock_threshold AND current_stock > 0"
        elif stock_filter == "Out of Stock":
            query += " AND current_stock <= 0"
        query += " ORDER BY current_stock ASC"
        
        df = execute_query(query)
        if not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.markdown(export_csv(df), unsafe_allow_html=True)
        else:
            st.info("No threads found.")
    
    with tab2:
        with st.form("add_thread"):
            st.subheader("Add New Thread")
            col1, col2 = st.columns(2)
            with col1:
                code = st.text_input("Thread Code *")
                name = st.text_input("Thread Name *")
                category = st.text_input("Category")
            with col2:
                stock = st.number_input("Opening Stock", min_value=0, value=0)
                unit = st.selectbox("Unit", ["Cone","Spool","kg","Box","Bundle","Piece","Dozen"])
                threshold = st.number_input("Low Stock Alert At", min_value=1, value=10)
            if st.form_submit_button("Save Thread"):
                if code and name:
                    execute_query("""
                        INSERT INTO threads (thread_code, thread_name, category, current_stock, unit, low_stock_threshold)
                        VALUES (%s,%s,%s,%s,%s,%s)
                        ON DUPLICATE KEY UPDATE thread_name=%s, category=%s, unit=%s, low_stock_threshold=%s, current_stock=current_stock+%s
                    """, (code.strip(), name.strip(), category.strip(), stock, unit, threshold,
                          name.strip(), category.strip(), unit, threshold, stock), fetch=False)
                    st.success(f"Thread '{name}' saved!")
                    st.rerun()
                else:
                    st.error("Code and Name are required.")
    
    with tab3:
        st.subheader("Edit or Delete Thread")
        all_threads = execute_query("SELECT thread_code, thread_name FROM threads")
        if not all_threads.empty:
            sel = st.selectbox("Select thread", all_threads['thread_name'])
            if sel:
                code = all_threads[all_threads['thread_name'] == sel]['thread_code'].iloc[0]
                row = execute_query(f"SELECT * FROM threads WHERE thread_code='{code}'").iloc[0]
                with st.form("edit_thread_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        new_name = st.text_input("Name", value=row['thread_name'])
                        new_cat = st.text_input("Category", value=row['category'])
                    with col2:
                        new_stock = st.number_input("Stock", value=int(row['current_stock']), min_value=0)
                        units = ["Cone","Spool","kg","Box","Bundle","Piece","Dozen"]
                        unit_index = units.index(row['unit']) if row['unit'] in units else 0
                        new_unit = st.selectbox("Unit", units, index=unit_index)
                    new_thresh = st.number_input("Low Stock Threshold", value=int(row['low_stock_threshold']), min_value=1)
                    c1, c2 = st.columns(2)
                    if c1.form_submit_button("Update"):
                        execute_query("UPDATE threads SET thread_name=%s, category=%s, current_stock=%s, unit=%s, low_stock_threshold=%s WHERE thread_code=%s",
                                      (new_name, new_cat, new_stock, new_unit, new_thresh, code), fetch=False)
                        st.success("Updated!")
                        st.rerun()
                    if c2.form_submit_button("Delete"):
                        execute_query("DELETE FROM threads WHERE thread_code=%s", (code,), fetch=False)
                        st.success("Deleted!")
                        st.rerun()

# ------------------ SELLERS ------------------
def show_sellers():
    st.markdown('<p class="main-header">Seller Directory</p>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["View Sellers", "Add Seller"])
    with tab1:
        search = st.text_input("Search sellers", placeholder="Name, phone, thread codes...")
        query = "SELECT * FROM sellers WHERE 1=1"
        if search:
            query += f" AND (name LIKE '%{search}%' OR phone LIKE '%{search}%' OR address LIKE '%{search}%' OR thread_codes LIKE '%{search}%')"
        query += " ORDER BY name"
        sellers = execute_query(query)
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
                        execute_query("DELETE FROM sellers WHERE id=%s", (s['id'],), fetch=False)
                        st.success("Deleted!")
                        st.rerun()
                    if st.session_state.get(f'edit_seller_{s["id"]}'):
                        with st.form(f"form_{s['id']}"):
                            nname = st.text_input("Name", value=s['name'])
                            nphone = st.text_input("Phone", value=s.get('phone',''))
                            naddr = st.text_area("Address", value=s.get('address',''))
                            nthreads = st.text_input("Thread Codes", value=s.get('thread_codes',''))
                            nnotes = st.text_area("Notes", value=s.get('notes',''))
                            if st.form_submit_button("Save"):
                                execute_query("UPDATE sellers SET name=%s, phone=%s, address=%s, thread_codes=%s, notes=%s WHERE id=%s",
                                              (nname, nphone, naddr, nthreads, nnotes, s['id']), fetch=False)
                                st.session_state[f'edit_seller_{s["id"]}'] = False
                                st.success("Updated!")
                                st.rerun()
        else:
            st.info("No sellers found.")
    with tab2:
        with st.form("add_seller"):
            st.subheader("Register New Seller")
            c1, c2 = st.columns(2)
            name = c1.text_input("Seller Name *")
            phone = c2.text_input("Phone")
            threads = c2.text_input("Thread Codes (e.g., T10, T20)")
            address = c1.text_area("Address")
            notes = st.text_area("Notes")
            if st.form_submit_button("Register"):
                if name:
                    execute_query("INSERT INTO sellers (name, phone, address, thread_codes, notes) VALUES (%s,%s,%s,%s,%s)",
                                  (name, phone, address, threads, notes), fetch=False)
                    st.success(f"Seller '{name}' added!")
                    st.rerun()
                else:
                    st.error("Name required!")

# ------------------ CUSTOMERS ------------------
def show_customers():
    st.markdown('<p class="main-header">Customer Directory</p>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["View Customers", "Add Customer"])
    with tab1:
        search = st.text_input("Search customers", placeholder="Name, phone, thread codes...")
        query = "SELECT * FROM customers WHERE 1=1"
        if search:
            query += f" AND (name LIKE '%{search}%' OR phone LIKE '%{search}%' OR address LIKE '%{search}%' OR thread_codes LIKE '%{search}%')"
        query += " ORDER BY name"
        custs = execute_query(query)
        if not custs.empty:
            for _, c in custs.iterrows():
                with st.expander(f"{c['name']} | {c.get('phone','N/A')} | Threads: {c.get('thread_codes','')}"):
                    st.write(f"Phone: {c.get('phone','')}")
                    st.write(f"Address: {c.get('address','')}")
                    st.write(f"Thread Codes: {c.get('thread_codes','')}")
                    if c.get('notes'): st.write(f"Notes: {c['notes']}")
                    hist = execute_query(f"SELECT transaction_date, thread_code, quantity FROM transactions WHERE party_name LIKE '%{c['name']}%' AND transaction_type='SELL' ORDER BY transaction_date DESC LIMIT 10")
                    if not hist.empty:
                        st.write("Purchase History:")
                        st.dataframe(hist, use_container_width=True, hide_index=True)
                    col1, col2 = st.columns(2)
                    if col1.button("Edit", key=f"ec_{c['id']}"):
                        st.session_state[f'edit_cust_{c["id"]}'] = True
                    if col2.button("Delete", key=f"dc_{c['id']}"):
                        execute_query("DELETE FROM customers WHERE id=%s", (c['id'],), fetch=False)
                        st.success("Deleted!")
                        st.rerun()
                    if st.session_state.get(f'edit_cust_{c["id"]}'):
                        with st.form(f"cform_{c['id']}"):
                            nname = st.text_input("Name", value=c['name'])
                            nphone = st.text_input("Phone", value=c.get('phone',''))
                            naddr = st.text_area("Address", value=c.get('address',''))
                            nthreads = st.text_input("Thread Codes", value=c.get('thread_codes',''))
                            nnotes = st.text_area("Notes", value=c.get('notes',''))
                            if st.form_submit_button("Save"):
                                execute_query("UPDATE customers SET name=%s, phone=%s, address=%s, thread_codes=%s, notes=%s WHERE id=%s",
                                              (nname, nphone, naddr, nthreads, nnotes, c['id']), fetch=False)
                                st.session_state[f'edit_cust_{c["id"]}'] = False
                                st.success("Updated!")
                                st.rerun()
        else:
            st.info("No customers found.")
    with tab2:
        with st.form("add_cust"):
            st.subheader("Add New Customer")
            c1, c2 = st.columns(2)
            name = c1.text_input("Customer Name *")
            phone = c2.text_input("Phone")
            threads = c2.text_input("Thread Codes they buy")
            address = c1.text_area("Address")
            notes = st.text_area("Notes")
            if st.form_submit_button("Register"):
                if name:
                    execute_query("INSERT INTO customers (name, phone, address, thread_codes, notes) VALUES (%s,%s,%s,%s,%s)",
                                  (name, phone, address, threads, notes), fetch=False)
                    st.success(f"Customer '{name}' added!")
                    st.rerun()
                else:
                    st.error("Name required!")

# ------------------ RECORD TRANSACTION ------------------
def show_transaction_form():
    st.markdown('<p class="main-header">Record Transaction</p>', unsafe_allow_html=True)
    threads = execute_query("SELECT thread_code, thread_name, current_stock FROM threads ORDER BY thread_name")
    if threads.empty:
        st.warning("Add threads first.")
        return
    with st.form("trans_form"):
        col1, col2 = st.columns(2)
        with col1:
            opts = [f"{r['thread_code']} - {r['thread_name']} (Stock: {r['current_stock']})" for _, r in threads.iterrows()]
            sel = st.selectbox("Thread *", opts)
            code = sel.split(' - ')[0]
            ttype = st.selectbox("Type *", ["SELL","BUY","DAMAGED","RETURN"])
        with col2:
            qty = st.number_input("Quantity *", min_value=1, value=1)
            party = st.text_input("Party Name")
            tdate = st.date_input("Date", value=date.today())
        notes = st.text_area("Notes")
        if st.form_submit_button("Record Transaction"):
            if code and qty > 0:
                execute_query("INSERT INTO transactions (transaction_date, transaction_type, thread_code, party_name, quantity, notes) VALUES (%s,%s,%s,%s,%s,%s)",
                              (tdate.isoformat(), ttype, code, party, qty, notes), fetch=False)
                if ttype in ["BUY","RETURN"]:
                    execute_query("UPDATE threads SET current_stock = current_stock + %s WHERE thread_code = %s", (qty, code), fetch=False)
                else:
                    execute_query("UPDATE threads SET current_stock = GREATEST(current_stock - %s, 0) WHERE thread_code = %s", (qty, code), fetch=False)
                st.success("Transaction recorded!")
                st.rerun()
            else:
                st.error("Thread and quantity required.")

# ------------------ SMART SEARCH ------------------
def show_smart_search():
    st.markdown('<p class="main-header">Smart Search</p>', unsafe_allow_html=True)
    search = st.text_input("", placeholder="🔍 Search threads, sellers, customers, transactions...")
    if search:
        st.markdown("---")
        threads_res = execute_query(f"SELECT 'Thread' as Type, thread_code, thread_name, category, current_stock FROM threads WHERE thread_code LIKE '%{search}%' OR thread_name LIKE '%{search}%' OR category LIKE '%{search}%' LIMIT 10")
        sellers_res = execute_query(f"SELECT 'Seller' as Type, name, phone, thread_codes FROM sellers WHERE name LIKE '%{search}%' OR phone LIKE '%{search}%' OR thread_codes LIKE '%{search}%' LIMIT 10")
        custs_res = execute_query(f"SELECT 'Customer' as Type, name, phone, thread_codes FROM customers WHERE name LIKE '%{search}%' OR phone LIKE '%{search}%' OR thread_codes LIKE '%{search}%' LIMIT 10")
        trans_res = execute_query(f"SELECT 'Transaction' as Type, transaction_date, transaction_type, thread_code, party_name, quantity FROM transactions WHERE thread_code LIKE '%{search}%' OR party_name LIKE '%{search}%' OR notes LIKE '%{search}%' ORDER BY transaction_date DESC LIMIT 10")
        
        if not threads_res.empty:
            st.subheader("Threads")
            st.dataframe(threads_res, use_container_width=True, hide_index=True)
        if not sellers_res.empty:
            st.subheader("Sellers")
            st.dataframe(sellers_res, use_container_width=True, hide_index=True)
        if not custs_res.empty:
            st.subheader("Customers")
            st.dataframe(custs_res, use_container_width=True, hide_index=True)
        if not trans_res.empty:
            st.subheader("Transactions")
            st.dataframe(trans_res, use_container_width=True, hide_index=True)
        if threads_res.empty and sellers_res.empty and custs_res.empty and trans_res.empty:
            st.info("No results found.")

# ------------------ TRANSACTION HISTORY ------------------
def show_transaction_history():
    st.markdown('<p class="main-header">Transaction History</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        ftype = st.selectbox("Type", ["All","SELL","BUY","DAMAGED","RETURN"])
    with col2:
        dr = st.selectbox("Date Range", ["All Time","Today","Last 7 Days","Last 30 Days","This Month"])
    with col3:
        party_search = st.text_input("Search party name")
    
    query = "SELECT * FROM transactions WHERE 1=1"
    if ftype != "All":
        query += f" AND transaction_type='{ftype}'"
    if dr == "Today":
        query += " AND transaction_date = CURDATE()"
    elif dr == "Last 7 Days":
        query += " AND transaction_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)"
    elif dr == "Last 30 Days":
        query += " AND transaction_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)"
    elif dr == "This Month":
        query += " AND MONTH(transaction_date) = MONTH(CURDATE()) AND YEAR(transaction_date) = YEAR(CURDATE())"
    if party_search:
        query += f" AND party_name LIKE '%{party_search}%'"
    query += " ORDER BY transaction_date DESC, id DESC"
    
    df = execute_query(query)
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown(export_csv(df), unsafe_allow_html=True)
    else:
        st.info("No transactions found.")

# ------------------ SETTINGS ------------------
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
            for k, v in {'store_name':store_name, 'owner_name':owner_name, 'phone':phone, 'address':address}.items():
                execute_query("INSERT INTO store_settings (setting_key, setting_value) VALUES (%s,%s) ON DUPLICATE KEY UPDATE setting_value=%s", (k, v, v), fetch=False)
            st.success("Settings saved!")
            st.rerun()

if __name__ == "__main__":
    main()