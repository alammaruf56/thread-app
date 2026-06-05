import streamlit as st
import mysql.connector
import pandas as pd

# ১. পেজ কনফিগারেশন ও প্রিমিয়াম UI স্টাইলিং (স্পেস ও ল্যাগ কমানোর জন্য)
st.set_page_config(page_title="Thread Suite Pro", layout="wide")
st.markdown("""
    <style>
    .block-container {padding-top: 1.5rem; padding-bottom: 1rem;}
    div.stButton > button {width: 100%; border-radius: 6px;}
    .stSelectbox div[data-baseweb="select"] {border-radius: 6px;}
    div[data-testid="stForm"] {border-radius: 8px; padding: 15px;}
    </style>
""", unsafe_with_html=True)

# ২. গ্লোবাল কানেকশন পুলিং (কানেকশন লিক ও ক্র্যাশ চিরতরে বন্ধ)
@st.cache_resource
def get_db_pool():
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
        st.error(f"Database Connection Failed: {e}")
        return None

db_conn = get_db_pool()

# ৩. হাই-স্পিড ডেটা কুয়েরি এক্সিকিউটর (মিলি-সেকেন্ডে রেসপন্স করবে)
def db_query(sql, params=None, fetch=False):
    if not db_conn:
        return pd.DataFrame() if fetch else False
    try:
        cur = db_conn.cursor(dictionary=True)
        cur.execute(sql, params or ())
        if fetch:
            rows = cur.fetchall()
            cur.close()
            return pd.DataFrame(rows) if rows else pd.DataFrame()
        cur.close()
        return True
    except Exception as e:
        return pd.DataFrame() if fetch else False

# সাইডবার নেভিগেশন
st.sidebar.title("THREAD SUITE")
st.sidebar.markdown("---")
menu = st.sidebar.radio("NAVIGATION", ["Thread Inventory & Stock", "Seller Records", "Customer Directory"])

# গ্লোবাল স্টেট ট্র্যাকিং (যাতে এডিট/ডিলিট করার সময় ল্যাগ বা ক্র্যাশ না করে)
if "delete_id" not in st.session_state: st.session_state.delete_id = None
if "delete_mode" not in st.session_state: st.session_state.delete_mode = None
if "edit_id" not in st.session_state: st.session_state.edit_id = None
if "edit_data" not in st.session_state: st.session_state.edit_data = {}

# ══════════════════════════════════════════════════════════════
# ১. থ্রেড ইনভেন্টরি ও স্টক পেজ (১০০% ইনস্ট্যান্ট সেভ ফিক্স)
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
            submit_btn = st.form_submit_button("Update Stock Ledger")
            
        if submit_btn:
            if t_code.strip() and t_name.strip():
                final_qty = t_qty if action == "Stock IN (Buy/Add)" else -t_qty
                
                # অন-ডুপ্লিকেট কিউওয়ার্ড ব্যবহার করে এক কুয়েরিতেই ইনসার্ট ও লাইভ স্টক ক্যালকুলেশন
                success = db_query("""
                    INSERT INTO threads (thread_code, thread_name, current_stock) 
                    VALUES (%s, %s, %s) 
                    ON DUPLICATE KEY UPDATE thread_name=%s, current_stock=current_stock+%s
                """, (t_code.strip(), t_name.strip(), final_qty, t_name.strip(), final_qty))
                
                if success:
                    st.success(f"Successfully updated: {t_name}")
                    st.rerun()
                else:
                    st.error("Database update failed.")
            else:
                st.error("SKU/Code and Product Name are required.")

    with col_view:
        st.subheader("Live Available Stock")
        search_t = st.text_input("Search Inventory by Code or Name (Any Case)...")
        
        sql = "SELECT thread_code as 'SKU/Code', thread_name as 'Product Name', current_stock as 'Available Stock' FROM threads"
        if search_t:
            search_val = f"%{search_t.strip().lower()}%"
            sql += " WHERE LOWER(thread_code) LIKE %s OR LOWER(thread_name) LIKE %s"
            df = db_query(sql, (search_val, search_val), fetch=True)
        else:
            df = db_query(sql, fetch=True)
            
        if df is not None and not df.empty:
            calc_height = min(len(df) * 35 + 45, 400)
            st.dataframe(df, use_container_width=True, hide_index=True, height=calc_height)
        else:
            st.info("No stock items found.")

