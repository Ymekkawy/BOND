import streamlit as st
from supabase import create_client
import base64

# --- 1. CONFIGURATION ---
URL = "https://lkzyubzuunlnkyaqqwzi.supabase.co"
KEY = "sb_publishable_GrCY2EOqAWGdDZUteIvEzA_O_D0TxQ3" 

try:
    supabase = create_client(URL, KEY)
except:
    pass

st.set_page_config(page_title="BOND STORE", layout="wide")

# CSS لتحسين شكل الكروت والأزرار
st.markdown("""
    <style>
    .product-card { border: 2px solid #eee; padding: 15px; border-radius: 12px; background: white; margin-bottom: 20px; }
    .product-img { width: 100%; height: 230px; object-fit: cover; border-radius: 10px; }
    .price-tag { font-size: 20px; color: #2ecc71; font-weight: bold; }
    .merchant-tag { font-size: 14px; color: #7f8c8d; font-style: italic; }
    .cat-label { background: #eee; padding: 2px 8px; border-radius: 5px; font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 style="text-align:center; background:black; color:white; padding:15px; border-radius:15px;">BOND STORE</h1>', unsafe_allow_html=True)

menu = st.radio("", ["🛒 SHOP", "🏪 SELLER LOGIN", "🛠️ ADMIN"], horizontal=True)

CATEGORIES = ["fashion", "phones", "electronics", "watches", "accessories", "perfumes", "other than"]

# --- 2. SHOP (مع خاصية الـ Category) ---
if menu == "🛒 SHOP":
    # فلتر التصنيفات للمشتري
    selected_cat = st.selectbox("Search by Category:", ["All"] + CATEGORIES)
    
    query = supabase.table("products").select("*")
    if selected_cat != "All":
        query = query.eq("category", selected_cat)
    
    p_res = query.execute().data
    
    if not p_res: st.info(f"No products found in {selected_cat}.")
    else:
        cols = st.columns(3)
        for idx, p in enumerate(p_res):
            with cols[idx % 3]:
                st.markdown('<div class="product-card">', unsafe_allow_html=True)
                if p.get('image'):
                    st.markdown(f'<img src="data:image/png;base64,{p["image"]}" class="product-img">', unsafe_allow_html=True)
                
                st.subheader(p['name'])
                st.markdown(f'<span class="cat-label">{p.get("category", "Other")}</span>', unsafe_allow_html=True)
                st.markdown(f'<div class="price-tag">{p["price"]} EGP</div>', unsafe_allow_html=True)
                
                m_info = supabase.table("merchants").select("name").eq("code", p.get('merchant_code')).execute().data
                m_name = m_info[0]['name'] if m_info else "Unknown Seller"
                st.markdown(f'<div class="merchant-tag">Seller: {m_name}</div>', unsafe_allow_html=True)
                
                if p.get('status') == "Sold Out":
                    st.error("SOLD OUT")
                else:
                    with st.expander("Order Details"):
                        with st.form(f"f_{p['id']}"):
                            n = st.text_input("Name"); a = st.text_input("Address"); ph = st.text_input("Phone")
                            if st.form_submit_button("Confirm Order"):
                                supabase.table("orders").insert({
                                    "customer_name": n, "address": a, "phone": ph,
                                    "product_name": p['name'], "merchant_code": p.get('merchant_code')
                                }).execute()
                                st.success("✅ Order Sent!")
                st.markdown('</div>', unsafe_allow_html=True)

# --- 3. SELLER LOGIN ---
elif menu == "🏪 SELLER LOGIN":
    code = st.text_input("Merchant Code", type="password")
    if code:
        m_check = supabase.table("merchants").select("code").execute().data
        if code in [r['code'] for r in m_check]:
            t1, t2 = st.tabs(["📦 Products", "📥 Orders"])
            with t1:
                with st.expander("➕ Add New Product", expanded=True):
                    with st.form("p_add"):
                        name = st.text_input("Product Name")
                        price = st.number_input("Price (EGP)", min_value=1)
                        # التاجر يحدد التصنيف هنا
                        cat = st.selectbox("Category", CATEGORIES)
                        wa = st.text_input("WhatsApp")
                        img = st.file_uploader("Image")
                        if st.form_submit_button("PUBLISH"):
                            img_s = base64.b64encode(img.read()).decode()
                            supabase.table("products").insert({
                                "name": name, "price": price, "category": cat, "phone": wa, 
                                "image": img_s, "status": "Available", "merchant_code": code
                            }).execute(); st.rerun()
                
                st.divider()
                my_items = supabase.table("products").select("*").eq("merchant_code", code).execute().data
                for i in my_items:
                    c1, c2, c3 = st.columns([2, 1, 1])
                    c1.write(f"**{i['name']}** ({i.get('category')})")
                    if c2.button("Sold Out", key=f"s_{i['id']}"):
                        supabase.table("products").update({"status": "Sold Out"}).eq("id", i['id']).execute(); st.rerun()
                    if c3.button("🗑️ Delete", key=f"d_{i['id']}"):
                        supabase.table("products").delete().eq("id", i['id']).execute(); st.rerun()
            with t2:
                orders = supabase.table("orders").select("*").eq("merchant_code", code).order("id", desc=True).execute().data
                for o in orders:
                    st.info(f"📦 {o['product_name']} | 👤 {o['customer_name']} | 📞 {o['phone']}")
                    if st.button(f"Complete Order {o['id']}", key=f"do_{o['id']}"):
                        supabase.table("orders").delete().eq("id", o['id']).execute(); st.rerun()
        else: st.error("Wrong Code")

# --- 4. ADMIN ---
elif menu == "🛠️ ADMIN":
    if st.text_input("Admin Password", type="password") == "1515":
        with st.form("m_reg"):
            m_n = st.text_input("Merchant Name"); m_c = st.text_input("Code")
            if st.form_submit_button("Authorize"):
                supabase.table("merchants").insert({"name": m_n, "code": m_c}).execute(); st.rerun()
        
        st.divider()
        all_m = supabase.table("merchants").select("*").execute().data
        for m in all_m:
            col1, col2 = st.columns([3, 1])
            col1.write(f"👤 {m['name']} (Code: {m['code']})")
            if col2.button("Remove Merchant", key=f"rm_{m['id']}"):
                supabase.table("merchants").delete().eq("id", m['id']).execute(); st.rerun()
