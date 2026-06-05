import streamlit as st
import mysql.connector
import pandas as pd
import datetime

# পেজ কনফিগারেশন
st.set_page_config(page_title="Thread Suite Pro", layout="wide")

# ডাটাবেস কানেকশন সেটআপ
@st.cache_resource(ttl=5)
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
    if not db_ok: return pd.DataFrame() if fetch else None
    cur = db_conn.cursor(dictionary=True)
    cur.execute(sql, params or ())
    if fetch:
        rows = cur.fetchall()
        cur.close()
        return pd.DataFrame(rows) if rows else pd.DataFrame()
    cur.close()

# সাইডবার মেনু
st.sidebar.title("THREAD SUITE")
st.sidebar.markdown("---")
menu = st.sidebar.radio("NAVIGATION", ["Thread Inventory", "Seller Records", "Customer Directory", "Quick Transaction"])

# ১. থ্রেড ইনভেন্টরি পেজ
if menu == "Thread Inventory":
    st.title("Thread Catalog and Stock")
    
    col_add, col_view = st.columns([1, 2], gap="large")
    
    with col_add:
        st.subheader("Add New Thread")
        with st.form("add_t", clear_on_submit=True):
            t_code = st.text_input("Thread Code / Number *")
            t_name = st.text_input("Thread Name / Description *")
            if st.form_submit_button("Save to Catalog"):
                if t_code and t_name:
                    qry("INSERT IGNORE INTO threads (thread_code, thread_name) VALUES (%s, %s)", (t_code, t_name))
                    st.success("Thread Saved!")
                    st.rerun()

    with col_view:
        st.subheader("Current Registered Stock")
        df = qry("SELECT thread_code as 'Thread Code', thread_name as 'Name' FROM threads", fetch=True)
        if not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No threads added yet.")

# ২. সেলার ডিরেক্টরি
elif menu == "Seller Records":
    st.title("Seller Profile Hub")
    
    col1, col2 = st.columns([1, 2], gap="large")
    
    with col1:
        st.subheader("Register Seller")
        with st.form("add_s", clear_on_submit=True):
            s_name = st.text_input("Seller Name *")
            s_phone = st.text_input("Phone Number")
            s_address = st.text_input("Address")
            if st.form_submit_button("Add Seller Profile"):
                if s_name:
                    qry("INSERT INTO sellers (name, phone, address) VALUES (%s, %s, %s)", (s_name, s_phone, s_address))
                    st.success("Seller Profile Created!")
                    st.rerun()

    with col2:
        st.subheader("Search Seller Profiles")
        search_s = st.text_input("🔍 Type Seller Name to Search...", placeholder="e.g. Rahim Traders")
        
        sql = "SELECT name, phone, address FROM sellers"
        if search_s:
            sql += f" WHERE name LIKE '%{search_s}%'"
        
        sdf = qry(sql, fetch=True)
        
        if not sdf.empty:
            for _, row in sdf.iterrows():
                st.write(f"### Seller: {row['name']}")
                st.write(f"Phone: {row['phone'] if row['phone'] else 'N/A'} | Address: {row['address'] if row['address'] else 'N/A'}")
                
                tsql = "SELECT thread_code, SUM(quantity) as qty FROM transactions WHERE party_name=%s AND transaction_type='BUY' GROUP BY thread_code"
                tdf = qry(tsql, (row['name'],), fetch=True)
                
                if not tdf.empty:
                    st.write("Threads Supplied:")
                    st.dataframe(tdf, use_container_width=True, hide_index=True)
                else:
                    st.caption("No supply history recorded yet.")
                st.markdown("---")
        else:
            st.info("No sellers found matching the search criteria.")

# ৩. কাস্টমার ডিরেক্টরি
elif menu == "Customer Directory":
    st.title("Customer Management Hub")
    
    col1, col2 = st.columns([1, 2], gap="large")
    
    with col1:
        st.subheader("Register Client")
        with st.form("add_c", clear_on_submit=True):
            c_name = st.text_input("Customer Name *")
            c_phone = st.text_input("Phone Number")
            c_address = st.text_input("Address")
            if st.form_submit_button("Create Client Profile"):
                if c_name:
                    qry("INSERT INTO customers (name, phone, address) VALUES (%s, %s, %s)", (c_name, c_phone, c_address))
                    st.success("Client Profile Created!")
                    st.rerun()

    with col2:
        st.subheader("Search Customer Directory")
        search_c = st.text_input("🔍 Type Customer Name to Search...", placeholder="e.g. Apex Apparel")
        
        sql = "SELECT name, phone, address FROM customers"
        if search_c:
            sql += f" WHERE name LIKE '%{search_c}%'"
            
        cdf = qry(sql, fetch=True)
        
        if not cdf.empty:
            for _, row in cdf.iterrows():
                st.write(f"### Customer: {row['name']}")
                st.write(f"Phone: {row['phone'] if row['phone'] else 'N/A'} | Address: {row['address'] if row['address'] else 'N/A'}")
                
                t_c_sql = "SELECT thread_code, SUM(quantity) as qty FROM transactions WHERE party_name=%s AND transaction_type='SELL' GROUP BY thread_code ORDER BY qty DESC"
                t_c_df = qry(t_c_sql, (row['name'],), fetch=True)
                
                if not t_c_df.empty:
                    st.write("Purchase History:")
                    st.dataframe(t_c_df, use_container_width=True, hide_index=True)
                else:
                    st.caption("No purchase history recorded yet.")
                st.markdown("---")
        else:
            st.info("No customers found matching the search criteria.")

# ৪. কুইক ট্রানজেকশন পেজ
elif menu == "Quick Transaction":
    st.title("Record Stock Movement")
    
    t_list = qry("SELECT thread_code FROM threads", fetch=True)
    s_list = qry("SELECT name FROM sellers", fetch=True)
    c_list = qry("SELECT name FROM customers", fetch=True)
    
    if not t_list.empty:
        with st.form("trans_entry", clear_on_submit=True):
            col1, col2 = st.columns(2)
            t_type = col1.radio("Action Type", ["Buy from Seller (Stock IN)", "Sell to Customer (Stock OUT)"])
            t_code = col2.selectbox("Select Thread Code", t_list['thread_code'].tolist())
            qty = col1.number_input("Quantity / Units", min_value=1, step=1)
            
            if t_type == "Buy from Seller (Stock IN)":
                party = col2.selectbox("Select Source Seller", s_list['name'].tolist() if not s_list.empty else ["No Seller Available"])
            else:
                party = col2.selectbox("Select Destination Customer", c_list['name'].tolist() if not c_list.empty else ["No Customer Available"])
                
            if st.form_submit_button("Log Transaction Entry"):
                db_type = "BUY" if "Buy" in t_type else "SELL"
                today_date = datetime.date.today().isoformat()
                qry("INSERT INTO transactions (transaction_date, transaction_type, thread_code, party_name, quantity) VALUES (%s, %s, %s, %s, %s)",
                    (today_date, db_type, t_code, party, qty))
                st.success("Transaction Successfully Logged!")
                st.rerun()
    else:
        st.warning("Please populate the Thread Catalog before making entries.")