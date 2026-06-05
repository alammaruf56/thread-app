import streamlit as st
import mysql.connector
import pandas as pd

# ১. পেজ কনফিগারেশন 
st.set_page_config(page_title="Thread Suite Pro", layout="wide")

# ২. একদম সিম্পল ও র-কানেকশন ফাংশন (কোনো ক্যাশিং ছাড়া, যাতে ল্যাগ না হয়)
def get_db_connection():
    try:
        return mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            port=int(st.secrets["mysql"]["port"]),
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"],
            autocommit=True
        )
    except:
        return None

# ৩. কুয়েরি এক্সিকিউটর ফাংশন
def run_query(sql, params=None, is_fetch=False):
    conn = get_db_connection()
    if conn is None:
        return pd.DataFrame() if is_fetch else False
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params or ())
        if is_fetch:
            rows = cur.fetchall()
            cur.close()
            conn.close()
            return pd.DataFrame(rows) if rows else pd.DataFrame()
        cur.close()
        conn.close()
        return True
    except:
        try: cur.close()
        except: pass
        try: conn.close()
        except: pass
        return pd.DataFrame() if is_fetch else False

# সাইডবার নেভিগেশন
st.sidebar.title("THREAD SUITE")
st.sidebar.markdown("---")
menu = st.sidebar.radio("NAVIGATION", ["Thread Inventory & Stock", "Seller Records", "Customer Directory"])

# সেশন স্টেট (ইনস্ট্যান্ট অ্যাকশনের জন্য)
if "edit_id" not in st.session_state: st.session_state.edit_id = None
if "edit_data" not in st.session_state: st.session_state.edit_data = {}

# ══════════════════════════════════════════════════════════════
# ১. থ্রেড ইনভেন্টরি ও স্টক পেজ
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
                success = run_query("""
                    INSERT INTO threads (thread_code, thread_name, current_stock) 
                    VALUES (%s, %s, %s) 
                    ON DUPLICATE KEY UPDATE thread_name=%s, current_stock=current_stock+%s
                """, (t_code.strip(), t_name.strip(), final_qty, t_name.strip(), final_qty))
                if success:
                    st.success("Stock updated successfully!")
                    st.rerun()
                else: st.error("Database Error.")
            else: st.error("All fields are required.")

    with col_view:
        st.subheader("Live Available Stock")
        search_t = st.text_input("Search Inventory...")
        sql = "SELECT thread_code as 'SKU/Code', thread_name as 'Product Name', current_stock as 'Available Stock' FROM threads"
        if search_t:
            search_val = f"%{search_t.strip().lower()}%"
            sql += " WHERE LOWER(thread_code) LIKE %s OR LOWER(thread_name) LIKE %s"
            df = run_query(sql, (search_val, search_val), is_fetch=True)
        else:
            df = run_query(sql, is_fetch=True)
            
        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
        else: st.info("No records found.")

# ══════════════════════════════════════════════════════════════
# ২. সেলার ডিরেক্টরি (ফালতু ড্রপডাউন বাদ, সরাসরি বাটন স্টাইল)
# ══════════════════════════════════════════════════════════════
elif menu == "Seller Records":
    st.title("Seller Directory Management")
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
                        run_query("UPDATE sellers SET name=%s, phone=%s, address=%s, thread_codes=%s WHERE id=%s",
                                 (s_name.strip(), s_phone.strip(), s_address.strip(), s_threads.strip(), st.session_state.edit_id))
                        st.session_state.edit_id = None
                        st.session_state.edit_data = {}
                    else:
                        run_query("INSERT INTO sellers (name, phone, address, thread_codes) VALUES (%s, %s, %s, %s)", 
                                 (s_name.strip(), s_phone.strip(), s_address.strip(), s_threads.strip()))
                    st.rerun()
                else: st.error("Seller Name is required.")
        
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
            sdf = run_query(sql, (search_val, search_val, search_val), is_fetch=True)
        else:
            sdf = run_query(sql, is_fetch=True)
        
        if sdf is not None and not sdf.empty:
            for _, row in sdf.iterrows():
                with st.container(border=True):
                    c1, c2, c3 = st.columns([4, 1, 1])
                    with c1:
                        st.markdown(f"**Seller:** {row['name']} | **Phone:** {row['phone']}")
                        st.markdown(f"📍 {row['address']} | 🧵 `{row['thread_codes']}`")
                    with c2:
                        # সরাসরি এডিট বাটন
                        if st.button("📝 Edit", key=f"edit_sel_{row['id']}", use_container_width=True):
                            st.session_state.edit_id = row['id']
                            st.session_state.edit_data = row
                            st.rerun()
                    with c3:
                        # সরাসরি ডিলিট বাটন (ক্লিক করলেই সাথে সাথে ডিলিট)
                        if st.button("🗑️ Del", key=f"del_sel_{row['id']}", type="primary", use_container_width=True):
                            run_query("DELETE FROM sellers WHERE id=%s", (row['id'],))
                            st.rerun()
        else: st.info("No sellers found.")

# ══════════════════════════════════════════════════════════════
# ৩. কাস্টমার ডিরেক্টরি (সরাসরি বাটন স্টাইল)
# ══════════════════════════════════════════════════════════════
elif menu == "Customer Directory":
    st.title("Customer Directory Management")
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
                        run_query("UPDATE customers SET name=%s, phone=%s, address=%s, thread_codes=%s WHERE id=%s",
                                 (c_name.strip(), c_phone.strip(), c_address.strip(), c_threads.strip(), st.session_state.edit_id))
                        st.session_state.edit_id = None
                        st.session_state.edit_data = {}
                    else:
                        run_query("INSERT INTO customers (name, phone, address, thread_codes) VALUES (%s, %s, %s, %s)", 
                                 (c_name.strip(), c_phone.strip(), c_address.strip(), c_threads.strip()))
                    st.rerun()
                else: st.error("Customer Name is required.")
                    
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
            cdf = run_query(sql, (search_val, search_val, search_val), is_fetch=True)
        else:
            cdf = run_query(sql, is_fetch=True)
        
        if cdf is not None and not cdf.empty:
            for _, row in cdf.iterrows():
                with st.container(border=True):
                    c1, c2, c3 = st.columns([4, 1, 1])
                    with c1:
                        st.markdown(f"**Customer:** {row['name']} | **Phone:** {row['phone']}")
                        st.markdown(f"📍 {row['address']} | 🧵 `{row['thread_codes']}`")
                    with c2:
                        # সরাসরি এডিট বাটন
                        if st.button("📝 Edit", key=f"edit_cus_{row['id']}", use_container_width=True):
                            st.session_state.edit_id = row['id']
                            st.session_state.edit_data = row
                            st.rerun()
                    with c3:
                        # সরাসরি ডিলিট বাটন
                        if st.button("🗑️ Del", key=f"del_cus_{row['id']}", type="primary", use_container_width=True):
                            run_query("DELETE FROM customers WHERE id=%s", (row['id'],))
                            st.rerun()
        else: st.info("No customers found.")