# ══════════════════════════════════════════════════════════════
# ২. সেলার ডিরেক্টরি (ড্রপডাউন অ্যাকশন ও পপ-আপ ডিলিট কনফার্মেশন)
# ══════════════════════════════════════════════════════════════
elif menu == "Seller Records":
    st.title("Seller Directory Management")
    
    # প্রফেশনাল ডিলিট কনফার্মেশন প্রম্পট
    if st.session_state.delete_id and st.session_state.delete_mode == "seller":
        with st.container(border=True):
            st.error("⚠️ Confirm Action: Are you sure you want to permanently delete this seller?")
            c_b1, c_b2, _ = st.columns([1, 1, 4])
            if c_b1.button("Yes, Confirm Delete", type="primary", key="conf_del_sel"):
                db_query("DELETE FROM sellers WHERE id=%s", (st.session_state.delete_id,))
                st.session_state.delete_id = None
                st.session_state.delete_mode = None
                st.rerun()
            if c_b2.button("Cancel", key="canc_del_sel"):
                st.session_state.delete_id = None
                st.session_state.delete_mode = None
                st.rerun()
        st.markdown("---")

    col1, col2 = st.columns([1, 2], gap="large")
    
    with col1:
        st.subheader("Register / Edit Seller")
        with st.form("seller_form", clear_on_submit=True):
            s_name = st.text_input("Seller Name *", value=st.session_state.edit_data.get('name', ''))
            s_phone = st.text_input("Phone Number", value=st.session_state.edit_data.get('phone', ''))
            s_address = st.text_input("Address", value=st.session_state.edit_data.get('address', ''))
            s_threads = st.text_input("Supplied Thread Codes", value=st.session_state.edit_data.get('thread_codes', ''))
            
            submit_label = "Update Profile" if st.session_state.edit_id else "Save New Seller"
            if st.form_submit_button(submit_label):
                if s_name.strip():
                    if st.session_state.edit_id:
                        db_query("UPDATE sellers SET name=%s, phone=%s, address=%s, thread_codes=%s WHERE id=%s",
                                 (s_name.strip(), s_phone.strip(), s_address.strip(), s_threads.strip(), st.session_state.edit_id))
                        st.session_state.edit_id = None
                        st.session_state.edit_data = {}
                    else:
                        db_query("INSERT INTO sellers (name, phone, address, thread_codes) VALUES (%s, %s, %s, %s)", 
                                 (s_name.strip(), s_phone.strip(), s_address.strip(), s_threads.strip()))
                    st.rerun()
                else:
                    st.error("Seller Name is required.")
        
        if st.session_state.edit_id:
            if st.button("Cancel Edit"):
                st.session_state.edit_id = None
                st.session_state.edit_data = {}
                st.rerun()

    with col2:
        st.subheader("Search & Manage Sellers")
        search_s = st.text_input("Search Sellers...")
        
        sql = "SELECT id, name, phone, address, thread_codes FROM sellers"
        if search_s:
            search_val = f"%{search_s.strip().lower()}%"
            sql += " WHERE LOWER(name) LIKE %s OR LOWER(phone) LIKE %s OR LOWER(thread_codes) LIKE %s"
            sdf = db_query(sql, (search_val, search_val, search_val), fetch=True)
        else:
            sdf = db_query(sql, fetch=True)
        
        if sdf is not None and not sdf.empty:
            for _, row in sdf.iterrows():
                with st.container(border=True):
                    c1, c2 = st.columns([4, 2])
                    with c1:
                        st.markdown(f"**Seller:** {row['name']} | **Phone:** {row['phone'] if row['phone'] else 'N/A'}")
                        st.markdown(f"📍 {row['address'] if row['address'] else 'N/A'} | 🧵 `{row['thread_codes'] if row['thread_codes'] else 'None'}`")
                    with c2:
                        # ক্লিন ড্রপডাউন ম্যানেজমেন্ট (কোনো বাটন ক্লাটার থাকবে না)
                        action_choice = st.selectbox("Action", ["Options...", "Edit", "Delete"], key=f"sel_act_{row['id']}")
                        if action_choice == "Edit":
                            st.session_state.edit_id = row['id']
                            st.session_state.edit_data = row
                            st.rerun()
                        elif action_choice == "Delete":
                            st.session_state.delete_id = row['id']
                            st.session_state.delete_mode = "seller"
                            st.rerun()
        else:
            st.info("No sellers found.")

