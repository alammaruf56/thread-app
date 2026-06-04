import streamlit as st
import mysql.connector
import pandas as pd
import datetime

# ══════════════════════════════════════════════════════════════
#  PAGE CONFIG & THEME
# ══════════════════════════════════════════════════════════════
st.set_page_config(page_title="My Thread Business", page_icon="🧵", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght=300;400;500;600;700&family=Playfair+Display:wght=400;600;700&family=IBM+Plex+Mono:wght=300;400;500&display=swap');
html, body, [class*="css"], .stApp { background-color: #FDFBF7 !important; color: #111111 !important; font-family: 'Outfit', sans-serif !important; }
footer { visibility: hidden !important; } #MainMenu { visibility: hidden !important; }
h1, h2, h3 { font-family: 'Playfair Display', serif !important; color: #111111 !important; }
label, div[data-testid="stWidgetLabel"] p { color: #333333 !important; font-size: 0.85rem !important; font-weight: 500 !important; }
.stTextInput>div>div>input, .stNumberInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div { background-color: #ffffff !important; color: #111111 !important; border: 1.5px solid #E0D8CC !important; border-radius: 6px !important; }
section[data-testid="stSidebar"] { background-color: #111111 !important; border-right: 1px solid #2a2a2a !important; }
section[data-testid="stSidebar"] * { color: #FDFBF7 !important; }
.stButton>button { background-color: #111111 !important; color: #FDFBF7 !important; border-radius: 6px !important; font-weight: 600 !important; border: 1.5px solid #111111 !important; }
.stButton>button:hover { background-color: #C4882A !important; border-color: #C4882A !important; }
.stDataFrame { border: 1.5px solid #E0D8CC !important; border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  DATABASE CONNECTION
# ══════════════════════════════════════════════════════════════
@st.cache_resource(ttl=30)
def get_connection():
    try:
        if "mysql" not in st.secrets: return False, None
        conn = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            port=int(st.secrets["mysql"]["port"]),
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"].get("database", "thread_business"),
            autocommit=True, connection_timeout=5, ssl_disabled=False
        )
        return True, conn
    except Exception as e:
        return False, str(e)

db_ok, db_conn = get_connection()

def qry(sql, params=None, fetch=False):
    if not db_ok or db_conn is None: return pd.DataFrame() if fetch else None
    try:
        db_conn.ping(reconnect=True, attempts=2, delay=1)
        cur = db_conn.cursor(dictionary=True)
        cur.execute(sql, params or ())
        if fetch:
            rows = cur.fetchall()
            cur.close()
            return pd.DataFrame(rows) if rows else pd.DataFrame()
        cur.close()
        return None
    except Exception as e:
        st.error(f"DB Error: {e}")
        return pd.DataFrame() if fetch else None

def today(): return datetime.date.today().isoformat()

# ══════════════════════════════════════════════════════════════
#  SIDEBAR & NAVIGATION
# ══════════════════════════════════════════════════════════════
st.sidebar.markdown("<h2>My Thread Business</h2>", unsafe_allow_html=True)

if db_ok:
    st.sidebar.success("● Database Connected")
else:
    st.sidebar.error("● No Database (Demo Mode)")

PAGES = {"📊 Dashboard": "dashboard", "🧵 Products": "products", "🤝 Sellers": "sellers", "👥 Customers": "customers", "💰 Sales & Stock": "sales"}
choice = st.sidebar.radio("Navigate", list(PAGES.keys()), label_visibility="collapsed")
page = PAGES[choice]

# ══════════════════════════════════════════════════════════════
#  1. DASHBOARD
# ══════════════════════════════════════════════════════════════
if page == "dashboard":
    st.markdown("<h1>Business Dashboard</h1>", unsafe_allow_html=True)
    if db_ok:
        total_p = qry("SELECT COUNT(*) as c FROM products", fetch=True).iloc[0]['c'] if not qry("SELECT COUNT(*) as c FROM products", fetch=True).empty else 0
        total_cust = qry("SELECT COUNT(*) as c FROM customers", fetch=True).iloc[0]['c'] if not qry("SELECT COUNT(*) as c FROM customers", fetch=True).empty else 0
        c1, c2 = st.columns(2)
        c1.metric("Total Products", total_p)
        c2.metric("Total Customers", total_cust)

# ══════════════════════════════════════════════════════════════
#  2. PRODUCTS (Simplified)
# ══════════════════════════════════════════════════════════════
elif page == "products":
    st.markdown("<h1>Product Catalog</h1>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["📋 View Products", "➕ Add Product"])

    with tab1:
        search_p = st.text_input("🔍 Search Product by Name or Code")
        if db_ok:
            sql = "SELECT product_name, sku_code as thread_code, category, current_stock, unit, sell_retail as price FROM products WHERE is_active=1"
            if search_p:
                sql += f" AND (product_name LIKE '%{search_p}%' OR sku_code LIKE '%{search_p}%')"
            df = qry(sql, fetch=True)
            if not df.empty: st.dataframe(df, use_container_width=True, hide_index=True)
            else: st.info("No products found.")

    with tab2:
        with st.form("prod_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            p_name = c1.text_input("Product Name *")
            p_sku = c2.text_input("Product Code / Thread Number (Manual) *")
            
            p_cat = c1.text_input("Category (Manual)")
            p_unit = c2.selectbox("Unit", ["Cone", "Spool", "kg", "Box", "Piece", "Dozen"])
            
            c3, c4 = st.columns(2)
            p_price = c3.number_input("Selling Price (৳)", min_value=0.0, step=1.0)
            p_stock = c4.number_input("Opening Stock", min_value=0, step=1)

            if st.form_submit_button("➕ Add Product"):
                if not p_name or not p_sku:
                    st.error("Name and Thread Code are required!")
                else:
                    if db_ok:
                        # Inserting minimal data. Other columns will take default/null values.
                        qry("INSERT INTO products (product_name, sku_code, category, sell_retail, current_stock, unit, is_active) VALUES (%s, %s, %s, %s, %s, %s, 1)", 
                            (p_name, p_sku, p_cat, p_price, p_stock, p_unit))
                        st.success(f"✓ '{p_name}' added successfully!")
                        st.rerun()

# ══════════════════════════════════════════════════════════════
#  3. SELLERS (With Search Bar)
# ══════════════════════════════════════════════════════════════
elif page == "sellers":
    st.markdown("<h1>Sellers Directory</h1>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["📋 View Sellers", "➕ Add Seller"])
    
    with tab1:
        search_s = st.text_input("🔍 Search Seller by Name or Phone")
        if db_ok:
            sql = "SELECT seller_name, phone, area, address FROM sellers WHERE is_active=1"
            if search_s:
                sql += f" AND (seller_name LIKE '%{search_s}%' OR phone LIKE '%{search_s}%')"
            df = qry(sql, fetch=True)
            if not df.empty: st.dataframe(df, use_container_width=True, hide_index=True)
            else: st.info("No sellers found.")

    with tab2:
        with st.form("seller_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            sel_name = c1.text_input("Seller Name *")
            sel_phone = c2.text_input("Phone Number")
            sel_area = st.text_input("Area")
            if st.form_submit_button("➕ Add Seller"):
                if db_ok and sel_name:
                    qry("INSERT INTO sellers (seller_name, phone, area, is_active) VALUES (%s, %s, %s, 1)", (sel_name, sel_phone, sel_area))
                    st.success("✓ Seller added.")
                    st.rerun()

# ══════════════════════════════════════════════════════════════
#  4. CUSTOMERS (With Search Bar)
# ══════════════════════════════════════════════════════════════
elif page == "customers":
    st.markdown("<h1>Customer Directory</h1>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["📋 View Customers", "➕ Add Customer"])
    
    with tab1:
        search_c = st.text_input("🔍 Search Customer by Name or Phone")
        if db_ok:
            sql = "SELECT customer_name, phone, address FROM customers"
            if search_c:
                sql += f" WHERE customer_name LIKE '%{search_c}%' OR phone LIKE '%{search_c}%'"
            df = qry(sql, fetch=True)
            if not df.empty: st.dataframe(df, use_container_width=True, hide_index=True)
            else: st.info("No customers found.")

    with tab2:
        with st.form("cust_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            cust_name = c1.text_input("Customer Name *")
            cust_phone = c2.text_input("Phone")
            cust_addr = st.text_input("Address")
            if st.form_submit_button("➕ Add Customer"):
                if db_ok and cust_name:
                    qry("INSERT INTO customers (customer_name, phone, address) VALUES (%s, %s, %s)", (cust_name, cust_phone, cust_addr))
                    st.success("✓ Customer added.")
                    st.rerun()

# ══════════════════════════════════════════════════════════════
#  5. SALES & STOCK (Simplified)
# ══════════════════════════════════════════════════════════════
elif page == "sales":
    st.markdown("<h1>Sales & Stock Entry</h1>", unsafe_allow_html=True)
    
    if db_ok:
        prods = qry("SELECT product_id, product_name, current_stock, sell_retail FROM products WHERE is_active=1", fetch=True)
        if not prods.empty:
            with st.form("sale_form", clear_on_submit=True):
                p_name = st.selectbox("Select Product", prods["product_name"].tolist())
                p_row = prods[prods["product_name"] == p_name].iloc[0]
                
                c1, c2 = st.columns(2)
                t_type = c1.selectbox("Type", ["Sale (-)", "Restock (+)"])
                qty = c2.number_input("Quantity", min_value=1, step=1)
                
                if st.form_submit_button("💾 Submit Entry"):
                    new_stock = int(p_row["current_stock"]) - qty if t_type == "Sale (-)" else int(p_row["current_stock"]) + qty
                    if t_type == "Sale (-)" and int(p_row["current_stock"]) < qty:
                        st.error("Not enough stock!")
                    else:
                        db_type = "OUTPUT_SALE" if t_type == "Sale (-)" else "INPUT_RESTOCK"
                        qry("INSERT INTO transactions (transaction_date, product_id, product_name, transaction_type, quantity, total_price) VALUES (%s,%s,%s,%s,%s,%s)",
                            (today(), int(p_row["product_id"]), p_name, db_type, qty, qty * float(p_row["sell_retail"])))
                        qry("UPDATE products SET current_stock=%s WHERE product_id=%s", (new_stock, int(p_row["product_id"])))
                        st.success(f"✓ Success! New Stock: {new_stock}")
                        st.rerun()
        else:
            st.warning("Please add a product first.")