import streamlit as st
import mysql.connector
import pandas as pd
import datetime

# পেজ কনফিগারেশন
st.set_page_config(page_title="Thread Shop ERP", page_icon="🧵", layout="wide")

# ══════════════════════════════════════════════════════════════
# ডাটাবেস কানেকশন সেটআপ
# ══════════════════════════════════════════════════════════════
@st.cache_resource(ttl=10)
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
    if not db_ok or db_conn is None: 
        return pd.DataFrame() if fetch else None
    try:
        db_conn.ping(reconnect=True, attempts=3, delay=1)
        cur = db_conn.cursor(dictionary=True)
        cur.execute(sql, params or ())
        if fetch:
            rows = cur.fetchall()
            cur.close()
            return pd.DataFrame(rows) if rows else pd.DataFrame()
        cur.close()
        return None
    except Exception as e:
        st.error(f"Database Query Error: {e}")
        return pd.DataFrame() if fetch else None

def today(): 
    return datetime.date.today().isoformat()

# ══════════════════════════════════════════════════════════════
# সাইডবার মেনু
# ══════════════════════════════════════════════════════════════
st.sidebar.title("🧵 Thread Shop System")
if db_ok: 
    st.sidebar.success("● Connected to TiDB Cloud")
else: 
    st.sidebar.error(f"● Database Error:\n{db_conn}")

menu = st.sidebar.radio("Navigation Menu", ["📦 Threads & Stock", "🤝 Seller Directory", "👥 Customer Directory", "🔄 Entry (Buy/Sell)"])

