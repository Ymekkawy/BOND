import streamlit as st
import sqlite3
import base64
from PIL import Image
import io
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. إعداد واجهة الموقع والاسم (عشان جوجل بحث)
st.set_page_config(page_title="BOND STORE - Online Shopping", layout="wide")

# 2. الربط بجوجل شيت (للأوردرات عشان متمسحش)
conn_gsheet = st.connection("gsheets", type=GSheetsConnection)

# 3. قاعدة بيانات محلية (للمنتجات والتجار)
def init_db():
    conn = sqlite3.connect('bond_final_stable.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS merchants (name TEXT, code TEXT)')
    c.execute('''CREATE TABLE IF NOT EXISTS products 
                 (merchant TEXT, name TEXT, category TEXT, price REAL, image_data TEXT, status TEXT)''')
    conn.commit()
    return conn

db_conn = init_db()
cursor = db_conn.cursor()

# 4. دوال مساعدة
def img_to_b64(file):
    img = Image.open(file).convert("RGB")
    img.thumbnail((500, 500)) 
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode()

# CSS الموبايل الاحترافي
st.markdown("""
    <style>
    html, body { font-size: 18px !important; }
    .main-header { background: black; color: white; padding: 20px; text-align: center; font-size: 30px; border-radius: 0 0 20px 20px; margin-bottom: 25px; }
    .product-card { border: 2px solid #f0f0f0; padding: 15px; border-radius: 20px; margin-bottom: 25px; background: white; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
    .price-tag { font-size: 22px !important; color: #28a745; font-weight: bold; }
    .stButton > button { width: 100% !important; border-radius: 12px !important; height: 50px !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-header">BOND STORE</div>', unsafe_allow_html=True)

t1, t2, t3 = st.tabs(["🛒 SHOP", "🏪 SELLER", "🛠️ ADMIN"])

# --- صفحة المتجر (الزبون) ---
with t1:
    cat = st.selectbox("Category", ["All", "Watches", "Electronics", "Fashion", "Other"])
    q = "SELECT * FROM products" if cat == "All" else "SELECT * FROM products WHERE category=?"
    p = () if cat == "All" else (cat,)
    cursor.execute(q, p)
    
    for i, item in enumerate(cursor.fetchall()):
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
                        # حفظ الأوردر في جوجل شيت فوراً
                        new_data = pd.DataFrame([{"merchant": item[0], "product_name": item[1], "phone": ph, "address": ad}])
                        try:
                            # جلب البيانات القديمة ودمجها مع الجديدة
                            existing_df = conn_gsheet.read(worksheet="Sheet1")
                            updated_df = pd.concat([existing_df, new_data], ignore_index=True)
                            conn_gsheet.update(worksheet="Sheet1", data=updated_df)
                            st.success("✅ Order Sent & Saved in Sheets!")
                        except:
                            st.warning("Order sent! (Connect GSheets in Settings to save forever)")
        st.markdown('</div>', unsafe_allow_html=True)

# --- صفحة التاجر (SELLER) ---
with t2:
    code = st.text_input("Merchant Code", type="password")
    cursor.execute("SELECT name FROM merchants WHERE code=?", (code,))
    auth = cursor.fetchone()
    if auth:
        st.header(f"Dashboard: {auth[0]}")
        
        # عرض الطلبات من جوجل شيت
        st.subheader("📥 Orders (from Google Sheets)")
        try:
            orders_df = conn_gsheet.read(worksheet="Sheet1")
            my_orders = orders_df[orders_df['merchant'] == auth[0]]
            if my_orders.empty:
                st.info("No orders yet.")
            else:
                st.dataframe(my_orders)
        except:
            st.info("Waiting for GSheets connection...")

        # التحكم في الـ Sold Out
        st.subheader("📦 Inventory")
        cursor.execute("SELECT rowid, name, status FROM products WHERE merchant=?", (auth[0],))
        for rid, name, status in cursor.fetchall():
            col1, col2 = st.columns([3, 1])
            col1.write(f"{name} - {status}")
            if status != "Sold Out":
                if col2.button("Sold Out", key=f"s{rid}"):
                    cursor.execute("UPDATE products SET status='Sold Out' WHERE rowid=?", (rid,))
                    db_conn.commit()
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
                        cursor.execute("INSERT INTO products VALUES (?,?,?,?,?,'Available')", (auth[0], n, ct, pr, b64))
                        db_conn.commit()
                        st.rerun()

# --- صفحة الـ ADMIN ---
with t3:
    if st.text_input("Admin Key", type="password") == "1515":
        with st.form("adm"):
            m_n = st.text_input("Merchant Name")
            m_c = st.text_input("Merchant Code")
            if st.form_submit_button("Register"):
                cursor.execute("INSERT INTO merchants VALUES (?,?)", (m_n, m_c))
                db_conn.commit()
                st.success("Merchant Added!")
