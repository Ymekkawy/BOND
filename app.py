import streamlit as st
import sqlite3
import base64
from PIL import Image
import io

# 1. Database
def init_db():
    conn = sqlite3.connect('bond_mobile_final.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS merchants (name TEXT, code TEXT)')
    c.execute('''CREATE TABLE IF NOT EXISTS products 
                 (merchant TEXT, name TEXT, category TEXT, price REAL, image_data TEXT, status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS orders (merchant TEXT, product_name TEXT, phone TEXT, address TEXT)''')
    conn.commit()
    return conn

conn = init_db()
c = conn.cursor()

# 2. Image Optimization
def img_to_b64(file):
    img = Image.open(file).convert("RGB")
    img.thumbnail((600, 600)) 
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return base64.b64encode(buf.getvalue()).decode()

# 3. Mobile-First CSS (هنا حل مشكلة الكلام والشكل)
st.set_page_config(page_title="BOND", layout="wide")

st.markdown("""
    <style>
    /* تكبير الخط العام للموبايل */
    html, body, [class*="css"] {
        font-size: 18px !important;
    }
    
    /* ستايل الهيدر */
    .main-header {
        background: black;
        color: white;
        padding: 20px;
        text-align: center;
        font-weight: bold;
        font-size: 30px;
        border-radius: 0 0 20px 20px;
        margin-bottom: 25px;
    }

    /* كارت المنتج - تعديل للموبايل */
    .product-card {
        border: 2px solid #f0f0f0;
        padding: 15px;
        border-radius: 20px;
        margin-bottom: 25px;
        background-color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }

    /* تخلي الكلام واضح وكبير */
    .product-title {
        font-size: 24px !important;
        font-weight: bold;
        color: #111;
        margin-top: 10px;
    }

    .price-tag {
        font-size: 22px !important;
        color: #28a745;
        font-weight: bold;
    }

    /* تكبير أزرار الـ Buy Now للموبايل */
    div.stButton > button {
        width: 100% !important;
        height: 50px !important;
        font-size: 20px !important;
        border-radius: 10px !important;
        background-color: black !important;
        color: white !important;
    }
    
    /* تظبيط التابات للموبايل */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        font-size: 16px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-header">BOND STORE</div>', unsafe_allow_html=True)

t1, t2, t3 = st.tabs(["🛒 SHOP", "🏪 SELLER", "🛠️ ADMIN"])

with t1:
    cat = st.selectbox("Choose Category", ["All", "Watches", "Electronics", "Fashion", "Other"])
    q = "SELECT * FROM products" if cat == "All" else "SELECT * FROM products WHERE category=?"
    p = () if cat == "All" else (cat,)
    c.execute(q, p)
    
    for i, item in enumerate(c.fetchall()):
        st.markdown('<div class="product-card">', unsafe_allow_html=True)
        # الصورة تاخد عرض الشاشة
        st.image(base64.b64decode(item[4]), use_container_width=True)
        st.markdown(f'<div class="product-title">{item[1]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="price-tag">${item[3]}</div>', unsafe_allow_html=True)
        
        if item[5] == "Sold Out":
            st.error("❌ SOLD OUT")
        else:
            with st.expander("👉 CLICK TO ORDER"):
                ph = st.text_input("Your Phone", key=f"p{i}", placeholder="01xxxxxxxxx")
                ad = st.text_area("Your Address", key=f"a{i}", placeholder="Street, Building, Flat...")
                if st.button("CONFIRM ORDER", key=f"b{i}"):
                    if ph and ad:
                        c.execute("INSERT INTO orders VALUES (?,?,?,?)", (item[0], item[1], ph, ad))
                        conn.commit()
                        st.success("✅ Order sent to merchant!")
        st.markdown('</div>', unsafe_allow_html=True)

with t2:
    code = st.text_input("Enter Merchant Code", type="password")
    c.execute("SELECT name FROM merchants WHERE code=?", (code,))
    auth = c.fetchone()
    if auth:
        st.header(f"Orders for {auth[0]}")
        c.execute("SELECT rowid, product_name, phone, address FROM orders WHERE merchant=?", (auth[0],))
        orders = c.fetchall()
        for rid, pn, pp, pa in orders:
            with st.container():
                st.write(f"📦 **{pn}**")
                st.write(f"📞 {pp} | 📍 {pa}")
                if st.button("Complete Order", key=f"d{rid}"):
                    c.execute("DELETE FROM orders WHERE rowid=?", (rid,))
                    conn.commit()
                    st.rerun()
        
        st.divider()
        with st.expander("➕ Add New Product"):
            with st.form("add"):
                n = st.text_input("Product Name")
                ct = st.selectbox("Category", ["Watches", "Electronics", "Fashion", "Other"])
                pr = st.number_input("Price ($)")
                img = st.file_uploader("Upload Image")
                if st.form_submit_button("POST NOW"):
                    if n and img:
                        b64 = img_to_b64(img)
                        c.execute("INSERT INTO products VALUES (?,?,?,?,?,'Available')", (auth[0], n, ct, pr, b64))
                        conn.commit()
                        st.rerun()

with t3:
    if st.text_input("Admin Password", type="password") == "1515":
        with st.form("adm"):
            m_n = st.text_input("Merchant Name")
            m_c = st.text_input("Merchant Code")
            if st.form_submit_button("ADD MERCHANT"):
                c.execute("INSERT INTO merchants VALUES (?,?)", (m_n, m_c))
                conn.commit()
                st.success("Merchant added!")
