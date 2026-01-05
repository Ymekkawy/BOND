import streamlit as st

# 1. إعدادات الصفحة
st.set_page_config(page_title="BOND STORE", layout="wide")

# --- قائمة البيانات الثابتة (عدلها من هنا عشان تثبت) ---
MERCHANTS_DATA = {
    "1515": {"name": "Youssef (Owner)", "phone": "201012345678"},
}

PRODUCTS = [
    {"m_code": "1515", "name": "Classic Watch", "price": 1500, "img": "https://via.placeholder.com/300"},
]

# CSS الموبايل
st.markdown("""
    <style>
    .main-header { background: black; color: white; padding: 20px; text-align: center; font-size: 30px; border-radius: 0 0 20px 20px; }
    .product-card { border: 2px solid #f0f0f0; padding: 15px; border-radius: 20px; margin-bottom: 25px; background: white; }
    .stButton > button { width: 100% !important; border-radius: 12px !important; height: 50px !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-header">BOND STORE</div>', unsafe_allow_html=True)

t1, t2, t3 = st.tabs(["🛒 SHOP", "🏪 SELLER", "🛠️ ADMIN"])

# --- صفحة المتجر ---
with t1:
    for i, p in enumerate(PRODUCTS):
        merchant = MERCHANTS_DATA.get(p['m_code'], {"name": "Unknown", "phone": "2010"})
        st.markdown('<div class="product-card">', unsafe_allow_html=True)
        st.image(p['img'], use_container_width=True)
        st.subheader(p['name'])
        st.write(f"Price: {p['price']} EGP")
        with st.expander("ORDER NOW"):
            n = st.text_input("Name", key=f"n{i}")
            wa_url = f"https://wa.me/{merchant['phone']}?text=Order:%20{p['name']}"
            st.markdown(f'<a href="{wa_url}" target="_blank"><button style="width:100%;height:45px;background:#25D366;color:white;border:none;border-radius:10px;">WhatsApp Order</button></a>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- صفحة التاجر ---
with t2:
    code = st.text_input("Merchant Code", type="password")
    if code in MERCHANTS_DATA:
        st.success(f"Welcome {MERCHANTS_DATA[code]['name']}")
        st.write("Your items are live!")

# --- صفحة الـ ADMIN (خانات الـ Developer اللي طلبتها) ---
with t3:
    if st.text_input("Dev Pass", type="password") == "1515":
        st.header("Developer Tools")
        
        # خانة إضافة تاجر
        with st.expander("➕ Add New Merchant"):
            m_id = st.text_input("New Merchant Code")
            m_name = st.text_input("Merchant Name")
            m_phone = st.text_input("Phone (start with 20)")
            if st.button("Generate Merchant Code"):
                new_line = f'"{m_id}": {{"name": "{m_name}", "phone": "{m_phone}"}},'
                st.code(new_line, language="python")
                st.info("Copy this line and paste it into MERCHANTS_DATA in GitHub")

        # خانة إضافة منتج
        with st.expander("📦 Add New Product"):
            p_m_code = st.text_input("Merchant Code for Product")
            p_name = st.text_input("Product Name")
            p_price = st.number_input("Price", min_value=0)
            p_img = st.text_input("Image URL")
            if st.button("Generate Product Code"):
                new_p = f'{{"m_code": "{p_m_code}", "name": "{p_name}", "price": {p_price}, "img": "{p_img}"}},'
                st.code(new_p, language="python")
                st.info("Copy this line and paste it into PRODUCTS in GitHub")
