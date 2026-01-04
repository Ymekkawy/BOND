import streamlit as st
import sqlite3
import base64
from PIL import Image
import io

# 1. قاعدة البيانات
def init_db():
    conn = sqlite3.connect('bond_final_v7.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS merchants (name TEXT, code TEXT)')
    c.execute('''CREATE TABLE IF NOT EXISTS products 
                 (merchant TEXT, name TEXT, category TEXT, price REAL, usage TEXT, description TEXT, image_data TEXT, status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS orders 
                 (merchant TEXT, product_name TEXT, customer_phone TEXT, address TEXT, payment TEXT, delivery_type TEXT)''')
    conn.commit()
    return conn

conn = init_db()
c = conn.cursor()

# 2. وظائف الصور
def get_image(base64_str):
    if base64_str:
        try: return base64.b64decode(base64_str)
        except: return None
    return None

def image_to_base64(image_file):
    if image_file:
        img = Image.open(image_file).convert("RGB")
        img.thumbnail((450, 450))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        return base64.b64encode(buf.getvalue()).decode()
    return ""

# 3. واجهة المستخدم (Responsive Design)
st.set_page_config(page_title="BOND Store", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #000; }
    .hero { background: #000; padding: 30px; border-radius: 20px; text-align: center; color: white; margin-bottom: 20px; }
    .hero h1 { color: #fff !important; font-size: 45px !important; font-weight: 900; }
    .product-card { border: 1px solid #eee; border-radius: 15px; padding: 20px; background: #fff; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.03); }
    .price-tag { color: #28a745; font-size: 24px; font-weight: bold; }
    /* تنسيق الصور للموبايل */
    [data-testid="stImage"] img { border-radius: 12px; max-height: 300px; object-fit: cover; }
    </style>
    """, unsafe_allow_html=True)

tabs = st.tabs(["🏠 Home", "🛠️ Admin", "🏪 Merchant", "🛒 Store"])

# --- 🏠 Home ---
with tabs[0]:
    st.markdown('<div class="hero"><h1>BOND.</h1></div>', unsafe_allow_html=True)
    st.write("### 🔥 New Collection")

# --- 🛠️ Admin ---
with tabs[1]:
    if st.text_input("Access Code", type="password") == "1515":
        with st.form("m_add"):
            n, c_m = st.text_input("Merchant Name"), st.text_input("Login Code")
            if st.form_submit_button("Save"):
                c.execute("INSERT INTO merchants VALUES (?,?)", (n, c_m))
                conn.commit()
                st.success("Merchant Added")

# --- 🏪 Merchant (التاجر يرفع بضاعته) ---
with tabs[2]:
    m_code = st.text_input("Merchant Login", type="password")
    c.execute("SELECT name FROM merchants WHERE code=?", (m_code,))
    auth = c.fetchone()
    if auth:
        st.success(f"Dashboard: {auth[0]}")
        # عرض طلبات الزبائن
        st.subheader("🔔 Customer Requests")
        c.execute("SELECT rowid, product_name, customer_phone, address FROM orders WHERE merchant=?", (auth[0],))
        for oid, pn, ph, ad in c.fetchall():
            with st.expander(f"Order for: {pn}"):
                st.write(f"📞 Phone: {ph} | 📍 Address: {ad}")
                if st.button("Delete Order Info", key=f"d_{oid}"):
                    c.execute("DELETE FROM orders WHERE rowid=?", (oid,))
                    conn.commit()
                    st.rerun()

        st.divider()
        # رفع المنتج بالخانات الكاملة
        with st.expander("➕ Add New Product"):
            with st.form("p_upload"):
                n = st.text_input("Product Name")
                # تصنيفات ثابتة يختار منها التاجر
                ct = st.selectbox("Category", ["Electronics", "Watches", "Fashion", "Sneakers", "Accessories"])
                pr = st.number_input("Price ($)")
                us = st.text_input("Condition (e.g. New)")
                ds = st.text_area("Description")
                fl = st.file_uploader("Image")
                if st.form_submit_button("Post"):
                    if n and fl:
                        b64 = image_to_base64(fl)
                        c.execute("INSERT INTO products VALUES (?,?,?,?,?,?,?,?)", (auth[0], n, ct, pr, us, ds, b64, 'Available'))
                        conn.commit()
                        st.rerun()

        # زرار الـ Sold Out
        c.execute("SELECT rowid, name, status FROM products WHERE merchant=?", (auth[0],))
        for pid, pname, pstat in c.fetchall():
            c1, c2 = st.columns([4, 1])
            c1.write(f"📦 {pname} ({pstat})")
            if pstat != "Sold Out" and c2.button("Sold", key=f"s_{pid}"):
                c.execute("UPDATE products SET status='Sold Out' WHERE rowid=?", (pid,))
                conn.commit()
                st.rerun()

# --- 🛒 Store (هنا الفلتر اللي طلبته للمشتري) ---
with tabs[3]:
    st.write("## 🛍️ Explore Store")
    
    # فلتر التصنيفات للمشتري (الخانات اللي يختار منها)
    category_filter = st.selectbox("🎯 Choose Category to Filter:", 
                                   ["All", "Electronics", "Watches", "Fashion", "Sneakers", "Accessories"])
    
    if category_filter == "All":
        c.execute("SELECT * FROM products")
    else:
        c.execute("SELECT * FROM products WHERE category=?", (category_filter,))
    
    items = c.fetchall()
    if not items:
        st.info("No items in this category yet.")
    
    for i, item in enumerate(items):
        st.markdown('<div class="product-card">', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1.8])
        
        with col1:
            img = get_image(item[6])
            if img: st.image(img, use_container_width=True)
            
        with col2:
            st.title(item[1])
            st.markdown(f'<p class="price-tag">${item[3]}</p>', unsafe_allow_html=True)
            st.write(f"🏷️ **Type:** {item[2]} | ✨ **Status:** {item[4]}")
            st.write(f"📝 **Description:** {item[5]}")
            
            if item[7] == "Sold Out":
                st.error("🚫 SOLD OUT")
            else:
                with st.expander("🛒 Buy - Click here to order"):
                    # خانات المشتري الاختيارية
                    p_meth = st.selectbox("Payment Method", ["Cash", "InstaPay", "Vodafone Cash"], key=f"pm_{i}")
                    d_addr = st.text_input("Delivery Address", key=f"ad_{i}")
                    d_phon = st.text_input("Phone Number", key=f"ph_{i}")
                    if st.button("Confirm Order", key=f"bt_{i}"):
                        if d_addr and d_phon:
                            c.execute("INSERT INTO orders VALUES (?,?,?,?,?,?)", (item[0], item[1], d_phon, d_addr, p_meth, ""))
                            conn.commit()
                            st.balloons()
                            st.success("Order sent to merchant!")
                        else:
                            st.error("Fill address & phone.")
        st.markdown('</div>', unsafe_allow_html=True)
