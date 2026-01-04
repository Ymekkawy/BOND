import streamlit as st
import sqlite3
import base64
from PIL import Image
import io

# 1. Database
def init_db():
    conn = sqlite3.connect('bond_final_fixed_v3.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS merchants (name TEXT, code TEXT)')
    c.execute('''CREATE TABLE IF NOT EXISTS products 
                 (merchant TEXT, name TEXT, category TEXT, price REAL, image_data TEXT, status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS orders (merchant TEXT, product_name TEXT, phone TEXT, address TEXT)''')
    conn.commit()
    return conn

conn = init_db()
c = conn.cursor()

def img_to_b64(file):
    img = Image.open(file).convert("RGB")
    img.thumbnail((600, 600)) 
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return base64.b64encode(buf.getvalue()).decode()

# UI Setup for Mobile
st.set_page_config(page_title="BOND", layout="wide")
st.markdown("""
    <style>
    html, body { font-size: 18px !important; }
    .main-header { background: black; color: white; padding: 20px; text-align: center; font-size: 30px; border-radius: 0 0 20px 20px; margin-bottom: 25px; }
    .product-card { border: 2px solid #f0f0f0; padding: 15px; border-radius: 20px; margin-bottom: 25px; background: white; }
    .price-tag { font-size: 22px !important; color: #28a745; font-weight: bold; }
    .stButton > button { width: 100% !important; border-radius: 10px !important; }
    .sold-out-btn { background-color: #ff4b4b !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-header">BOND STORE</div>', unsafe_allow_html=True)

t1, t2, t3 = st.tabs(["🛒 SHOP", "🏪 SELLER", "🛠️ ADMIN"])

# --- SHOP (الزبون) ---
with t1:
    cat = st.selectbox("Category", ["All", "Watches", "Electronics", "Fashion", "Other"])
    q = "SELECT * FROM products" if cat == "All" else "SELECT * FROM products WHERE category=?"
    p = () if cat == "All" else (cat,)
    c.execute(q, p)
    
    for i, item in enumerate(c.fetchall()):
        st.markdown('<div class="product-card">', unsafe_allow_html=True)
        st.image(base64.b64decode(item[4]), use_container_width=True)
        st.subheader(item[1])
        st.markdown(f'<div class="price-tag">${item[3]}</div>', unsafe_allow_html=True)
        
        if item[5] == "Sold Out":
            st.error("❌ SOLD OUT")
        else:
            with st.expander("ORDER NOW"):
                ph = st.text_input("Phone", key=f"p{i}")
                ad = st.text_area("Address", key=f"a{i}")
                if st.button("CONFIRM ORDER", key=f"b{i}"):
                    if ph and ad:
                        c.execute("INSERT INTO orders VALUES (?,?,?,?)", (item[0], item[1], ph, ad))
                        conn.commit()
                        st.success("Sent!")
        st.markdown('</div>', unsafe_allow_html=True)

# --- SELLER (التاجر - فيها زرار Sold Out) ---
with t2:
    code = st.text_input("Merchant Code", type="password")
    c.execute("SELECT name FROM merchants WHERE code=?", (code,))
    auth = c.fetchone()
    if auth:
        st.header(f"Dashboard: {auth[0]}")
        
        # عرض المنتجات للتحكم فيها
        st.subheader("📦 My Inventory")
        c.execute("SELECT rowid, name, status FROM products WHERE merchant=?", (auth[0],))
        my_items = c.fetchall()
        for rid, name, status in my_items:
            col1, col2 = st.columns([3, 1])
            col1.write(f"**{name}** ({status})")
            if status != "Sold Out":
                if col2.button("Mark Sold Out", key=f"sold_{rid}"):
                    c.execute("UPDATE products SET status='Sold Out' WHERE rowid=?", (rid,))
                    conn.commit()
                    st.rerun()
        
        st.divider()
        st.subheader("📥 Orders")
        c.execute("SELECT rowid, product_name, phone, address FROM orders WHERE merchant=?", (auth[0],))
        for rid, pn, pp, pa in c.fetchall():
            st.info(f"Product: {pn}\nPhone: {pp}\nAddr: {pa}")
            if st.button("Clear Order", key=f"ord_{rid}"):
                c.execute("DELETE FROM orders WHERE rowid=?", (rid,))
                conn.commit()
                st.rerun()
        
        with st.expander("➕ Add Product"):
            with st.form("add"):
                n = st.text_input("Name")
                ct = st.selectbox("Type", ["Watches", "Electronics", "Fashion", "Other"])
                pr = st.number_input("Price")
                img = st.file_uploader("Image")
                if st.form_submit_button("Post"):
                    if n and img:
                        b64 = img_to_b64(img)
                        c.execute("INSERT INTO products VALUES (?,?,?,?,?,'Available')", (auth[0], n, ct, pr, b64))
                        conn.commit()
                        st.rerun()

# --- ADMIN ---
with t3:
    if st.text_input("Admin Password", type="password") == "1515":
        with st.form("adm"):
            m_n = st.text_input("Merchant Name")
            m_c = st.text_input("Merchant Code")
            if st.form_submit_button("ADD"):
                c.execute("INSERT INTO merchants VALUES (?,?)", (m_n, m_c))
                conn.commit()
                st.success("Merchant Registered!")
