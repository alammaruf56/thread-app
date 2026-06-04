import streamlit as st
import mysql.connector
import pandas as pd
import datetime

# ১. পেজ কনফিগারেশন
st.set_page_config(
    page_title="ThreadTrack Pro — Business Suite", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# ২. আল্ট্রা-প্রফেশনাল লাক্সারি থিম সিএসএস (লেবেল কালার ফিক্সড)
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@0,400;0,600;1,400&display=swap');
        
        /* ব্যাকগ্রাউন্ড এবং গ্লোবাল ফন্ট */
        html, body, [class*="css"], .stApp {
            background-color: #FDFBF7 !important;
            color: #111111 !important;
            font-family: 'Outfit', sans-serif !important;
        }
        
        /* ফুটার হাইড */
        footer { visibility: hidden !important; }
        
        /* 🚨 ইনপুট ফিল্ডের ওপরের টাইটেল/লেবেল ফিক্স (যাতে পরিষ্কার দেখা যায়) */
        label, div[data-testid="stWidgetLabel"] p {
            color: #111111 !important;
            font-size: 0.9rem !important;
            font-weight: 500 !important;
            margin-bottom: 5px !important;
        }
        
        /* ইনপুট বক্সের ভেতরের টেক্সট এবং বর্ডার */
        .stTextInput>div>div>input, .stSelectbox>div>div>div, .stNumberInput>div>div>input {
            background-color: #ffffff !important;
            color: #111111 !important;
            border: 1px solid #EAE4DA !important;
            border-radius: 4px !important;
        }
        
        /* সাইডবার ডিজাইন - ডার্ক লাক্সারি */
        section[data-testid="stSidebar"] {
            background-color: #111111 !important;
            border-right: 1px solid #222222 !important;
        }
        section[data-testid="stSidebar"] * {
            color: #FDFBF7 !important;
        }
        /* সাইডবারের ভেতরের লেবেল গোল্ডেন রাখা */
        section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] div[data-testid="stWidgetLabel"] p {
            color: #C5A059 !important;
            font-size: 0.8rem !important;
            text-transform: uppercase !important;
            letter-spacing: 1.5px !important;
        }
        
        /* প্রফেশনাল টাইপোগ্রাফি */
        h1, h2, h3 {
            font-family: 'Playfair Display', serif !important;
            color: #111111 !important;
            font-weight: 600 !important;
        }
        
        /* ব্র্যান্ড স্টোর মেট্রিক কার্ডস */
        div[data-testid="stMetricContainer"] {
            background-color: #ffffff !important;
            border: 1px solid #EAE4DA !important;
            border-radius: 4px !important;
            padding: 24px !important;
            box-shadow: 0 5px 25px rgba(17,17,17,0.02) !important;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 0.75rem !important;
            text-transform: uppercase !important;
            letter-spacing: 2px !important;
            color: #777777 !important;
        }
        div[data-testid="stMetricValue"] {
            font-family: 'Playfair Display', serif !important;
            font-size: 2.4rem !important;
            color: #111111 !important;
        }
        
        /* ফর্ম এবং ইনপুট ফিল্ড কন্টেইনার */
        .stForm {
            background-color: #ffffff !important;
            border: 1px solid #EAE4DA !important;
            border-radius: 4px !important;
            padding: 35px !important;
            box-shadow: 0 10px 30px rgba(17,17,17,0.01) !important;
        }
        
        /* লাক্সারি সিগনেচার বাটন */
        button[kind="primary"], .stButton>button {
            background-color: #111111 !important;
            color: #FDFBF7 !important;
            border-radius: 4px !important;
            font-family: 'Outfit', sans-serif !important;
            font-weight: 500 !important;
            text-transform: uppercase !important;
            letter-spacing: 2px !important;
            font-size: 0.8rem !important;
            border: 1px solid #111111 !important;
            padding: 0.7rem 2.5rem !important;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
            width: 100% !important;
        }
        button[kind="primary"]:hover, .stButton>button:hover {
            background-color: #C5A059 !important;
            border-color: #C5A059 !important;
            color: #ffffff !important;
        }
        
        /* প্রিমিয়াম ডাটা টেবিল গ্রিড */
        .stDataFrame, div[data-testid="stTable"] {
            border: 1px solid #EAE4DA !important;
            background-color: #ffffff !important;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# প্রফেশনাল ডেমো ডাটা (সেফটি ব্যাকআপ)
# ==========================================
if "sources" not in st.session_state:
    st.session_state.sources = [
        {"source_id": 1, "source_name": "Giza Silk & Thread Mills", "phone": "+8801711002233", "speciality": "Premium Long-Staple Egyptian", "address": "Narayanganj Industrial Zone, Dhaka"},
        {"source_id": 2, "source_name": "Kyoto Filament Corp", "phone": "+810334556677", "speciality": "High-Tenacity Filament", "address": "Kyoto, Japan"}
    ]
if "products" not in st.session_state:
    st.session_state.products = [
        {"product_id": 1, "product_name": "Imperial Giza Cotton Thread #40", "sku_code": "SKU-GIZA-WT01", "category": "Cotton", "source_id": 1, "buy_price": 140.0, "sell_retail": 240.0, "sell_wholesale": 195.0, "current_stock": 620, "low_stock_threshold": 50},
        {"product_id": 2, "product_name": "Mulberry Luxe Filament-Z", "sku_code": "SKU-SILK-GL02", "category": "Silk", "source_id": 2, "buy_price": 480.0, "sell_retail": 890.0, "sell_wholesale": 750.0, "current_stock": 180, "low_stock_threshold": 20},
        {"product_id": 3, "product_name": "Core-Spun Poly Strength-X", "sku_code": "SKU-POLY-BK09", "category": "Polyester", "source_id": 1, "buy_price": 50.0, "sell_retail": 110.0, "sell_wholesale": 85.0, "current_stock": 12, "low_stock_threshold": 30}
    ]
if "customers" not in st.session_state:
    st.session_state.customers = [
        {"customer_id": 1, "customer_name": "Apex Apparel Corporate", "phone": "+8801822334455", "contact_notes": "Tier-1 wholesale corporate account."},
        {"customer_id": 2, "customer_name": "Envoy Premium Outlets", "phone": "+8801911778899", "contact_notes": "Standard retail contract buyer."}
    ]
if "transactions" not in st.session_state:
    st.session_state.transactions = [
        {"transaction_id": 1, "product_id": 1, "transaction_type": "OUTPUT_SALE", "sale_vector": "WHOLESALE", "quantity": 100, "discount": 500.0, "total_price": 19000.0, "customer_id": 1, "transaction_date": "2026-06-04"}
    ]

# ==========================================
# ডাটাবেজ ব্যাকএন্ড রাউটার
# ==========================================
@st.cache_resource(ttl=20)
def get_db_link():
    try:
        if "mysql" not in st.secrets:
            return False, None
        conn = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            port=int(st.secrets["mysql"]["port"]),
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database="thread_business",
            autocommit=True,
            connection_timeout=2
        )
        return True, conn
    except:
        return False, None

