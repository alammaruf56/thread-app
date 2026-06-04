import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime

# ══════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="ThreadTrack Pro",
    page_icon="🧵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════════
#  THEME CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Playfair+Display:wght@400;600;700&family=IBM+Plex+Mono:wght@300;400;500&display=swap');

html, body, [class*="css"], .stApp {
    background-color: #FDFBF7 !important;
    color: #111111 !important;
    font-family: 'Outfit', sans-serif !important;
}
footer { visibility: hidden !important; }
#MainMenu { visibility: hidden !important; }

h1, h2, h3 {
    font-family: 'Playfair Display', serif !important;
    color: #111111 !important;
}

/* Labels */
label, div[data-testid="stWidgetLabel"] p {
    color: #333333 !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
}

/* Inputs */
.stTextInput>div>div>input,
.stNumberInput>div>div>input,
.stTextArea>div>div>textarea,
.stSelectbox>div>div>div {
    background-color: #ffffff !important;
    color: #111111 !important;
    border: 1.5px solid #E0D8CC !important;
    border-radius: 6px !important;
    font-family: 'Outfit', sans-serif !important;
}
.stTextInput>div>div>input:focus,
.stTextArea>div>div>textarea:focus {
    border-color: #C4882A !important;
    box-shadow: 0 0 0 2px rgba(196,136,42,0.15) !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #111111 !important;
    border-right: 1px solid #2a2a2a !important;
}
section[data-testid="stSidebar"] * { color: #FDFBF7 !important; }
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] div[data-testid="stWidgetLabel"] p {
    color: #C4882A !important;
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
}
section[data-testid="stSidebar"] .stSelectbox>div>div>div {
    background-color: #1e1e1e !important;
    border-color: #333 !important;
    color: #FDFBF7 !important;
}

/* Metrics */
div[data-testid="stMetricContainer"] {
    background: #ffffff !important;
    border: 1.5px solid #E0D8CC !important;
    border-radius: 10px !important;
    padding: 20px !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.04) !important;
}
div[data-testid="stMetricLabel"] > div {
    font-size: 0.72rem !important;
    text-transform: uppercase !important;
    letter-spacing: 2px !important;
    color: #888888 !important;
    font-family: 'IBM Plex Mono', monospace !important;
}
div[data-testid="stMetricValue"] > div {
    font-family: 'Playfair Display', serif !important;
    font-size: 2.2rem !important;
    color: #C4882A !important;
}

/* Buttons */
.stButton>button {
    background-color: #111111 !important;
    color: #FDFBF7 !important;
    border-radius: 6px !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    border: 1.5px solid #111111 !important;
    padding: 0.6rem 1.8rem !important;
    transition: all 0.2s ease !important;
}
.stButton>button:hover {
    background-color: #C4882A !important;
    border-color: #C4882A !important;
}

/* Forms */
.stForm {
    background: #ffffff !important;
    border: 1.5px solid #E0D8CC !important;
    border-radius: 12px !important;
    padding: 28px !important;
}

/* Dataframe */
.stDataFrame { border: 1.5px solid #E0D8CC !important; border-radius: 8px !important; }

/* Success / Error */
.stSuccess { border-radius: 8px !important; }
.stError   { border-radius: 8px !important; }

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: #F0EBE3;
    border-radius: 8px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 6px !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    color: #666 !important;
}
.stTabs [aria-selected="true"] {
    background: #ffffff !important;
    color: #C4882A !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.1) !important;
}

/* Search result highlight */
.search-card {
    background: #ffffff;
    border: 1.5px solid #E0D8CC;
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 12px;
    border-left: 4px solid #C4882A;
}
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    font-family: 'IBM Plex Mono', monospace;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  DATABASE CONNECTION
# ══════════════════════════════════════════════════════════════
@st.cache_resource(ttl=30)
def get_connection():
    try:
        if "mysql" not in st.secrets:
            return False, None
        conn = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            port=int(st.secrets["mysql"]["port"]),
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"].get("database", "thread_business"),
            autocommit=True,
            connection_timeout=5,
            ssl_disabled=False
        )
        return True, conn
    except Exception as e:
        return False, str(e)

db_ok, db_conn = get_connection()

def qry(sql, params=None, fetch=False):
    """Run a query. Returns DataFrame if fetch=True, else None."""
    if not db_ok or db_conn is None:
        return pd.DataFrame() if fetch else None
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

def qry_one(sql, params=None):
    df = qry(sql, params, fetch=True)
    if df is not None and not df.empty:
        return df.iloc[0].to_dict()
    return {}

# ══════════════════════════════════════════════════════════════
#  DEMO DATA (fallback when no DB)
# ══════════════════════════════════════════════════════════════
def init_demo():
    if "sources" not in st.session_state:
        st.session_state.sources = [
            {"source_id":1,"source_name":"Dhaka Thread Mills","phone":"01711002233","speciality":"Cotton","address":"Narayanganj","pay_terms":"Cash","notes":""},
            {"source_id":2,"source_name":"Kyoto Filament Corp","phone":"0334556677","speciality":"Silk","address":"Japan","pay_terms":"30 days","notes":""},
        ]
    if "sellers" not in st.session_state:
        st.session_state.sellers = [
            {"seller_id":1,"seller_name":"Rahim Traders","phone":"01811223344","address":"Mirpur, Dhaka","area":"Mirpur","notes":"","is_active":1},
            {"seller_id":2,"seller_name":"Karim Fabrics","phone":"01922334455","address":"Gulshan, Dhaka","area":"Gulshan","notes":"","is_active":1},
        ]
    if "products" not in st.session_state:
        st.session_state.products = [
            {"product_id":1,"product_name":"Red Cotton Thread 40/2","sku_code":"CT-RED-001","barcode":"","category":"Cotton","colour":"Red","spec":"40/2","source_id":1,"buy_price":140.0,"sell_retail":240.0,"sell_wholesale":195.0,"current_stock":620,"low_stock_threshold":50,"unit":"Cone","is_active":1},
            {"product_id":2,"product_name":"Mulberry Silk Thread","sku_code":"SK-MUL-002","barcode":"","category":"Silk","colour":"White","spec":"30D","source_id":2,"buy_price":480.0,"sell_retail":890.0,"sell_wholesale":750.0,"current_stock":180,"low_stock_threshold":20,"unit":"Spool","is_active":1},
            {"product_id":3,"product_name":"Black Polyester Thread","sku_code":"PL-BLK-003","barcode":"","category":"Polyester","colour":"Black","spec":"120D/2","source_id":1,"buy_price":50.0,"sell_retail":110.0,"sell_wholesale":85.0,"current_stock":12,"low_stock_threshold":30,"unit":"Cone","is_active":1},
        ]
    if "seller_products" not in st.session_state:
        st.session_state.seller_products = [
            {"id":1,"seller_id":1,"product_id":1,"assigned_date":"2026-01-01","notes":""},
            {"id":2,"seller_id":1,"product_id":3,"assigned_date":"2026-01-01","notes":""},
            {"id":3,"seller_id":2,"product_id":2,"assigned_date":"2026-01-01","notes":""},
        ]
    if "customers" not in st.session_state:
        st.session_state.customers = [
            {"customer_id":1,"customer_name":"Apex Apparel","phone":"01822334455","address":"Uttara","contact_notes":"Wholesale buyer"},
            {"customer_id":2,"customer_name":"Envoy Outlets","phone":"01911778899","address":"Banani","contact_notes":"Retail buyer"},
        ]
    if "transactions" not in st.session_state:
        st.session_state.transactions = [
            {"transaction_id":1,"transaction_date":"2026-06-04","product_id":1,"product_name":"Red Cotton Thread 40/2","transaction_type":"OUTPUT_SALE","sale_vector":"WHOLESALE","quantity":100,"unit_price":195.0,"discount":500.0,"total_price":19000.0,"customer_id":1,"seller_id":1,"notes":""},
        ]
    if "store_settings" not in st.session_state:
        st.session_state.store_settings = {"store_name":"My Thread Business","owner_name":"","phone":"","address":"","currency":"৳"}

