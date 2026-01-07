import streamlit as st
from supabase import create_client
import base64

# --- 1. CONNECTION ---
SUPABASE_URL = "https://lkzyubzuunlnkyaqqwzi.supabase.co"
SUPABASE_KEY = "sb_publishable_GrCY2EOqAWGdDZUteIvEzA_O_D0TxQ3" 

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except:
    pass

st.set_page_config(page_title="BOND STORE", layout="wide")

# CSS لتنظيم الصور والطلبات
st.markdown("""
    <style>
    .product-img { width: 100%; height: 200px; object-fit: cover; border-radius: 10px; }
    .order-card { border: 2px solid #eee; padding: 15px; border-radius: 10px; margin-bottom: 10px; background: #fff; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 style="text-align:center; background:black; color:white; padding:15px; border-radius:15px;">BOND STORE</h1>', unsafe_allow_html=True)

menu = st.radio("", ["🛒 SHOP", "🏪 SELLER LOGIN", "🛠️ ADMIN"], horizontal=True)

# --- 2. SHOP (العميل يطلب هنا) ---
if menu == "🛒 SHOP":
    items = supabase.table("products").select("*").execute().data
    if not items: st.info("Store is empty.")
    else:
        cols = st.columns(3)
        for idx, p in enumerate(items):
            with cols[idx % 3]:
                st.markdown('<div style="border:1px solid #eee; padding:10px; border-radius:10px;">', unsafe_allow_html=True)
                if p.get('image'):
                    st.markdown(f'<img src="data:image/png;base64,{p["image"]}" class="product-img">', unsafe_allow_html=True)
                st.subheader(p['name'])
                st.write(f"Price: {p['price']} EGP")
                
                if p.get('status') == "Sold Out":
                    st.error("SOLD OUT")
                else:
                    # زرار الطلب يفتح فورم بيانات
                    with st.expander(f"Buy {p['name']}"):
                        with st.form(f"order_{p['id']}"):
                            c_name = st.text_input("Full Name")
                            c_addr = st.text_input("Address")
                            c_phone = st.text_input("Phone Number")
                            c_pay = st.selectbox("Payment Method", ["Cash on Delivery", "InstaPay", "Vodafone Cash"])
                            if st.form_submit_button("Confirm Order"):
                                # حفظ الطلب في جدول orders
                                order_data = {
                                    "customer_name": c_name, "address": c_addr, "phone": c_phone,
                                    "payment_method": c_pay, "product_name": p['name'], "merchant_code": p.get('merchant_code', 'general')
                                }
                                supabase.table("orders").insert(order_data).execute()
                                st.success("Order Placed Successfully!")
                st.markdown('</div>', unsafe_allow_html=True)

# --- 3. SELLER LOGIN (التاجر يشوف طلباته بالترتيب) ---
elif menu == "🏪 SELLER LOGIN":
    code = st.text_input("Enter Merchant Code", type="password")
    if code:
        res = supabase.table("merchants").select("code").execute().data
        if code in [r['code'] for r in res]:
            tab1, tab2 = st.tabs(["📦 Manage Products", "📥 View Orders"])
            
            with tab1: # إدارة المنتجات
                with st.expander("Add New Product"):
                    with st.form("add_p"):
                        n = st.text_input("Name"); pr = st.number_input("Price"); ph = st.text_input("WhatsApp")
                        img = st.file_uploader("Image", type=['jpg','png'])
                        if st.form_submit_button("Publish"):
                            img_str = base64.b64encode(img.read()).decode()
                            supabase.table("products").insert({"name":n, "price":pr, "phone":ph, "image":img_str, "status":"Available", "merchant_code":code}).execute()
                            st.rerun()
                
                # مسح وتحويل Sold Out
                my_p = supabase.table("products").select("*").eq("merchant_code", code).execute().data
                for i in my_p:
                    c1, c2, c3 = st.columns([2,1,1])
                    c1.write(f"{i['name']} - {i['status']}")
                    if c2.button("Sold Out", key=f"s_{i['id']}"):
                        supabase.table("products").update({"status":"Sold Out"}).eq("id", i['id']).execute(); st.rerun()
                    if c3.button("Delete", key=f"d_{i['id']}"):
                        supabase.table("products").delete().eq("id", i['id']).execute(); st.rerun()

            with tab2: # عرض الطلبات بالترتيب
                st.subheader("Customer Orders (Newest First)")
                # جلب الطلبات الخاصة بالتاجر مرتبة من الأحدث للأقدم
                orders = supabase.table("orders").select("*").eq("merchant_code", code).order("id", desc=True).execute().data
                if not orders: st.info("No orders yet.")
                for o in orders:
                    st.markdown(f"""
                    <div class="order-card">
                        <b>Product:</b> {o['product_name']} <br>
                        <b>Customer:</b> {o['customer_name']} | <b>Phone:</b> {o['phone']} <br>
                        <b>Address:</b> {o['address']} <br>
                        <b>Payment:</b> {o['payment_method']}
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("Mark as Completed", key=f"done_{o['id']}"):
                        supabase.table("orders").delete().eq("id", o['id']).execute()
                        st.rerun()
        else: st.error("Wrong Code.")

# --- 4. ADMIN ---
elif menu == "🛠️ ADMIN":
    if st.text_input("Admin Password", type="password") == "1515":
        m_n = st.text_input("Name"); m_c = st.text_input("Code")
        if st.button("Add Merchant"):
            supabase.table("merchants").insert({"name":m_n, "code":m_c}).execute(); st.success("Added!")
