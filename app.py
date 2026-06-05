import streamlit as st
import mysql.connector
import pandas as pd
import datetime

# মডার্ন ফুল-উইডথ ও টাইটেল সেটআপ
st.set_page_config(page_title="Thread Suite Pro", page_icon="🧵", layout="wide")

# 🎨 প্রিমিয়াম ব্র্যান্ডেড লুকের জন্য কাস্টম সিএসএস (CSS)
st.markdown("""
    <style>
    /* ব্যাকগ্রাউন্ড ও ফন্ট স্টাইল */
    .stApp { background-color: #f8f9fa; }
    h1, h2, h3 { color: #1e293b; font-family: 'Segoe UI', sans-serif; font-weight: 700; }
    
    /* কাস্টম ডেটা কার্ড স্টাইল (বড় ব্র্যান্ডের মতো) */
    .premium-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03);
        border: 1px solid #e2e8f0;
        margin-bottom: 15px;
    }
    .badge-buy {
        background-color: #dcfce7; color: #15803d;
        padding: 4px 10px; border-radius: 20px; font-weight: bold; font-size: 13px;
    }
    .badge-sell {
        background-color: #fee2e2; color: #b91c1c;
        padding: 4px 10px; border-radius: 20px; font-weight: bold; font-size: 13px;
    }
    </style>
""", unsafe_with_html=True)

# ডাটাবেস কানেকশন
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

# সাইডবার মেনু ডিজাইন
st.sidebar.markdown("<h2 style='text-align:center; color:#4f46e5;'>🧵 THREAD SUITE</h2>", unsafe_with_html=True)
st.sidebar.markdown("---")
menu = st.sidebar.radio("NAVIGATION", ["📦 Thread Inventory", "🤝 Seller Records", "👥 Customer Directory", "🔄 Quick Transaction"])

# ══════════════════════════════════════════════════════════════
# ১. থ্রেড ইনভেন্টরি পেজ
# ══════════════════════════════════════════════════════════════
if menu == "📦 Thread Inventory":
    st.markdown("<h1>📦 Thread Catalog & Stock</h1>", unsafe_with_html=True)
    
    col_add, col_view = st.columns([1, 2], gap="large")
    
    with col_add:
        st.markdown("<div class='premium-card'><h3>➕ Add New Thread</h3>", unsafe_with_html=True)
        with st.form("add_t", clear_on_submit=True):
            t_code = st.text_input("Thread Code / Number *")
            t_name = st.text_input("Thread Name / Description *")
            if st.form_submit_button("Save to Catalog"):
                if t_code and t_name:
                    qry("INSERT IGNORE INTO threads (thread_code, thread_name) VALUES (%s, %s)", (t_code, t_name))
                    st.success("Thread Saved!")
                    st.rerun()
        st.markdown("</div>", unsafe_with_html=True)

    with col_view:
        st.markdown("<h3>📋 Current Registered Stock</h3>", unsafe_with_html=True)
        df = qry("SELECT thread_code as 'Thread Code', thread_name as 'Name' FROM threads", fetch=True)
        if not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No threads added yet.")

# ══════════════════════════════════════════════════════════════
# ২. সেলার ডিরেক্টরি (প্রিমিয়াম কার্ড সার্চ ও সুতার তথ্য)
# ══════════════════════════════════════════════════════════════
elif menu == "🤝 Seller Records":
    st.markdown("<h1>🤝 Seller Profile Hub</h1>", unsafe_with_html=True)
    
    col1, col2 = st.columns([1, 2], gap="large")
    
    with col1:
        st.markdown("<div class='premium-card'><h3>➕ Register Seller</h3>", unsafe_with_html=True)
        with st.form("add_s", clear_on_submit=True):
            s_name = st.text_input("Seller Name *")
            s_phone = st.text_input("Phone Number")
            s_address = st.text_input("Address")
            if st.form_submit_button("Add Seller Profile"):
                if s_name:
                    qry("INSERT INTO sellers (name, phone, address) VALUES (%s, %s, %s)", (s_name, s_phone, s_address))
                    st.success("Seller Profile Created!")
                    st.rerun()
        st.markdown("</div>", unsafe_with_html=True)

    with col2:
        st.markdown("<h3>🔍 Search Seller Profiles</h3>", unsafe_with_html=True)
        search_s = st.text_input("Type Seller Name to Search...", placeholder="e.g. Rahim Traders")
        
        sql = "SELECT name, phone, address FROM sellers"
        if search_s:
            sql += f" WHERE name LIKE '%{search_s}%'"
        
        sdf = qry(sql, fetch=True)
        
        if not sdf.empty:
            for _, row in sdf.iterrows():
                # কার্ড ফরম্যাটে সেলারের তথ্য দেখানো
                st.markdown(f"""
                    <div class='premium-card'>
                        <h3 style='color:#4f46e5; margin-bottom:5px;'>👤 {row['name']}</h3>
                        <p style='margin:2px 0;'>📞 <b>Phone:</b> {row['phone'] if row['phone'] else 'N/A'}</p>
                        <p style='margin:2px 0;'>📍 <b>Address:</b> {row['address'] if row['address'] else 'N/A'}</p>
                    </div>
                """, unsafe_with_html=True)
                
                # ওই সেলার কোন সুতা সাপ্লাই দিয়েছে তার কার্ড লিস্ট
                tsql = "SELECT thread_code, SUM(quantity) as qty FROM transactions WHERE party_name=%s AND transaction_type='BUY' GROUP BY thread_code"
                tdf = qry(tsql, (row['name'],), fetch=True)
                
                if not tdf.empty:
                    st.markdown(f"**🧵 Threads Supplied by {row['name']}:**")
                    cols = st.columns(len(tdf) if len(tdf) < 4 else 4)
                    for i, t_row in tdf.iterrows():
                        with cols[i % 4]:
                            st.markdown(f"""
                                <div style='background:#ffffff; padding:10px; border-radius:8px; border:1px solid #cbd5e1; text-align:center;'>
                                    <span class='badge-buy'>SUPPLIED</span>
                                    <h4 style='margin:8px 0 2px 0;'>Code: {t_row['thread_code']}</h4>
                                    <p style='margin:0; color:#64748b;'>Qty: <b>{t_row['qty']}</b></p>
                                </div>
                            """, unsafe_with_html=True)
                else:
                    st.caption("No supply history recorded yet.")
        else:
            st.info("No sellers found matching the search criteria.")

