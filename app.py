import streamlit as st
import mysql.connector
import pandas as pd

# ১. পেজ কনফিগারেশন 
st.set_page_config(page_title="Thread Suite Pro", layout="wide")

# ২. কানেকশন ম্যানেজার ফাংশন (যা কুয়েরি শেষে রিসোর্স ফ্রি করে দেয়)
def get_db_connection():
    try:
        return mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            port=int(st.secrets["mysql"]["port"]),
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"],
            autocommit=True,
            connect_timeout=5
        )
    except Exception as e:
        return None

# ৩. লাইভ ডেটা রিড করার কুয়েরি (যা কানেকশন লিক হতে দেয় না)
def run_fetch_query(sql, params=None):
    conn = get_db_connection()
    if conn is None:
        st.error("⚠️ Database connection offline. Please check your credentials/secrets configuration.")
        return pd.DataFrame()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params or ())
        rows = cur.fetchall()
        cur.close()
        conn.close() # অত্যন্ত গুরুত্বপূর্ণ: কুয়েরি শেষে কানেকশন বন্ধ করা
        return pd.DataFrame(rows) if rows else pd.DataFrame()
    except Exception as e:
        try: cur.close()
        except: pass
        try: conn.close()
        except: pass
        return pd.DataFrame()

# ৪. ডেটা রাইট/আপডেট/ডিলিট কুয়েরি এক্সিকিউটর
def run_execute_query(sql, params=None):
    conn = get_db_connection()
    if conn is None:
        st.error("⚠️ Database connection offline. Action aborted.")
        return False
    try:
        cur = conn.cursor()
        cur.execute(sql, params or ())
        cur.close()
        conn.close() # অত্যন্ত গুরুত্বপূর্ণ
        return True
    except Exception as e:
        try: cur.close()
        except: pass
        try: conn.close()
        except: pass
        return False

# সাইডবার নেভিগেশন
st.sidebar.title("THREAD SUITE")
st.sidebar.markdown("---")
menu = st.sidebar.radio("NAVIGATION", ["Thread Inventory & Stock", "Seller Records", "Customer Directory"])

# গ্লোবাল সেশন স্টেট ভ্যারিয়েবলস
if "delete_id" not in st.session_state: st.session_state.delete_id = None
if "delete_mode" not in st.session_state: st.session_state.delete_mode = None
if "edit_id" not in st.session_state: st.session_state.edit_id = None
if "edit_data" not in st.session_state: st.session_state.edit_data = {}

# ══════════════════════════════════════════════════════════════
# ১. থ্রেড ইনভেন্টরি ও স্টক পেজ (ইনস্ট্যান্ট সেভ গ্যারান্টি)
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
                
                success = run_execute_query("""
                    INSERT INTO threads (thread_code, thread_name, current_stock) 
                    VALUES (%s, %s, %s) 
                    ON DUPLICATE KEY UPDATE thread_name=%s, current_stock=current_stock+%s
                """, (t_code.strip(), t_name.strip(), final_qty, t_name.strip(), final_qty))
                
                if success:
                    st.success(f"Successfully recorded: {t_name}")
                    st.rerun()
                else:
                    st.error("Failed to save data. Please try again.")
            else:
                st.error("SKU/Code and Product Name are required.")

    with col_view:
        st.subheader("Live Available Stock")
        search_t = st.text_input("Search Inventory by Code or Name...")
        
        sql = "SELECT thread_code as 'SKU/Code', thread_name as 'Product Name', current_stock as 'Available Stock' FROM threads"
        if search_t:
            search_val = f"%{search_t.strip().lower()}%"
            sql += " WHERE LOWER(thread_code) LIKE %s OR LOWER(thread_name) LIKE %s"
            df = run_fetch_query(sql, (search_val, search_val))
        else:
            df = run_fetch_query(sql)
            
        if df is not None and not df.empty:
            calc_height = min(len(df) * 35 + 45, 400)
            st.dataframe(df, use_container_width=True, hide_index=True, height=calc_height)
        else:
            st.info("No stock data found or database connection is waiting.")

# ══════════════════════════════════════════════════════════════
# ২. সেলার ডিরেক্টরি (নিরাপদ ড্রপডাউন ও কনফার্মেশন সহ ডিলিট)
# ══════════════════════════════════════════════════════════════
elif menu == "Seller Records":
    st.title("Seller Directory Management")
    
    # পপ আপ কনফার্মেশন প্রম্পট
    if st.session_state.delete_id and st.session_state.delete_mode == "seller":
        with st.container(border=True):
            st.error("⚠️ Confirm Action: Are you sure you want to permanently delete this seller?")
            c_b1, c_b2, _ = st.columns([1, 1, 4])
            if c_b1.button("Yes, Confirm Delete", type="primary", key="conf_del_sel"):
                run_execute_query("DELETE FROM sellers WHERE id=%s", (st.session_state.delete_id,))
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
                        run_execute_query("UPDATE sellers SET name=%s, phone=%s, address=%s, thread_codes=%s WHERE id=%s",
                                 (s_name.strip(), s_phone.strip(), s_address.strip(), s_threads.strip(), st.session_state.edit_id))
                        st.session_state.edit_id = None
                        st.session_state.edit_data = {}
                    else:
                        run_execute_query("INSERT INTO sellers (name, phone, address, thread_codes) VALUES (%s, %s, %s, %s)", 
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
            sdf = run_fetch_query(sql, (search_val, search_val, search_val))
        else:
            sdf = run_fetch_query(sql)
        
        if sdf is not None and not sdf.empty:
            for _, row in sdf.iterrows():
                with st.container(border=True):
                    c1, c2 = st.columns([4, 2])
                    with c1:
                        st.markdown(f"**Seller:** {row['name']} | **Phone:** {row['phone'] if row['phone'] else 'N/A'}")
                        st.markdown(f"📍 {row['address'] if row['address'] else 'N/A'} | 🧵 `{row['thread_codes'] if row['thread_codes'] else 'None'}`")
                    with c2:
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
            st.info("No sellers registered yet.")

# ══════════════════════════════════════════════════════════════
# ৩. কাস্টমার ডিরেক্টরি (নিরাপদ ড্রপডাউন ও কনফার্মেশন সহ ডিলিট)
# ══════════════════════════════════════════════════════════════
elif menu == "Customer Directory":
    st.title("Customer Directory Management")
    
    if st.session_state.delete_id and st.session_state.delete_mode == "customer":
        with st.container(border=True):
            st.error("⚠️ Confirm Action: Are you sure you want to permanently delete this customer?")
            c_b1, c_b2, _ = st.columns([1, 1, 4])
            if c_b1.button("Yes, Confirm Delete", type="primary", key="conf_del_cust"):
                run_execute_query("DELETE FROM customers WHERE id=%s", (st.session_state.delete_id,))
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
                        run_execute_query("UPDATE customers SET name=%s, phone=%s, address=%s, thread_codes=%s WHERE id=%s",
                                 (c_name.strip(), c_phone.strip(), c_address.strip(), c_threads.strip(), st.session_state.edit_id))
                        st.session_state.edit_id = None
                        st.session_state.edit_data = {}
                    else:
                        run_execute_query("INSERT INTO customers (name, phone, address, thread_codes) VALUES (%s, %s, %s, %s)", 
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
            cdf = run_fetch_query(sql, (search_val, search_val, search_val))
        else:
            cdf = run_fetch_query(sql)
        
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
            st.info("No customers registered yet.")