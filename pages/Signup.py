import streamlit as st
import sqlite3
import re

# --------- Database Functions ---------
def create_usertable():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT, password TEXT)')
    conn.commit()
    conn.close()

def add_userdata(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('INSERT INTO userstable(username,password) VALUES (?,?)', (username, password))
    conn.commit()
    conn.close()

# --------- Validation ---------
def validate_inputs(username, password):
    if len(username.strip()) == 0:
        return "❌ Username cannot be empty"
    if not re.match("^[A-Za-z0-9]+$", username):
        return "❌ Username should only contain letters and numbers (no underscores or special characters)"
    if len(password.strip()) == 0:
        return "❌ Password cannot be empty"
    if len(password) < 6:
        return "❌ Password must be at least 6 characters long"
    return None

# --------- Signup Page UI ---------
st.set_page_config(page_title="Signup", layout="centered")
st.subheader("📝 Signup Page")

new_user = st.text_input("Create Username")
new_pass = st.text_input("Create Password", type="password")

if st.button("Create Account"):
    error_msg = validate_inputs(new_user, new_pass)
    if error_msg:
        st.error(error_msg)
    else:
        create_usertable()
        add_userdata(new_user, new_pass)
        st.success("✅ Account created successfully!")
        st.info("Go to Login Page from sidebar to login.")
