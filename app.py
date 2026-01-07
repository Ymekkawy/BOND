import streamlit as st
from supabase import create_client
import base64

# --- 1. CONFIGURATION ---
URL = "https://lkzyubzuunlnkyaqqwzi.supabase.co"
KEY = "sb_publishable_GrCY2EOqAWGdDZUteIvEzA_O_D0TxQ3" # حط الـ Key بتاعك هنا

try:
    supabase = create_client(URL, KEY)
except:
    pass

st.set_page_config(page_title="BOND STORE", layout="wide")

# تحسين شكل عرض المنتجات والزراير
st.markdown("""
    <style>
    .product-card { border: 1px solid #ddd; padding: 15px; border-radius: 10px; background: white; margin-bottom: 20px; }
    .product-img { width: 100%; height: 200px; object-fit: cover; border-radius: 8px; }
    .sold-out-status { color: white; background: red; text-align: center; padding: 5px; font-weight: bold; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 style="text-align:center; background:black; color:white; padding:15px; border-radius:15px;">BOND STORE</h1>', unsafe_allow_html=True)

menu = st.radio("", ["🛒 SHOP", "🏪 SELLER LOGIN", "🛠️ ADMIN"], horizontal=True)

# --- 2. SHOP (الجمهور) ---
if menu == "🛒 SHOP":
    p_res = supabase.table("products").select("*").execute().data
    if not p_res: st.info("Store is empty.")
    else:
        cols = st.columns(3)
        for idx, p in enumerate(p_res):
            with cols[idx % 3]:
                st.markdown('<div class="product-card">', unsafe_allow_html=True)
                if p.get('image'):
                    st.markdown(f'<img src="data:image/png;base64,{p["image"]}" class="product-img">', unsafe_allow_html=True)
                st.subheader(p['name'])
                st.write(f"💰 {p['price']} EGP")
                if p.get('status') == "Sold Out":
                    st.markdown('<div class="sold-out-status">SOLD OUT</div>', unsafe_allow_html=True)
                else:
                    with st.expander("Order Now"):
                        with st.form(f"f_{p['id']}"):
                            n = st.text_input("Name"); a = st.text_input("Address"); ph = st.text_input("Phone")
                            if st.form_submit_button("Confirm Order"):
                                supabase.table("orders").insert({
                                    "customer_name": n, "address": a, "phone": ph,
                                    "product_name": p['name'], "merchant_code": p.get('merchant_code')
                                }).execute()
                                st.success("Order Sent!")
                st.markdown('</div>', unsafe_allow_html=True)

# --- 3. SELLER LOGIN (التاجر والتحكم الكامل) ---
elif menu == "🏪 SELLER LOGIN":
    code = st.text_input("Merchant Code", type="password")
    if code:
        m_check = supabase.table("merchants").select("code").execute().data
        if code in [r['code'] for r in m_check]:
            t1, t2 = st.tabs(["📦 My Products", "📥 Customer Orders"])
            
            with t1: # إضافة ومسح و Sold Out
                with st.expander("Add New Product"):
                    with st.form("p_add"):
                        name = st.text_input("Name"); price = st.number_input("Price")
                        wa = st.text_input("WhatsApp"); img = st.file_uploader("Image")
                        if st.form_submit_button("Publish"):
                            img_s = base64.b64encode(img.read()).decode()
                            supabase.table("products").insert({
                                "name": name, "price": price, "phone": wa, "image": img_s, 
                                "status": "Available", "merchant_code": code
                            }).execute(); st.rerun()
                
                st.divider()
                st.subheader("Manage Current Items")
                my_items = supabase.table("products").select("*").eq("merchant_code", code).execute().data
                for i in my_items:
                    c1, c2, c3 = st.columns([2, 1, 1])
                    c1.write(f"**{i['name']}** ({i['status']})")
                    # زرار Sold Out
                    if c2.button("Sold Out", key=f"so_{i['id']}"):
                        supabase.table("products").update({"status": "Sold Out"}).eq("id", i['id']).execute(); st.rerun()
                    # زرار مسح المنتج
                    if c3.button("🗑️ Delete", key=f"del_{i['id']}"):
                        supabase.table("products").delete().eq("id", i['id']).execute(); st.rerun()

            with t2: # رؤية ومسح الطلبات القديمة
                orders = supabase.table("orders").select("*").eq("merchant_code", code).order("id", desc=True).execute().data
                if not orders: st.info("No orders yet.")
                for o in orders:
                    st.info(f"📦 {o['product_name']} | 👤 {o['customer_name']} | 📞 {o['phone']} | 🏠 {o['address']}")
                    # زرار مسح الأوردر بعد التوصيل
                    if st.button(f"Order Completed (Delete)", key=f"done_{o['id']}"):
                        supabase.table("orders").delete().eq("id", o['id']).execute(); st.rerun()
        else: st.error("Invalid Merchant Code")

# --- 4. ADMIN (إلغاء التاجر) ---
elif menu == "🛠️ ADMIN":
    if st.text_input("Admin Password", type="password") == "1515":
        st.subheader("Authorize New Merchant")
        with st.form("m_reg"):
            m_n = st.text_input("Name"); m_c = st.text_input("Code")
            if st.form_submit_button("Authorize"):
                supabase.table("merchants").insert({"name": m_n, "code": m_c}).execute(); st.rerun()
        
        st.divider()
        st.subheader("Manage Existing Merchants")
        all_m = supabase.table("merchants").select("*").execute().data
        for m in all_m:
            col1, col2 = st.columns([3, 1])
            col1.write(f"👤 {m['name']} (Code: {m['code']})")
            # زرار مسح التاجر نهائياً
            if col2.button("❌ Remove Merchant", key=f"rm_{m['id']}"):
                supabase.table("merchants").delete().eq("id", m['id']).execute(); st.rerun()
