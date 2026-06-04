import streamlit as st
import mysql.connector
import pandas as pd

# Clean page configuration - no emojis in title strings
st.set_page_config(page_title="Thread Inventory System", layout="wide")

# Inject Custom Minimalist HTML and CSS Theme styling to override Streamlit colors
st.markdown("""
    <style>
        /* Minimalist professional clean palette */
        :root {
            --primary-color: #000000;
            --background-color: #FFFFFF;
            --secondary-background-color: #F8F9FA;
            --text-color: #212529;
        }
        
        /* Remove default decorative headers/footers */
        header {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Typography overrides */
        html, body, [class*="css"]  {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: #212529;
        }
        
        /* Box and form container standardization */
        .stForm {
            border: 1px solid #DEE2E6 !important;
            padding: 20px !important;
            border-radius: 4px !important;
            background-color: #FFFFFF !important;
        }
        
        /* Flat uniform buttons */
        button {
            background-color: #212529 !important;
            color: #FFFFFF !important;
            border-radius: 4px !important;
            border: none !important;
        }
    </style>
""", unsafe_allow_html=True)

st.title("Thread Business Inventory and Sales System")

# Safe TiDB Database connection handler utilizing Streamlit secrets configuration
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
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        if is_select:
            result = cursor.fetchall()
            return pd.DataFrame(result)
    except Exception as e:
        st.error(f"Database System Error: {e}")
    finally:
        cursor.close()
        conn.close()

# Sidebar Navigation Control - Clean text strings
menu = ["Global Search Dashboard", "Suppliers Entry", "Product Catalog", "Customer Profiles", "Record Transaction Ledger"]
choice = st.sidebar.selectbox("Navigation Modules", menu)

# ==========================================
# MODULE 1: GLOBAL SEARCH & LOGISTICS
# ==========================================
if choice == "Global Search Dashboard":
    st.subheader("Global Search Engine")
    
    tab1, tab2, tab3 = st.tabs(["Search Inventory and Suppliers", "Trace Sales and Customer Contacts", "Low Stock Priorities"])
    
    with tab1:
        search_term = st.text_input("🔍 Enter product name, color specification, or supplier name:")
        sql = """
            SELECT p.product_name, p.color_code, p.unit_price, p.current_stock, 
                   s.source_name AS supplier_name, s.phone AS supplier_phone 
            FROM products p 
            LEFT JOIN sources s ON p.source_id = s.source_id
        """
        if search_term:
            sql += " WHERE p.product_name LIKE %s OR p.color_code LIKE %s OR s.source_name LIKE %s"
            like_val = f"%{search_term}%"
            df = run_query(sql, (like_val, like_val, like_val), is_select=True)
        else:
            df = run_query(sql, is_select=True)
            
        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.write("No matching items found.")

    with tab2:
        st.subheader("Trace Sales Records")
        buyer_search = st.text_input("🔍 Search past customer names or product descriptions to follow up:")
        sql_sales = """
            SELECT t.transaction_date, p.product_name, p.color_code, t.quantity, t.total_price,
                   c.customer_name, c.phone AS customer_phone
            FROM transactions t
            JOIN products p ON t.product_id = p.product_id
            LEFT JOIN customers c ON t.customer_id = c.customer_id
            WHERE t.transaction_type = 'OUTPUT_SALE'
        """
        if buyer_search:
            sql_sales += " AND (c.customer_name LIKE %s OR p.product_name LIKE %s)"
            like_buyer = f"%{buyer_search}%"
            sales_df = run_query(sql_sales, (like_buyer, like_buyer), is_select=True)
        else:
            sales_df = run_query(sql_sales, is_select=True)
            
        if sales_df is not None and not sales_df.empty:
            st.dataframe(sales_df, use_container_width=True)
        else:
            st.write("No historical sales logs matched criteria.")

    with tab3:
        st.subheader("Restock Analysis")
        low_stock_df = run_query("SELECT product_name, color_code, current_stock FROM products WHERE current_stock <= low_stock_threshold", is_select=True)
        if low_stock_df is not None and not low_stock_df.empty:
            st.write("Attention Required: The following items are low on stock.")
            st.table(low_stock_df)
        else:
            st.write("All inventory metrics are operating within optimal capacities.")

# ==========================================
# MODULE 2: SUPPLIERS ENTRY
# ==========================================
elif choice == "Suppliers Entry":
    st.subheader("Manage Thread Suppliers and Sources")
    with st.form("add_source_form", clear_on_submit=True):
        name = st.text_input("Supplier Business Name")
        phone = st.text_input("Phone Number")
        addr = st.text_area("Office Address")
        if st.form_submit_button("Save Supplier Details") and name:
            run_query("INSERT INTO sources (source_name, phone, address) VALUES (%s, %s, %s)", (name, phone, addr))
            st.info("Supplier data successfully written to TiDB cluster.")
            
    st.subheader("Active Registered Suppliers")
    active_sources = run_query("SELECT * FROM sources", is_select=True)
    if active_sources is not None and not active_sources.empty:
        st.dataframe(active_sources, use_container_width=True)

