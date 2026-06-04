import streamlit as st
import mysql.connector
import pandas as pd
import datetime

# Clean luxury page definition configuration
st.set_page_config(page_title="ThreadTrack Pro", layout="wide")

# Custom Embedded Styling Matrix recreating the high-end dashboard appearance
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Outfit:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');
        
        /* Apply Base Luxury Ivory Tone Framework */
        html, body, [class*="css"], .stApp {
            background-color: #f7f4ef !important;
            color: #1a1510 !important;
            font-family: 'Outfit', sans-serif !important;
        }
        
        /* Remove Default Structural Distractions */
        header, footer { visibility: hidden !important; }
        
        /* Typography Layout Customizations */
        h1, h2, h3 {
            font-family: 'Playfair Display', serif !important;
            color: #1a1510 !important;
            font-weight: 700 !important;
        }
        
        /* Component Cards Design System */
        div[data-testid="stMetricContainer"], .stForm {
            background-color: #ffffff !important;
            border: 1.5px solid #e0d8cc !important;
            border-radius: 12px !important;
            padding: 20px !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08) !important;
        }
        
        /* Custom Warm Accent Buttons */
        button[kind="primary"], .stButton>button {
            background-color: #c4882a !important;
            color: #ffffff !important;
            border-radius: 30px !important;
            font-family: 'Outfit', sans-serif !important;
            font-weight: 600 !important;
            border: none !important;
            padding: 0.5rem 1.5rem !important;
            transition: all .15s ease !important;
        }
        
        button[kind="primary"]:hover, .stButton>button:hover {
            background-color: #e8a83a !important;
            box-shadow: 0 4px 12px rgba(196,136,42,.3) !important;
            transform: translateY(-1px) !important;
        }
        
        /* Data Grid Table Polishing */
        .dataframe {
            border: 1px solid #e0d8cc !important;
            border-radius: 8px !important;
        }
    </style>