# ══════════════════════════════════════════════════════════════
# ১. থ্রেড এবং স্টক পেজ
# ══════════════════════════════════════════════════════════════
if menu == "📦 Threads & Stock":
    st.header("Thread Catalog & Inventory")
    tab1, tab2 = st.tabs(["📋 Current Stock", "➕ Add New Thread"])
    
    with tab1:
        search_t = st.text_input("🔍 Search Thread by Code or Name/Color")
        sql = "SELECT thread_code as 'Thread Code', thread_name as 'Name/Color', category as 'Category', current_stock as 'Available Stock' FROM threads"
        if search_t:
            sql += f" WHERE thread_code LIKE '%{search_t}%' OR thread_name LIKE '%{search_t}%'"
        
        df = qry(sql, fetch=True)
        if not df.empty: 
            st.dataframe(df, use_container_width=True, hide_index=True)
        else: 
            st.info("No threads found in stock.")

    with tab2:
        with st.form("add_thread_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            t_code = col1.text_input("Thread Code / Number (Manual Input) *")
            t_name = col2.text_input("Thread Name / Color Description *")
            t_cat = col1.text_input("Category (Manual Input)")
            p_stock = col2.number_input("Opening Stock Quantity", min_value=0, step=1)
            
            if st.form_submit_button("Save Thread"):
                if t_code and t_name:
                    check_exist = qry("SELECT thread_code FROM threads WHERE thread_code=%s", (t_code,), fetch=True)
                    if not check_exist.empty:
                        st.error("This Thread Code already exists!")
                    else:
                        qry("INSERT INTO threads (thread_code, thread_name, category, current_stock) VALUES (%s, %s, %s, %s)", 
                            (t_code, t_name, t_cat, p_stock))
                        st.success(f"Thread Code '{t_code}' added successfully!")
                        st.rerun()
                else:
                    st.error("Thread Code and Name are required!")

# ══════════════════════════════════════════════════════════════
# ২. সেলার ডিরেক্টরি (সার্চ বার ও সেলিং হিস্ট্রি সহ)
# ══════════════════════════════════════════════════════════════
elif menu == "🤝 Seller Directory":
    st.header("Sellers Profile & Supply History")
    tab1, tab2 = st.tabs(["📋 View & Search Sellers", "➕ Add New Seller"])
    
    with tab1:
        search_s = st.text_input("🔍 Search Seller by Name or Phone")
        sql = "SELECT name as 'Seller Name', phone as 'Phone Number', address as 'Address' FROM sellers"
        if search_s:
            sql += f" WHERE name LIKE '%{search_s}%' OR phone LIKE '%{search_s}%'"
        
        sellers_df = qry(sql, fetch=True)
        if not sellers_df.empty:
            st.dataframe(sellers_df, use_container_width=True, hide_index=True)
            
            st.subheader("💡 Supply History (Which Seller Sells Which Thread)")
            for idx, row in sellers_df.iterrows():
                s_name = row['Seller Name']
                history_sql = """
                    SELECT thread_code as 'Thread Code', SUM(quantity) as 'Total Supplied Units' 
                    FROM transactions 
                    WHERE party_name=%s AND transaction_type='BUY' 
                    GROUP BY thread_code
                """
                history_df = qry(history_sql, (s_name,), fetch=True)
                with st.expander(f"See threads supplied by: **{s_name}**"):
                    if not history_df.empty:
                        st.dataframe(history_df, use_container_width=True, hide_index=True)
                    else:
                        st.info(f"No supply records found for {s_name} yet.")
        else:
            st.info("No sellers found.")

    with tab2:
        with st.form("add_seller_form", clear_on_submit=True):
            s_name = st.text_input("Seller Name *")
            s_phone = st.text_input("Phone Number")
            s_address = st.text_input("Address")
            
            if st.form_submit_button("Register Seller"):
                if s_name:
                    qry("INSERT INTO sellers (name, phone, address) VALUES (%s, %s, %s)", (s_name, s_phone, s_address))
                    st.success(f"Seller '{s_name}' registered successfully!")
                    st.rerun()
                else:
                    st.error("Seller Name is required!")

# ══════════════════════════════════════════════════════════════
# ৩. কাস্টমার ডিরেক্টরি (সার্চ বার ও পারচেজ হিস্ট্রি সহ)
# ══════════════════════════════════════════════════════════════
elif menu == "👥 Customer Directory":
    st.header("Customers Profile & Purchase History")
    tab1, tab2 = st.tabs(["📋 View & Search Customers", "➕ Add New Customer"])
    
    with tab1:
        search_c = st.text_input("🔍 Search Customer by Name or Phone")
        sql = "SELECT name as 'Customer Name', phone as 'Phone Number', address as 'Address' FROM customers"
        if search_c:
            sql += f" WHERE name LIKE '%{search_c}%' OR phone LIKE '%{search_c}%'"
        
        customers_df = qry(sql, fetch=True)
        if not customers_df.empty:
            st.dataframe(customers_df, use_container_width=True, hide_index=True)
            
            st.subheader("💡 Purchase History (Which Customer Buys Which Thread Most)")
            for idx, row in customers_df.iterrows():
                c_name = row['Customer Name']
                history_sql = """
                    SELECT thread_code as 'Thread Code', SUM(quantity) as 'Total Purchased Units' 
                    FROM transactions 
                    WHERE party_name=%s AND transaction_type='SELL' 
                    GROUP BY thread_code 
                    ORDER BY SUM(quantity) DESC
                """
                history_df = qry(history_sql, (c_name,), fetch=True)
                with st.expander(f"See purchase records of: **{c_name}**"):
                    if not history_df.empty:
                        st.dataframe(history_df, use_container_width=True, hide_index=True)
                    else:
                        st.info(f"No purchase records found for {c_name} yet.")
        else:
            st.info("No customers found.")

    with tab2:
        with st.form("add_customer_form", clear_on_submit=True):
            c_name = st.text_input("Customer Name *")
            c_phone = st.text_input("Phone Number")
            c_address = st.text_input("Address")
            
            if st.form_submit_button("Register Customer"):
                if c_name:
                    qry("INSERT INTO customers (name, phone, address) VALUES (%s, %s, %s)", (c_name, c_phone, c_address))
                    st.success(f"Customer '{c_name}' registered successfully!")
                    st.rerun()
                else:
                    st.error("Customer Name is required!")

# ══════════════════════════════════════════════════════════════
# ৪. স্টক ইন এবং আউট (Buy/Sell Entry) পেজ
# ══════════════════════════════════════════════════════════════
elif menu == "🔄 Entry (Buy/Sell)":
    st.header("Record New Transaction")
    
    threads_df = qry("SELECT thread_code, current_stock FROM threads", fetch=True)
    sellers_df = qry("SELECT name FROM sellers", fetch=True)
    customers_df = qry("SELECT name FROM customers", fetch=True)
    
    if not threads_df.empty:
        with st.form("transaction_form", clear_on_submit=True):
            t_type = st.radio("What are you doing?", ["Buy Thread (Stock IN from Seller)", "Sell Thread (Stock OUT to Customer)"])
            t_code = st.selectbox("Select Thread Code", threads_df['thread_code'].tolist())
            qty = st.number_input("Quantity (Amount)", min_value=1, step=1)
            
            if "Buy" in t_type:
                party_list = sellers_df['name'].tolist() if not sellers_df.empty else []
                party_name = st.selectbox("Select the Seller", party_list)
            else:
                party_list = customers_df['name'].tolist() if not customers_df.empty else []
                party_name = st.selectbox("Select the Customer", party_list)
                
            if st.form_submit_button("Save Transaction Entry"):
                if not party_name:
                    st.error("Error: Please select or add a Seller/Customer first!")
                else:
                    if "Buy" in t_type:
                        # স্টক বাড়ানো এবং লেনদেন সেভ করা
                        qry("UPDATE threads SET current_stock = current_stock + %s WHERE thread_code = %s", (qty, t_code))
                        qry("INSERT INTO transactions (transaction_date, transaction_type, thread_code, party_name, quantity) VALUES (%s, 'BUY', %s, %s, %s)",
                            (today(), t_code, party_name, qty))
                        st.success(f"Recorded: Bought {qty} units of {t_code} from {party_name}.")
                    else:
                        # স্টক কমানোর আগে চেক করা
                        current_stock = int(threads_df[threads_df['thread_code'] == t_code].iloc[0]['current_stock'])
                        if current_stock < qty:
                            st.error(f"Insufficient Stock! You only have {current_stock} units left for code {t_code}.")
                        else:
                            qry("UPDATE threads SET current_stock = current_stock - %s WHERE thread_code = %s", (qty, t_code))
                            qry("INSERT INTO transactions (transaction_date, transaction_type, thread_code, party_name, quantity) VALUES (%s, 'SELL', %s, %s, %s)",
                                (today(), t_code, party_name, qty))
                            st.success(f"Recorded: Sold {qty} units of {t_code} to {party_name}.")
                    st.rerun()
    else:
        st.warning("Please add some Thread Codes in the 'Threads & Stock' page first to start trading.")