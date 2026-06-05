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
        return True
    except Exception as e:
        st.cache_resource.clear()
        return pd.DataFrame() if fetch else False

# সাইডবার নেভিগেশন
st.sidebar.title("THREAD SUITE")
st.sidebar.markdown("---")
menu = st.sidebar.radio("NAVIGATION", ["Thread Inventory & Stock", "Seller Records", "Customer Directory"])

# ══════════════════════════════════════════════════════════════
# ১. থ্রেড ইনভেন্টরি ও স্টক ভলিউম পেজ (ইনপুট, আউটপুট ও সার্চ)
# ══════════════════════════════════════════════════════════════
if menu == "Thread Inventory & Stock":
    st.title("Product Catalog & Stock Volume")
    col_add, col_view = st.columns([1, 2], gap="large")
    
    with col_add:
        st.subheader("Add / Update Thread Stock")
        with st.form("add_thread_form", clear_on_submit=True):
            t_code = st.text_input("SKU / Code *")
            t_name = st.text_input("Product Name *")
            t_qty = st.number_input("Initial Stock / Volume Qty", min_value=0, value=0, step=1)
            if st.form_submit_button("Save Product to Stock"):
                if t_code and t_name:
                    qry("""
                        INSERT INTO threads (thread_code, thread_name, current_stock) 
                        VALUES (%s, %s, %s) 
                        ON DUPLICATE KEY UPDATE thread_name=%s, current_stock=current_stock+%s
                    """, (t_code.strip(), t_name.strip(), t_qty, t_name.strip(), t_qty))
                    st.success("Product stock catalog successfully updated!")
                    st.rerun()
                else:
                    st.error("Please fill in all required fields.")

    with col_view:
        st.subheader("Live Available Stock & Volume")
        
        # সুতার কোড বা নাম দিয়ে সার্চ করার জন্য কেস-ইনসেনসিটিভ সার্চ বক্স
        search_t = st.text_input("Search Inventory by Code or Name (Any Case)...", placeholder="Type e.g., T10 or Cotton")
        
        sql = "SELECT thread_code as 'SKU/Code', thread_name as 'Product Name', current_stock as 'Available Stock (Volume)' FROM threads"
        if search_t:
            search_val = f"%{search_t.strip().lower()}%"
            sql += " WHERE LOWER(thread_code) LIKE %s OR LOWER(thread_name) LIKE %s"
            df = qry(sql, (search_val, search_val), fetch=True)
        else:
            df = qry(sql, fetch=True)
            
        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No stock data found matching the criteria.")

# ══════════════════════════════════════════════════════════════
# ২. সেলার ডিরেক্টরি
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
            s_threads = st.text_input("Supplied Thread Codes (e.g., T10, T20)", value=st.session_state.edit_seller_data.get('thread_codes', ''))
            
            submit_label = "Update Seller Profile" if st.session_state.edit_seller_id else "Save New Seller"
            if st.form_submit_button(submit_label):
                if s_name:
                    if st.session_state.edit_seller_id:
                        qry("UPDATE sellers SET name=%s, phone=%s, address=%s, thread_codes=%s WHERE id=%s",
                            (s_name.strip(), s_phone.strip(), s_address.strip(), s_threads.strip(), st.session_state.edit_seller_id))
                        st.success("Seller profile successfully updated!")
                        st.session_state.edit_seller_id = None
                        st.session_state.edit_seller_data = {}
                    else:
                        qry("INSERT INTO sellers (name, phone, address, thread_codes) VALUES (%s, %s, %s, %s)", 
                            (s_name.strip(), s_phone.strip(), s_address.strip(), s_threads.strip()))
                        st.success("New seller profile saved successfully!")
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
        search_s = st.text_input("Search by Name, Phone, or Thread Code (Any Case)...")
        
        sql = "SELECT id, name, phone, address, thread_codes FROM sellers"
        if search_s:
            search_val = f"%{search_s.strip().lower()}%"
            sql += " WHERE LOWER(name) LIKE %s OR LOWER(phone) LIKE %s OR LOWER(thread_codes) LIKE %s"
            sdf = qry(sql, (search_val, search_val, search_val), fetch=True)
        else:
            sdf = qry(sql, fetch=True)
        
        if sdf is not None and not sdf.empty:
            for _, row in sdf.iterrows():
                st.write(f"### {row['name']}")
                st.write(f"**Phone:** {row['phone'] if row['phone'] else 'N/A'} | **Address:** {row['address'] if row['address'] else 'N/A'}")
                st.write(f"**Deals with Threads:** `{row['thread_codes'] if row['thread_codes'] else 'None Assigned'}`")
                
                b_col1, b_col2, _ = st.columns([1, 1, 4])
                if b_col1.button("Edit", key=f"edit_s_{row['id']}"):
                    st.session_state.edit_seller_id = row['id']
                    st.session_state.edit_seller_data = row
                    st.rerun()
                if b_col2.button("Delete", key=f"del_s_{row['id']}"):
                    qry("DELETE FROM sellers WHERE id=%s", (row['id'],))
                    st.success(f"Deleted {row['name']} successfully.")
                    st.rerun()
                st.markdown("---")
        else:
            st.info("No sellers found matching the criteria.")