init_demo()

# ══════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════
def get_setting(key):
    if db_ok:
        r = qry_one("SELECT setting_value FROM store_settings WHERE setting_key=%s", (key,))
        return r.get("setting_value", "") if r else ""
    return st.session_state.store_settings.get(key, "")

def save_setting(key, val):
    if db_ok:
        qry("INSERT INTO store_settings (setting_key,setting_value) VALUES(%s,%s) ON DUPLICATE KEY UPDATE setting_value=%s", (key,val,val))
    else:
        st.session_state.store_settings[key] = val

def get_products_list():
    if db_ok:
        return qry("SELECT product_id, product_name, sku_code, category, colour, current_stock, unit, sell_retail, sell_wholesale, low_stock_threshold FROM products WHERE is_active=1 ORDER BY product_name", fetch=True)
    return pd.DataFrame(st.session_state.products)

def get_sellers_list():
    if db_ok:
        return qry("SELECT seller_id, seller_name, phone, area FROM sellers WHERE is_active=1 ORDER BY seller_name", fetch=True)
    return pd.DataFrame(st.session_state.sellers)

def get_customers_list():
    if db_ok:
        return qry("SELECT customer_id, customer_name, phone FROM customers ORDER BY customer_name", fetch=True)
    return pd.DataFrame(st.session_state.customers)

def currency():
    return get_setting("currency") or "৳"

def fmt_money(v):
    try: return f"{currency()}{float(v):,.2f}"
    except: return f"{currency()}0.00"

def today():
    return datetime.date.today().isoformat()

# ══════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════
store_name = get_setting("store_name") or "ThreadTrack Pro"

st.sidebar.markdown(f"""
<div style='padding:8px 0 24px'>
  <div style='font-family:"Playfair Display",serif;font-size:1.4rem;color:#E8A83A;letter-spacing:-0.5px;line-height:1.1'>{store_name}</div>
  <div style='font-family:"IBM Plex Mono",monospace;font-size:0.6rem;color:#C4882A;letter-spacing:3px;margin-top:4px;text-transform:uppercase'>Business Suite</div>
</div>
""", unsafe_allow_html=True)

# Connection status
if db_ok:
    st.sidebar.markdown("<div style='background:#1a2e1a;border:1px solid #2d5a2d;border-radius:6px;padding:8px 12px;font-family:monospace;font-size:0.7rem;color:#7ecf7e;margin-bottom:16px'>● TiDB Connected</div>", unsafe_allow_html=True)
else:
    st.sidebar.markdown("<div style='background:#2e1a1a;border:1px solid #5a2d2d;border-radius:6px;padding:8px 12px;font-family:monospace;font-size:0.7rem;color:#cf7e7e;margin-bottom:16px'>● Demo Mode (no DB)</div>", unsafe_allow_html=True)

PAGES = {
    "📊  Dashboard":        "dashboard",
    "🔍  Smart Search":     "search",
    "🧵  Products":         "products",
    "🏭  Suppliers":        "suppliers",
    "🤝  Sellers":          "sellers",
    "👥  Customers":        "customers",
    "💰  Sales & Stock":    "sales",
    "📈  Reports":          "reports",
    "⚙️  Store Settings":   "settings",
}

choice = st.sidebar.radio("Navigate", list(PAGES.keys()), label_visibility="collapsed")
page = PAGES[choice]

