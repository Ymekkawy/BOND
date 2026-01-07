import streamlit as st
from supabase import create_client
import base64

# --- 1. CONNECTION ---
SUPABASE_URL = "https://lkzyubzuunlnkyaqqwzi.supabase.co"
SUPABASE_KEY = "sb_publishable_GrCY2EOqAWGdDZUteIvEzA_O_D0TxQ3" # حط الـ Key بتاعك هنا

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except:
    pass

st.set_page_config(page_title="BOND STORE", layout="wide")

# CSS لتصغير الصور وتحسين الشكل
st.markdown("""
    <style>
    .product-img { width: 250px; height: 250px; object-fit: cover; border-radius: 10px; }
    .stButton>button { width: 100%; border-radius: 8px; }
    .sold-out { color: red; font-weight: bold; font-size: 20px; text-align: center; border: 2px solid red; padding: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 style="text-align:center; background:black; color:white; padding:15px; border-radius:15px;">BOND STORE</h1>', unsafe_allow_html=True)

menu = st.radio("", ["🛒 SHOP", "🏪 SELLER LOGIN", "🛠️ ADMIN"], horizontal=True)

# --- 2. SHOP (العرض للجمهور) ---
if menu == "🛒 SHOP":
    try:
        items = supabase.table("products").select("*").execute().data
        if not items: st.info("Store is empty.")
        else:
            cols = st.columns(3) # عرض المنتجات في 3 أعمدة عشان الصور متبقاش ضخمة
            for idx, p in enumerate(items):
                with cols[idx % 3]:
                    st.markdown('<div style="border:1px solid #eee; padding:10px; border-radius:10px; background:white;">', unsafe_allow_html=True)
                    if p.get('image'):
                        img_html = f'<img src="data:image/png;base64,{p["image"]}" class="product-img">'
                        st.markdown(img_html, unsafe_allow_html=True)
                    
                    st.subheader(p['name'])
                    st.write(f"💰 {p['price']} EGP")
                    
                    # التحقق من حالة المنتج (مباع أم لا)
                    if p.get('status') == "Sold Out":
                        st.markdown('<div class="sold-out">SOLD OUT</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<a href="https://wa.me/{p["phone"]}" target="_blank"><button style="background:#25D366; color:white; border:none; padding:10px; width:100%; cursor:pointer; border-radius:5px;">Order Now</button></a>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
    except: st.error("Database connection issue.")

# --- 3. SELLER LOGIN (إدارة البضاعة للتاجر) ---
elif menu == "🏪 SELLER LOGIN":
    code = st.text_input("Enter Merchant Code", type="password")
    if code:
        res = supabase.table("merchants").select("code").execute().data
        if code in [r['code'] for r in res]:
            st.success("Welcome Back!")
            
            # إضافة منتج جديد
            with st.expander("➕ Add New Product"):
                with st.form("new_p"):
                    n = st.text_input("Product Name")
                    p = st.number_input("Price")
                    ph = st.text_input("WhatsApp")
                    img = st.file_uploader("Image", type=['jpg','png'])
                    if st.form_submit_button("Publish"):
                        img_str = base64.b64encode(img.read()).decode()
                        supabase.table("products").insert({"name":n, "price":p, "phone":ph, "image":img_str, "status":"Available"}).execute()
                        st.rerun()

            # إدارة المنتجات الحالية (Sold Out & Delete)
            st.divider()
            st.subheader("Manage Your Products")
            my_items = supabase.table("products").select("*").execute().data
            for i in my_items:
                c1, c2, c3 = st.columns([2, 1, 1])
                c1.write(f"📦 {i['name']} ({i['status']})")
                
                # زرار تحويل الحالة لـ Sold Out
                if c2.button("Sold Out", key=f"sold_{i['id']}"):
                    supabase.table("products").update({"status": "Sold Out"}).eq("id", i['id']).execute()
                    st.rerun()
                
                # زرار مسح المنتج نهائياً
                if c3.button("🗑️ Delete", key=f"del_p_{i['id']}"):
                    supabase.table("products").delete().eq("id", i['id']).execute()
                    st.rerun()
        else: st.error("Wrong Code.")

# --- 4. ADMIN (إدارة التجار) ---
elif menu == "🛠️ ADMIN":
    if st.text_input("Admin Password", type="password") == "1515":
        with st.form("add_m"):
            m_n = st.text_input("Merchant Name")
            m_c = st.text_input("Merchant Code")
            if st.form_submit_button("Add Merchant"):
                supabase.table("merchants").insert({"name":m_n, "code":m_c}).execute()
                st.success("Added!")