# ══════════════════════════════════════════════════════════════
# ৩. কাস্টমার ডিরেক্টরি
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
            c_threads = st.text_input("Required Thread Codes (e.g., T10, T40)", value=st.session_state.edit_customer_data.get('thread_codes', ''))
            
            submit_label = "Update Customer Profile" if st.session_state.edit_customer_id else "Save New Customer"
            if st.form_submit_button(submit_label):
                if c_name:
                    if st.session_state.edit_customer_id:
                        qry("UPDATE customers SET name=%s, phone=%s, address=%s, thread_codes=%s WHERE id=%s",
                            (c_name.strip(), c_phone.strip(), c_address.strip(), c_threads.strip(), st.session_state.edit_customer_id))
                        st.success("Customer profile successfully updated!")
                        st.session_state.edit_customer_id = None
                        st.session_state.edit_customer_data = {}
                    else:
                        qry("INSERT INTO customers (name, phone, address, thread_codes) VALUES (%s, %s, %s, %s)", 
                            (c_name.strip(), c_phone.strip(), c_address.strip(), c_threads.strip()))
                        st.success("New customer profile saved successfully!")
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
        search_c = st.text_input("Search by Name, Phone, or Thread Code (Any Case)...")
        
        sql = "SELECT id, name, phone, address, thread_codes FROM customers"
        if search_c:
            search_val = f"%{search_c.strip().lower()}%"
            sql += " WHERE LOWER(name) LIKE %s OR LOWER(phone) LIKE %s OR LOWER(thread_codes) LIKE %s"
            cdf = qry(sql, (search_val, search_val, search_val), fetch=True)
        else:
            cdf = qry(sql, fetch=True)
        
        if cdf is not None and not cdf.empty:
            for _, row in cdf.iterrows():
                st.write(f"### {row['name']}")
                st.write(f"**Phone:** {row['phone'] if row['phone'] else 'N/A'} | **Address:** {row['address'] if row['address'] else 'N/A'}")
                st.write(f"**Demanded Threads:** `{row['thread_codes'] if row['thread_codes'] else 'None Assigned'}`")
                
                b_col1, b_col2, _ = st.columns([1, 1, 4])
                if b_col1.button("Edit", key=f"edit_c_{row['id']}"):
                    st.session_state.edit_customer_id = row['id']
                    st.session_state.edit_customer_data = row
                    st.rerun()
                if b_col2.button("Delete", key=f"del_c_{row['id']}"):
                    qry("DELETE FROM customers WHERE id=%s", (row['id'],))
                    st.success(f"Deleted {row['name']} successfully.")
                    st.rerun()
                st.markdown("---")
        else:
            st.info("No customers found matching the criteria.")