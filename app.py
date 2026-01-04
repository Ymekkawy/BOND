import streamlit as st
import sqlite3
import base64
from PIL import Image
import io

# 1. قاعدة بيانات جديدة تماماً لتجنب الـ OperationalError
def init_db():
    # غيرنا الاسم لـ bond_v20 عشان يمسح أي خطأ قديم
    conn = sqlite3.connect('bond_v20.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS merchants (name TEXT, code TEXT)')
    # الجدول ده متظبط عشان يستقبل كل البيانات صح
    c.execute('''CREATE TABLE IF NOT EXISTS products 
                 (merchant TEXT, name TEXT, category TEXT, price REAL, condition TEXT, description TEXT, image_data TEXT, status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS orders (merchant TEXT, product_name TEXT, phone TEXT, address TEXT)''')
    conn.commit()
    return conn

conn = init_db()
c = conn.cursor()

# 2. وظيفة تصغير الصور
def img_to_b64(file):
    img = Image.open(file).convert("RGB")
    img.thumbnail((500, 500)) 
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode()

# 3. ستايل الموقع
st.set_page_config(page_title="BOND STORE", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: white; color: black; }
    .header-box { background: black; color: white; padding: 25px; text-align: center; border-radius: 15px; margin-bottom: 20px; }
    .order-card { border-left: 5px solid #28a745; background: #f0fff4; padding: 15px; border-radius: 8px; margin-bottom: 10px; color: black; }
    .product-card { border: 1px solid #eee; padding: 15px; border-radius: 15px; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="header-box"><h1>BOND.</h1></div>', unsafe_allow_html=True)

tabs = st.tabs(["🛒 STORE", "🏪 MERCHANT", "🛠️ ADMIN"])

# --- 🛒 صفحة المتجر (الزبون) ---
with tabs[0]:
    cats = ["All", "Watches", "Electronics", "Fashion", "Other"]
    sel_cat = st.selectbox("Category", cats)
    
    query = "SELECT * FROM products" if sel_cat == "All" else "SELECT * FROM products WHERE category=?"
    params = () if sel_cat == "All" else (sel_cat,)
    c.execute(query, params)
    
    for i, item in enumerate(c.fetchall()):
        with st.container():
            st.markdown('<div class="product-card">', unsafe_allow_html=True)
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(base64.b64decode(item[6]))
            with col2:
                st.subheader(item[1])
                st.write(f"Price: ${item[3]}")
                if item[7] == "Sold Out": st.error("SOLD OUT")
                else:
                    with st.expander("BUY NOW"):
                        u_phone = st.text_input("Phone", key=f"ph_{i}")
                        u_addr = st.text_area("Address", key=f"ad_{i}")
                        if st.button("Order Now", key=f"btn_{i}"):
                            if u_phone and u_addr:
                                # حفظ الطلب للتاجر
                                c.execute("INSERT INTO orders VALUES (?,?,?,?)", (item[0], item[1], u_phone, u_addr))
                                conn.commit()
                                st.success("Order Sent!")
            st.markdown('</div>', unsafe_allow_html=True)

# --- 🏪 صفحة التاجر (بيانات الزبائن بتظهر هنا) ---
with tabs[1]:
    m_code = st.text_input("Merchant Code", type="password")
    c.execute("SELECT name FROM merchants WHERE code=?", (m_code,))
    auth = c.fetchone()
    if auth:
        st.success(f"Dashboard: {auth[0]}")
        
        # عرض الطلبات (البيانات اللي كنت بتدور عليها)
        st.subheader("📥 Orders Received")
        c.execute("SELECT rowid, product_name, phone, address FROM orders WHERE merchant=?", (auth[0],))
        my_orders = c.fetchall()
        if not my_orders:
            st.info("No orders found.")
        else:
            for rid, p_name, p_phone, p_addr in my_orders:
                st.markdown(f"""
                <div class="order-card">
                    <b>Product:</b> {p_name} <br>
                    <b>Customer Phone:</b> {p_phone} <br>
                    <b>Address:</b> {p_addr}
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Delete Order #{rid}", key=f"del_{rid}"):
                    c.execute("DELETE FROM orders WHERE rowid=?", (rid,))
                    conn.commit()
                    st.rerun()

        st.divider()
        with st.expander("➕ Add Product"):
            with st.form("add_p", clear_on_submit=True):
                n = st.text_input("Product Name")
                ct = st.selectbox("Category", ["Watches", "Electronics", "Fashion", "Other"])
                pr = st.number_input("Price")
                fl = st.file_uploader("Image")
                if st.form_submit_button("Submit"):
                    if n and fl:
                        b64 = img_to_b64(fl)
                        # الخانات هنا متوافقة تماماً مع الجدول الجديد
                        c.execute("INSERT INTO products VALUES (?,?,?,?,?,?,?,?)", (auth[0], n, ct, pr, "New", "", b64, "Available"))
                        conn.commit()
                        st.rerun()

# --- 🛠️ صفحة الـ Admin ---
with tabs[2]:
    if st.text_input("Admin Key", type="password") == "1515":
        with st.form("reg"):
            m_name = st.text_input("Name")
            m_key = st.text_input("Key")
            if st.form_submit_button("Register"):
                c.execute("INSERT INTO merchants VALUES (?,?)", (m_name, m_key))
                conn.commit()
                st.success("Merchant Added!")
