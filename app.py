import streamlit as st
import sqlite3
import base64
from PIL import Image
import io

# 1. إعداد قاعدة بيانات جديدة (v10) لضمان نظافة البيانات
def init_db():
    conn = sqlite3.connect('bond_final_v10.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS merchants (name TEXT, code TEXT)')
    c.execute('''CREATE TABLE IF NOT EXISTS products 
                 (merchant TEXT, name TEXT, category TEXT, price REAL, condition TEXT, description TEXT, image_data TEXT, status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS orders 
                 (merchant TEXT, product_name TEXT, customer_phone TEXT, address TEXT, payment TEXT)''')
    conn.commit()
    return conn

conn = init_db()
c = conn.cursor()

# 2. وظائف معالجة الصور (تصغير الصور للوضوح على الموبايل)
def get_image(base64_str):
    if base64_str:
        try: return base64.b64decode(base64_str)
        except: return None
    return None

def image_to_base64(image_file):
    if image_file:
        img = Image.open(image_file).convert("RGB")
        img.thumbnail((400, 400)) # حجم مثالي للموبايل واللابتوب
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=80)
        return base64.b64encode(buf.getvalue()).decode()
    return ""

# 3. تنسيق الواجهة (Responsive Design)
st.set_page_config(page_title="BOND Store", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: white; color: black; }
    .hero { background: black; padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 20px; }
    .hero h1 { color: white !important; font-size: 40px !important; margin: 0; }
    .card { border: 1px solid #eee; padding: 15px; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.02); }
    /* ضبط حجم الصور تلقائياً */
    [data-testid="stImage"] img {
        max-width: 100%;
        height: auto;
        max-height: 300px;
        object-fit: contain;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

tabs = st.tabs(["🏠 Home", "🛠️ Admin", "🏪 Merchant", "🛒 Store"])

# --- صفحة التاجر (رفع البضاعة) ---
with tabs[2]:
    m_code = st.text_input("Merchant Login", type="password")
    c.execute("SELECT name FROM merchants WHERE code=?", (m_code,))
    auth = c.fetchone()
    if auth:
        st.success(f"Welcome {auth[0]}")
        with st.expander("➕ Post New Item"):
            with st.form("p_form", clear_on_submit=True):
                n = st.text_input("Product Name")
                cat = st.selectbox("Category", ["Watches", "Electronics", "Fashion", "Other"])
                pr = st.number_input("Price ($)")
                cond = st.text_input("Condition (e.g. Brand New)")
                desc = st.text_area("Description")
                file = st.file_uploader("Image")
                if st.form_submit_button("Post"):
                    if n and file:
                        b64 = image_to_base64(file)
                        c.execute("INSERT INTO products VALUES (?,?,?,?,?,?,?,?)", (auth[0], n, cat, pr, cond, desc, b64, 'Available'))
                        conn.commit()
                        st.success("Live!")
        
        # إدارة الـ Sold Out
        st.subheader("Inventory")
        c.execute("SELECT rowid, name, status FROM products WHERE merchant=?", (auth[0],))
        for pid, pname, pstat in c.fetchall():
            c1, c2 = st.columns([3, 1])
            c1.write(f"**{pname}** ({pstat})")
            if pstat != "Sold Out" and c2.button("Mark Sold", key=f"s_{pid}"):
                c.execute("UPDATE products SET status='Sold Out' WHERE rowid=?", (pid,))
                conn.commit()
                st.rerun()

# --- صفحة المتجر (المشتري يختار التصنيف) ---
with tabs[3]:
    st.markdown('<div class="hero"><h1>BOND.</h1></div>', unsafe_allow_html=True)
    # الفلتر اللي طلبته
    f_cat = st.selectbox("🎯 Select Category:", ["All", "Watches", "Electronics", "Fashion", "Other"])
    
    if f_cat == "All":
        c.execute("SELECT * FROM products")
    else:
        c.execute("SELECT * FROM products WHERE category=?", (f_cat,))
    
    for i, item in enumerate(c.fetchall()):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1.5])
        with col1:
            img = get_image(item[6])
            if img: st.image(img)
        with col2:
            st.subheader(item[1])
            st.write(f"**Price:** ${item[3]} | **Condition:** {item[4]}")
            st.info(f"**Description:** {item[5]}")
            if item[7] == "Sold Out":
                st.error("🚫 SOLD OUT")
            else:
                with st.expander("🛒 Buy Now"):
                    addr = st.text_input("Address", key=f"ad_{i}")
                    phone = st.text_input("Phone", key=f"ph_{i}")
                    if st.button("Confirm Order", key=f"b_{i}"):
                        if addr and phone:
                            c.execute("INSERT INTO orders VALUES (?,?,?,?,?)", (item[0], item[1], phone, addr, "Pending"))
                            conn.commit()
                            st.balloons()
                            st.success("Sent to merchant!")
        st.markdown('</div>', unsafe_allow_html=True)

# باقي الأقسام (Home & Admin)
with tabs[0]: st.write("### Welcome to BOND Luxury Marketplace")
with tabs[1]:
    if st.text_input("Admin Access", type="password") == "1515":
        with st.form("admin"):
            n, c_m = st.text_input("Merchant Name"), st.text_input("Code")
            if st.form_submit_button("Add"):
                c.execute("INSERT INTO merchants VALUES (?,?)", (n, c_m))
                conn.commit()
                st.success("Done")
