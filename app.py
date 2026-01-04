import streamlit as st
import sqlite3
import base64
from PIL import Image
import io

# 1. Database Setup
def init_db():
    conn = sqlite3.connect('bond_final_v15.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS merchants (name TEXT, code TEXT)')
    c.execute('''CREATE TABLE IF NOT EXISTS products 
                 (merchant TEXT, name TEXT, category TEXT, price REAL, condition TEXT, description TEXT, image_data TEXT, status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS orders (merchant TEXT, product_name TEXT, phone TEXT, address TEXT)''')
    conn.commit()
    return conn

conn = init_db()
c = conn.cursor()

# 2. Image Fix
def img_to_b64(file):
    img = Image.open(file).convert("RGB")
    img.thumbnail((500, 500)) 
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode()

# 3. UI Setup
st.set_page_config(page_title="BOND STORE", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: white; color: black; }
    .header-box { background: black; color: white; padding: 25px; text-align: center; border-radius: 15px; margin-bottom: 20px; }
    .product-card { border: 1px solid #f0f0f0; padding: 20px; border-radius: 15px; margin-bottom: 20px; background: #fafafa; }
    .order-box { border-left: 5px solid #28a745; background: #e9f7ef; padding: 15px; border-radius: 8px; margin-bottom: 10px; }
    [data-testid="stImage"] img { max-height: 280px; object-fit: contain; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="header-box"><h1>BOND.</h1></div>', unsafe_allow_html=True)

tabs = st.tabs(["🛒 STORE", "🏪 MERCHANT", "🛠️ ADMIN"])

# --- 🛒 STORE (الزبون) ---
with tabs[0]:
    cat_list = ["All", "Watches", "Electronics", "Fashion", "Other"]
    selected_cat = st.selectbox("Select Category", cat_list)
    query = "SELECT * FROM products" if selected_cat == "All" else "SELECT * FROM products WHERE category=?"
    params = () if selected_cat == "All" else (selected_cat,)
    c.execute(query, params)
    for i, item in enumerate(c.fetchall()):
        st.markdown('<div class="product-card">', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1.5])
        with col1: st.image(base64.b64decode(item[6]))
        with col2:
            st.title(item[1])
            st.write(f"**Price:** ${item[3]}")
            if item[7] == "Sold Out": st.error("SOLD OUT")
            else:
                with st.expander("BUY NOW"):
                    ph = st.text_input("Phone", key=f"ph_{i}")
                    ad = st.text_area("Address", key=f"ad_{i}")
                    if st.button("Confirm Order", key=f"bt_{i}"):
                        if ph and ad:
                            # بيحفظ اسم التاجر واسم المنتج والبيانات
                            c.execute("INSERT INTO orders VALUES (?,?,?,?)", (item[0], item[1], ph, ad))
                            conn.commit()
                            st.success("Order Sent Successfully!")

# --- 🏪 MERCHANT (التاجر - هيشوف بيانات الزبون هنا) ---
with tabs[1]:
    m_login = st.text_input("Merchant Code", type="password")
    c.execute("SELECT name FROM merchants WHERE code=?", (m_login,))
    auth = c.fetchone()
    if auth:
        st.success(f"Welcome {auth[0]}")
        
        # عرض الطلبات الجديدة (Orders)
        st.subheader("📥 New Orders")
        c.execute("SELECT rowid, product_name, phone, address FROM orders WHERE merchant=?", (auth[0],))
        my_orders = c.fetchall()
        if not my_orders:
            st.info("No orders yet.")
        else:
            for oid, p_name, p_phone, p_addr in my_orders:
                st.markdown(f"""
                <div class="order-box">
                    <b>Product:</b> {p_name}<br>
                    <b>Customer Phone:</b> {p_phone}<br>
                    <b>Address:</b> {p_addr}
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Done / Delete Order {oid}", key=f"del_{oid}"):
                    c.execute("DELETE FROM orders WHERE rowid=?", (oid,))
                    conn.commit()
                    st.rerun()

        st.divider()
        with st.expander("➕ Add Product"):
            with st.form("add_p", clear_on_submit=True):
                n = st.text_input("Name")
                ct = st.selectbox("Category", ["Watches", "Electronics", "Fashion", "Other"])
                pr = st.number_input("Price")
                fl = st.file_uploader("Image")
                if st.form_submit_button("Post"):
                    if n and fl:
                        b64 = img_to_b64(fl)
                        c.execute("INSERT INTO products VALUES (?,?,?,?,?,?,'Available')", (auth[0], n, ct, pr, "", "", b64))
                        conn.commit()
                        st.rerun()

# --- 🛠️ ADMIN ---
with tabs[2]:
    if st.text_input("Admin Password", type="password") == "1515":
        with st.form("reg_m"):
            new_n = st.text_input("Merchant Name")
            new_c = st.text_input("Merchant Code")
            if st.form_submit_button("Register"):
                c.execute("INSERT INTO merchants VALUES (?,?)", (new_n, new_c))
                conn.commit()
                st.success("Merchant Registered!")