# ══════════════════════════════════════════════════════════════
# ৩. কাস্টমার ডিরেক্টরি (প্রিমিয়াম কার্ড সার্চ ও কাস্টমার ট্র্যাকিং)
# ══════════════════════════════════════════════════════════════
elif menu == "👥 Customer Directory":
    st.markdown("<h1>👥 Customer Management Hub</h1>", unsafe_with_html=True)
    
    col1, col2 = st.columns([1, 2], gap="large")
    
    with col1:
        st.markdown("<div class='premium-card'><h3>➕ Register Client</h3>", unsafe_with_html=True)
        with st.form("add_c", clear_on_submit=True):
            c_name = st.text_input("Customer Name *")
            c_phone = st.text_input("Phone Number")
            c_address = st.text_input("Address")
            if st.form_submit_button("Create Client Profile"):
                if c_name:
                    qry("INSERT INTO customers (name, phone, address) VALUES (%s, %s, %s)", (c_name, c_phone, c_address))
                    st.success("Client Profile Created!")
                    st.rerun()
        st.markdown("</div>", unsafe_with_html=True)

    with col2:
        st.markdown("<h3>🔍 Search Customer Directory</h3>", unsafe_with_html=True)
        search_c = st.text_input("Type Customer Name to Search...", placeholder="e.g. Apex Apparel")
        
        sql = "SELECT name, phone, address FROM customers"
        if search_c:
            sql += f" WHERE name LIKE '%{search_c}%'"
            
        cdf = qry(sql, fetch=True)
        
        if not cdf.empty:
            for _, row in cdf.iterrows():
                # কার্ড ফরম্যাটে কাস্টমারের তথ্য দেখানো
                st.markdown(f"""
                    <div class='premium-card'>
                        <h3 style='color:#0ea5e9; margin-bottom:5px;'>🏢 {row['name']}</h3>
                        <p style='margin:2px 0;'>📞 <b>Phone:</b> {row['phone'] if row['phone'] else 'N/A'}</p>
                        <p style='margin:2px 0;'>📍 <b>Address:</b> {row['address'] if row['address'] else 'N/A'}</p>
                    </div>
                """, unsafe_with_html=True)
                
                # ওই কাস্টমার কোন সুতা কতটুকু নিয়েছে তার কার্ড লিস্ট
                t_c_sql = "SELECT thread_code, SUM(quantity) as qty FROM transactions WHERE party_name=%s AND transaction_type='SELL' GROUP BY thread_code ORDER BY qty DESC"
                t_c_df = qry(t_c_sql, (row['name'],), fetch=True)
                
                if not t_c_df.empty:
                    st.markdown(f"**📊 Purchase History for {row['name']}:**")
                    cols = st.columns(len(t_c_df) if len(t_c_df) < 4 else 4)
                    for i, tc_row in t_c_df.iterrows():
                        with cols[i % 4]:
                            st.markdown(f"""
                                <div style='background:#ffffff; padding:10px; border-radius:8px; border:1px solid #cbd5e1; text-align:center;'>
                                    <span class='badge-sell'>BOUGHT</span>
                                    <h4 style='margin:8px 0 2px 0;'>Code: {tc_row['thread_code']}</h4>
                                    <p style='margin:0; color:#64748b;'>Qty: <b>{tc_row['qty']}</b></p>
                                </div>
                            """, unsafe_with_html=True)
                else:
                    st.caption("No purchase history recorded yet.")
        else:
            st.info("No customers found matching the search criteria.")

# ══════════════════════════════════════════════════════════════
# ৪. কুইক ট্রানজেকশন বা ডাটা এন্ট্রি পেজ
# ══════════════════════════════════════════════════════════════
elif menu == "🔄 Quick Transaction":
    st.markdown("<h1>🔄 Record Stock Movement</h1>", unsafe_with_html=True)
    
    t_list = qry("SELECT thread_code FROM threads", fetch=True)
    s_list = qry("SELECT name FROM sellers", fetch=True)
    c_list = qry("SELECT name FROM customers", fetch=True)
    
    if not t_list.empty:
        st.markdown("<div class='premium-card'>", unsafe_with_html=True)
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
        st.markdown("</div>", unsafe_with_html=True)
    else:
        st.warning("Please populate the Thread Catalog before making entries.")