import streamlit as st
import mysql.connector
import pandas as pd

# পেজ কনফিগারেশন
st.set_page_config(page_title="Thread Suite Pro", layout="wide")

# ১. ডেটাবেস কানেকশন (এটি একবারই তৈরি হবে এবং কখনোই ডিলিট হবে না)
@st.cache_resource
def init_connection():
    try:
        return mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            port=int(st.secrets["mysql"]["port"]),
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"],
            autocommit=True
        )
    except Exception as e:
        st.error(f"Database Connection Error: {e}")
        return None

db_conn = init_connection()

# ২. ডেটা রিড করার কুয়েরি ক্যাশ (এটি ডেটা সেভ হলে অটো রিফ্রেশ হবে, কানেকশন ভাঙবে না)
@st.cache_data(ttl=10)
def fetch_data(sql, params=None):
    if not db_conn:
        return pd.DataFrame()
    try:
        cur = db_conn.cursor(dictionary=True)
        cur.execute(sql, params or ())
        rows = cur.fetchall()
        cur.close()
        return pd.DataFrame(rows) if rows else pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

# ৩. ডেটা রাইট/আপডেট করার কুয়েরি (কোনো ক্যাশিং ছাড়া সরাসরি এক্সিকিউট)
def execute_data(sql, params=None):
    if not db_conn:
        return False
    try:
        cur = db_conn.cursor()
        cur.execute(sql, params or ())
        cur.close()
        return True
    except Exception as e:
        return False

# সাইডবার নেভিগেশন
st.sidebar.title("THREAD SUITE")
st.sidebar.markdown("---")
menu = st.sidebar.radio("NAVIGATION", ["Thread Inventory & Stock", "Seller Records", "Customer Directory"])

# ══════════════════════════════════════════════════════════════
# ১. থ্রেড ইনভেন্টরি ও স্টক ভলিউম পেজ
# ══════════════════════════════════════════════════════════════
if menu == "Thread Inventory & Stock":
    st.title("Product Catalog & Stock Volume")
    col_add, col_view = st.columns([1, 2], gap="large")
    
    with col_add:
        st.subheader("Manage Thread Stock")
        with st.form("add_thread_form", clear_on_submit=True):
            t_code = st.text_input("SKU / Code *")
            t_name = st.text_input("Product Name *")
            action = st.selectbox("Stock Action", ["Stock IN (Buy/Add)", "Stock OUT (Sell/Reduce)"])
            t_qty = st.number_input("Quantity / Volume", min_value=1, value=1, step=1)
            
            if st.form_submit_button("Update Stock Ledger"):
                if t_code and t_name:
                    final_qty = t_qty if action == "Stock IN (Buy/Add)" else -t_qty
                    
                    # সরাসরি ডাটাবেসে সেভ
                    execute_data("""
                        INSERT INTO threads (thread_code, thread_name, current_stock) 
                        VALUES (%s, %s, %s) 
                        ON DUPLICATE KEY UPDATE thread_name=%s, current_stock=current_stock+%s
                    """, (t_code.strip(), t_name.strip(), final_qty, t_name.strip(), final_qty))
                    
                    st.cache_data.clear() # শুধুমাত্র ডেটার ক্যাশ ক্লিয়ার হবে, কানেকশন অক্ষুণ্ণ থাকবে
                    st.success(f"Stock successfully recorded as {action}!")
                    st.rerun()
                else:
                    st.error("Please fill in all required fields.")

    with col_view:
        st.subheader("Live Available Stock")
        search_t = st.text_input("Search Inventory by Code or Name...")
        
        sql = "SELECT thread_code as 'SKU/Code', thread_name as 'Product Name', current_stock as 'Available Stock' FROM threads"
        if search_t:
            search_val = f"%{search_t.strip().lower()}%"
            sql += " WHERE LOWER(thread_code) LIKE %s OR LOWER(thread_name) LIKE %s"
            df = fetch_data(sql, (search_val, search_val))
        else:
            df = fetch_data(sql)
            
        if df is not None and not df.empty:
            calc_height = min(len(df) * 35 + 45, 350)
            st.dataframe(df, use_container_width=True, hide_index=True, height=calc_height)
        else:
            st.info("No stock data found in database.")

