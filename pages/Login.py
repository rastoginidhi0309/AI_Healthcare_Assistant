import streamlit as st
import sqlite3
import time

# --------- Database Functions ---------
def login_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT, password TEXT)')
    c.execute('SELECT * FROM userstable WHERE username = ? AND password = ?', (username, password))
    data = c.fetchall()
    conn.close()
    return data

# --------- Login Page UI ---------
st.set_page_config(page_title="Login", layout="centered")
st.subheader("🔑 Login Page")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    # ---- Validation for underscore ----
    if "_" in username:
        st.error("❌ Username cannot contain underscores '_'")
    else:
        result = login_user(username, password)
        if result:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.login_time = time.time()  # Store login timestamp
            st.success("✅ Login Successfully!")

            # Redirect to dashboard
            st.switch_page("streamlit_app.py")
        else:
            st.error("❌ Invalid Username or Password")

# ---- Show login success only for 2 minutes ----
if "login_time" in st.session_state:
    elapsed = time.time() - st.session_state.login_time
    if elapsed < 120:  # 120 seconds = 2 minutes
        st.success("✅ Login Successfully!")
    else:
        del st.session_state["login_time"]  