""", unsafe_allow_html=True)

st.title("ThreadTrack Pro Business Manager")

# ==========================================
# LOCAL MEMORY ENGINE FALLBACK BACKUP DATA
# ==========================================
if "sources" not in st.session_state:
    st.session_state.sources = [
        {"source_id": 1, "source_name": "Siam Yarn Mills", "phone": "+8801711112222", "speciality": "Organic Egyptian Cotton", "address": "Narayanganj, Dhaka"}
    ]
if "products" not in st.session_state:
    st.session_state.products = [
        {"product_id": 1, "product_name": "Premium Spun Poly Blue", "sku_code": "SKU-POLY-BL01", "category": "Polyester", "source_id": 1, "buy_price": 65.0, "sell_retail": 110.0, "sell_wholesale": 90.0, "current_stock": 140, "low_stock_threshold": 15}
    ]
if "customers" not in st.session_state:
    st.session_state.customers = [
        {"customer_id": 1, "customer_name": "Abanti Fashions Ltd", "phone": "+8801822223333", "contact_notes": "Requires wholesale delivery packages."}
    ]
if "transactions" not in st.session_state:
    st.session_state.transactions = [
        {"transaction_id": 1, "product_id": 1, "transaction_type": "OUTPUT_SALE", "sale_vector": "WHOLESALE", "quantity": 10, "discount": 0.0, "total_price": 900.0, "customer_id": 1, "transaction_date": "2026-06-04"}
    ]

# ==========================================
# SMART AUTO-DETECTION SYSTEM
# ==========================================
@st.cache_resource(ttl=60)
def check_database_link():
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
            connection_timeout=3  # 3-second strict timeout prevents hanging!
        )
        return True, conn
    except:
        return False, None

db_active, db_connection = check_database_link()

# Render status banner quietly in sidebar
if db_active:
    st.sidebar.success("⚡ Live Connection: TiDB Cloud Active")
else:
    st.sidebar.warning("💾 Offline Mode: Local Memory Engine Active")

# Helper function for live database routing
def run_db_query(query, params=None, is_select=False):
    if not db_active or db_connection is None:
        return pd.DataFrame()
    try:
        db_connection.ping(reconnect=True, attempts=2, delay=1)
        cursor = db_connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        if is_select:
            res = cursor.fetchall()
            cursor.close()
            return pd.DataFrame(res)
        cursor.close()
        return pd.DataFrame()
    except:
        return pd.DataFrame()

# Navigation Selection Array Matrix
menu = ["Dashboard Metrics", "Thread Products SKU Catalog", "Registered Supplier Base", "Client Ledger Profiles", "Process Log Ledger"]
choice = st.sidebar.selectbox("Navigation Sections", menu)

# ==========================================
# MODULE 1: SEARCH & METRICS DASHBOARD
# ==========================================
if choice == "Dashboard Metrics":
    st.subheader("Business Metrics Analytics")
    
    if db_active:
        p_count = run_db_query("SELECT COUNT(*) as total FROM products", is_select=True)
        s_count = run_db_query("SELECT COUNT(*) as total FROM sources", is_select=True)
        alerts = run_db_query("SELECT COUNT(*) as total FROM products WHERE current_stock <= low_stock_threshold", is_select=True)
        rev_calc = run_db_query("SELECT SUM(total_price) as total FROM transactions WHERE transaction_type='OUTPUT_SALE'", is_select=True)
        
        val_p = int(p_count['total'].iloc[0]) if not p_count.empty else 0
        val_s = int(s_count['total'].iloc[0]) if not s_count.empty else 0
        val_a = int(alerts['total'].iloc[0]) if not alerts.empty else 0
        val_r = float(rev_calc['total'].iloc[0]) if (not rev_calc.empty and rev_calc['total'].iloc[0] is not None) else 0.0
    else:
        val_p = len(st.session_state.products)
        val_s = len(st.session_state.sources)
        val_a = sum(1 for x in st.session_state.products if x['current_stock'] <= x['low_stock_threshold'])
        val_r = sum(float(x['total_price']) for x in st.session_state.transactions if x['transaction_type'] == 'OUTPUT_SALE')

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Products Cataloged", val_p)
    c2.metric("Active Suppliers", val_s)
    c3.metric("Low Stock Alerts", val_a)
    c4.metric("Gross Sales Revenue", f"৳{val_r:,.2f}")
    
    st.markdown("---")
    st.subheader("Global Inventory Search Engine")
    search_term = st.text_input("🔍 Filter parameters across names, codes or categories:")
    
    if db_active:
        sql = """
            SELECT p.product_name, p.sku_code, p.category, p.current_stock, p.sell_retail, p.sell_wholesale,
                   s.source_name as supplier_assigned
            FROM products p LEFT JOIN sources s ON p.source_id = s.source_id
        """
        if search_term:
            sql += " WHERE p.product_name LIKE %s OR p.sku_code LIKE %s OR p.category LIKE %s"
            t = f"%{search_term}%"
            df = run_db_query(sql, (t, t, t), is_select=True)
        else:
            df = run_db_query(sql, is_select=True)
    else:
        df_p = pd.DataFrame(st.session_state.products)
        df_s = pd.DataFrame(st.session_state.sources)
        if not df_p.empty and not df_s.empty:
            df = pd.merge(df_p, df_s, on="source_id", how="left").rename(columns={"source_name": "supplier_assigned"})
            df = df[["product_name", "sku_code", "category", "current_stock", "sell_retail", "sell_wholesale", "supplier_assigned"]]
            if search_term:
                df = df[df['product_name'].str.contains(search_term, case=False) | 
                        df['sku_code'].str.contains(search_term, case=False) | 
                        df['category'].str.contains(search_term, case=False)]
        else:
            df = pd.DataFrame()
            
    if df is not None and not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.write("No matching inventory records found.")

# ==========================================
# MODULE 2: THREAD SKU CATALOG MANAGER
# ==========================================
elif choice == "Thread Products SKU Catalog":
    st.subheader("Thread Variants SKU Management")
    
    if db_active:
        sups_df = run_db_query("SELECT source_id, source_name FROM sources", is_select=True)
        sup_list = list(sups_df['source_name']) if not sups_df.empty else []
        sup_dict = {row['source_name']: row['source_id'] for _, row in sups_df.iterrows()} if not sups_df.empty else {}
    else:
        sup_list = [x['source_name'] for x in st.session_state.sources]
        sup_dict = {x['source_name']: x['source_id'] for x in st.session_state.sources}
        
    if sup_list:
        with st.form("new_product_skuline", clear_on_submit=True):
            col1, col2 = st.columns(2)
            p_name = col1.text_input("Product Identifier Name")
            p_sku = col2.text_input("Unique SKU Code")
            p_cat = col1.selectbox("Material Category Group", ["Cotton", "Silk", "Polyester", "Wool", "Nylon", "Mixed", "Other"])
            p_sup = col2.selectbox("Allocated Supplier Partner", sup_list)
            
            col3, col4, col5 = st.columns(3)
            b_cost = col3.number_input("Purchase Buying Cost (৳)", min_value=0.0, step=1.0)
            s_retail = col4.number_input("Retail Selling Price (৳)", min_value=0.0, step=1.0)
            s_wholesale = col5.number_input("Wholesale Selling Price (৳)", min_value=0.0, step=1.0)
            init_stk = st.number_input("Initial Starting Stock Volume", min_value=0, step=1)
            
            if st.form_submit_button("Commit Product Configuration") and p_name:
                if db_active:
                    run_db_query("""INSERT INTO products (product_name, sku_code, category, source_id, buy_price, sell_retail, sell_wholesale, current_stock) 
                                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                              (p_name, p_sku, p_cat, sup_dict[p_sup], b_cost, s_retail, s_wholesale, init_stk))
                else:
                    new_id = len(st.session_state.products) + 1
                    st.session_state.products.append({
                        "product_id": new_id, "product_name": p_name, "sku_code": p_sku, "category": p_cat,
                        "source_id": sup_dict[p_sup], "buy_price": b_cost, "sell_retail": s_retail, "sell_wholesale": s_wholesale,
                        "current_stock": init_stk, "low_stock_threshold": 10
                    })
                st.success("New product variant line cataloged successfully.")
    else:
        st.warning("Please record at least one supplier vendor before adding inventory products.")

    st.subheader("Active Stock Registry")
    if db_active:
        all_p = run_db_query("SELECT sku_code, product_name, category, buy_price, sell_retail, current_stock FROM products", is_select=True)
    else:
        all_p = pd.DataFrame(st.session_state.products)[["sku_code", "product_name", "category", "buy_price", "sell_retail", "current_stock"]]
        
    if all_p is not None and not all_p.empty:
        st.dataframe(all_p, use_container_width=True)