st.sidebar.markdown("---")
st.sidebar.markdown(f"<div style='font-family:monospace;font-size:0.65rem;color:#555'>Today: {today()}</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  PAGE HEADER HELPER
# ══════════════════════════════════════════════════════════════
def page_header(label, title, subtitle=""):
    st.markdown(f"<p style='text-transform:uppercase;letter-spacing:3px;color:#C4882A;font-size:0.72rem;margin-bottom:2px;font-family:monospace'>{label}</p>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='margin-top:0;font-size:2.2rem;margin-bottom:4px'>{title}</h1>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<p style='color:#888;font-size:0.85rem;margin-top:0;margin-bottom:20px;font-family:monospace'>{subtitle}</p>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='margin-bottom:20px'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  1. DASHBOARD
# ══════════════════════════════════════════════════════════════
if page == "dashboard":
    page_header("Overview", "Business Dashboard", "Real-time metrics and alerts")

    # Stats
    if db_ok:
        total_p   = qry_one("SELECT COUNT(*) as c FROM products WHERE is_active=1").get("c",0)
        total_s   = qry_one("SELECT COUNT(*) as c FROM sources").get("c",0)
        total_sel = qry_one("SELECT COUNT(*) as c FROM sellers WHERE is_active=1").get("c",0)
        total_cust= qry_one("SELECT COUNT(*) as c FROM customers").get("c",0)
        low_stk   = qry_one("SELECT COUNT(*) as c FROM products WHERE current_stock <= low_stock_threshold AND is_active=1").get("c",0)
        rev_today = qry_one(f"SELECT COALESCE(SUM(total_price),0) as r FROM transactions WHERE transaction_type='OUTPUT_SALE' AND transaction_date='{today()}'").get("r",0)
        rev_total = qry_one("SELECT COALESCE(SUM(total_price),0) as r FROM transactions WHERE transaction_type='OUTPUT_SALE'").get("r",0)
        stk_val   = qry_one("SELECT COALESCE(SUM(current_stock*buy_price),0) as v FROM products WHERE is_active=1").get("v",0)
    else:
        prods = st.session_state.products
        total_p   = len(prods)
        total_s   = len(st.session_state.sources)
        total_sel = len(st.session_state.sellers)
        total_cust= len(st.session_state.customers)
        low_stk   = sum(1 for p in prods if p["current_stock"] <= p["low_stock_threshold"])
        rev_today = sum(t["total_price"] for t in st.session_state.transactions if t["transaction_type"]=="OUTPUT_SALE" and t["transaction_date"]==today())
        rev_total = sum(t["total_price"] for t in st.session_state.transactions if t["transaction_type"]=="OUTPUT_SALE")
        stk_val   = sum(p["current_stock"]*p["buy_price"] for p in prods)

    c1,c2,c3,c4,c5,c6,c7,c8 = st.columns(8)
    c1.metric("Products",    total_p)
    c2.metric("Suppliers",   total_s)
    c3.metric("Sellers",     total_sel)
    c4.metric("Customers",   total_cust)
    c5.metric("Low Stock ⚠", low_stk)
    c6.metric("Today Sales", fmt_money(rev_today))
    c7.metric("Total Revenue", fmt_money(rev_total))
    c8.metric("Stock Value", fmt_money(stk_val))

    st.markdown("---")

    col1, col2 = st.columns([2,1])

    with col1:
        st.markdown("### Recent Transactions")
        if db_ok:
            recent = qry("SELECT t.transaction_date, t.product_name, t.transaction_type, t.sale_vector, t.quantity, t.total_price, c.customer_name FROM transactions t LEFT JOIN customers c ON c.customer_id=t.customer_id ORDER BY t.created_at DESC LIMIT 10", fetch=True)
        else:
            recent = pd.DataFrame(st.session_state.transactions).sort_values("transaction_id", ascending=False).head(10)
        if recent is not None and not recent.empty:
            st.dataframe(recent, use_container_width=True, hide_index=True)
        else:
            st.info("No transactions yet.")

    with col2:
        st.markdown("### ⚠ Low Stock Alerts")
        if db_ok:
            low_df = qry("SELECT product_name, sku_code, current_stock, low_stock_threshold, unit FROM products WHERE current_stock <= low_stock_threshold AND is_active=1 ORDER BY current_stock ASC LIMIT 10", fetch=True)
        else:
            low_df = pd.DataFrame([p for p in st.session_state.products if p["current_stock"] <= p["low_stock_threshold"]])
        if low_df is not None and not low_df.empty:
            for _, row in low_df.iterrows():
                color = "#c0392b" if row["current_stock"] <= 0 else "#C4882A"
                st.markdown(f"""
                <div class='search-card' style='border-left-color:{color};padding:10px 14px;margin-bottom:8px'>
                  <b style='font-size:0.85rem'>{row['product_name']}</b><br>
                  <span style='font-family:monospace;font-size:0.75rem;color:{color}'>
                    Stock: {row['current_stock']} {row.get('unit','')} &nbsp;|&nbsp; Alert at: {row['low_stock_threshold']}
                  </span>
                </div>""", unsafe_allow_html=True)
        else:
            st.success("All stock levels OK ✓")

# ══════════════════════════════════════════════════════════════
#  2. SMART SEARCH (Universal)
# ══════════════════════════════════════════════════════════════
elif page == "search":
    page_header("Tools", "Smart Search", "Search anything — product, seller, customer, SKU, phone, category")

    q = st.text_input("", placeholder="🔍  Type product name, SKU, seller name, customer name, phone, category...", key="global_q")

    if q and len(q.strip()) >= 1:
        like = f"%{q.strip()}%"
        st.markdown("---")

        # Products
        if db_ok:
            p_res = qry("SELECT product_name, sku_code, category, colour, spec, current_stock, unit, sell_retail, sell_wholesale FROM products WHERE is_active=1 AND (product_name LIKE %s OR sku_code LIKE %s OR barcode LIKE %s OR category LIKE %s OR colour LIKE %s OR spec LIKE %s)", (like,)*6, fetch=True)
        else:
            prods = pd.DataFrame(st.session_state.products)
            p_res = prods[prods.apply(lambda r: any(q.lower() in str(r[c]).lower() for c in ["product_name","sku_code","category","colour","spec"]), axis=1)] if not prods.empty else pd.DataFrame()

        if p_res is not None and not p_res.empty:
            st.markdown(f"#### 🧵 Products — {len(p_res)} found")
            for _, r in p_res.iterrows():
                sc = "🔴" if r["current_stock"]<=0 else ("🟡" if r["current_stock"]<=r.get("low_stock_threshold",10) else "🟢")
                st.markdown(f"""
                <div class='search-card'>
                  <b style='font-size:1rem'>{r['product_name']}</b>
                  <span style='background:#F0EBE3;border-radius:4px;padding:2px 8px;font-family:monospace;font-size:0.72rem;margin-left:8px'>{r.get('sku_code','')}</span>
                  <span style='background:#E8F0E8;border-radius:4px;padding:2px 8px;font-family:monospace;font-size:0.72rem;margin-left:4px;color:#2d5a2d'>{r.get('category','')}</span>
                  <br><span style='font-size:0.8rem;color:#666'>
                    Colour: <b>{r.get('colour','—')}</b> &nbsp;|&nbsp;
                    Stock: <b>{sc} {r['current_stock']} {r.get('unit','')}</b> &nbsp;|&nbsp;
                    Retail: <b>{fmt_money(r['sell_retail'])}</b> &nbsp;|&nbsp;
                    Wholesale: <b>{fmt_money(r['sell_wholesale'])}</b>
                  </span>
                </div>""", unsafe_allow_html=True)

        # Sellers
        if db_ok:
            s_res = qry("SELECT s.seller_name, s.phone, s.area, GROUP_CONCAT(p.product_name SEPARATOR ', ') as products FROM sellers s LEFT JOIN seller_products sp ON sp.seller_id=s.seller_id LEFT JOIN products p ON p.product_id=sp.product_id WHERE s.is_active=1 AND (s.seller_name LIKE %s OR s.phone LIKE %s OR s.area LIKE %s) GROUP BY s.seller_id", (like, like, like), fetch=True)
        else:
            sellers = pd.DataFrame(st.session_state.sellers)
            s_res = sellers[sellers.apply(lambda r: any(q.lower() in str(r[c]).lower() for c in ["seller_name","phone","area"]), axis=1)] if not sellers.empty else pd.DataFrame()

        if s_res is not None and not s_res.empty:
            st.markdown(f"#### 🤝 Sellers — {len(s_res)} found")
            for _, r in s_res.iterrows():
                prods_txt = r.get("products","—") or "—"
                st.markdown(f"""
                <div class='search-card' style='border-left-color:#2d7a4a'>
                  <b style='font-size:1rem'>{r['seller_name']}</b>
                  <br><span style='font-size:0.8rem;color:#666'>
                    📞 {r.get('phone','—')} &nbsp;|&nbsp; 📍 {r.get('area','—')}
                    <br>🧵 Sells: <b>{prods_txt}</b>
                  </span>
                </div>""", unsafe_allow_html=True)

        # Customers
        if db_ok:
            c_res = qry("SELECT c.customer_name, c.phone, c.address, COUNT(t.transaction_id) as total_orders, COALESCE(SUM(t.total_price),0) as total_spent FROM customers c LEFT JOIN transactions t ON t.customer_id=c.customer_id AND t.transaction_type='OUTPUT_SALE' WHERE c.customer_name LIKE %s OR c.phone LIKE %s GROUP BY c.customer_id", (like, like), fetch=True)
        else:
            custs = pd.DataFrame(st.session_state.customers)
            c_res = custs[custs.apply(lambda r: any(q.lower() in str(r[c]).lower() for c in ["customer_name","phone"]), axis=1)] if not custs.empty else pd.DataFrame()

        if c_res is not None and not c_res.empty:
            st.markdown(f"#### 👥 Customers — {len(c_res)} found")
            for _, r in c_res.iterrows():
                orders = r.get("total_orders", "—")
                spent  = fmt_money(r.get("total_spent", 0))
                st.markdown(f"""
                <div class='search-card' style='border-left-color:#1a5f8a'>
                  <b style='font-size:1rem'>{r['customer_name']}</b>
                  <br><span style='font-size:0.8rem;color:#666'>
                    📞 {r.get('phone','—')} &nbsp;|&nbsp; 📍 {r.get('address','—')}
                    <br>📦 Orders: <b>{orders}</b> &nbsp;|&nbsp; 💰 Total Spent: <b>{spent}</b>
                  </span>
                </div>""", unsafe_allow_html=True)

        if (p_res is None or p_res.empty) and (s_res is None or s_res.empty) and (c_res is None or c_res.empty):
            st.warning(f"No results found for **'{q}'**. Try a different keyword.")

    elif q:
        st.info("Keep typing to search...")
    else:
        st.markdown("""
        <div style='background:#ffffff;border:1.5px solid #E0D8CC;border-radius:12px;padding:28px;text-align:center;margin-top:20px'>
          <div style='font-size:2.5rem;margin-bottom:12px'>🔍</div>
          <div style='font-family:"Playfair Display",serif;font-size:1.2rem;color:#333;margin-bottom:8px'>Search Everything</div>
          <div style='font-family:monospace;font-size:0.78rem;color:#888'>
            Product name · SKU code · Barcode · Category · Colour<br>
            Seller name · Seller phone · Area<br>
            Customer name · Customer phone
          </div>
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  3. PRODUCTS
# ══════════════════════════════════════════════════════════════
elif page == "products":
    page_header("Inventory", "Product Catalog", "Manage your thread & yarn database")

    tab1, tab2 = st.tabs(["📋  View Products", "➕  Add Product"])

    with tab1:
        col1, col2, col3 = st.columns([3,1,1])
        search_p = col1.text_input("", placeholder="🔍 Search by name, SKU, colour, category...", key="psearch", label_visibility="collapsed")
        cat_filter = col2.selectbox("Category", ["All","Cotton","Silk","Polyester","Wool","Nylon","Mixed","Other"], label_visibility="collapsed")
        stk_filter = col3.selectbox("Stock", ["All Stock","Low Stock","Out of Stock"], label_visibility="collapsed")

        if db_ok:
            sql = "SELECT p.product_name, p.sku_code, p.category, p.colour, p.spec, s.source_name as supplier, p.buy_price, p.sell_retail, p.sell_wholesale, p.current_stock, p.unit, p.low_stock_threshold FROM products p LEFT JOIN sources s ON s.source_id=p.source_id WHERE p.is_active=1"
            params = []
            if search_p:
                sql += " AND (p.product_name LIKE %s OR p.sku_code LIKE %s OR p.colour LIKE %s OR p.barcode LIKE %s)"
                like = f"%{search_p}%"
                params += [like]*4
            if cat_filter != "All":
                sql += " AND p.category=%s"; params.append(cat_filter)
            if stk_filter == "Low Stock":
                sql += " AND p.current_stock <= p.low_stock_threshold AND p.current_stock > 0"
            elif stk_filter == "Out of Stock":
                sql += " AND p.current_stock <= 0"
            sql += " ORDER BY p.product_name"
            df = qry(sql, params or None, fetch=True)
        else:
            df = pd.DataFrame(st.session_state.products)
            if search_p:
                df = df[df.apply(lambda r: any(search_p.lower() in str(r[c]).lower() for c in ["product_name","sku_code","colour","category"]), axis=1)]
            if cat_filter != "All": df = df[df["category"]==cat_filter]
            if stk_filter == "Low Stock": df = df[df["current_stock"] <= df["low_stock_threshold"]]
            elif stk_filter == "Out of Stock": df = df[df["current_stock"] <= 0]

        if df is not None and not df.empty:
            st.markdown(f"<span style='font-family:monospace;font-size:0.75rem;color:#888'>{len(df)} products found</span>", unsafe_allow_html=True)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No products found.")

    with tab2:
        if db_ok:
            sup_df = qry("SELECT source_id, source_name FROM sources ORDER BY source_name", fetch=True)
            sup_names = list(sup_df["source_name"]) if sup_df is not None and not sup_df.empty else ["—"]
            sup_map   = dict(zip(sup_df["source_name"], sup_df["source_id"])) if sup_df is not None and not sup_df.empty else {}
        else:
            sup_names = [s["source_name"] for s in st.session_state.sources]
            sup_map   = {s["source_name"]:s["source_id"] for s in st.session_state.sources}

        with st.form("prod_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            p_name   = c1.text_input("Product Name *")
            p_sku    = c2.text_input("SKU / Code")
            p_barcode= c1.text_input("Barcode (optional)")
            p_cat    = c2.selectbox("Category", ["Cotton","Silk","Polyester","Wool","Nylon","Mixed","Other"])
            p_colour = c1.text_input("Colour")
            p_spec   = c2.text_input("Specification (e.g. 40/2)")
            p_sup    = c1.selectbox("Supplier", sup_names if sup_names else ["—"])
            p_unit   = c2.selectbox("Unit", ["Cone","Spool","kg","Box","Bundle","Piece","Dozen"])

            c3,c4,c5 = st.columns(3)
            p_buy  = c3.number_input("Buy Price (৳)", min_value=0.0, step=0.5)
            p_sret = c4.number_input("Retail Price (৳)", min_value=0.0, step=0.5)
            p_swhl = c5.number_input("Wholesale Price (৳)", min_value=0.0, step=0.5)

            c6, c7 = st.columns(2)
            p_stock = c6.number_input("Opening Stock", min_value=0, step=1)
            p_low   = c7.number_input("Low Stock Alert At", min_value=1, value=10, step=1)
            p_notes = st.text_area("Notes (optional)")

            if st.form_submit_button("➕ Add Product"):
                if not p_name:
                    st.error("Product name is required.")
                else:
                    sid = sup_map.get(p_sup)
                    if db_ok:
                        qry("INSERT INTO products (product_name,sku_code,barcode,category,colour,spec,source_id,buy_price,sell_retail,sell_wholesale,current_stock,unit,low_stock_threshold) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                            (p_name,p_sku or None,p_barcode or None,p_cat,p_colour or None,p_spec or None,sid,p_buy,p_sret,p_swhl,p_stock,p_unit,p_low))
                    else:
                        nid = max((p["product_id"] for p in st.session_state.products), default=0)+1
                        st.session_state.products.append({"product_id":nid,"product_name":p_name,"sku_code":p_sku,"barcode":p_barcode,"category":p_cat,"colour":p_colour,"spec":p_spec,"source_id":sid,"buy_price":p_buy,"sell_retail":p_sret,"sell_wholesale":p_swhl,"current_stock":p_stock,"low_stock_threshold":p_low,"unit":p_unit,"is_active":1})
                    st.success(f"✓ Product '{p_name}' added successfully!")
                    st.rerun()

# ══════════════════════════════════════════════════════════════
#  4. SUPPLIERS
# ══════════════════════════════════════════════════════════════
elif page == "suppliers":
    page_header("Records", "Suppliers", "Your source / vendor database")

    tab1, tab2 = st.tabs(["📋  View Suppliers", "➕  Add Supplier"])

    with tab1:
        if db_ok:
            df = qry("SELECT source_name, phone, speciality, address, pay_terms, notes, created_at FROM sources ORDER BY source_name", fetch=True)
        else:
            df = pd.DataFrame(st.session_state.sources)
        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No suppliers yet.")

    with tab2:
        with st.form("sup_form", clear_on_submit=True):
            c1,c2 = st.columns(2)
            s_name = c1.text_input("Supplier Name *")
            s_phone= c2.text_input("Phone")
            s_spec = c1.text_input("Speciality (e.g. Cotton, Silk)")
            s_pay  = c2.text_input("Payment Terms (e.g. Cash, 30 days)")
            s_addr = st.text_area("Address")
            s_notes= st.text_area("Notes")
            if st.form_submit_button("➕ Add Supplier"):
                if not s_name:
                    st.error("Supplier name required.")
                else:
                    if db_ok:
                        qry("INSERT INTO sources (source_name,phone,speciality,pay_terms,address,notes) VALUES(%s,%s,%s,%s,%s,%s)",(s_name,s_phone,s_spec,s_pay,s_addr,s_notes))
                    else:
                        nid = max((s["source_id"] for s in st.session_state.sources),default=0)+1
                        st.session_state.sources.append({"source_id":nid,"source_name":s_name,"phone":s_phone,"speciality":s_spec,"address":s_addr,"pay_terms":s_pay,"notes":s_notes})
                    st.success(f"✓ Supplier '{s_name}' added!")
                    st.rerun()

# ══════════════════════════════════════════════════════════════
#  5. SELLERS
# ══════════════════════════════════════════════════════════════
elif page == "sellers":
    page_header("Records", "Sellers", "Register sellers and assign products to them")

    tab1, tab2, tab3 = st.tabs(["📋  View Sellers", "➕  Add Seller", "🔗  Assign Products"])

    with tab1:
        sq = st.text_input("", placeholder="🔍 Search seller by name, phone, area...", key="seller_search", label_visibility="collapsed")
        if db_ok:
            sql = "SELECT s.seller_id, s.seller_name, s.phone, s.area, s.address, GROUP_CONCAT(p.product_name ORDER BY p.product_name SEPARATOR ' | ') as products_selling FROM sellers s LEFT JOIN seller_products sp ON sp.seller_id=s.seller_id LEFT JOIN products p ON p.product_id=sp.product_id WHERE s.is_active=1"
            params = []
            if sq:
                sql += " AND (s.seller_name LIKE %s OR s.phone LIKE %s OR s.area LIKE %s)"
                like = f"%{sq}%"; params=[like,like,like]
            sql += " GROUP BY s.seller_id ORDER BY s.seller_name"
            df = qry(sql, params or None, fetch=True)
        else:
            df = pd.DataFrame(st.session_state.sellers)
            if sq:
                df = df[df.apply(lambda r: any(sq.lower() in str(r[c]).lower() for c in ["seller_name","phone","area"]), axis=1)]

        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Seller detail card
            sel_names = list(df["seller_name"])
            chosen = st.selectbox("View seller detail", ["— Select —"] + sel_names, key="sel_detail")
            if chosen != "— Select —":
                row = df[df["seller_name"]==chosen].iloc[0]
                st.markdown(f"""
                <div class='search-card'>
                  <b style='font-size:1.1rem'>🤝 {row['seller_name']}</b><br>
                  📞 {row.get('phone','—')} &nbsp;|&nbsp; 📍 {row.get('area','—')}<br>
                  <b>Products selling:</b><br>
                  <span style='font-family:monospace;font-size:0.8rem;color:#C4882A'>{row.get('products_selling','None assigned yet')}</span>
                </div>""", unsafe_allow_html=True)

                # Sales history for this seller
                if db_ok:
                    sid_val = int(row["seller_id"])
                    sh = qry(f"SELECT transaction_date, product_name, sale_vector, quantity, total_price FROM transactions WHERE seller_id={sid_val} AND transaction_type='OUTPUT_SALE' ORDER BY transaction_date DESC LIMIT 20", fetch=True)
                    if sh is not None and not sh.empty:
                        st.markdown("**Recent Sales by this Seller:**")
                        st.dataframe(sh, use_container_width=True, hide_index=True)
        else:
            st.info("No sellers found.")

    with tab2:
        with st.form("seller_form", clear_on_submit=True):
            c1,c2 = st.columns(2)
            sl_name  = c1.text_input("Seller Name *")
            sl_phone = c2.text_input("Phone *")
            sl_area  = c1.text_input("Area / Zone (e.g. Mirpur, Uttara)")
            sl_addr  = c2.text_input("Full Address")
            sl_notes = st.text_area("Notes")
            if st.form_submit_button("➕ Register Seller"):
                if not sl_name or not sl_phone:
                    st.error("Name and phone required.")
                else:
                    if db_ok:
                        qry("INSERT INTO sellers (seller_name,phone,area,address,notes) VALUES(%s,%s,%s,%s,%s)",(sl_name,sl_phone,sl_area,sl_addr,sl_notes))
                    else:
                        nid = max((s["seller_id"] for s in st.session_state.sellers),default=0)+1
                        st.session_state.sellers.append({"seller_id":nid,"seller_name":sl_name,"phone":sl_phone,"area":sl_area,"address":sl_addr,"notes":sl_notes,"is_active":1})
                    st.success(f"✓ Seller '{sl_name}' registered!")
                    st.rerun()

    with tab3:
        st.markdown("**Assign which products a seller is selling**")
        sellers_df = get_sellers_list()
        products_df = get_products_list()

        if sellers_df.empty or products_df.empty:
            st.warning("Add sellers and products first.")
        else:
            with st.form("assign_form", clear_on_submit=True):
                c1,c2 = st.columns(2)
                sel_names_list = list(sellers_df["seller_name"])
                prod_names_list = list(products_df["product_name"])
                sel_map  = dict(zip(sellers_df["seller_name"], sellers_df["seller_id"]))
                prod_map = dict(zip(products_df["product_name"], products_df["product_id"]))

                chosen_seller  = c1.selectbox("Select Seller", sel_names_list)
                chosen_products= c2.multiselect("Select Products", prod_names_list)
                assign_notes   = st.text_input("Notes (optional)")

                if st.form_submit_button("🔗 Assign Products to Seller"):
                    if not chosen_products:
                        st.error("Select at least one product.")
                    else:
                        sid = sel_map[chosen_seller]
                        added = 0
                        for pname in chosen_products:
                            pid = prod_map[pname]
                            if db_ok:
                                qry("INSERT IGNORE INTO seller_products (seller_id,product_id,notes) VALUES(%s,%s,%s)",(sid,pid,assign_notes))
                                added += 1
                            else:
                                exists = any(sp["seller_id"]==sid and sp["product_id"]==pid for sp in st.session_state.seller_products)
                                if not exists:
                                    nid = len(st.session_state.seller_products)+1
                                    st.session_state.seller_products.append({"id":nid,"seller_id":sid,"product_id":pid,"assigned_date":today(),"notes":assign_notes})
                                    added += 1
                        st.success(f"✓ Assigned {added} product(s) to {chosen_seller}!")
                        st.rerun()

        # Current assignments table
        st.markdown("**Current Assignments:**")
        if db_ok:
            asgn = qry("SELECT sel.seller_name, sel.phone, p.product_name, p.category, sp.assigned_date FROM seller_products sp JOIN sellers sel ON sel.seller_id=sp.seller_id JOIN products p ON p.product_id=sp.product_id ORDER BY sel.seller_name", fetch=True)
        else:
            rows=[]
            for sp in st.session_state.seller_products:
                sel_ = next((s for s in st.session_state.sellers if s["seller_id"]==sp["seller_id"]),{})
                prd_ = next((p for p in st.session_state.products if p["product_id"]==sp["product_id"]),{})
                rows.append({"seller_name":sel_.get("seller_name",""),"phone":sel_.get("phone",""),"product_name":prd_.get("product_name",""),"category":prd_.get("category",""),"assigned_date":sp.get("assigned_date","")})
            asgn = pd.DataFrame(rows)
        if asgn is not None and not asgn.empty:
            st.dataframe(asgn, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════
#  6. CUSTOMERS
# ══════════════════════════════════════════════════════════════
elif page == "customers":
    page_header("Records", "Customers", "Buyer database with purchase history")

    tab1, tab2 = st.tabs(["📋  View Customers", "➕  Add Customer"])

    with tab1:
        cq = st.text_input("", placeholder="🔍 Search customer by name or phone...", key="csearch", label_visibility="collapsed")
        if db_ok:
            sql = "SELECT c.customer_id, c.customer_name, c.phone, c.address, COUNT(t.transaction_id) as orders, COALESCE(SUM(t.total_price),0) as total_spent FROM customers c LEFT JOIN transactions t ON t.customer_id=c.customer_id AND t.transaction_type='OUTPUT_SALE'"
            params=[]
            if cq:
                sql += " WHERE c.customer_name LIKE %s OR c.phone LIKE %s"
                like=f"%{cq}%"; params=[like,like]
            sql += " GROUP BY c.customer_id ORDER BY total_spent DESC"
            df = qry(sql, params or None, fetch=True)
        else:
            df = pd.DataFrame(st.session_state.customers)
            if cq:
                df = df[df.apply(lambda r: any(cq.lower() in str(r[c]).lower() for c in ["customer_name","phone"]), axis=1)]

        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Customer purchase history
            cust_names = list(df["customer_name"])
            chosen_c = st.selectbox("View purchase history", ["— Select —"]+cust_names, key="cust_hist")
            if chosen_c != "— Select —":
                row = df[df["customer_name"]==chosen_c].iloc[0]
                st.markdown(f"""
                <div class='search-card' style='border-left-color:#1a5f8a'>
                  <b style='font-size:1.1rem'>👥 {row['customer_name']}</b><br>
                  📞 {row.get('phone','—')} &nbsp;|&nbsp; 📍 {row.get('address','—')}<br>
                  📦 Total Orders: <b>{row.get('orders','—')}</b> &nbsp;|&nbsp;
                  💰 Total Spent: <b>{fmt_money(row.get('total_spent',0))}</b>
                </div>""", unsafe_allow_html=True)

                if db_ok:
                    cid_val = int(row["customer_id"])
                    ch = qry(f"SELECT transaction_date, product_name, sale_vector, quantity, unit_price, discount, total_price FROM transactions WHERE customer_id={cid_val} AND transaction_type='OUTPUT_SALE' ORDER BY transaction_date DESC LIMIT 30", fetch=True)
                    if ch is not None and not ch.empty:
                        st.markdown("**Purchase History:**")
                        st.dataframe(ch, use_container_width=True, hide_index=True)
        else:
            st.info("No customers found.")

    with tab2:
        with st.form("cust_form", clear_on_submit=True):
            c1,c2 = st.columns(2)
            cu_name  = c1.text_input("Customer Name *")
            cu_phone = c2.text_input("Phone *")
            cu_addr  = st.text_input("Address")
            cu_notes = st.text_area("Notes / Requirements")
            if st.form_submit_button("➕ Add Customer"):
                if not cu_name or not cu_phone:
                    st.error("Name and phone required.")
                else:
                    if db_ok:
                        qry("INSERT INTO customers (customer_name,phone,address,contact_notes) VALUES(%s,%s,%s,%s)",(cu_name,cu_phone,cu_addr,cu_notes))
                    else:
                        nid = max((c["customer_id"] for c in st.session_state.customers),default=0)+1
                        st.session_state.customers.append({"customer_id":nid,"customer_name":cu_name,"phone":cu_phone,"address":cu_addr,"contact_notes":cu_notes})
                    st.success(f"✓ Customer '{cu_name}' added!")
                    st.rerun()

# ══════════════════════════════════════════════════════════════
#  7. SALES & STOCK
# ══════════════════════════════════════════════════════════════
elif page == "sales":
    page_header("Transactions", "Sales & Stock Management", "Record sales, restock and view transaction history")

    tab1, tab2, tab3 = st.tabs(["💰  Record Sale", "📦  Stock Movement", "📋  Transaction History"])

    products_df = get_products_list()
    customers_df = get_customers_list()
    sellers_df = get_sellers_list()

    prod_names = list(products_df["product_name"]) if not products_df.empty else []
    prod_map = {r["product_name"]:r for _,r in products_df.iterrows()} if not products_df.empty else {}
    cust_names = ["Walk-in (no record)"] + (list(customers_df["customer_name"]) if not customers_df.empty else [])
    cust_map = {"Walk-in (no record)": None}
    if not customers_df.empty:
        for _, r in customers_df.iterrows(): cust_map[r["customer_name"]] = r["customer_id"]
    seller_names = ["— Not linked —"] + (list(sellers_df["seller_name"]) if not sellers_df.empty else [])
    seller_map = {"— Not linked —": None}
    if not sellers_df.empty:
        for _, r in sellers_df.iterrows(): seller_map[r["seller_name"]] = r["seller_id"]

    with tab1:
        if not prod_names:
            st.warning("Add products first before recording sales.")
        else:
            with st.form("sale_form", clear_on_submit=True):
                c1,c2,c3 = st.columns(3)
                sl_prod   = c1.selectbox("Product *", prod_names)
                sl_type   = c2.selectbox("Sale Type", ["RETAIL","WHOLESALE"])
                sl_date   = c3.date_input("Sale Date", value=datetime.date.today())
                c4,c5     = st.columns(2)
                sl_cust   = c4.selectbox("Customer", cust_names)
                sl_seller = c5.selectbox("Linked Seller (optional)", seller_names)

                prod_info = prod_map.get(sl_prod, {})
                default_price = float(prod_info.get("sell_retail",0) if sl_type=="RETAIL" else prod_info.get("sell_wholesale",0))

                c6,c7,c8 = st.columns(3)
                sl_qty   = c6.number_input("Quantity *", min_value=1, step=1)
                sl_price = c7.number_input("Unit Price (৳)", min_value=0.0, value=default_price, step=0.5)
                sl_disc  = c8.number_input("Discount (৳)", min_value=0.0, step=0.5)
                sl_notes = st.text_input("Notes (optional)")

                avail = int(prod_info.get("current_stock",0))
                total = max((sl_qty * sl_price) - sl_disc, 0)
                st.markdown(f"""
                <div style='background:#F0F8F4;border:1px solid #b8dcc8;border-radius:8px;padding:12px 16px;font-family:monospace;font-size:0.82rem'>
                  Available stock: <b style='color:#2d7a4a'>{avail} {prod_info.get('unit','')}</b> &nbsp;|&nbsp;
                  Total: <b style='color:#C4882A;font-size:1rem'>{fmt_money(total)}</b>
                </div>""", unsafe_allow_html=True)

                if st.form_submit_button("✅ Record Sale"):
                    if sl_qty > avail:
                        st.error(f"❌ Not enough stock! Available: {avail}")
                    elif sl_qty <= 0:
                        st.error("Quantity must be at least 1.")
                    else:
                        pid    = int(prod_info.get("product_id",0))
                        cid    = cust_map.get(sl_cust)
                        sel_id = seller_map.get(sl_seller)
                        new_stk = avail - sl_qty
                        if db_ok:
                            qry("INSERT INTO transactions (transaction_date,product_id,product_name,transaction_type,sale_vector,quantity,unit_price,discount,total_price,customer_id,seller_id,notes) VALUES(%s,%s,%s,'OUTPUT_SALE',%s,%s,%s,%s,%s,%s,%s,%s)",
                                (sl_date.isoformat(), pid, sl_prod, sl_type, sl_qty, sl_price, sl_disc, total, cid, sel_id, sl_notes))
                            qry("UPDATE products SET current_stock=%s WHERE product_id=%s",(new_stk, pid))
                        else:
                            for p in st.session_state.products:
                                if p["product_id"]==pid: p["current_stock"]=new_stk
                            nid = max((t["transaction_id"] for t in st.session_state.transactions),default=0)+1
                            st.session_state.transactions.append({"transaction_id":nid,"transaction_date":sl_date.isoformat(),"product_id":pid,"product_name":sl_prod,"transaction_type":"OUTPUT_SALE","sale_vector":sl_type,"quantity":sl_qty,"unit_price":sl_price,"discount":sl_disc,"total_price":total,"customer_id":cid,"seller_id":sel_id,"notes":sl_notes})
                        st.success(f"✓ Sale recorded! Total: {fmt_money(total)} | Remaining stock: {new_stk}")
                        st.rerun()

    with tab2:
        if not prod_names:
            st.warning("Add products first.")
        else:
            with st.form("stock_form", clear_on_submit=True):
                c1,c2 = st.columns(2)
                stk_prod = c1.selectbox("Product *", prod_names, key="stk_prod")
                stk_type = c2.selectbox("Movement Type", ["INPUT_RESTOCK","DAMAGED","RETURN"])
                stk_date = c1.date_input("Date", value=datetime.date.today(), key="stk_date")
                stk_qty  = c2.number_input("Quantity *", min_value=1, step=1, key="stk_qty")
                stk_src  = st.text_input("Source / Reason (e.g. From supplier, Invoice #12)")
                stk_notes= st.text_area("Notes")

                if st.form_submit_button("📦 Save Movement"):
                    prod_info2 = prod_map.get(stk_prod,{})
                    pid2 = int(prod_info2.get("product_id",0))
                    cur_stk = int(prod_info2.get("current_stock",0))
                    new_stk2 = cur_stk + stk_qty if stk_type in ["INPUT_RESTOCK","RETURN"] else max(cur_stk - stk_qty, 0)
                    if db_ok:
                        qry("INSERT INTO transactions (transaction_date,product_id,product_name,transaction_type,sale_vector,quantity,unit_price,discount,total_price,notes) VALUES(%s,%s,%s,%s,'N/A',%s,0,0,0,%s)",
                            (stk_date.isoformat(),pid2,stk_prod,stk_type,stk_qty,f"{stk_src} | {stk_notes}".strip(" |")))
                        qry("UPDATE products SET current_stock=%s WHERE product_id=%s",(new_stk2,pid2))
                    else:
                        for p in st.session_state.products:
                            if p["product_id"]==pid2: p["current_stock"]=new_stk2
                        nid=max((t["transaction_id"] for t in st.session_state.transactions),default=0)+1
                        st.session_state.transactions.append({"transaction_id":nid,"transaction_date":stk_date.isoformat(),"product_id":pid2,"product_name":stk_prod,"transaction_type":stk_type,"sale_vector":"N/A","quantity":stk_qty,"unit_price":0,"discount":0,"total_price":0,"customer_id":None,"seller_id":None,"notes":stk_src})
                    st.success(f"✓ {stk_type} recorded. New stock: {new_stk2}")
                    st.rerun()

    with tab3:
        c1,c2,c3 = st.columns(3)
        hist_type = c1.selectbox("Type", ["All","OUTPUT_SALE","INPUT_RESTOCK","DAMAGED","RETURN"])
        hist_from = c2.date_input("From", value=datetime.date.today() - datetime.timedelta(days=30))
        hist_to   = c3.date_input("To",   value=datetime.date.today())
        hist_q    = st.text_input("", placeholder="🔍 Filter by product or customer name...", label_visibility="collapsed")

        if db_ok:
            sql = "SELECT t.transaction_date, t.product_name, t.transaction_type, t.sale_vector, t.quantity, t.unit_price, t.discount, t.total_price, c.customer_name, s.seller_name, t.notes FROM transactions t LEFT JOIN customers c ON c.customer_id=t.customer_id LEFT JOIN sellers s ON s.seller_id=t.seller_id WHERE t.transaction_date BETWEEN %s AND %s"
            params = [hist_from.isoformat(), hist_to.isoformat()]
            if hist_type != "All":
                sql += " AND t.transaction_type=%s"; params.append(hist_type)
            if hist_q:
                sql += " AND (t.product_name LIKE %s OR c.customer_name LIKE %s)"
                like=f"%{hist_q}%"; params+=[like,like]
            sql += " ORDER BY t.created_at DESC LIMIT 200"
            h_df = qry(sql, params, fetch=True)
        else:
            h_df = pd.DataFrame(st.session_state.transactions)
            if hist_type != "All": h_df = h_df[h_df["transaction_type"]==hist_type]
            if hist_q: h_df = h_df[h_df["product_name"].str.contains(hist_q,case=False,na=False)]

        if h_df is not None and not h_df.empty:
            total_shown = h_df["total_price"].apply(pd.to_numeric, errors="coerce").sum() if "total_price" in h_df else 0
            st.markdown(f"<span style='font-family:monospace;font-size:0.78rem;color:#888'>{len(h_df)} records &nbsp;|&nbsp; Total: <b style='color:#C4882A'>{fmt_money(total_shown)}</b></span>", unsafe_allow_html=True)
            st.dataframe(h_df, use_container_width=True, hide_index=True)
        else:
            st.info("No transactions found for this filter.")

# ══════════════════════════════════════════════════════════════
#  8. REPORTS
# ══════════════════════════════════════════════════════════════
elif page == "reports":
    page_header("Analytics", "Business Reports", "Revenue, profit, top products and more")

    if db_ok:
        # Revenue by type
        rev_df = qry("SELECT sale_vector, COUNT(*) as txn, SUM(total_price) as revenue FROM transactions WHERE transaction_type='OUTPUT_SALE' GROUP BY sale_vector", fetch=True)
        # Top products
        top_df = qry("SELECT product_name, COUNT(*) as sales_count, SUM(quantity) as total_qty, SUM(total_price) as revenue FROM transactions WHERE transaction_type='OUTPUT_SALE' GROUP BY product_name ORDER BY revenue DESC LIMIT 10", fetch=True)
        # Daily sales last 30 days
        daily_df = qry(f"SELECT transaction_date, SUM(total_price) as revenue, COUNT(*) as txn FROM transactions WHERE transaction_type='OUTPUT_SALE' AND transaction_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY) GROUP BY transaction_date ORDER BY transaction_date", fetch=True)
        # Category
        cat_df = qry("SELECT p.category, SUM(t.total_price) as revenue FROM transactions t JOIN products p ON p.product_id=t.product_id WHERE t.transaction_type='OUTPUT_SALE' GROUP BY p.category ORDER BY revenue DESC", fetch=True)
    else:
        txns = pd.DataFrame(st.session_state.transactions)
        sales_txns = txns[txns["transaction_type"]=="OUTPUT_SALE"] if not txns.empty else pd.DataFrame()
        rev_df  = sales_txns.groupby("sale_vector").agg(txn=("transaction_id","count"), revenue=("total_price","sum")).reset_index() if not sales_txns.empty else pd.DataFrame()
        top_df  = sales_txns.groupby("product_name").agg(sales_count=("transaction_id","count"), total_qty=("quantity","sum"), revenue=("total_price","sum")).reset_index().sort_values("revenue",ascending=False).head(10) if not sales_txns.empty else pd.DataFrame()
        daily_df= pd.DataFrame()
        cat_df  = pd.DataFrame()

    c1,c2 = st.columns(2)

    with c1:
        st.markdown("#### Revenue by Sale Type")
        if rev_df is not None and not rev_df.empty:
            fig = px.pie(rev_df, names="sale_vector", values="revenue",
                         color_discrete_sequence=["#C4882A","#E8A83A","#F5D080"],
                         hole=0.4)
            fig.update_layout(paper_bgcolor="white", plot_bgcolor="white", showlegend=True,
                              font_family="Outfit", margin=dict(t=20,b=20,l=20,r=20))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No sales data yet.")

    with c2:
        st.markdown("#### Top 10 Products by Revenue")
        if top_df is not None and not top_df.empty:
            fig2 = px.bar(top_df, x="revenue", y="product_name", orientation="h",
                          color="revenue", color_continuous_scale=["#F5D080","#C4882A"],
                          labels={"revenue":"Revenue","product_name":""})
            fig2.update_layout(paper_bgcolor="white", plot_bgcolor="white",
                               font_family="Outfit", margin=dict(t=10,b=10,l=10,r=10),
                               coloraxis_showscale=False, yaxis={"autorange":"reversed"})
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No sales data yet.")

    if daily_df is not None and not daily_df.empty:
        st.markdown("#### Daily Revenue (Last 30 Days)")
        fig3 = px.line(daily_df, x="transaction_date", y="revenue",
                       markers=True, line_shape="spline",
                       color_discrete_sequence=["#C4882A"])
        fig3.update_layout(paper_bgcolor="white", plot_bgcolor="#FDFBF7",
                           font_family="Outfit", margin=dict(t=10,b=10,l=10,r=10),
                           xaxis_title="", yaxis_title="Revenue (৳)")
        fig3.update_traces(line_width=2.5, marker_size=6)
        st.plotly_chart(fig3, use_container_width=True)

    if top_df is not None and not top_df.empty:
        st.markdown("#### Full Product Performance Table")
        st.dataframe(top_df, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════
#  9. STORE SETTINGS
# ══════════════════════════════════════════════════════════════
elif page == "settings":
    page_header("System", "Store Settings", "Edit your business name and preferences")

    if db_ok:
        raw = qry("SELECT setting_key, setting_value FROM store_settings", fetch=True)
        cfg = dict(zip(raw["setting_key"], raw["setting_value"])) if raw is not None and not raw.empty else {}
    else:
        cfg = st.session_state.store_settings

    with st.form("settings_form"):
        st.markdown("#### Business Information")
        c1,c2 = st.columns(2)
        new_name   = c1.text_input("Store / Business Name",  value=cfg.get("store_name",""))
        new_owner  = c2.text_input("Owner Name",              value=cfg.get("owner_name",""))
        new_phone  = c1.text_input("Business Phone",          value=cfg.get("phone",""))
        new_curr   = c2.text_input("Currency Symbol",         value=cfg.get("currency","৳"))
        new_addr   = st.text_area("Business Address",         value=cfg.get("address",""))

        st.markdown("#### Database Info")
        if db_ok:
            st.success("✅ Connected to TiDB Cloud MySQL")
        else:
            st.error("⚠ Not connected to database. Running in demo mode.")
            st.markdown("""
            **To connect:**
            1. Create free TiDB Cloud account at **tidbcloud.com**
            2. Create a free Serverless cluster
            3. Run `schema.sql` in TiDB SQL editor
            4. Go to Streamlit Cloud → App Settings → Secrets → paste your credentials
            """)

        if st.form_submit_button("💾 Save Settings"):
            updates = {"store_name":new_name,"owner_name":new_owner,"phone":new_phone,"currency":new_curr,"address":new_addr}
            for k,v in updates.items():
                save_setting(k,v)
            st.success("✓ Settings saved! Refresh to see updated store name.")
            st.rerun()

    st.markdown("---")
    st.markdown("#### About ThreadTrack Pro")
    st.markdown("""
    <div style='background:#ffffff;border:1.5px solid #E0D8CC;border-radius:10px;padding:20px;font-size:0.85rem;color:#444'>
    <b>Version:</b> 2.0 &nbsp;|&nbsp; <b>Stack:</b> Python · Streamlit · TiDB Cloud (MySQL) · Plotly<br><br>
    <b>Features:</b> Products · Suppliers · Seller Registration · Seller-Product Assignment ·
    Customer Database · Smart Universal Search · Sales Recording · Stock Management ·
    Revenue Reports · Store Name Customization
    </div>""", unsafe_allow_html=True) 