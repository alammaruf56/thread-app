import streamlit as st
import mysql.connector
import pandas as pd
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
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght=300;400;500;600;700&family=Playfair+Display:wght=400;600;700&family=IBM+Plex+Mono:wght=300;400;500&display=swap');

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
    "   Dashboard":        "dashboard",
    "🔍  Smart Search":     "search",
    "    Products":         "products",
    "    Suppliers":        "suppliers",
    "    Sellers":          "sellers",
    "   Customers":        "customers",
    "  Sales & Stock":    "sales",
    "  Reports":          "reports",
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
            recent = qry("SELECT t.transaction_date, t.product_name, t.transaction_type, t.sale_vector, t.quantity, t.total_price, c.customer_name FROM transactions t LEFT JOIN customers c ON c.customer_id=t.customer_id ORDER BY t.transaction_date DESC LIMIT 10", fetch=True)
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
        cat_filter = col2.text_input("Filter Category", placeholder="All")
        stk_filter = col3.selectbox("Stock", ["All Stock","Low Stock","Out of Stock"], label_visibility="collapsed")

        if db_ok:
            sql = "SELECT p.product_name, p.sku_code, p.category, p.colour, p.spec, s.source_name as supplier, p.buy_price, p.sell_retail, p.sell_wholesale, p.current_stock, p.unit, p.low_stock_threshold FROM products p LEFT JOIN sources s ON s.source_id=p.source_id WHERE p.is_active=1"
            params = []
            if search_p:
                sql += " AND (p.product_name LIKE %s OR p.sku_code LIKE %s OR p.colour LIKE %s OR p.barcode LIKE %s)"
                like = f"%{search_p}%"
                params += [like]*4
            if cat_filter and cat_filter != "All":
                sql += " AND p.category LIKE %s"
                params.append(f"%{cat_filter}%")
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
            if cat_filter and cat_filter != "All": 
                df = df[df["category"].str.lower().str.contains(cat_filter.lower(), na=False)]
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
            
            p_cat    = c2.text_input("Category")
            
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
                        qry("INSERT INTO products (product_name,sku_code,barcode,category,colour,spec,source_id,buy_price,sell_retail,sell_wholesale,current_stock,low_stock_threshold,unit) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                            (p_name,p_sku or None,p_barcode or None,p_cat,p_colour or None,p_spec or None,sid,p_buy,p_sret,p_swhl,p_stock,p_low,p_unit))
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
            df = qry("SELECT source_name, phone, speciality, address, pay_terms, notes FROM sources ORDER BY source_name", fetch=True)
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
            s_spec = c1.text_input("Speciality")
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
    page_header("Records", "Sellers", "Manage dynamic distribution loops and fields")
    
    tab1, tab2 = st.tabs(["📋 View Sellers", "➕ Add Seller"])
    
    with tab1:
        if db_ok:
            df = qry("SELECT seller_name, phone, area, address, notes FROM sellers WHERE is_active=1 ORDER BY seller_name", fetch=True)
        else:
            df = pd.DataFrame(st.session_state.sellers)
        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No active sellers enrolled yet.")

    with tab2:
        with st.form("seller_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            sel_name = c1.text_input("Seller / Hub Name *")
            sel_phone = c2.text_input("Contact Number")
            sel_area = c1.text_input("Distribution Territory / Area")
            sel_addr = st.text_area("Full Address")
            sel_notes = st.text_area("Internal Assignment Notes")
            
            if st.form_submit_button("➕ Register Seller"):
                if not sel_name:
                    st.error("Seller name is structurally mandatory.")
                else:
                    if db_ok:
                        qry("INSERT INTO sellers (seller_name, phone, area, address, notes, is_active) VALUES (%s, %s, %s, %s, %s, 1)",
                            (sel_name, sel_phone, sel_area, sel_addr, sel_notes))
                    else:
                        nid = max((s["seller_id"] for s in st.session_state.sellers), default=0) + 1
                        st.session_state.sellers.append({"seller_id": nid, "seller_name": sel_name, "phone": sel_phone, "address": sel_addr, "area": sel_area, "notes": sel_notes, "is_active": 1})
                    st.success(f"✓ Seller Unit '{sel_name}' registered successfully.")
                    st.rerun()

# ══════════════════════════════════════════════════════════════
#  6. CUSTOMERS
# ══════════════════════════════════════════════════════════════
elif page == "customers":
    page_header("Records", "Customer Directory", "Customer profiles and interactions log")
    
    tab1, tab2 = st.tabs(["📋 View Directory", "➕ Add Client Profile"])
    
    with tab1:
        if db_ok:
            df = qry("SELECT customer_name, phone, address, contact_notes FROM customers ORDER BY customer_name", fetch=True)
        else:
            df = pd.DataFrame(st.session_state.customers)
        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No customers found.")

    with tab2:
        with st.form("cust_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            cust_name = c1.text_input("Customer Entity Name *")
            cust_phone = c2.text_input("Primary Phone")
            cust_addr = st.text_area("Billing/Delivery Address")
            cust_notes = st.text_area("Category Details (Wholesale/Retail preferences)")
            
            if st.form_submit_button("➕ Save Profile"):
                if not cust_name:
                    st.error("Customer name cannot be empty.")
                else:
                    if db_ok:
                        qry("INSERT INTO customers (customer_name, phone, address, contact_notes) VALUES (%s, %s, %s, %s)",
                            (cust_name, cust_phone, cust_addr, cust_notes))
                    else:
                        nid = max((c["customer_id"] for c in st.session_state.customers), default=0) + 1
                        st.session_state.customers.append({"customer_id": nid, "customer_name": cust_name, "phone": cust_phone, "address": cust_addr, "contact_notes": cust_notes})
                    st.success(f"✓ Profile for '{cust_name}' created.")
                    st.rerun()

# ══════════════════════════════════════════════════════════════
#  7. SALES & STOCK
# ══════════════════════════════════════════════════════════════
elif page == "sales":
    page_header("Operations", "Dispatches & Inventory Inbound", "Post stock reductions or supply orders")
    
    col_p = get_products_list()
    col_s = get_sellers_list()
    col_c = get_customers_list()
    
    if col_p.empty:
        st.warning("Please configure products first before logging sales transactions.")
    else:
        with st.form("transaction_form", clear_on_submit=True):
            t_type = st.selectbox("Transaction Flow Type", ["OUTPUT_SALE", "INPUT_RESTOCK", "DAMAGED", "RETURN"])
            
            c1, c2 = st.columns(2)
            p_choice = c1.selectbox("Target Product Thread", col_p["product_name"].tolist())
            p_row = col_p[col_p["product_name"] == p_choice].iloc[0]
            
            vector = c2.selectbox("Sale Vector Format", ["RETAIL", "WHOLESALE", "N/A"])
            qty_input = c1.number_input("Quantity Volumetric Unit", min_value=1, step=1)
            
            fallback_price = float(p_row["sell_wholesale"] if vector == "WHOLESALE" else p_row["sell_retail"])
            u_price = c2.number_input("Custom Execution Rate (Per Unit)", min_value=0.0, value=fallback_price, step=0.5)
            discount = c1.number_input("Discount Deductions Applied", min_value=0.0, step=1.0)
            
            c_choice = c2.selectbox("Assigned Buyer Client", ["None"] + (col_c["customer_name"].tolist() if not col_c.empty else []))
            s_choice = c1.selectbox("Fulfillment Sales Representative", ["None"] + (col_s["seller_name"].tolist() if not col_s.empty else []))
            
            t_notes = st.text_area("Transaction Context Signature")
            
            if st.form_submit_button("💾 Dispatch Order and Synchronize Inventories"):
                tot_price = (qty_input * u_price) - discount
                cid = None if c_choice == "None" else int(col_c[col_c["customer_name"] == c_choice].iloc[0]["customer_id"])
                sid = None if s_choice == "None" else int(col_s[col_s["seller_name"] == s_choice].iloc[0]["seller_id"])
                
                # Check Stock constraints dynamically
                if t_type in ["OUTPUT_SALE", "DAMAGED"] and int(p_row["current_stock"]) < qty_input:
                    st.error(f"Insufficient stock allocation available. Present balance: {p_row['current_stock']}")
                else:
                    if t_type in ["INPUT_RESTOCK", "RETURN"]:
                        new_stock = int(p_row["current_stock"]) + qty_input
                    else:
                        new_stock = int(p_row["current_stock"]) - qty_input
                    
                    if db_ok:
                        qry("INSERT INTO transactions (transaction_date, product_id, product_name, transaction_type, sale_vector, quantity, unit_price, discount, total_price, customer_id, seller_id, notes) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                            (today(), int(p_row["product_id"]), p_choice, t_type, vector, qty_input, u_price, discount, tot_price, cid, sid, t_notes))
                        qry("UPDATE products SET current_stock=%s WHERE product_id=%s", (new_stock, int(p_row["product_id"])))
                    else:
                        nid = max((t["transaction_id"] for t in st.session_state.transactions), default=0) + 1
                        st.session_state.transactions.append({
                            "transaction_id": nid, "transaction_date": today(), "product_id": int(p_row["product_id"]), "product_name": p_choice,
                            "transaction_type": t_type, "sale_vector": vector, "quantity": qty_input, "unit_price": u_price, "discount": discount,
                            "total_price": tot_price, "customer_id": cid, "seller_id": sid, "notes": t_notes
                        })
                        for p in st.session_state.products:
                            if p["product_id"] == p_row["product_id"]:
                                p["current_stock"] = new_stock
                                
                    st.success(f"✓ Transaction tracked correctly. Internal adjustments synchronized ({new_stock} remaining units).")
                    st.rerun()

# ══════════════════════════════════════════════════════════════
#  8. REPORTS
# ══════════════════════════════════════════════════════════════
elif page == "reports":
    page_header("Analytics", "Performance Intelligence Reports", "A summary analysis of commercial performance metrics")
    
    if db_ok:
        tx_df = qry("SELECT * FROM transactions", fetch=True)
    else:
        tx_df = pd.DataFrame(st.session_state.transactions)
        
    if tx_df.empty:
        st.info("Insufficient volumetric tracking logs to populate graphical visualizations.")
    else:
        sales_only = tx_df[tx_df["transaction_type"] == "OUTPUT_SALE"]
        
        if not sales_only.empty:
            c1, c2 = st.columns(2)
            
            with c1:
                st.markdown("### Structural Volume by Thread Class")
                prod_sales = sales_only.groupby("product_name")["total_price"].sum().reset_index()
                st.bar_chart(data=prod_sales, x="product_name", y="total_price")
                
            with c2:
                st.markdown("### Aggregated Revenue Time Series")
                time_sales = sales_only.groupby("transaction_date")["total_price"].sum().reset_index()
                st.line_chart(data=time_sales, x="transaction_date", y="total_price")
        else:
            st.info("Log sales info to display comparative dashboards.")

# ══════════════════════════════════════════════════════════════
#  9. STORE SETTINGS
# ══════════════════════════════════════════════════════════════
elif page == "settings":
    page_header("Configuration", "Suite Controls & Identity", "Calibrate framework configurations and layout options")
    
    with st.form("settings_form"):
        s_name = st.text_input("Business Application Brand Title", value=get_setting("store_name") or "ThreadTrack Pro")
        s_owner = st.text_input("Proprietor Management Authority Identity Name", value=get_setting("owner_name"))
        s_curr = st.selectbox("Operational ISO Financial Denomination Character Set", ["৳", "$", "€", "£", "₹"], index=0)
        
        if st.form_submit_button("⚡ Re-index Metadata Rules"):
            save_setting("store_name", s_name)
            save_setting("owner_name", s_owner)
            save_setting("currency", s_curr)
            st.success("✓ Platform settings successfully saved configuration changes.")
            st.rerun()