# ==========================================
# MODULE 3: REGISTERED SUPPLIER BASE
# ==========================================
elif choice == "Registered Supplier Base":
    st.subheader("Manage Production Vendors")
    with st.form("new_vendor_entry", clear_on_submit=True):
        v_name = st.text_input("Supplier Business Identity Name")
        v_phone = st.text_input("Primary Contact Phone Interface")
        v_spec = st.text_input("Production Speciality Line")
        v_addr = st.text_area("Corporate Headquarters Address")
        
        if st.form_submit_button("Record Supplier Registry") and v_name:
            if db_active:
                run_db_query("INSERT INTO sources (source_name, phone, address, speciality) VALUES (%s, %s, %s, %s)", 
                          (v_name, v_phone, v_addr, v_spec))
            else:
                new_sid = len(st.session_state.sources) + 1
                st.session_state.sources.append({"source_id": new_sid, "source_name": v_name, "phone": v_phone, "speciality": v_spec, "address": v_addr})
            st.success("Supplier profile tracked into memory base.")
            
    st.subheader("Affiliated Vendor Network")
    if db_active:
        active_s = run_db_query("SELECT source_name, phone, speciality, address FROM sources", is_select=True)
    else:
        active_s = pd.DataFrame(st.session_state.sources)[["source_name", "phone", "speciality", "address"]]
        
    if active_s is not None and not active_s.empty:
        st.dataframe(active_s, use_container_width=True)

# ==========================================
# MODULE 4: CLIENT LEDGER PROFILES
# ==========================================
elif choice == "Client Ledger Profiles":
    st.subheader("Client Portfolios Matrix")
    with st.form("new_buyer_form", clear_on_submit=True):
        c_name = st.text_input("Client Corporate Identity Name")
        c_phone = st.text_input("Operational Phone Matrix Contact")
        c_notes = st.text_area("Purchasing Requirements Notes")
        
        if st.form_submit_button("Archive Profile Matrix") and c_name:
            if db_active:
                run_db_query("INSERT INTO customers (customer_name, phone, contact_notes) VALUES (%s, %s, %s)", (c_name, c_phone, c_notes))
            else:
                new_cid = len(st.session_state.customers) + 1
                st.session_state.customers.append({"customer_id": new_cid, "customer_name": c_name, "phone": c_phone, "contact_notes": c_notes})
            st.success("Customer client metadata saved.")
            
    st.subheader("Active Customer Portfolio List")
    if db_active:
        custs = run_db_query("SELECT customer_name, phone, contact_notes FROM customers", is_select=True)
    else:
        custs = pd.DataFrame(st.session_state.customers)[["customer_name", "phone", "contact_notes"]]
        
    if custs is not None and not custs.empty:
        st.dataframe(custs, use_container_width=True)