# ==========================================
# MODULE 3: PRODUCT CATALOG
# ==========================================
elif choice == "Product Catalog":
    st.subheader("Thread SKU Catalog")
    sources_df = run_query("SELECT source_id, source_name FROM sources", is_select=True)
    if sources_df is not None and not sources_df.empty:
        source_map = {row['source_name']: row['source_id'] for _, row in sources_df.iterrows()}
        with st.form("add_product_form", clear_on_submit=True):
            p_name = st.text_input("Thread Description or Name")
            color = st.text_input("Color Specification Code")
            selected_source = st.selectbox("Assign Supplier Source", list(source_map.keys()))
            price = st.number_input("Unit Price", min_value=0.0, step=0.01)
            init_stock = st.number_input("Initial Opening Stock Volume", min_value=0, step=1)
            
            if st.form_submit_button("Save Product to SKU Records") and p_name:
                run_query("INSERT INTO products (product_name, color_code, source_id, unit_price, current_stock) VALUES (%s, %s, %s, %s, %s)",
                          (p_name, color, source_map[selected_source], price, init_stock))
                st.info("Product variant cataloged successfully.")
    else:
        st.error("Error: Register a Supplier entry profile first before allocating physical variants.")

# ==========================================
# MODULE 4: CUSTOMER PROFILES
# ==========================================
elif choice == "Customer Profiles":
    st.subheader("Customer Profiles Database")
    with st.form("add_cust_form", clear_on_submit=True):
        c_name = st.text_input("Customer Name")
        c_phone = st.text_input("Contact Number")
        c_notes = st.text_area("Business Preference Notes (e.g. tracking specific buyer demands)")
        if st.form_submit_button("Save Profile") and c_name:
            run_query("INSERT INTO customers (customer_name, phone, contact_notes) VALUES (%s, %s, %s)", (c_name, c_phone, c_notes))
            st.info("Buyer ledger record saved safely.")
            
    st.subheader("Registered Client Portfolio")
    all_custs = run_query("SELECT * FROM customers", is_select=True)
    if all_custs is not None and not all_custs.empty:
        st.dataframe(all_custs, use_container_width=True)

# ==========================================
# MODULE 5: TRANSACTION LOGISTICS LEDGER
# ==========================================
elif choice == "Record Transaction Ledger":
    st.subheader("Post Transaction Entry (Inbound or Outbound)")
    products_df = run_query("SELECT product_id, product_name, current_stock, unit_price FROM products", is_select=True)
    customers_df = run_query("SELECT customer_id, customer_name FROM customers", is_select=True)
    
    if products_df is not None and not products_df.empty:
        prod_map = {f"{r['product_name']} (Available: {r['current_stock']})": r for _, r in products_df.iterrows()}
        cust_map = {"[No Customer Linked / Inventory Inbound Restock]": None}
        if customers_df is not None and not customers_df.empty:
            for _, r in customers_df.iterrows():
                cust_map[r['customer_name']] = r['customer_id']
                
        with st.form("ledger_form", clear_on_submit=True):
            chosen_prod_str = st.selectbox("Select Target Product Line", list(prod_map.keys()))
            txn_type = st.selectbox("Transaction Vector Direction", ["OUTPUT_SALE", "INPUT_RESTOCK"])
            qty = st.number_input("Quantity Volume", min_value=1, step=1)
            chosen_cust_str = st.selectbox("Assign Customer Entity (Traceable for Sales)", list(cust_map.keys()))
            
            if st.form_submit_button("Commit Ledger Records"):
                target_prod = prod_map[chosen_prod_str]
                pid = target_prod['product_id']
                current_vol = target_prod['current_stock']
                
                if txn_type == "OUTPUT_SALE" and qty > current_vol:
                    st.error("Error: Insufficient stock volumes available to complete transaction execution.")
                else:
                    new_vol = current_vol - qty if txn_type == "OUTPUT_SALE" else current_vol + qty
                    calculated_aggregate_cost = float(target_prod['unit_price']) * qty
                    cid = cust_map[chosen_cust_str]
                    
                    # Log core transactional matrix
                    run_query("INSERT INTO transactions (product_id, transaction_type, quantity, total_price, customer_id) VALUES (%s, %s, %s, %s, %s)",
                              (pid, txn_type, qty, calculated_aggregate_cost, cid))
                    # Synchronize base parameters
                    run_query("UPDATE products SET current_stock = %s WHERE product_id = %s", (new_vol, pid))
                    st.info(f"Transaction logged successfully. Financial processing metric: ${calculated_aggregate_cost:,.2f}")
    else:
        st.error("Error: Register an item row inside the Product Catalog before initializing system entries.")