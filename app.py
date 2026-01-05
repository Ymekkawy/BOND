import streamlit as st
import base64

# 1. إعدادات الصفحة وشكل الموبايل
st.set_page_config(page_title="BOND STORE", layout="wide")

st.markdown("""
    <style>
    .main-header { background: black; color: white; padding: 20px; text-align: center; font-size: 30px; border-radius: 0 0 20px 20px; margin-bottom: 20px; }
    .product-card { border: 2px solid #f0f0f0; padding: 15px; border-radius: 20px; margin-bottom: 25px; background: white; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
    .price-tag { font-size: 22px; color: #28a745; font-weight: bold; }
    .stButton > button { width: 100% !important; border-radius: 12px !important; height: 55px !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-header">BOND STORE</div>', unsafe_allow_html=True)

# 2. بيانات التجار والبضاعة (ثابتة هنا عشان متمسحش)
# تقدر تزود تجار وبضاعة براحتك في القوائم دي
MERCHANTS = {
    "1515": "Admin",
    "1010": "Youssef Store",
    "2020": "Ahmed Watch"
}

# قائمة البضاعة (اسم التاجر، اسم المنتج، السعر، لينك الصورة، القسم)
PRODUCTS = [
    {"merchant": "Youssef Store", "name": "BOND Silver Watch", "price": 1200, "img": "https://via.placeholder.com/300", "cat": "Watches", "status": "Available"},
    {"merchant": "Ahmed Watch", "name": "Smart Bracelet", "price": 550, "img": "https://via.placeholder.com/300", "cat": "Electronics", "status": "Available"},
]

t1, t2 = st.tabs(["🛒 SHOP", "🏪 SELLER"])

with t1:
    st.subheader("Explore Products")
    for i, p in enumerate(PRODUCTS):
        st.markdown('<div class="product-card">', unsafe_allow_html=True)
        st.image(p['img'], use_container_width=True)
        st.subheader(p['name'])
        st.markdown(f'<div class="price-tag">{p["price"]} EGP</div>', unsafe_allow_html=True)
        
        with st.expander("ORDER NOW (WhatsApp)"):
            name = st.text_input("Your Name", key=f"n{i}")
            address = st.text_area("Address", key=f"a{i}")
            
            # رسالة الواتساب اللي هتروح للتاجر (حط رقمك مكان 2010xxxxxxxx)
            order_msg = f"New Order from BOND Store:\nProduct: {p['name']}\nCustomer: {name}\nAddress: {address}"
            wa_url = f"https://wa.me/201012345678?text={order_msg.replace(' ', '%20')}"
            
            if st.markdown(f'<a href="{wa_url}" target="_blank"><button style="width:100%; height:50px; background-color:#25D366; color:white; border:none; border-radius:12px; cursor:pointer;">Confirm on WhatsApp</button></a>', unsafe_allow_html=True):
                pass
        st.markdown('</div>', unsafe_allow_html=True)

with t2:
    code = st.text_input("Enter Merchant Code", type="password")
    if code in MERCHANTS:
        st.success(f"Welcome, {MERCHANTS[code]}!")
        st.info("Orders are sent directly to your WhatsApp. Check your messages!")
        # هنا ممكن تعرض لستة البضاعة الخاصة بالتاجر ده بس
        st.write("Your active products:")
        for p in PRODUCTS:
            if p['merchant'] == MERCHANTS[code]:
                st.write(f"- {p['name']} ({p['price']} EGP)")
    elif code:
        st.error("Invalid Code")