# ══════════════════════════════════════════════════════════════
# ২. সেলার ডিরেক্টরি (কম্প্যাক্ট সাইজ লেআউট)
# ══════════════════════════════════════════════════════════════
elif menu == "Seller Records":
    st.title("Seller Directory Management")
    col1, col2 = st.columns([1, 2], gap="large")
    
    with col1:
        st.subheader("Register / Edit Seller")
        if "edit_seller_id" not in st.session_state:
            st.session_state.edit_seller_id = None
            st.session_state.edit_seller_data = {}

        with st.form("seller_form", clear_on_submit=True):
            s_name = st.text_input("Seller Name *", value=st.session_state.edit_seller_data.get('name', ''))
            s_phone = st.text_input("Phone Number", value=st.session_state.edit_seller_data.get('phone', ''))
            s_address = st.text_input("Address", value=st.session_state.edit_seller_data.get('address', ''))
            s_threads = st.text_input("Supplied Thread Codes", value=st.session_state.edit_seller_data.get('thread_codes', ''))
            
            submit_label = "Update Seller Profile" if st.session_state.edit_seller_id else "Save New Seller"
            if st.form_submit_button(submit_label):
                if s_name:
                    if st.session_state.edit_seller_id:
                        execute_data("UPDATE sellers SET name=%s, phone=%s, address=%s, thread_codes=%s WHERE id=%s",
                                     (s_name.strip(), s_phone.strip(), s_address.strip(), s_threads.strip(), st.session_state.edit_seller_id))
                        st.success("Seller profile successfully updated!")
                        st.session_state.edit_seller_id = None
                        st.session_state.edit_seller_data = {}
                    else:
                        execute_data("INSERT INTO sellers (name, phone, address, thread_codes) VALUES (%s, %s, %s, %s)", 
                                     (s_name.strip(), s_phone.strip(), s_address.strip(), s_threads.strip()))
                        st.success("New seller profile saved successfully!")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("Seller Name is required.")
        
        if st.session_state.edit_seller_id:
            if st.button("Cancel Edit Mode"):
                st.session_state.edit_seller_id = None
                st.session_state.edit_seller_data = {}
                st.rerun()

    with col2:
        st.subheader("Search & Manage Sellers")
        search_s = st.text_input("Search Sellers...")
        
        sql = "SELECT id, name, phone, address, thread_codes FROM sellers"
        if search_s:
            search_val = f"%{search_s.strip().lower()}%"
            sql += " WHERE LOWER(name) LIKE %s OR LOWER(phone) LIKE %s OR LOWER(thread_codes) LIKE %s"
            sdf = fetch_data(sql, (search_val, search_val, search_val))
        else:
            sdf = fetch_data(sql)
        
        if sdf is not None and not sdf.empty:
            for _, row in sdf.iterrows():
                with st.container(border=True):
                    c1, c2, c3 = st.columns([2, 3, 1.5])
                    c1.markdown(f"**👤 {row['name']}**")
                    c2.markdown(f"📞 {row['phone'] if row['phone'] else 'N/A'} | 📍 {row['address'] if row['address'] else 'N/A'}\n\n🧵 `{row['thread_codes'] if row['thread_codes'] else 'None'}`")
                    
                    b1, b2 = c3.columns(2)
                    if b1.button("✏️", key=f"edit_s_{row['id']}", help="Edit"):
                        st.session_state.edit_seller_id = row['id']
                        st.session_state.edit_seller_data = row
                        st.rerun()
                    if b2.button("❌", key=f"del_s_{row['id']}", help="Delete"):
                        execute_data("DELETE FROM sellers WHERE id=%s", (row['id'],))
                        st.cache_data.clear()
                        st.rerun()
        else:
            st.info("No sellers found matching the criteria.")

