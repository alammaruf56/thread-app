import streamlit as st
import mysql.connector
import pandas as pd

# পেজ কনফিগারেশন
st.set_page_config(page_title="Thread Suite Pro", layout="wide")

# ডাটাবেস কানেকশন সেটআপ (কানেকশন পুলিং এবং ক্যাশিং অপ্টিমাইজড)
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
    if not db_ok: 
        return pd.DataFrame() if fetch else None
    try:
        cur = db_conn.cursor(dictionary=True)
        cur.execute(sql, params or ())
        if fetch:
            rows = cur.fetchall()
            cur.close()
            return pd.DataFrame(rows) if rows else pd.DataFrame()
        cur.close()
    except Exception:
        # কোনো কারণে কানেকশন ড্রপ হলে ক্যাশ ক্লিয়ার করবে
        st.cache_resource.clear()
        return pd.DataFrame() if fetch else None

# সাইডবার নেভিগেশন
st.sidebar.title("THREAD SUITE")
st.sidebar.markdown("---")
menu = st.sidebar.radio("NAVIGATION", ["Thread Inventory", "Seller Records", "Customer Directory"])

# ১. থ্রেড ইনভেন্টরি পেজ
if menu == "Thread Inventory":
    st.title("Product Catalog")
    col_add, col_view = st.columns([1, 2], gap="large")
    
    with col_add:
        st.subheader("Add New Thread")
        with st.form("add_thread_form", clear_on_submit=True):
            t_code = st.text_input("SKU / Code *")
            t_name = st.text_input("Product Name *")
            if st.form_submit_button("Save Product"):
                if t_code and t_name:
                    qry("INSERT IGNORE INTO threads (thread_code, thread_name) VALUES (%s, %s)", (t_code.strip(), t_name.strip()))
                    st.success("Product successfully added to catalog!")
                    st.rerun()
                else:
                    st.error("Please fill in all required fields.")

    with col_view:
        st.subheader("Registered Product List")
        df = qry("SELECT thread_code as 'SKU/Code', thread_name as 'Product Name' FROM threads", fetch=True)
        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No products available in the catalog.")

# ২. সেলার ডিরেক্টরি (মাল্টিপল থ্রেড ও অ্যাডভান্সড সার্চ)
elif menu == "Seller Records":
    st.title("Seller Directory")
    col1, col2 = st.columns([1, 2], gap="large")
    
    with col1:
        st.subheader("Register New Seller")
        with st.form("add_seller_form", clear_on_submit=True):
            s_name = st.text_input("Seller Name *")
            s_phone = st.text_input("Phone Number")
            s_address = st.text_input("Address")
            s_threads = st.text_input("Supplied Thread Codes (e.g., T10, T20, 40/2)")
            if st.form_submit_button("Save Seller Profile"):
                if s_name:
                    qry("INSERT INTO sellers (name, phone, address, thread_codes) VALUES (%s, %s, %s, %s)", 
                        (s_name.strip(), s_phone.strip(), s_address.strip(), s_threads.strip()))
                    st.success("Seller profile saved successfully!")
                    st.rerun()
                else:
                    st.error("Seller Name is required.")

    with col2:
        st.subheader("Search & Filter Sellers")
        search_s = st.text_input("Search by Name, Phone, Address, or Thread Code...")
        
        sql = "SELECT name, phone, address, thread_codes FROM sellers"
        if search_s:
            search_val = f"%{search_s.strip()}%"
            sql += " WHERE name LIKE %s OR phone LIKE %s OR address LIKE %s OR thread_codes LIKE %s"
            sdf = qry(sql, (search_val, search_val, search_val, search_val), fetch=True)
        else:
            sdf = qry(sql, fetch=True)
        
        if sdf is not None and not sdf.empty:
            for _, row in sdf.iterrows():
                st.write(f"### {row['name']}")
                st.write(f"**Phone:** {row['phone'] if row['phone'] else 'N/A'} | **Address:** {row['address'] if row['address'] else 'N/A'}")
                st.write(f"**Deals with Threads:** `{row['thread_codes'] if row['thread_codes'] else 'None Assigned'}`")
                st.markdown("---")
        else:
            st.info("No sellers found matching the criteria.")

# ৩. কাস্টমার ডিরেক্টরি (মাল্টিপল থ্রেড ও অ্যাডভান্সড সার্চ)
elif menu == "Customer Directory":
    st.title("Customer Directory")
    col1, col2 = st.columns([1, 2], gap="large")
    
    with col1:
        st.subheader("Register New Customer")
        with st.form("add_customer_form", clear_on_submit=True):
            c_name = st.text_input("Customer Name *")
            c_phone = st.text_input("Phone Number")
            c_address = st.text_input("Address")
            c_threads = st.text_input("Required Thread Codes (e.g., T10, T40)")
            if st.form_submit_button("Save Customer Profile"):
                if c_name:
                    qry("INSERT INTO customers (name, phone, address, thread_codes) VALUES (%s, %s, %s, %s)", 
                        (c_name.strip(), c_phone.strip(), c_address.strip(), c_threads.strip()))
                    st.success("Customer profile saved successfully!")
                    st.rerun()
                else:
                    st.error("Customer Name is required.")

    with col2:
        st.subheader("Search & Filter Customers")
        search_c = st.text_input("Search by Name, Phone, Address, or Thread Code...")
        
        sql = "SELECT name, phone, address, thread_codes FROM customers"
        if search_c:
            search_val = f"%{search_c.strip()}%"
            sql += " WHERE name LIKE %s OR phone LIKE %s OR address LIKE %s OR thread_codes LIKE %s"
            cdf = qry(sql, (search_val, search_val, search_val, search_val), fetch=True)
        else:
            cdf = qry(sql, fetch=True)
        
        if cdf is not None and not cdf.empty:
            for _, row in cdf.iterrows():
                st.write(f"### {row['name']}")
                st.write(f"**Phone:** {row['phone'] if row['phone'] else 'N/A'} | **Address:** {row['address'] if row['address'] else 'N/A'}")
                st.write(f"**Demanded Threads:** `{row['thread_codes'] if row['thread_codes'] else 'None Assigned'}`")
                st.markdown("---")
        else:
            st.info("No customers found matching the criteria.")