# ==========================================
# MODULE 5: PROCESS LOG LEDGER
# ==========================================
elif choice == "Process Log Ledger":
    st.subheader("Execute Stock Transaction Movements")
    
    if db_active:
        prods = run_db_query("SELECT product_id, product_name, current_stock, sell_retail, sell_wholesale FROM products", is_select=True)
        clis = run_db_query("SELECT customer_id, customer_name FROM customers", is_select=True)
        prod_list = list(prods['product_name']) if not prods.empty else []
        prod_map = {r['product_name']: r for _, r in prods.iterrows()} if not prods.empty else {}
    else:
        prod_list = [x['product_name'] for x in st.session_state.products]
        prod_map = {x['product_name']: x for x in st.session_state.products}
        clis = pd.DataFrame(st.session_state.customers)
        
    if prod_list:
        cli_map = {"[No Customer Associated - Inbound Stocking]": None}
        if db_active and not clis.empty:
            for _, r in clis.iterrows(): cli_map[r['customer_name']] = r['customer_id']
        elif not db_active and not clis.empty:
            for _, r in clis.iterrows(): cli_map[r['customer_name']] = r['customer_id']
                
        with st.form("transaction_processing_ledger", clear_on_submit=True):
            p_selected = st.selectbox("Target Product Variant", prod_list)
            t_vector = st.selectbox("Operation Flow Vector", ["OUTPUT_SALE", "INPUT_RESTOCK"])
            s_mode = st.selectbox("Pricing Tier (Sales Only)", ["RETAIL", "WHOLESALE"])
            t_qty = st.number_input("Transactional Quantity Volume", min_value=1, step=1)
            t_disc = st.number_input("Applied Discount (৳)", min_value=0.0, step=5.0)
            c_linked = st.selectbox("Linked Client Entity", list(cli_map.keys()))
            
            if st.form_submit_button("Commit Operational Entry"):
                row_match = prod_map[p_selected]
                pid = row_match['product_id']
                stk_current = row_match['current_stock']
                
                if t_vector == "OUTPUT_SALE" and t_qty > stk_current:
                    st.error("Operation Aborted: Requested checkout inventory metrics exceed active physical allocations.")
                else:
                    base_rate = float(row_match['sell_retail'] if s_mode == "RETAIL" else row_match['sell_wholesale'])
                    total_price = (base_rate * t_qty) - float(t_disc)
                    if total_price < 0: total_price = 0.0
                    
                    stk_updated = stk_current - t_qty if t_vector == "OUTPUT_SALE" else stk_current + t_qty
                    cid = cli_map[c_linked]
                    
                    if db_active:
                        run_db_query("INSERT INTO transactions (product_id, transaction_type, sale_vector, quantity, discount, total_price, customer_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                                  (pid, t_vector, s_mode, t_qty, t_disc, total_price, cid))
                        run_db_query("UPDATE products SET current_stock = %s WHERE product_id = %s", (stk_updated, pid))
                    else:
                        # Mutate the local session store states
                        for x in st.session_state.products:
                            if x['product_id'] == pid:
                                x['current_stock'] = stk_updated
                        st.session_state.transactions.append({
                            "transaction_id": len(st.session_state.transactions) + 1, "product_id": pid,
                            "transaction_type": t_vector, "sale_vector": s_mode, "quantity": t_qty,
                            "discount": t_disc, "total_price": total_price, "customer_id": cid,
                            "transaction_date": str(datetime.date.today())
                        })
                    st.success(f"Log complete. Calculated Total Rate: ৳{total_price:,.2f}")
    else:
        st.error("Process Blocked: Populate items inside the Catalog before processing transaction entries.")