# ══════════════════════════════════════════════════════════════
# ৩. কাস্টমার ডিরেক্টরি (কম্প্যাক্ট সাইজ লেআউট)
# ══════════════════════════════════════════════════════════════
elif menu == "Customer Directory":
    st.title("Customer Directory Management")
    col1, col2 = st.columns([1, 2], gap="large")
    
    with col1:
        st.subheader("Register / Edit Customer")
        if "edit_customer_id" not in st.session_state:
            st.session_state.edit_customer_id = None
            st.session_state.edit_customer_data = {}

        with st.form("customer_form", clear_on_submit=True):
            c_name = st.text_input("Customer Name *", value=st.session_state.edit_customer_data.get('name', ''))
            c_phone = st.text_input("Phone Number", value=st.session_state.edit_customer_data.get('phone', ''))
            c_address = st.text_input("Address", value=st.session_state.edit_customer_data.get('address', ''))
            c_threads = st.text_input("Required Thread Codes", value=st.session_state.edit_customer_data.get('thread_codes', ''))
            
            submit_label = "Update Customer Profile" if st.session_state.edit_customer_id else "Save New Customer"
            if st.form_submit_button(submit_label):
                if c_name:
                    if st.session_state.edit_customer_id:
                        execute_data("UPDATE customers SET name=%s, phone=%s, address=%s, thread_codes=%s WHERE id=%s",
                                     (c_name.strip(), c_phone.strip(), c_address.strip(), c_threads.strip(), st.session_state.edit_customer_id))
                        st.success("Customer profile successfully updated!")
                        st.session_state.edit_customer_id = None
                        st.session_state.edit_customer_data = {}
                    else:
                        execute_data("INSERT INTO customers (name, phone, address, thread_codes) VALUES (%s, %s, %s, %s)", 
                                     (c_name.strip(), c_phone.strip(), c_address.strip(), c_threads.strip()))
                        st.success("New customer profile saved successfully!")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("Customer Name is required.")
                    
        if st.session_state.edit_customer_id:
            if st.button("Cancel Edit Mode"):
                st.session_state.edit_customer_id = None
                st.session_state.edit_customer_data = {}
                st.rerun()

    with col2:
        st.subheader("Search & Manage Customers")
        search_c = st.text_input("Search Customers...")
        
        sql = "SELECT id, name, phone, address, thread_codes FROM customers"
        if search_c:
            search_val = f"%{search_c.strip().lower()}%"
            sql += " WHERE LOWER(name) LIKE %s OR LOWER(phone) LIKE %s OR LOWER(thread_codes) LIKE %s"
            cdf = fetch_data(sql, (search_val, search_val, search_val))
        else:
            cdf = fetch_data(sql)
        
        if cdf is not None and not cdf.empty:
            for _, row in cdf.iterrows():
                with st.container(border=True):
                    c1, c2, c3 = st.columns([2, 3, 1.5])
                    c1.markdown(f"**👤 {row['name']}**")
                    c2.markdown(f"📞 {row['phone'] if row['phone'] else 'N/A'} | 📍 {row['address'] if row['address'] else 'N/A'}\n\n🧵 `{row['thread_codes'] if row['thread_codes'] else 'None'}`")
                    
                    b1, b2 = c3.columns(2)
                    if b1.button("✏️", key=f"edit_c_{row['id']}", help="Edit"):
                        st.session_state.edit_customer_id = row['id']
                        st.session_state.edit_customer_data = row
                        st.rerun()
                    if b2.button("❌", key=f"del_c_{row['id']}", help="Delete"):
                        execute_data("DELETE FROM customers WHERE id=%s", (row['id'],))
                        st.cache_data.clear()
                        st.rerun()
        else:
            st.info("No customers found matching the criteria.")