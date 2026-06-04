import streamlit as st
import mysql.connector
import pandas as pd
import datetime

st.set_page_config(page_title="Thread Business CRM", page_icon="🧵", layout="wide")

# ══════════════════════════════════════════════════════════════
# DATABASE CONNECTION
# ══════════════════════════════════════════════════════════════
@st.cache_resource(ttl=30)
def get_connection():
    try:
        conn = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            port=int(st.secrets["mysql"]["port"]),
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"],
            autocommit=True
        )
        return True, conn
    except Exception as e:
        return False, str(e)

db_ok, db_conn = get_connection()

def qry(sql, params=None, fetch=False):
    if not db_ok or db_conn is None: return pd.DataFrame() if fetch else None
    cur = db_conn.cursor(dictionary=True)
    cur.execute(sql, params or ())
    if fetch:
        rows = cur.fetchall()
        cur.close()
        return pd.DataFrame(rows)
    cur.close()

def today(): return datetime.date.today().isoformat()

# ══════════════════════════════════════════════════════════════
# SIDEBAR MENU
# ══════════════════════════════════════════════════════════════
st.sidebar.title("🧵 Thread CRM")
if db_ok: st.sidebar.success("Database Connected")
else: st.sidebar.error("Database Error")

menu = st.sidebar.radio("Navigation", ["📦 Threads & Stock", "🤝 Sellers", "👥 Customers", "🔄 Buy & Sell Entry"])

# ══════════════════════════════════════════════════════════════
# 1. THREADS & STOCK
# ══════════════════════════════════════════════════════════════
if menu == "📦 Threads & Stock":
    st.header("Thread Inventory")
    tab1, tab2 = st.tabs(["📋 View Stock", "➕ Add New Thread"])
    
    with tab1:
        search_t = st.text_input("🔍 Search Thread by Code or Name")
        sql = "SELECT thread_code as 'Thread Code', thread_name as 'Name/Color', current_stock as 'Stock' FROM threads"
        if search_t:
            sql += f" WHERE thread_code LIKE '%{search_t}%' OR thread_name LIKE '%{search_t}%'"
        df = qry(sql, fetch=True)
        if not df.empty: st.dataframe(df, use_container_width=True, hide_index=True)
        else: st.info("No threads found.")

    with tab2:
        with st.form("add_thread"):
            col1, col2 = st.columns(2)
            t_code = col1.text_input("Thread Code (Unique) *")
            t_name = col2.text_input("Thread Name / Color")
            stock = st.number_input("Opening Stock", min_value=0, step=1)
            
            if st.form_submit_button("Add Thread"):
                if t_code:
                    qry("INSERT INTO threads (thread_code, thread_name, current_stock) VALUES (%s, %s, %s)", (t_code, t_name, stock))
                    st.success(f"Thread {t_code} Added!")
                    st.rerun()

# ══════════════════════════════════════════════════════════════
# 2. SELLERS
# ══════════════════════════════════════════════════════════════
elif menu == "🤝 Sellers":
    st.header("Seller Directory")
    tab1, tab2 = st.tabs(["📋 View Sellers", "➕ Add Seller"])
    
    with tab1:
        search_s = st.text_input("🔍 Search Seller by Name or Phone")
        sql = "SELECT name as 'Seller Name', phone as 'Phone', address as 'Address' FROM sellers"
        if search_s:
            sql += f" WHERE name LIKE '%{search_s}%' OR phone LIKE '%{search_s}%'"
        df = qry(sql, fetch=True)
        if not df.empty: st.dataframe(df, use_container_width=True, hide_index=True)
        else: st.info("No sellers found.")

    with tab2:
        with st.form("add_seller"):
            s_name = st.text_input("Seller Name *")
            s_phone = st.text_input("Phone Number")
            s_address = st.text_input("Address")
            if st.form_submit_button("Add Seller"):
                if s_name:
                    qry("INSERT INTO sellers (name, phone, address) VALUES (%s, %s, %s)", (s_name, s_phone, s_address))
                    st.success("Seller Added!")
                    st.rerun()

