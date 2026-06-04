import streamlit as st
import mysql.connector
import pandas as pd

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
# SUPER-SPEED DATABASE CONNECTION MANAGER
# ==========================================
# This @st.cache_resource tag keeps the connection open permanently!
@st.cache_resource
def get_connection():
    return mysql.connector.connect(
        host=st.secrets["mysql"]["host"],
        port=int(st.secrets["mysql"]["port"]),
        user=st.secrets["mysql"]["user"],
        password=st.secrets["mysql"]["password"],
        database="thread_business",
        autocommit=True
    )

def run_query(query, params=None, is_select=False):
    conn = get_connection()
    
    # Auto-reconnect if the database went to sleep
    try:
        conn.ping(reconnect=True, attempts=3, delay=1)
    except Exception as e:
        st.error(f"Connection lost and could not be restored: {e}")
        
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        if is_select:
            return pd.DataFrame(cursor.fetchall())
    except Exception as e:
        st.error(f"Database Connectivity Failure Core: {e}")
    finally:
        cursor.close()
        # WE NO LONGER CLOSE THE CONNECTION HERE! It stays alive for speed.

# Navigation Selection Array Matrix
menu = ["Dashboard Metrics", "Thread Products SKU Catalog", "Registered Supplier Base", "Client Ledger Profiles", "Process Log Ledger"]
choice = st.sidebar.selectbox("Navigation Sections", menu)

# ==========================================
# MODULE 1: PREMIUM SEARCH & METRICS DASHBOARD
# ==========================================
if choice == "Dashboard Metrics":
    st.subheader("Business Metrics Analytics")
    
    # Live Aggregates Computation Engine (Now executes instantly)
    p_count = run_query("SELECT COUNT(*) as total FROM products", is_select=True)
    s_count = run_query("SELECT COUNT(*) as total FROM sources", is_select=True)
    alerts = run_query("SELECT COUNT(*) as total FROM products WHERE current_stock <= low_stock_threshold", is_select=True)
    rev_calc = run_query("SELECT SUM(total_price) as total FROM transactions WHERE transaction_type='OUTPUT_SALE'", is_select=True)
    
    # Render Stat Cards mirroring prototype design layouts
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Products Cataloged", int(p_count['total'].iloc[0] if not p_count.empty else 0))
    c2.metric("Active Suppliers", int(s_count['total'].iloc[0] if not s_count.empty else 0))
    c3.metric("Low Stock Alerts", int(alerts['total'].iloc[0] if not alerts.empty else 0))
    
    rev_val = float(rev_calc['total'].iloc[0]) if not rev_calc.empty and rev_calc['total'].iloc[0] is not None else 0.0
    c4.metric("Gross Sales Revenue", f"৳{rev_val:,.2f}")
    
    st.markdown("---")
    st.subheader("Global Inventory Search Engine")
    search_term = st.text_input("🔍 Filter matching parameters across categories, product descriptions or SKUs:")
    
    sql = """
        SELECT p.product_name, p.sku_code, p.category, p.current_stock, p.sell_retail, p.sell_wholesale,
               s.source_name as supplier_assigned
        FROM products p
        LEFT JOIN sources s ON p.source_id = s.source_id
    """
    if search_term:
        sql += " WHERE p.product_name LIKE %s OR p.sku_code LIKE %s OR p.category LIKE %s"
        l_term = f"%{search_term}%"
        df = run_query(sql, (l_term, l_term, l_term), is_select=True)
    else:
        df = run_query(sql, is_select=True)
        
    if df is not None and not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.write("No catalog lines matching selection criteria found.")

