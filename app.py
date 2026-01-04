import streamlit as st
import sqlite3
import base64
from PIL import Image
import io

# --- 1. إعداد قاعدة البيانات (حفظ دائم) ---
def init_db():
    conn = sqlite3.connect('bond_final_v10.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS merchants (name TEXT, code TEXT)')
    c.execute('''CREATE TABLE IF NOT EXISTS products 
                 (merchant TEXT, name TEXT, category TEXT, price REAL, usage TEXT, description TEXT, image_data TEXT, status TEXT)''')
    conn.commit()
    return conn

conn = init_db()
c = conn.cursor()

# --- 2. وظيفة تحويل وعرض الصور ---
def get_image(base64_str):
    if base64_str:
        try:
            return base64.b64decode(base64_str)
        except:
            return None
    return None

def image_to_base64(image_file):
    if image_file:
        img = Image.open(image_file)
        img.thumbnail((500, 500))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()
    return ""

# --- 3. التصميم والشكل ---
st.set_page_config(page_title="BOND | Marketplace", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #fcfcfc; }
    [data-testid="stMetricValue"] { font-size: 30px; color: #000; }
    .stButton>button { border-radius: 10px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. الأقسام (TABS) ---
# الترتيب ده مهم جداً عشان مطلعش NameError
tabs = st.tabs(["🏠 Home", "🛠️ Developer", "🏪 Merchant", "🛒 Buyer"])

# --- 🏠 واجهة الـ HOME ---
with tabs[0]:
    st.markdown('<div style="background:#000; padding:60px; border-radius:25px; color:#fff; text-align:center;">'
                '<h1 style="font-size:70px; margin:0;">BOND.</h1><p>Luxury Modern Trading</p></div>', unsafe_allow_html=True)
    
    st.write("##")
    c.execute('SELECT COUNT(*) FROM products')
    p_num = c.fetchone()[0]
    st.metric("Total Items Available", p_num)
    
    st.divider()
    st.subheader("Latest Releases")
    c.execute('SELECT * FROM products ORDER BY rowid DESC LIMIT 3')
    for r in c.fetchall():
        col1, col2 = st.columns([1, 3])
        with col1:
            img_data = get_image(r[6])
            if img_data: st.image(img_data, width=150)
        with col2:
            st.write(f"### {r[1]}")
            st.write(f"Price: **${r[3]}** | Status: `{r[7] or 'Available'}`")

# --- 🛠️ واجهة الـ DEVELOPER ---
with tabs[1]:
    st.header("Admin Access")
    if st.text_input("Enter Secret Code", type="password") == "1515":
        with st.form("dev_add"):
            m_n = st.text_input("Merchant Name")
            m_c = st.text_input("Merchant Access Code")
            if st.form_submit_button("Register Merchant"):
                if m_n and m_c:
                    c.execute("INSERT INTO merchants VALUES (?,?)", (m_n, m_c))
                    conn.commit()
                    st.success("Merchant Added!")

# --- 🏪 واجهة الـ MERCHANT (لوحة التاجر) ---
with tabs[2]:
    st.header("Seller Dashboard")
    login = st.text_input("Login with your Code", type="password")
    c.execute("SELECT name FROM merchants WHERE code=?", (login,))
    m_info = c.fetchone()
    
    if m_info:
        st.success(f"Welcome {m_info[0]}")
        
        # إدارة الـ Sold Out
        st.subheader("Your Products")
        c.execute("SELECT rowid, name, status FROM products WHERE merchant=?", (m_info[0],))
        for pid, pname, pstat in c.fetchall():
            c1, c2 = st.columns([3, 1])
            c1.write(f"📦 {pname} - `{pstat}`")
            if pstat != "Sold Out":
                if c2.button(f"Mark Sold", key=f"s_{pid}"):
                    c.execute("UPDATE products SET status='Sold Out' WHERE rowid=?", (pid,))
                    conn.commit()
                    st.rerun()

        st.divider()
        with st.expander("➕ Upload New Product"):
            with st.form("upload_p", clear_on_submit=True):
                name = st.text_input("Product Name*")
                cat = st.selectbox("Category", ["Clothes", "Electronics", "Phones", "Accessories", "Perfumes"])
                price = st.number_input("Price ($)*", min_value=1.0)
                usage = st.text_input("Usage*")
                file = st.file_uploader("Image*", type=['jpg', 'png'])
                if st.form_submit_button("Launch"):
                    if name and file:
                        b64 = image_to_base64(file)
                        c.execute("INSERT INTO products VALUES (?,?,?,?,?,?,?,'Available')", 
                                  (m_info[0], name, cat, price, usage, "", b64))
                        conn.commit()
                        st.success("Live!")
                    else: st.error("Missing Data!")

# --- 🛒 واجهة الـ BUYER (واجهة المشتري المضمونة) ---
with tabs[3]:
    st.header("The Marketplace")
    c.execute("SELECT * FROM products")
    all_p = c.fetchall()
    
    cat_select = st.selectbox("Category Filter", ["All", "Clothes", "Electronics", "Phones", "Accessories", "Perfumes"])
    
    st.write("---")
    
    for i, p in enumerate(all_p):
        if cat_select == "All" or p[2] == cat_select:
            # هنا بنستخدم أسلوب عرض نضيف جداً ومضمون
            with st.container():
                col_img, col_info = st.columns([1, 2])
                
                with col_img:
                    img_bytes = get_image(p[6])
                    if img_bytes:
                        st.image(img_bytes, use_container_width=True)
                    else:
                        st.write("🖼️ No Image")
                
                with col_info:
                    st.title(p[1])
                    st.subheader(f"Price: ${p[3]}")
                    st.write(f"**Seller:** {p[0]} | **Condition:** {p[4]}")
                    
                    if p[7] == "Sold Out":
                        st.error("🚫 SOLD OUT")
                    else:
                        with st.expander("🛒 Buy This Item"):
                            st.text_input("Your Phone", key=f"t_{i}")
                            st.text_input("Address", key=f"a_{i}")
                            if st.button("Confirm Purchase", key=f"b_{i}"):
                                st.balloons()
                                st.success("Ordered!")
            st.write("---")