# ══════════════════════════════════════════════════════════════
# ৩. কাস্টমার ডিরেক্টরি (ড্রপডাউন অ্যাকশন ও পপ-আপ ডিলিট কনফার্মেশন)
# ══════════════════════════════════════════════════════════════
elif menu == "Customer Directory":
    st.title("Customer Directory Management")
    
    # প্রফেশনাল ডিলিট কনফার্মেশন প্রম্পট
    if st.session_state.delete_id and st.session_state.delete_mode == "customer":
        with st.container(border=True):
            st.error("⚠️ Confirm Action: Are you sure you want to permanently delete this customer?")
            c_b1, c_b2, _ = st.columns([1, 1, 4])
            if c_b1.button("Yes, Confirm Delete", type="primary", key="conf_del_cust"):
                db_query("DELETE FROM customers WHERE id=%s", (st.session_state.delete_id,))
                st.session_state.delete_id = None
                st.session_state.delete_mode = None
                st.rerun()
            if c_b2.button("Cancel", key="canc_del_cust"):
                st.session_state.delete_id = None
                st.session_state.delete_mode = None
                st.rerun()
        st.markdown("---")

    col1, col2 = st.columns([1, 2], gap="large")
    
    with col1:
        st.subheader("Register / Edit Customer")
        with st.form("customer_form", clear_on_submit=True):
            c_name = st.text_input("Customer Name *", value=st.session_state.edit_data.get('name', ''))
            c_phone = st.text_input("Phone Number", value=st.session_state.edit_data.get('phone', ''))
            c_address = st.text_input("Address", value=st.session_state.edit_data.get('address', ''))
            c_threads = st.text_input("Required Thread Codes", value=st.session_state.edit_data.get('thread_codes', ''))
            
            submit_label = "Update Profile" if st.session_state.edit_id else "Save New Customer"
            if st.form_submit_button(submit_label):
                if c_name.strip():
                    if st.session_state.edit_id:
                        db_query("UPDATE customers SET name=%s, phone=%s, address=%s, thread_codes=%s WHERE id=%s",
                                 (c_name.strip(), c_phone.strip(), c_address.strip(), c_threads.strip(), st.session_state.edit_id))
                        st.session_state.edit_id = None
                        st.session_state.edit_data = {}
                    else:
                        db_query("INSERT INTO customers (name, phone, address, thread_codes) VALUES (%s, %s, %s, %s)", 
                                 (c_name.strip(), c_phone.strip(), c_address.strip(), c_threads.strip()))
                    st.rerun()
                else:
                    st.error("Customer Name is required.")
                    
        if st.session_state.edit_id:
            if st.button("Cancel Edit"):
                st.session_state.edit_id = None
                st.session_state.edit_data = {}
                st.rerun()

    with col2:
        st.subheader("Search & Manage Customers")
        search_c = st.text_input("Search Customers...")
        
        sql = "SELECT id, name, phone, address, thread_codes FROM customers"
        if search_c:
            search_val = f"%{search_c.strip().lower()}%"
            sql += " WHERE LOWER(name) LIKE %s OR LOWER(phone) LIKE %s OR LOWER(thread_codes) LIKE %s"
            cdf = db_query(sql, (search_val, search_val, search_val), fetch=True)
        else:
            cdf = db_query(sql, fetch=True)
        
        if cdf is not None and not cdf.empty:
            for _, row in cdf.iterrows():
                with st.container(border=True):
                    c1, c2 = st.columns([4, 2])
                    with c1:
                        st.markdown(f"**Customer:** {row['name']} | **Phone:** {row['phone'] if row['phone'] else 'N/A'}")
                        st.markdown(f"📍 {row['address'] if row['address'] else 'N/A'} | 🧵 `{row['thread_codes'] if row['thread_codes'] else 'None'}`")
                    with c2:
                        action_choice = st.selectbox("Action", ["Options...", "Edit", "Delete"], key=f"cust_act_{row['id']}")
                        if action_choice == "Edit":
                            st.session_state.edit_id = row['id']
                            st.session_state.edit_data = row
                            st.rerun()
                        elif action_choice == "Delete":
                            st.session_state.delete_id = row['id']
                            st.session_state.delete_mode = "customer"
                            st.rerun()
        else:
            st.info("No customers found.")