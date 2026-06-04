import streamlit as st
import mysql.connector
import pandas as pd
import datetime

# Industrial Luxury Page Framework Configuration
st.set_page_config(page_title="ThreadTrack Pro", layout="wide", initial_sidebar_state="expanded")

# High-End Brand Store Design Matrix (Ivory, Charcoal, Brushed Gold)
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=Outfit:wght@300;400;500;600&display=swap');
        
        /* Base Premium Canvas */
        html, body, [class*="css"], .stApp {
            background-color: #fbf9f6 !important;
            color: #1a1510 !important;
            font-family: 'Outfit', sans-serif !important;
        }
        
        /* Structural Cleanup */
        header, footer { visibility: hidden !important; }
        
        /* Sidebar Styling - Clean Luxury Menu */
        section[data-testid="stSidebar"] {
            background-color: #1a1510 !important;
            color: #fbf9f6 !important;
            border-right: 1px solid #332a21 !important;
        }
        section[data-testid="stSidebar"] * {
            color: #fbf9f6 !important;
        }
        section[data-testid="stSidebar"] .stSelectbox label {
            color: #b8a898 !important;
            font-size: 0.85rem !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
        }
        
        /* Luxury Typography */
        h1, h2, h3 {
            font-family: 'Playfair Display', serif !important;
            color: #1a1510 !important;
            font-weight: 600 !important;
            letter-spacing: -0.5px !important;
        }
        
        /* Brand Metric Cards */
        div[data-testid="stMetricContainer"] {
            background-color: #ffffff !important;
            border: 1px solid #e6dfd5 !important;
            border-radius: 4px !important;
            padding: 24px !important;
            box-shadow: 0 4px 20px rgba(26,21,16,0.02) !important;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 0.8rem !important;
            text-transform: uppercase !important;
            letter-spacing: 1.5px !important;
            color: #8a7a68 !important;
        }
        div[data-testid="stMetricValue"] {
            font-family: 'Playfair Display', serif !important;
            font-size: 2.2rem !important;
            color: #1a1510 !important;
        }
        
        /* Clean Input Forms */
        .stForm {
            background-color: #ffffff !important;
            border: 1px solid #e6dfd5 !important;
            border-radius: 4px !important;
            padding: 30px !important;
        }
        
        /* Luxury Brand Buttons */
        button[kind="primary"], .stButton>button {
            background-color: #1a1510 !important;
            color: #fbf9f6 !important;
            border-radius: 0px !important;
            font-family: 'Outfit', sans-serif !important;
            font-weight: 500 !important;
            text-transform: uppercase !important;
            letter-spacing: 1.5px !important;
            font-size: 0.8rem !important;
            border: 1px solid #1a1510 !important;
            padding: 0.6rem 2.5rem !important;
            transition: all 0.3s ease !important;
            width: 100% !important;
        }
        button[kind="primary"]:hover, .stButton>button:hover {
            background-color: #c4882a !important;
            border-color: #c4882a !important;
            color: #ffffff !important;
        }
        
        /* Pristine Data Tables */
        .stDataFrame, div[data-testid="stTable"] {
            border: 1px solid #e6dfd5 !important;
            background-color: #ffffff !important;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# ENTERPRISE RECONCILED DATA MATRIX (MOCK BASE)
# ==========================================
if "sources" not in st.session_state:
    st.session_state.sources = [
        {"source_id": 1, "source_name": "Giza Luxury Cottons Ltd", "phone": "+8801711002233", "speciality": "Premium Long-Staple Egyptian", "address": "Gulshan Industrial Zone, Dhaka"},
        {"source_id": 2, "source_name": "Kyoto Mulberry Silk Co.", "phone": "+810334556677", "speciality": "Fine Mulberry Filaments", "address": "Kyoto Export District, Japan"}
    ]
if "products" not in st.session_state:
    st.session_state.products = [
        {"product_id": 1, "product_name": "Royal Giza Cotton Thread #40", "sku_code": "SKU-GIZA-WT01", "category": "Cotton", "source_id": 1, "buy_price": 120.0, "sell_retail": 220.0, "sell_wholesale": 180.0, "current_stock": 450, "low_stock_threshold": 50},
        {"product_id": 2, "product_name": "Imperial Mulberry Silk Weave", "sku_code": "SKU-SILK-GL02", "category": "Silk", "source_id": 2, "buy_price": 450.0, "sell_retail": 850.0, "sell_wholesale": 710.0, "current_stock": 120, "low_stock_threshold": 20},
        {"product_id": 3, "product_name": "High-Tenacity Poly Glaze", "sku_code": "SKU-POLY-BK09", "category": "Polyester", "source_id": 1, "buy_price": 45.0, "sell_retail": 95.0, "sell_wholesale": 75.0, "current_stock": 14, "low_stock_threshold": 30}
    ]
if "customers" not in st.session_state:
    st.session_state.customers = [
        {"customer_id": 1, "customer_name": "Apex Apparel Corporate", "phone": "+8801822334455", "contact_notes": "Premium tier wholesale distributor."},
        {"customer_id": 2, "customer_name": "Envoy Textiles Holding", "phone": "+8801911778899", "contact_notes": "Sourcing partner for high-end catalog runs."}
    ]
if "transactions" not in st.session_state:
    st.session_state.transactions = [
        {"transaction_id": 1, "product_id": 1, "transaction_type": "OUTPUT_SALE", "sale_vector": "WHOLESALE", "quantity": 100, "discount": 500.0, "total_price": 17500.0, "customer_id": 1, "transaction_date": "2026-06-04"},
        {"transaction_id": 2, "product_id": 2, "transaction_type": "OUTPUT_SALE", "sale_vector": "RETAIL", "quantity": 10, "discount": 0.0, "total_price": 8500.0, "customer_id": 2, "transaction_date": "2026-06-05"}
    ]

# ==========================================
# SILENT CONNECTION ROUTER
# ==========================================
@st.cache_resource(ttl=30)
def check_db_pipeline():
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

db_live, db_conn = check_db_pipeline()

def execute_query(query, params=None, is_select=False):
    if not db_live or db_conn is None:
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
# SIDEBAR NAVIGATION
# ==========================================
st.sidebar.markdown("<h2 style='color:#ffffff; font-family:\"Playfair Display\"; margin-bottom:30px;'>THREADTRACK PRO</h2>", unsafe_allow_html=True)
menu = ["Brand Dashboard", "Product Catalog Matrix", "Supplier Database", "Client Ledger Profiles", "Inventory Ledger Logs"]
choice = st.sidebar.selectbox("Navigate System", menu)

# ==========================================
# MODULE 1: BRAND DASHBOARD METRICS
# ==========================================
if choice == "Brand Dashboard":
    st.markdown("<p style='text-transform:uppercase; letter-spacing:2px; color:#8a7a68; margin-bottom:0;'>System Overview</p>", unsafe_allow_html=True)
    st.markdown("<h1 style='margin-top:0;'>Corporate Analytics Interface</h1>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    if db_live:
        p_data = execute_query("SELECT COUNT(*) as total FROM products", is_select=True)
        s_data = execute_query("SELECT COUNT(*) as total FROM sources", is_select=True)
        a_data = execute_query("SELECT COUNT(*) as total FROM products WHERE current_stock <= low_stock_threshold", is_select=True)
        r_data = execute_query("SELECT SUM(total_price) as total FROM transactions WHERE transaction_type='OUTPUT_SALE'", is_select=True)
        
        tot_p = int(p_data['total'].iloc[0]) if not p_data.empty else 0
        tot_s = int(s_data['total'].iloc[0]) if not s_data.empty else 0
        tot_a = int(a_data['total'].iloc[0]) if not a_data.empty else 0
        tot_r = float(r_data['total'].iloc[0]) if (not r_data.empty and r_data['total'].iloc[0] is not None) else 0.0
    else:
        tot_p = len(st.session_state.products)
        tot_s = len(st.session_state.sources)
        tot_a = sum(1 for x in st.session_state.products if x['current_stock'] <= x['low_stock_threshold'])
        tot_r = sum(float(x['total_price']) for x in st.session_state.transactions if x['transaction_type'] == 'OUTPUT_SALE')

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Active SKUs", tot_p)
    c2.metric("Verified Vendors", tot_s)
    c3.metric("Critical Low Stock", tot_a)
    c4.metric("Gross Sales Realized", f"৳{tot_r:,.2f}")
    
    st.markdown("<br><hr style='border:0; border-top: 1px solid #e6dfd5;'><br>", unsafe_allow_html=True)
    st.subheader("Global Inventory Search Locator")
    search_query = st.text_input("🔍 Search lines across product classifications, identifiers, or unique SKU tags:")
    
    if db_live:
        sql = "SELECT p.product_name, p.sku_code, p.category, p.current_stock, p.sell_retail, p.sell_wholesale FROM products p"
        if search_query:
            sql += " WHERE p.product_name LIKE %s OR p.sku_code LIKE %s OR p.category LIKE %s"
            term = f"%{search_query}%"
            df = execute_query(sql, (term, term, term), is_select=True)
        else:
            df = execute_query(sql, is_select=True)
    else:
        df = pd.DataFrame(st.session_state.products)[["product_name", "sku_code", "category", "current_stock", "sell_retail", "sell_wholesale"]]
        if search_query:
            df = df[df['product_name'].str.contains(search_query, case=False) | 
                    df['sku_code'].str.contains(search_query, case=False) | 
                    df['category'].str.contains(search_query, case=False)]
            
    st.dataframe(df, use_container_width=True)

# ==========================================
# MODULE 2: PRODUCT SKU CATALOG MATRIX
# ==========================================
elif choice == "Product Catalog Matrix":
    st.markdown("<h1 style='margin-top:0;'>Product SKU Management</h1>", unsafe_allow_html=True)
    
    if db_live:
        v_df = execute_query("SELECT source_id, source_name FROM sources", is_select=True)
        v_list = list(v_df['source_name']) if not v_df.empty else []
        v_dict = {row['source_name']: row['source_id'] for _, row in v_df.iterrows()} if not v_df.empty else {}
    else:
        v_list = [x['source_name'] for x in st.session_state.sources]
        v_dict = {x['source_name']: x['source_id'] for x in st.session_state.sources}
        
    with st.form("product_entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        p_name = col1.text_input("Product Premium Line Label")
        p_sku = col2.text_input("Unique Inventory SKU Designation Code")
        p_cat = col1.selectbox("Material Category Matrix", ["Cotton", "Silk", "Polyester", "Wool", "Nylon", "Mixed", "Other"])
        p_vendor = col2.selectbox("Assigned Corporate Vendor", v_list if v_list else ["Default Generic"])
        
        col3, col4, col5 = st.columns(3)
        b_cost = col3.number_input("Acquisition Direct Cost (৳)", min_value=0.0)
        s_retail = col4.number_input("Retail Listing Price (৳)", min_value=0.0)
        s_wholesale = col5.number_input("Wholesale Unit Price (৳)", min_value=0.0)
        init_stk = st.number_input("Opening Vault Stock Volume", min_value=0)
        
        if st.form_submit_button("Register Product Asset Line") and p_name:
            assigned_sid = v_dict.get(p_vendor, 1)
            if db_live:
                execute_query("INSERT INTO products (product_name, sku_code, category, source_id, buy_price, sell_retail, sell_wholesale, current_stock) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                              (p_name, p_sku, p_cat, assigned_sid, b_cost, s_retail, s_wholesale, init_stk))
            else:
                st.session_state.products.append({
                    "product_id": len(st.session_state.products)+1, "product_name": p_name, "sku_code": p_sku, "category": p_cat,
                    "source_id": assigned_sid, "buy_price": b_cost, "sell_retail": s_retail, "sell_wholesale": s_wholesale, "current_stock": init_stk, "low_stock_threshold": 25
                })
            st.success("Asset configuration mapped successfully.")
            st.rerun()

    st.subheader("Current Active SKU Ledger")
    if db_live:
        ledger_df = execute_query("SELECT sku_code, product_name, category, buy_price, sell_retail, current_stock FROM products", is_select=True)
    else:
        ledger_df = pd.DataFrame(st.session_state.products)[["sku_code", "product_name", "category", "buy_price", "sell_retail", "current_stock"]]
    st.dataframe(ledger_df, use_container_width=True)

# ==========================================
# MODULE 3: SUPPLIER DATABASE
# ==========================================
elif choice == "Supplier Database":
    st.markdown("<h1 style='margin-top:0;'>Corporate Supplier Ledger</h1>", unsafe_allow_html=True)
    with st.form("vendor_form", clear_on_submit=True):
        v_name = st.text_input("Vendor Corporate Group Name")
        v_phone = st.text_input("Secure Secure Phone Communications Link")
        v_spec = st.text_input("Production Specialization Index")
        v_addr = st.text_area("Global HQ Location Infrastructure")
        
        if st.form_submit_button("Archive Vendor Account") and v_name:
            if db_live:
                execute_query("INSERT INTO sources (source_name, phone, address, speciality) VALUES (%s, %s, %s, %s)", (v_name, v_phone, v_addr, v_spec))
            else:
                st.session_state.sources.append({"source_id": len(st.session_state.sources)+1, "source_name": v_name, "phone": v_phone, "speciality": v_spec, "address": v_addr})
            st.success("Vendor profile permanently committed.")
            st.rerun()
            
    st.subheader("Monitored Vendor Infrastructure Network")
    if db_live:
        s_df = execute_query("SELECT source_name, phone, speciality, address FROM sources", is_select=True)
    else:
        s_df = pd.DataFrame(st.session_state.sources)[["source_name", "phone", "speciality", "address"]]
    st.dataframe(s_df, use_container_width=True)

# ==========================================
# MODULE 4: CLIENT LEDGER PROFILES
# ==========================================
elif choice == "Client Ledger Profiles":
    st.markdown("<h1 style='margin-top:0;'>Client Corporate Accounts</h1>", unsafe_allow_html=True)
    with st.form("buyer_form", clear_on_submit=True):
        c_name = st.text_input("Client Corporate Purchasing Name")
        c_phone = st.text_input("Accounts Management Phone Line")
        c_notes = st.text_area("Custom Contract Fulfillment Logistics Notes")
        
        if st.form_submit_button("Map Client Registry Profile") and c_name:
            if db_live:
                execute_query("INSERT INTO customers (customer_name, phone, contact_notes) VALUES (%s, %s, %s)", (c_name, c_phone, c_notes))
            else:
                st.session_state.customers.append({"customer_id": len(st.session_state.customers)+1, "customer_name": c_name, "phone": c_phone, "contact_notes": c_notes})
            st.success("Client operational matrix updated.")
            st.rerun()
            
    st.subheader("Authorized Buyer Portfolios")
    if db_live:
        c_df = execute_query("SELECT customer_name, phone, contact_notes FROM customers", is_select=True)
    else:
        c_df = pd.DataFrame(st.session_state.customers)[["customer_name", "phone", "contact_notes"]]
    st.dataframe(c_df, use_container_width=True)

# ==========================================
# MODULE 5: INVENTORY LEDGER TRANSACTION LOGS
# ==========================================
elif choice == "Inventory Ledger Logs":
    st.markdown("<h1 style='margin-top:0;'>Execute Value Asset Movements</h1>", unsafe_allow_html=True)
    
    if db_live:
        p_list_df = execute_query("SELECT product_id, product_name, current_stock, sell_retail, sell_wholesale FROM products", is_select=True)
        c_list_df = execute_query("SELECT customer_id, customer_name FROM customers", is_select=True)
        p_names = list(p_list_df['product_name']) if not p_list_df.empty else []
        p_map = {r['product_name']: r for _, r in p_list_df.iterrows()} if not p_list_df.empty else {}
    else:
        p_names = [x['product_name'] for x in st.session_state.products]
        p_map = {x['product_name']: x for x in st.session_state.products}
        c_list_df = pd.DataFrame(st.session_state.customers)
        
    if p_names:
        cli_dictionary = {"[No External Customer - Vault Inventory Inbound Adjustment]": None}
        if not c_list_df.empty:
            for _, r in c_list_df.iterrows():
                cli_dictionary[r['customer_name']] = r['customer_id']
                
        with st.form("transaction_matrix_form", clear_on_submit=True):
            target_p = st.selectbox("Select Target Product Variant SKU Line", p_names)
            flow_dir = st.selectbox("Asset Allocation Flow Vector", ["OUTPUT_SALE", "INPUT_RESTOCK"])
            pricing_tier = st.selectbox("Corporate Pricing Contract Tier (Sales Only)", ["RETAIL", "WHOLESALE"])
            volume = st.number_input("Transactional Stock Volume Metric", min_value=1, step=1)
            discount_val = st.number_input("Authorized Contractual Discount Value (৳)", min_value=0.0)
            target_c = st.selectbox("Linked Corporate Client Account", list(cli_dictionary.keys()))
            
            if st.form_submit_button("Authorize and Process Asset Transfer"):
                match = p_map[target_p]
                pid = match['product_id']
                current_v = match['current_stock']
                
                if flow_dir == "OUTPUT_SALE" and volume > current_v:
                    st.error("Transaction Aborted: Request allocation quantity exceeds maximum physical asset capacity inside vaults.")
                else:
                    unit_cost = float(match['sell_retail'] if pricing_tier == "RETAIL" else match['sell_wholesale'])
                    finalized_price = (unit_cost * volume) - float(discount_val)
                    if finalized_price < 0: finalized_price = 0.0
                    
                    new_computed_stock = current_v - volume if flow_dir == "OUTPUT_SALE" else current_v + volume
                    linked_cid = cli_dictionary[target_c]
                    
                    if db_live:
                        execute_query("INSERT INTO transactions (product_id, transaction_type, sale_vector, quantity, discount, total_price, customer_id) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                                      (pid, flow_dir, pricing_tier, volume, discount_val, finalized_price, linked_cid))
                        execute_query("UPDATE products SET current_stock = %s WHERE product_id = %s", (new_computed_stock, pid))
                    else:
                        for item in st.session_state.products:
                            if item['product_id'] == pid:
                                item['current_stock'] = new_computed_stock
                        st.session_state.transactions.append({
                            "transaction_id": len(st.session_state.transactions)+1, "product_id": pid,
                            "transaction_type": flow_dir, "sale_vector": pricing_tier, "quantity": volume,
                            "discount": discount_val, "total_price": finalized_price, "customer_id": linked_cid,
                            "transaction_date": str(datetime.date.today())
                        })
                    st.success(f"Transaction recorded successfully. Realized Matrix Income Rate: ৳{finalized_price:,.2f}")
                    st.rerun()