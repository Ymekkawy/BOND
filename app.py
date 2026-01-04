import streamlit as st
import sqlite3
import base64
from PIL import Image
import io

# 1. Database Setup (Final Version)
def init_db():
    conn = sqlite3.connect('bond_final_fixed.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS merchants (name TEXT, code TEXT)')
    c.execute('''CREATE TABLE IF NOT EXISTS products 
                 (merchant TEXT, name TEXT, category TEXT, price REAL, condition TEXT, description TEXT, image_data TEXT, status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS orders (merchant TEXT, product_name TEXT, phone TEXT, address TEXT)''')
    conn.commit()
    return conn

conn = init_db()
c = conn.cursor()

# 2. Image Resizing (Fixes the "Huge Image" issue on mobile)
def img_to_b64(file):
    img = Image.open(file).convert("RGB")
    img.thumbnail((500, 500)) 
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode()

# 3. Clean CSS for Mobile & Desktop
st.set_page_config(page_title="BOND STORE", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: white; color: black; }
    .header-box { background: black; color: white; padding: 25px; text-align: center; border-radius: 15px; margin-bottom: 20px; }
    .header-box h1 { color: white !important; font-size: 40px !important; letter-spacing: 3px; margin: 0; }
    .product-card { border: 1px solid #f0f0f0; padding: 20px; border-radius: 15px; margin-bottom: 20px; background: #fafafa; }
    [data-testid="stImage"] img { max-height: 280px; object-fit: contain; border-radius: 10px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="header-box"><h1>BOND.</h1></div>', unsafe_allow_html=True)

# Important: Tabs order
tabs = st.tabs(["🛒 STORE", "🏪 MERCHANT", "🛠️ ADMIN"])

# --- 🛒 STORE (The Buyer's View) ---
with tabs[0]:
    cat_list = ["All", "Watches", "Electronics", "Fashion", "Other"]
    selected_cat = st.selectbox("Select Category", cat_list)
    
    if selected_cat == "All":
        c.execute("SELECT * FROM products")
    else:
        c.execute("SELECT * FROM products WHERE category=?", (selected_cat,))
    
    items = c.fetchall()
    for i, item in enumerate(items):
        st.markdown('<div class="product-card">', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1.5])
        with col1:
            st.image(base64.b64decode(item[6]))
        with col2:
            st.title(item[1])
            st.write(f"**Price:** ${item[3]} | **Condition:** {item[4]}")
            st.write(f"**Details:** {item[5]}")
            if item[7] == "Sold Out": st.error("SOLD OUT")
            else:
                with st.expander("BUY NOW"):
                    ph = st.text_input("Phone", key=f"ph_{i}")
                    ad = st.text_area("Address", key=f"ad_{i}")
                    if st.button("Confirm Order", key=f"bt_{i}"):
                        if ph and ad:
                            c.execute("INSERT INTO orders VALUES (?,?,?,?)", (item[0], item[1], ph, ad))
                            conn.commit()
                            st.success("Order Sent!")
        st.markdown('</div>', unsafe_allow_html=True)

# --- 🏪 MERCHANT (The Seller's View) ---
with tabs[1]:
    st.subheader("Merchant Portal")
    m_login = st.text_input("Enter Merchant Code", type="password")
    c.execute("SELECT name FROM merchants WHERE code=?", (m_login,))
    auth = c.fetchone()
    if auth:
        st.success(f"Log in successful: {auth[0]}")
        with st.expander("➕ Add New Product"):
            with st.form("add_p", clear_on_submit=True):
                name = st.text_input("Name")
                category = st.selectbox("Category", ["Watches", "Electronics", "Fashion", "Other"])
                price = st.number_input("Price ($)")
                cond = st.text_input("Condition")
                desc = st.text_area("Description")
                file = st.file_uploader("Image")
                if st.form_submit_button("Post Product"):
                    if name and file:
                        img_str = img_to_b64(file)
                        c.execute("INSERT INTO products VALUES (?,?,?,?,?,?,?,'Available')", (auth[0], name, category, price, cond, desc, img_str))
                        conn.commit()
                        st.rerun()
        
        # Display Merchant Inventory
        st.divider()
        c.execute("SELECT rowid, name, status FROM products WHERE merchant=?", (auth[0],))
        for rid, n, s in c.fetchall():
            c1, c2 = st.columns([4, 1])
            c1.write(f"**{n}** ({s})")
            if s != "Sold Out" and c2.button("Mark Sold Out", key=f"s_{rid}"):
                c.execute("UPDATE products SET status='Sold Out' WHERE rowid=?", (rid,))
                conn.commit()
                st.rerun()

# --- 🛠️ ADMIN (Registration View) ---
with tabs[2]:
    st.subheader("Admin Control")
    if st.text_input("Admin Password", type="password", key="admin_pass") == "1515":
        with st.form("reg_m"):
            new_n = st.text_input("Merchant Name")
            new_c = st.text_input("Merchant Code")
            if st.form_submit_button("Register Merchant"):
                if new_n and new_c:
                    c.execute("INSERT INTO merchants VALUES (?,?)", (new_n, new_c))
                    conn.commit()
                    st.success(f"Merchant {new_n} added!")
