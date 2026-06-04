import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Thread Business Manager", layout="wide")
st.title("Thread Business Inventory & Sales (Local)")

def get_connection():
    conn = sqlite3.connect("thread_business.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS sources (source_id INTEGER PRIMARY KEY AUTOINCREMENT, source_name TEXT NOT NULL, phone TEXT);")
    cursor.execute("CREATE TABLE IF NOT EXISTS products (product_id INTEGER PRIMARY KEY AUTOINCREMENT, product_name TEXT NOT NULL, color_code TEXT, source_id INTEGER, unit_price REAL NOT NULL, current_stock INTEGER DEFAULT 0);")
    cursor.execute("CREATE TABLE IF NOT EXISTS transactions (transaction_id INTEGER PRIMARY KEY AUTOINCREMENT, product_id INTEGER, transaction_type TEXT NOT NULL, quantity INTEGER NOT NULL, total_price REAL NOT NULL, transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP);")
    conn.commit()
    conn.close()

def run_query(query, params=None, is_select=False):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params or ())
        if is_select:
            result = cursor.fetchall()
            return pd.DataFrame([dict(row) for row in result])
        conn.commit()
    except Exception as e:
        st.error(f"Database Error: {e}")
    finally:
        cursor.close()
        conn.close()

init_db()

menu = ["Search Inventory", "Add Supplier/Source", "Add Product", "Record Sale/Input"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Search Inventory":
    st.header("🔍 Inventory Search")
    search_query = st.text_input("Search products by name:")
    sql = "SELECT p.product_id, p.product_name, p.color_code, p.unit_price, p.current_stock, s.source_name AS supplier_name FROM products p LEFT JOIN sources s ON p.source_id = s.source_id"
    if search_query:
        sql += " WHERE p.product_name LIKE ?"
        df = run_query(sql, (f"%{search_query}%",), is_select=True)
    else:
        df = run_query(sql, is_select=True)
    if df is not None and not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.write("No products found.")

elif choice == "Add Supplier/Source":
    st.header("🏢 Add Supplier Details")
    with st.form("source_form", clear_on_submit=True):
        name = st.text_input("Supplier / Source Name*")
        phone = st.text_input("Phone Number")
        submitted = st.form_submit_button("Save Supplier")
        if submitted and name:
            run_query("INSERT INTO sources (source_name, phone) VALUES (?, ?)", (name, phone))
            st.success("Supplier saved successfully!")

elif choice == "Add Product":
    st.header("Add Thread Product")
    sources_df = run_query("SELECT source_id, source_name FROM sources", is_select=True)
    if sources_df is not None and not sources_df.empty:
        source_options = {row['source_name']: row['source_id'] for _, row in sources_df.iterrows()}
        with st.form("product_form", clear_on_submit=True):
            p_name = st.text_input("Thread Name*")
            color = st.text_input("Color Code")
            selected_source = st.selectbox("Select Supplier / Source", list(source_options.keys()))
            price = st.number_input("Unit Price", min_value=0.0, step=0.01)
            stock = st.number_input("Initial Stock Quantity", min_value=0, step=1)
            submitted = st.form_submit_button("Save Product")
            if submitted and p_name:
                s_id = source_options[selected_source]
                run_query("INSERT INTO products (product_name, color_code, source_id, unit_price, current_stock) VALUES (?, ?, ?, ?, ?)", (p_name, color, s_id, price, stock))
                st.success("Product saved successfully!")
    else:
        st.warning("Please add a supplier/source first!")

elif choice == "Record Sale/Input":
    st.header("Record Transaction")
    products_df = run_query("SELECT product_id, product_name, current_stock, unit_price FROM products", is_select=True)
    if products_df is not None and not products_df.empty:
        product_options = {f"{row['product_name']} (Stock: {row['current_stock']})": row for _, row in products_df.iterrows()}
        with st.form("txn_form", clear_on_submit=True):
            selected_prod = st.selectbox("Select Product", list(product_options.keys()))
            t_type = st.selectbox("Transaction Type", ["OUTPUT_SALE", "INPUT"])
            qty = st.number_input("Quantity", min_value=1, step=1)
            submitted = st.form_submit_button("Save Transaction")
            if submitted:
                prod = product_options[selected_prod]
                if t_type == "OUTPUT_SALE" and qty > prod['current_stock']:
                    st.error("Not enough stock available!")
                else:
                    new_stock = prod['current_stock'] + qty if t_type == "INPUT" else prod['current_stock'] - qty
                    total = float(prod['unit_price']) * qty
                    run_query("INSERT INTO transactions (product_id, transaction_type, quantity, total_price) VALUES (?, ?, ?, ?)", (prod['product_id'], t_type, qty, total))
                    run_query("UPDATE products SET current_stock = ? WHERE product_id = ?", (new_stock, prod['product_id']))
                    st.success(f"Transaction Recorded! Total: ${total:.2f}")