# ==========================================
# MODULE 2: THREAD SKU CATALOG MANAGER
# ==========================================
elif choice == "Thread Products SKU Catalog":
    st.subheader("Thread Variants SKU Management")
    
    sups_df = run_query("SELECT source_id, source_name FROM sources", is_select=True)
    if sups_df is not None and not sups_df.empty:
        sup_dict = {row['source_name']: row['source_id'] for _, row in sups_df.iterrows()}
        
        with st.form("new_product_skuline", clear_on_submit=True):
            col1, col2 = st.columns(2)
            p_name = col1.text_input("Product Identifier Line Name")
            p_sku = col2.text_input("Unique SKU Code")
            p_cat = col1.selectbox("Material Category Group", ["Cotton", "Silk", "Polyester", "Wool", "Nylon", "Mixed", "Other"])
            p_sup = col2.selectbox("Allocated Source Supplier Partner", list(sup_dict.keys()))
            
            col3, col4, col5 = st.columns(3)
            b_cost = col3.number_input("Purchase Buying Cost (৳)", min_value=0.0, step=1.0)
            s_retail = col4.number_input("Retail Selling Unit Price (৳)", min_value=0.0, step=1.0)
            s_wholesale = col5.number_input("Wholesale Selling Unit Price (৳)", min_value=0.0, step=1.0)
            
            init_stk = st.number_input("Initial Starting Physical Stock Volume", min_value=0, step=1)
            
            if st.form_submit_button("Commit Product Configuration") and p_name:
                run_query("""INSERT INTO products 
                             (product_name, sku_code, category, source_id, buy_price, sell_retail, sell_wholesale, current_stock) 
                             VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                          (p_name, p_sku, p_cat, sup_dict[p_sup], b_cost, s_retail, s_wholesale, init_stk))
                st.success("New product asset line successfully structured.")
    else:
        st.warning("Ensure at least one operational supplier is initialized before registering inventory assets.")

    st.subheader("Active Stock Registry")
    all_p = run_query("SELECT sku_code, product_name, category, buy_price, sell_retail, current_stock FROM products", is_select=True)
    if all_p is not None and not all_p.empty:
        st.dataframe(all_p, use_container_width=True)

# ==========================================
# MODULE 3: REGISTERED SUPPLIER BASE
# ==========================================
elif choice == "Registered Supplier Base":
    st.subheader("Manage Global Production Vendors")
    with st.form("new_vendor_entry", clear_on_submit=True):
        v_name = st.text_input("Supplier Corporate Identity Name")
        v_phone = st.text_input("Primary Contact Phone Interface")
        v_spec = st.text_input("Production Speciality Line (e.g., Organic Cotton, Dyed Silk)")
        v_addr = st.text_area("Corporate Headquaters Mailing Address")
        
        if st.form_submit_button("Record Supplier Registry") and v_name:
            run_query("INSERT INTO sources (source_name, phone, address, speciality) VALUES (%s, %s, %s, %s)", 
                      (v_name, v_phone, v_addr, v_spec))
            st.success("Supplier tracking index saved.")
            
    st.subheader("Affiliated Active Vendor Network")
    active_s = run_query("SELECT source_name, phone, speciality, address FROM sources", is_select=True)
    if active_s is not None and not active_s.empty:
        st.dataframe(active_s, use_container_width=True)

# ==========================================
# MODULE 4: CLIENT LEDGER PROFILES
# ==========================================
elif choice == "Client Ledger Profiles":
    st.subheader("Client Portfolios Matrix")
    with st.form("new_buyer_form", clear_on_submit=True):
        c_name = st.text_input("Client Entity Business Name")
        c_phone = st.text_input("Operational Phone Matrix Contact")
        c_notes = st.text_area("Specific Purchasing Standard Requirements Notes")
        
        if st.form_submit_button("Archive Profile Matrix") and c_name:
            run_query("INSERT INTO customers (customer_name, phone, contact_notes) VALUES (%s, %s, %s)", 
                      (c_name, c_phone, c_notes))
            st.success("Customer metadata structural mapping complete.")
            
    st.subheader("Active Customer Portfolio List")
    custs = run_query("SELECT customer_name, phone, contact_notes FROM customers", is_select=True)
    if custs is not None and not custs.empty:
        st.dataframe(custs, use_container_width=True)

# ==========================================
# MODULE 5: INBOUND / OUTBOUND PROCESS LOG LEDGER
# ==========================================
elif choice == "Process Log Ledger":
    st.subheader("Execute Stock Transaction Movements")
    
    prods = run_query("SELECT product_id, product_name, current_stock, sell_retail, sell_wholesale FROM products", is_select=True)
    clis = run_query("SELECT customer_id, customer_name FROM customers", is_select=True)
    
    if prods is not None and not prods.empty:
        prod_map = {f"{r['product_name']} (In Stock: {r['current_stock']})": r for _, r in prods.iterrows()}
        cli_map = {"[No Customer Associated - Inbound Restock System]": None}
        if clis is not None and not clis.empty:
            for _, r in clis.iterrows():
                cli_map[r['customer_name']] = r['customer_id']
                
        with st.form("transaction_processing_ledger", clear_on_submit=True):
            p_selected = st.selectbox("Target Catalog Product Variant", list(prod_map.keys()))
            t_vector = st.selectbox("Operation Matrix Flow Vector", ["OUTPUT_SALE", "INPUT_RESTOCK"])
            s_mode = st.selectbox("Pricing Target Mode Tier (Sales Only)", ["RETAIL", "WHOLESALE"])
            t_qty = st.number_input("Transactional Quantity Volume Metric", min_value=1, step=1)
            t_disc = st.number_input("Applied Transaction Discount (৳)", min_value=0.0, step=5.0)
            c_linked = st.selectbox("Linked Client Account Entity", list(cli_map.keys()))
            
            if st.form_submit_button("Commit Operational Entry Ledger"):
                row_match = prod_map[p_selected]
                pid = row_match['product_id']
                stk_current = row_match['current_stock']
                
                if t_vector == "OUTPUT_SALE" and t_qty > stk_current:
                    st.error("Operation Aborted: Requested checkout inventory metrics exceed active physical allocations.")
                else:
                    # Resolve Price Target Tier Logic Matrix
                    base_unit_rate = float(row_match['sell_retail'] if s_mode == "RETAIL" else row_match['sell_wholesale'])
                    aggregate_cost = (base_unit_rate * t_qty) - float(t_disc)
                    if aggregate_cost < 0: aggregate_cost = 0.0
                    
                    stk_updated = stk_current - t_qty if t_vector == "OUTPUT_SALE" else stk_current + t_qty
                    cid = cli_map[c_linked]
                    
                    # Update parameters inside database engine
                    run_query("INSERT INTO transactions (product_id, transaction_type, sale_vector, quantity, discount, total_price, customer_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                              (pid, t_vector, s_mode, t_qty, t_disc, aggregate_cost, cid))
                    run_query("UPDATE products SET current_stock = %s WHERE product_id = %s", (stk_updated, pid))
                    st.success(f"Log processing complete. Total calculated transaction rate: ৳{aggregate_cost:,.2f}")
    else:
        st.error("Process Blocked: Populate items inside the Product SKU Catalog before opening transaction logs.")