# ══════════════════════════════════════════════════════════════
# 3. CUSTOMERS
# ══════════════════════════════════════════════════════════════
elif menu == "👥 Customers":
    st.header("Customer Directory")
    tab1, tab2 = st.tabs(["📋 View Customers", "➕ Add Customer"])
    
    with tab1:
        search_c = st.text_input("🔍 Search Customer by Name or Phone")
        sql = "SELECT name as 'Customer Name', phone as 'Phone', address as 'Address' FROM customers"
        if search_c:
            sql += f" WHERE name LIKE '%{search_c}%' OR phone LIKE '%{search_c}%'"
        df = qry(sql, fetch=True)
        if not df.empty: st.dataframe(df, use_container_width=True, hide_index=True)
        else: st.info("No customers found.")

    with tab2:
        with st.form("add_customer"):
            c_name = st.text_input("Customer Name *")
            c_phone = st.text_input("Phone Number")
            c_address = st.text_input("Address")
            if st.form_submit_button("Add Customer"):
                if c_name:
                    qry("INSERT INTO customers (name, phone, address) VALUES (%s, %s, %s)", (c_name, c_phone, c_address))
                    st.success("Customer Added!")
                    st.rerun()

# ══════════════════════════════════════════════════════════════
# 4. BUY & SELL ENTRY
# ══════════════════════════════════════════════════════════════
elif menu == "🔄 Buy & Sell Entry":
    st.header("Record Transaction")
    
    threads = qry("SELECT thread_code, current_stock FROM threads", fetch=True)
    sellers = qry("SELECT name, phone FROM sellers", fetch=True)
    customers = qry("SELECT name, phone FROM customers", fetch=True)
    
    if not threads.empty:
        with st.form("transaction_form"):
            t_type = st.radio("Transaction Type", ["Buy Thread (From Seller)", "Sell Thread (To Customer)"])
            
            t_code = st.selectbox("Select Thread Code", threads['thread_code'].tolist())
            qty = st.number_input("Quantity", min_value=1, step=1)
            
            if "Buy" in t_type:
                party_list = [f"{r['name']} - {r['phone']}" for i, r in sellers.iterrows()] if not sellers.empty else []
                party = st.selectbox("Select Seller", party_list)
            else:
                party_list = [f"{r['name']} - {r['phone']}" for i, r in customers.iterrows()] if not customers.empty else []
                party = st.selectbox("Select Customer", party_list)
                
            if st.form_submit_button("Submit Transaction"):
                if not party:
                    st.error("Please select a Seller or Customer!")
                else:
                    party_name = party.split(" - ")[0]
                    
                    if "Buy" in t_type:
                        # সুতা কিনলে স্টক বাড়বে
                        qry("UPDATE threads SET current_stock = current_stock + %s WHERE thread_code = %s", (qty, t_code))
                        qry("INSERT INTO transactions (transaction_date, transaction_type, thread_code, party_name, quantity) VALUES (%s, 'BUY', %s, %s, %s)",
                            (today(), t_code, party_name, qty))
                        st.success(f"Successfully Bought {qty} units of {t_code} from {party_name}.")
                    else:
                        # সুতা বিক্রি করলে স্টক কমবে (চেক করতে হবে স্টক আছে কিনা)
                        current_stock = int(threads[threads['thread_code'] == t_code].iloc[0]['current_stock'])
                        if current_stock < qty:
                            st.error(f"Not enough stock! Current stock is {current_stock}.")
                        else:
                            qry("UPDATE threads SET current_stock = current_stock - %s WHERE thread_code = %s", (qty, t_code))
                            qry("INSERT INTO transactions (transaction_date, transaction_type, thread_code, party_name, quantity) VALUES (%s, 'SELL', %s, %s, %s)",
                                (today(), t_code, party_name, qty))
                            st.success(f"Successfully Sold {qty} units of {t_code} to {party_name}.")
                    st.rerun()
    else:
        st.warning("Please add some Thread Codes in the 'Threads & Stock' page first.")