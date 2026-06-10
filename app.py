import streamlit as st
import mysql.connector

st.write("Testing TiDB connection...")

try:
    conn = mysql.connector.connect(
        host=st.secrets["tidb"]["host"],
        port=st.secrets["tidb"]["port"],
        user=st.secrets["tidb"]["user"],
        password=st.secrets["tidb"]["password"],
        database="thread_business",
        connect_timeout=10
    )
    st.success("Connection successful!")
    st.write("Tables:", conn.cmd_query("SHOW TABLES"))
    conn.close()
except Exception as e:
    st.error(f"Connection failed: {e}")