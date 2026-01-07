import streamlit as st
from supabase import create_client
import base64

# --- 1. CONFIGURATION ---
URL = "https://lkzyubzuunlnkyaqqwzi.supabase.co"
KEY = "sb_publishable_GrCY2EOqAWGdDZUteIvEzA_O_D0TxQ3" # تأكد من وضع المفتاح الصحيح

try:
    supabase = create_client(URL, KEY)
except:
    pass

st.set_page_config(page_title="BOND STORE", layout="wide")

# تصميم لتحسين شكل الموقع والصور
st.markdown("""
    <style>
    .product-img { width: 100%; height: 200px; object-fit: cover; border-radius: 10px; }
    .order-card { border: 1px solid #ddd; padding: 15px; border-radius: 10px; background: #f9f9f9; margin-bottom: 10px; }
    .sold-out-label { color: red; font-weight: bold; border: 2px solid red; padding: 5px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 style="text-align:center; background:black; color:white; padding:15px; border-radius:15px;">BOND STORE</h1>', unsafe_allow_html=True)

menu = st.radio("", ["🛒 SHOP", "🏪 SELLER LOGIN", "🛠️ ADMIN"], horizontal=True)

# --- 2. SHOP (العرض للجمهور) ---
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
                    st.markdown('<div class="sold-out-label">SOLD OUT</div>', unsafe_allow_html=True)
                else:
                    with st.expander("Order Now"):
                        with st.form(f"ord_{p['id']}"):
                            n = st.text_input("Name"); a = st.text_input("Address"); ph = st.text_input("Phone")
                            pay = st.selectbox("Payment", ["Cash", "InstaPay"])
                            if st.form_submit_button("Confirm"):
                                supabase.table("orders").insert({
                                    "customer_name": n, "address": a, "phone": ph, "payment_method": pay,
                                    "product_name": p['name'], "merchant_code": p.get('merchant_code')
                                }).execute()
                                st.success("Order Placed!")
                st.markdown('</div>', unsafe_allow_html=True)

# --- 3. SELLER LOGIN (صلاحيات التاجر) ---
elif menu == "🏪 SELLER LOGIN":
    code = st.text_input("Merchant Code", type="password")
    if code:
        m_res = supabase.table("merchants").select("code").execute().data
        if code in [r['code'] for r in m_res]:
            t1, t2 = st.tabs(["📦 Products Management", "📥 Orders Received"])
            
            with t1: # إضافة، مسح، وتغيير حالة المنتج
                with st.expander("Add New Product"):
                    with st.form("p_form"):
                        pn = st.text_input("Name"); pp = st.number_input("Price")
                        pwa = st.text_input("WhatsApp"); pimg = st.file_uploader("Image")
                        if st.form_submit_button("Publish"):
                            img_s = base64.b64encode(pimg.read()).decode()
                            supabase.table("products").insert({"name":pn, "price":pp, "phone":pwa, "image":img_s, "status":"Available", "merchant_code":code}).execute()
                            st.rerun()
                
                st.divider()
                my_p = supabase.table("products").select("*").eq("merchant_code", code).execute().data
                for i in my_p:
                    c1, c2, c3 = st.columns([2,1,1])
                    c1.write(f"**{i['name']}** ({i['status']})")
                    if c2.button("Sold Out", key=f"so_{i['id']}"): # زرار Sold Out للتاجر
                        supabase.table("products").update({"status":"Sold Out"}).eq("id", i['id']).execute(); st.rerun()
                    if c3.button("🗑️ Delete", key=f"del_{i['id']}"): # زرار مسح المنتج للتاجر
                        supabase.table("products").delete().eq("id", i['id']).execute(); st.rerun()

            with t2: # رؤية الطلبات الخاصة بالتاجر
                orders = supabase.table("orders").select("*").eq("merchant_code", code).order("id", desc=True).execute().data
                for o in orders:
                    st.markdown(f'<div class="order-card"><b>Product:</b> {o["product_name"]}<br><b>Customer:</b> {o["customer_name"]} | {o["phone"]}<br><b>Address:</b> {o["address"]}</div>', unsafe_allow_html=True)
                    if st.button("Complete/Clear", key=f"clr_{o['id']}"):
                        supabase.table("orders").delete().eq("id", o['id']).execute(); st.rerun()

# --- 4. ADMIN (صلاحيات الأدمن) ---
elif menu == "🛠️ ADMIN":
    if st.text_input("Admin Password", type="password") == "1515":
        st.subheader("Manage Merchants")
        with st.form("m_form"):
            mn = st.text_input("Merchant Name"); mc = st.text_input("Merchant Code")
            if st.form_submit_button("Authorize Merchant"):
                supabase.table("merchants").insert({"name":mn, "code":mc}).execute(); st.success("Added!"); st.rerun()
        
        st.divider()
        st.subheader("Existing Merchants")
        all_m = supabase.table("merchants").select("*").execute().data
        for m in all_m:
            col1, col2 = st.columns([3, 1])
            col1.write(f"👤 {m['name']} (Code: {m['code']})")
            if col2.button("❌ Remove Merchant", key=f"rm_{m['id']}"): # زرار إلغاء صلاحية التاجر
                supabase.table("merchants").delete().eq("id", m['id']).execute(); st.rerun()