db_status, db_conn = get_db_link()

def run_brand_query(query, params=None, is_select=False):
    if not db_status or db_conn is None:
        return pd.DataFrame()
    try:
        db_conn.ping(reconnect=True, attempts=1)
        cursor = db_conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        if is_select:
            res = cursor.fetchall()
            cursor.close()
            return pd.DataFrame(res)
        cursor.close()
        return pd.DataFrame()
    except:
        return pd.DataFrame()

# ==========================================
# সাইডবার নেভিগেশন
# ==========================================
st.sidebar.markdown(
    "<h2 style='color:#FDFBF7; font-family:\"Playfair Display\"; letter-spacing:1px; margin-bottom:5px;'>THREADTRACK</h2>"
    "<p style='color:#C5A059; font-size:0.65rem; text-transform:uppercase; letter-spacing:3px; margin-top:0; margin-bottom:40px;'>Luxury Enterprise Suite</p>", 
    unsafe_allow_html=True
)

menu = ["Brand Dashboard", "Product Catalog Matrix", "Supplier Database", "Client Ledger Profiles", "Inventory Ledger Logs"]
choice = st.sidebar.selectbox("Navigate System", menu)

# ==========================================
# মডিউল ১: ব্র্যান্ড ড্যাশবোর্ড মেট্রিক্স
# ==========================================
if choice == "Brand Dashboard":
    st.markdown("<p style='text-transform:uppercase; letter-spacing:3px; color:#C5A059; margin-bottom:0; font-size:0.8rem;'>System Overview</p>", unsafe_allow_html=True)
    st.markdown("<h1 style='margin-top:0; font-size:2.5rem;'>Real-Time Business Matrix</h1>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    if db_status:
        p_res = run_brand_query("SELECT COUNT(*) as total FROM products", is_select=True)
        s_res = run_brand_query("SELECT COUNT(*) as total FROM sources", is_select=True)
        a_res = run_brand_query("SELECT COUNT(*) as total FROM products WHERE current_stock <= low_stock_threshold", is_select=True)
        r_res = run_brand_query("SELECT SUM(total_price) as total FROM transactions WHERE transaction_type='OUTPUT_SALE'", is_select=True)
        
        metrics_p = int(p_res['total'].iloc[0]) if not p_res.empty else 0
        metrics_s = int(s_res['total'].iloc[0]) if not s_res.empty else 0
        metrics_a = int(a_res['total'].iloc[0]) if not a_res.empty else 0
        metrics_r = float(r_res['total'].iloc[0]) if (not r_res.empty and r_res['total'].iloc[0] is not None) else 0.0
    else:
        metrics_p = len(st.session_state.products)
        metrics_s = len(st.session_state.sources)
        metrics_a = sum(1 for x in st.session_state.products if x['current_stock'] <= x['low_stock_threshold'])
        metrics_r = sum(float(x['total_price']) for x in st.session_state.transactions if x['transaction_type'] == 'OUTPUT_SALE')

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Active Catalog SKUs", metrics_p)
    c2.metric("Verified Vendors", metrics_s)
    c3.metric("Stock Alerts", metrics_a)
    c4.metric("Gross Sales Revenue", f"৳{metrics_r:,.2f}")
    
    st.markdown("<br><hr style='border:0; border-top: 1px solid #EAE4DA;'><br>", unsafe_allow_html=True)
    st.subheader("Global Stock Locator")
    search = st.text_input("🔍 Live filter across luxury collections, materials, or SKU reference numbers:")
    
    if db_status:
        sql = "SELECT p.product_name, p.sku_code, p.category, p.current_stock, p.sell_retail, p.sell_wholesale FROM products p"
        if search:
            sql += " WHERE p.product_name LIKE %s OR p.sku_code LIKE %s OR p.category LIKE %s"
            t = f"%{search}%"
            df = run_brand_query(sql, (t, t, t), is_select=True)
        else:
            df = run_brand_query(sql, is_select=True)
    else:
        df = pd.DataFrame(st.session_state.products)[["product_name", "sku_code", "category", "current_stock", "sell_retail", "sell_wholesale"]]
        if search:
            df = df[df['product_name'].str.contains(search, case=False) | 
                    df['sku_code'].str.contains(search, case=False) | 
                    df['category'].str.contains(search, case=False)]
            
    st.dataframe(df, use_container_width=True)

# ==========================================
# মডিউল ২: প্রোডাক্ট ক্যাটালগ
# ==========================================
elif choice == "Product Catalog Matrix":
    st.markdown("<h1 style='margin-top:0;'>Inventory Stock Configuration</h1>", unsafe_allow_html=True)
    
    if db_status:
        v_df = run_brand_query("SELECT source_id, source_name FROM sources", is_select=True)
        v_list = list(v_df['source_name']) if not v_df.empty else []
        v_dict = {row['source_name']: row['source_id'] for _, row in v_df.iterrows()} if not v_df.empty else {}
    else:
        v_list = [x['source_name'] for x in st.session_state.sources]
        v_dict = {x['source_name']: x['source_id'] for x in st.session_state.sources}
        
    with st.form("prod_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        p_name = col1.text_input("Product Collection Line Title")
        p_sku = col2.text_input("Unique SKU Vault Reference Code")
        p_cat = col1.selectbox("Material Framework Group", ["Cotton", "Silk", "Polyester", "Wool", "Nylon", "Mixed", "Other"])
        p_vendor = col2.selectbox("Assigned Registered Supplier", v_list if v_list else ["Generic Factory Base"])
        
        col3, col4, col5 = st.columns(3)
        b_cost = col3.number_input("Direct Acquisition Cost (৳)", min_value=0.0)
        s_retail = col4.number_input("Retail Showroom Price (৳)", min_value=0.0)
        s_wholesale = col5.number_input("Wholesale Client Price (৳)", min_value=0.0)
        init_stk = st.number_input("Initial Opening Stock Level", min_value=0)
        
        if st.form_submit_button("Commit Product Registry Asset") and p_name:
            sid = v_dict.get(p_vendor, 1)
            if db_status:
                run_brand_query("INSERT INTO products (product_name, sku_code, category, source_id, buy_price, sell_retail, sell_wholesale, current_stock) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                              (p_name, p_sku, p_cat, sid, b_cost, s_retail, s_wholesale, init_stk))
            else:
                st.session_state.products.append({
                    "product_id": len(st.session_state.products)+1, "product_name": p_name, "sku_code": p_sku, "category": p_cat,
                    "source_id": sid, "buy_price": b_cost, "sell_retail": s_retail, "sell_wholesale": s_wholesale, "current_stock": init_stk, "low_stock_threshold": 20
                })
            st.success("New asset matrix line successfully saved.")
            st.rerun()

    st.subheader("Active Asset Portfolio Registry")
    if db_status:
        l_df = run_brand_query("SELECT sku_code, product_name, category, buy_price, sell_retail, current_stock FROM products", is_select=True)
    else:
        l_df = pd.DataFrame(st.session_state.products)[["sku_code", "product_name", "category", "buy_price", "sell_retail", "current_stock"]]
    st.dataframe(l_df, use_container_width=True)

# ==========================================
# মডিউল ৩: সাপ্লায়ার ডেটাবেজ
# ==========================================
elif choice == "Supplier Database":
    st.markdown("<h1 style='margin-top:0;'>Corporate Supplier Matrix</h1>", unsafe_allow_html=True)
    with st.form("sup_form", clear_on_submit=True):
        v_name = st.text_input("Vendor Corporate Group Identifier")
        v_phone = st.text_input("Direct Communications Secure Line")
        v_spec = st.text_input("Speciality Material Focus Index")
        v_addr = st.text_area("Global Headquarter Logistics Address")
        
        if st.form_submit_button("Archive Vendor Account Node") and v_name:
            if db_status:
                run_brand_query("INSERT INTO sources (source_name, phone, address, speciality) VALUES (%s, %s, %s, %s)", (v_name, v_phone, v_addr, v_spec))
            else:
                st.session_state.sources.append({"source_id": len(st.session_state.sources)+1, "source_name": v_name, "phone": v_phone, "speciality": v_spec, "address": v_addr})
            st.success("Supplier corporate profile locked down.")
            st.rerun()
            
    st.subheader("Monitored Production Network Vendors")
    if db_status:
        s_df = run_brand_query("SELECT source_name, phone, speciality, address FROM sources", is_select=True)
    else:
        s_df = pd.DataFrame(st.session_state.sources)[["source_name", "phone", "speciality", "address"]]
    st.dataframe(s_df, use_container_width=True)

# ==========================================
# মডিউল ৪: ক্লায়েন্ট লেজার
# ==========================================
elif choice == "Client Ledger Profiles":
    st.markdown("<h1 style='margin-top:0;'>Client Account Ledgers</h1>", unsafe_allow_html=True)
    with st.form("c_form", clear_on_submit=True):
        c_name = st.text_input("Client Corporate Business Identity")
        c_phone = st.text_input("Finance/Procurement Office Contact")
        c_notes = st.text_area("Custom Shipping & Fulfillment Requirements")
        
        if st.form_submit_button("Map Client Contract Matrix") and c_name:
            if db_status:
                run_brand_query("INSERT INTO customers (customer_name, phone, contact_notes) VALUES (%s, %s, %s)", (c_name, c_phone, c_notes))
            else:
                st.session_state.customers.append({"customer_id": len(st.session_state.customers)+1, "customer_name": c_name, "phone": c_phone, "contact_notes": c_notes})
            st.success("Client data asset securely archived.")
            st.rerun()
            
    st.subheader("Authorized Commercial Purchasing Clients")
    if db_status:
        c_df = run_brand_query("SELECT customer_name, phone, contact_notes FROM customers", is_select=True)
    else:
        c_df = pd.DataFrame(st.session_state.customers)[["customer_name", "phone", "contact_notes"]]
    st.dataframe(c_df, use_container_width=True)

# ==========================================
# মডিউল ৫: ইনভেন্টরি লগস
# ==========================================
elif choice == "Inventory Ledger Logs":
    st.markdown("<h1 style='margin-top:0;'>Execute Value Asset Movements</h1>", unsafe_allow_html=True)
    
    if db_status:
        p_list = run_brand_query("SELECT product_id, product_name, current_stock, sell_retail, sell_wholesale FROM products", is_select=True)
        c_list = run_brand_query("SELECT customer_id, customer_name FROM customers", is_select=True)
        p_names = list(p_list['product_name']) if not p_list.empty else []
        p_map = {r['product_name']: r for _, r in p_list.iterrows()} if not p_list.empty else {}
    else:
        p_names = [x['product_name'] for x in st.session_state.products]
        p_map = {x['product_name']: x for x in st.session_state.products}
        c_list = pd.DataFrame(st.session_state.customers)
        
    if p_names:
        cli_dict = {"[Internal Vault Direct Restock Stocking]": None}
        if not c_list.empty:
            for _, r in c_list.iterrows(): cli_dict[r['customer_name']] = r['customer_id']
                
        with st.form("tx_form", clear_on_submit=True):
            target_p = st.selectbox("Target Catalog Product Variant Line", p_names)
            flow = st.selectbox("Asset Allocation Flow Direction", ["OUTPUT_SALE", "INPUT_RESTOCK"])
            tier = st.selectbox("Pricing Mode Tier (Sales Only)", ["RETAIL", "WHOLESALE"])
            qty = st.number_input("Operational Transaction Volume Metric", min_value=1, step=1)
            disc = st.number_input("Authorized Transaction Discount (৳)", min_value=0.0)
            target_c = st.selectbox("Linked Corporate Client Account Entity", list(cli_dict.keys()))
            
            if st.form_submit_button("Authorize & Process Stock Allocation"):
                match = p_map[target_p]
                pid = match['product_id']
                current_stk = match['current_stock']
                
                if flow == "OUTPUT_SALE" and qty > current_stk:
                    st.error("Transaction Aborted: Request quantity exceeds physical vault asset limit.")
                else:
                    rate = float(match['sell_retail'] if tier == "RETAIL" else match['sell_wholesale'])
                    final_p = (rate * qty) - float(disc)
                    if final_p < 0: final_p = 0.0
                    
                    new_stk = current_stk - qty if flow == "OUTPUT_SALE" else current_stk + qty
                    cid = cli_dict[target_c]
                    
                    if db_status:
                        run_brand_query("INSERT INTO transactions (product_id, transaction_type, sale_vector, quantity, discount, total_price, customer_id) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                                      (pid, flow, tier, qty, disc, final_p, cid))
                        run_brand_query("UPDATE products SET current_stock = %s WHERE product_id = %s", (new_stk, pid))
                    else:
                        for x in st.session_state.products:
                            if x['product_id'] == pid: x['current_stock'] = new_stk
                        st.session_state.transactions.append({
                            "transaction_id": len(st.session_state.transactions)+1, "product_id": pid, "transaction_type": flow,
                            "sale_vector": tier, "quantity": qty, "discount": disc, "total_price": final_p, "customer_id": cid, "transaction_date": str(datetime.date.today())
                        })
                    st.success(f"Transaction successfully posted. Total Registered Premium Yield: ৳{final_p:,.2f}")
                    st.rerun()