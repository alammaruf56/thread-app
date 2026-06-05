import streamlit as st
import mysql.connector
import pandas as pd
import datetime

# পেজ কনফিগারেশন ও অপ্টিমাইজেশন
st.set_page_config(page_title="Thread Suite Pro", layout="wide")

# ডাটাবেস কানেকশন সেটআপ (কানেকশন পুলিং সহ ফাস্ট লোডিংয়ের জন্য)
@st.cache_resource(ttl=60)
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
    try:
        cur = db_conn.cursor(dictionary=True)
        cur.execute(sql, params or ())
        if fetch:
            rows = cur.fetchall()
            cur.close()
            return pd.DataFrame(rows) if rows else pd.DataFrame()
        cur.close()
    except:
        # কানেকশন ড্রপ হলে রিকানেক্ট ট্রাই করবে
        st.cache_resource.clear()

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
                    qry("INSERT IGNORE INTO threads (thread_code, thread_name) VALUES (%s, %s)", (t_code.strip(), t_name.strip()))
                    st.success("Thread Saved!")
                    st.columns(1) # রিরানের বিকল্প হিসেবে নিরাপদ ফ্লো

    with col_view:
        st.subheader("Current Registered Stock")
        df = qry("SELECT thread_code as 'Thread Code', thread_name as 'Name' FROM threads", fetch=True)
        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No threads added yet.")

# ২. সেলার ডিরেক্টরি (মাল্টিপল থ্রেড অ্যাসাইন ও সার্চ সহ)
elif menu == "Seller Records":
    st.title("Seller Profile Hub")
    col1, col2 = st.columns([1, 2], gap="large")
    
    with col1:
        st.subheader("Register Seller")
        with st.form("add_s", clear_on_submit=True):
            s_name = st.text_input("Seller Name *")
            s_phone = st.text_input("Phone Number")
            s_address = st.text_input("Address")
            s_threads = st.text_input("Supplied Thread Codes (e.g. T10, T20, T30)")
            if st.form_submit_button("Add Seller Profile"):
                if s_name:
                    qry("INSERT INTO sellers (name, phone, address, thread_codes) VALUES (%s, %s, %s, %s)", 
                        (s_name.strip(), s_phone.strip(), s_address.strip(), s_threads.strip()))
                    st.success("Seller Profile Created!")

    with col2:
        st.subheader("Search Seller Directory")
        search_s = st.text_input("Search by Seller Name or Thread Code...", placeholder="Type name or code (e.g., T10)")
        
        sql = "SELECT name, phone, address, thread_codes FROM sellers"
        if search_s:
            sql += f" WHERE name LIKE '%{search_s}%' OR thread_codes LIKE '%{search_s}%'"
        
        sdf = qry(sql, fetch=True)
        
        if sdf is not None and not sdf.empty:
            for _, row in sdf.iterrows():
                st.write(f"### Seller: {row['name']}")
                st.write(f"Phone: {row['phone'] if row['phone'] else 'N/A'} | Address: {row['address'] if row['address'] else 'N/A'}")
                st.write(f"**Deals with Threads:** {row['thread_codes'] if row['thread_codes'] else 'None Assigned'}")
                st.markdown("---")
        else:
            st.info("No sellers found matching the search criteria.")

# ৩. কাস্টমার ডিরেক্টরি (মাল্টিপল থ্রেড অ্যাসাইন ও সার্চ সহ)
elif menu == "Customer Directory":
    st.title("Customer Management Hub")
    col1, col2 = st.columns([1, 2], gap="large")
    
    with col1:
        st.subheader("Register Client")
        with st.form("add_c", clear_on_submit=True):
            c_name = st.text_input("Customer Name *")
            c_phone = st.text_input("Phone Number")
            c_address = st.text_input("Address")
            c_threads = st.text_input("Purchased Thread Codes (e.g. T10, T40)")
            if st.form_submit_button("Create Client Profile"):
                if c_name:
                    qry("INSERT INTO customers (name, phone, address, thread_codes) VALUES (%s, %s, %s, %s)", 
                        (c_name.strip(), c_phone.strip(), c_address.strip(), c_threads.strip()))
                    st.success("Client Profile Created!")

    with col2:
        st.subheader("Search Customer Directory")
        search_c = st.text_input("Search by Customer Name or Thread Code...", placeholder="Type name or code (e.g., T40)")
        
        sql = "SELECT name, phone, address, thread_codes FROM customers"
        if search_c:
            sql += f" WHERE name LIKE '%{search_c}%' OR thread_codes LIKE '%{search_c}%'"
            
        cdf = qry(sql, fetch=True)
        
        if cdf is not None and not cdf.empty:
            for _, row in cdf.iterrows():
                st.write(f"### Customer: {row['name']}")
                st.write(f"Phone: {row['phone'] if row['phone'] else 'N/A'} | Address: {row['address'] if row['address'] else 'N/A'}")
                st.write(f"**Interested in Threads:** {row['thread_codes'] if row['thread_codes'] else 'None Assigned'}")
                st.markdown("---")
        else:
            st.info("No customers found matching the search criteria.")

# ৪. কুইক ট্রানজেকশন পেজ
elif menu == "Quick Transaction":
    st.title("Record Stock Movement")
    t_list = qry("SELECT thread_code FROM threads", fetch=True)
    s_list = qry("SELECT name FROM sellers", fetch=True)
    c_list = qry("SELECT name FROM customers", fetch=True)
    
    if t_list is not None and not t_list.empty:
        with st.form("trans_entry", clear_on_submit=True):
            col1, col2 = st.columns(2)
            t_type = col1.radio("Action Type", ["Buy from Seller (Stock IN)", "Sell to Customer (Stock OUT)"])
            t_code = col2.selectbox("Select Thread Code", t_list['thread_code'].tolist())
            qty = col1.number_input("Quantity / Units", min_value=1, step=1)
            
            if t_type == "Buy from Seller (Stock IN)":
                party = col2.selectbox("Select Source Seller", s_list['name'].tolist() if (s_list is not None and not s_list.empty) else ["No Seller Available"])
            else:
                party = col2.selectbox("Select Destination Customer", c_list['name'].tolist() if (c_list is not None and not c_list.empty) else ["No Customer Available"])
                
            if st.form_submit_button("Log Transaction Entry"):
                db_type = "BUY" if "Buy" in t_type else "SELL"
                today_date = datetime.date.today().isoformat()
                qry("INSERT INTO transactions (transaction_date, transaction_type, thread_code, party_name, quantity) VALUES (%s, %s, %s, %s, %s)",
                    (today_date, db_type, t_code, party, qty))
                st.success("Transaction Successfully Logged!")
    else:
        st.warning("Please populate the Thread Catalog before making entries.")