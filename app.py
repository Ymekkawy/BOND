import streamlit as st
from supabase import create_client
import base64

# --- API CONNECTION ---
SUPABASE_URL = "https://lkzyubzuunlnkyaqqwzi.supabase.co" 
# حط الـ Key اللي في صورتك هنا
SUPABASE_KEY = "sb_publishable_GrCY2EOqAWGddZUteIvEzA_O_D0T..." 
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="BOND STORE", layout="wide")

# Header
st.markdown('<h1 style="text-align:center; background:black; color:white; padding:20px; border-radius:15px;">BOND STORE</h1>', unsafe_allow_html=True)

# Navigation
menu = st.radio("", ["🛒 SHOP", "🏪 SELLER LOGIN", "🛠️ ADMIN"], horizontal=True)

# --- 1. SHOP ---
if menu == "🛒 SHOP":
    try:
        items = supabase.table("products").select("*").execute().data
        if not items: st.info("Store is empty.")
        else:
            for p in items:
                st.markdown('<div style="border:1px solid #ddd; padding:15px; border-radius:15px; margin-bottom:20px;">', unsafe_allow_html=True)
                if p.get('image'): st.image(base64.b64decode(p['image']), use_container_width=True)
                st.subheader(p['name'])
                st.write(f"Price: {p['price']} EGP")
                st.markdown(f'<a href="https://wa.me/{p["phone"]}" target="_blank"><button style="width:100%;">Order</button></a>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
    except: st.error("Setting up database...")

# --- 2. SELLER LOGIN ---
elif menu == "🏪 SELLER LOGIN":
    st.header("Seller Login")
    pwd = st.text_input("Enter Merchant Code", type="password")
    
    # بيشيك لو الكود موجود في جدول التجار اللي الأدمن ضافهم
    try:
        res = supabase.table("merchants").select("code").execute().data
        allowed_codes = [r['code'] for r in res]
        if pwd in allowed_codes:
            st.success("Access Granted!")
            with st.form("add_p"):
                name = st.text_input("Product Name")
                price = st.number_input("Price")
                phone = st.text_input("WhatsApp")
                img = st.file_uploader("Image")
                if st.form_submit_button("Publish"):
                    img_str = base64.b64encode(img.read()).decode()
                    supabase.table("products").insert({"name": name, "price": price, "phone": phone, "image": img_str}).execute()
                    st.success("Product is live!")
        elif pwd: st.error("Access Denied!")
    except: st.warning("No merchants authorized yet.")

# --- 3. ADMIN (إدارة التجار) ---
elif menu == "🛠️ ADMIN":
    st.header("Admin Control Panel")
    if st.text_input("Admin Password", type="password") == "1515":
        # إضافة تاجر جديد
        st.subheader("Add New Merchant")
        with st.form("new_m"):
            m_name = st.text_input("Merchant Name")
            m_code = st.text_input("Set Access Code")
            if st.form_submit_button("Authorize"):
                supabase.table("merchants").insert({"name": m_name, "code": m_code}).execute()
                st.success(f"Merchant {m_name} added!")
                st.rerun()

        # مسح تاجر (منع الـ access)
        st.subheader("Manage Merchants")
        try:
            merchants = supabase.table("merchants").select("*").execute().data
            for m in merchants:
                c1, c2 = st.columns([3, 1])
                c1.write(f"👤 {m['name']} (Code: {m['code']})")
                if c2.button("Delete Access", key=f"del_{m['id']}"):
                    supabase.table("merchants").delete().eq("id", m['id']).execute()
                    st.rerun()
        except: st.write("No merchants found.")
