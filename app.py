import streamlit as st
from supabase import create_client
import base64

# --- API CONNECTION ---
# الرابط بتاعك أنا حطيتهولك جاهز
SUPABASE_URL = "https://lkzyubzuunlnkyaqqwzi.supabase.co" 
# حط هنا الـ Key اللي بيبدأ بـ sb_publishable من صورتك
SUPABASE_KEY = "sb_publishable_GrCY2EOqAWGdDZUteIvEzA_O_D0TxQ3"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="BOND STORE", layout="wide")

# Header
st.markdown('<h1 style="text-align:center; background:black; color:white; padding:20px; border-radius:15px;">BOND STORE</h1>', unsafe_allow_html=True)

# Navigation Menu
menu = st.radio("", ["🛒 SHOP", "🏪 SELLER LOGIN", "🛠️ ADMIN"], horizontal=True)

# --- 1. SHOP (Customers) ---
if menu == "🛒 SHOP":
    try:
        items = supabase.table("products").select("*").execute().data
        if not items: st.info("Store is currently empty.")
        else:
            for p in items:
                st.markdown('<div style="border:1px solid #ddd; padding:15px; border-radius:15px; margin-bottom:20px;">', unsafe_allow_html=True)
                if p.get('image'): st.image(base64.b64decode(p['image']), use_container_width=True)
                st.subheader(p['name'])
                st.write(f"Price: {p['price']} EGP")
                st.markdown(f'<a href="https://wa.me/{p["phone"]}" target="_blank"><button style="width:100%; background:#25D366; color:white; border:none; padding:10px; border-radius:10px; font-weight:bold; cursor:pointer;">Order via WhatsApp</button></a>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
    except: st.error("Setting up store...")

# --- 2. SELLER LOGIN (Merchants) ---
elif menu == "🏪 SELLER LOGIN":
    st.header("Merchant Login")
    pwd = st.text_input("Enter Merchant Code", type="password")
    
    # بيشيك على الأكواد المسموحة من جدول التجار اللي إنت عملته
    try:
        res = supabase.table("merchants").select("code").execute().data
        allowed_codes = [r['code'] for r in res]
        
        if pwd in allowed_codes:
            st.success("Access Granted! Fill in product details.")
            with st.form("add_p"):
                name = st.text_input("Product Name")
                price = st.number_input("Price", min_value=0)
                phone = st.text_input("WhatsApp Number (ex: 2010...)")
                img = st.file_uploader("Upload Image", type=['jpg', 'png'])
                if st.form_submit_button("Publish Product"):
                    if img and name:
                        img_str = base64.b64encode(img.read()).decode()
                        supabase.table("products").insert({"name": name, "price": price, "phone": phone, "image": img_str}).execute()
                        st.success("Product is live!")
                    else: st.error("Please add an image and name.")
        elif pwd: st.error("Invalid Code. Contact Admin.")
    except: st.warning("Admin hasn't authorized any merchants yet.")

# --- 3. ADMIN (You - Password: 1515) ---
elif menu == "🛠️ ADMIN":
    st.header("Admin Control Panel")
    if st.text_input("Admin Password", type="password") == "1515":
        # إضافة تاجر جديد
        st.subheader("Add New Merchant")
        with st.form("new_m"):
            m_name = st.text_input("Merchant Name")
            m_code = st.text_input("Create Secret Code for Merchant")
            if st.form_submit_button("Authorize This Merchant"):
                supabase.table("merchants").insert({"name": m_name, "code": m_code}).execute()
                st.success(f"Merchant '{m_name}' can now login with code '{m_code}'")
                st.rerun()

        # عرض ومسح التجار (التحكم في الـ Access)
        st.subheader("Authorized Merchants List")
        try:
            merchants = supabase.table("merchants").select("*").execute().data
            for m in merchants:
                c1, c2 = st.columns([3, 1])
                c1.write(f"👤 {m['name']} (Code: {m['code']})")
                if c2.button("Remove Access", key=f"del_{m['id']}"):
                    supabase.table("merchants").delete().eq("id", m['id']).execute()
                    st.warning(f"Access Revoked for {m['name']}")
                    st.rerun()
        except: st.info("No merchants authorized yet.")
        
        if st.button("Delete All Products (Wipe Store)"):
            supabase.table("products").delete().neq("id", 0).execute()
            st.success("Store Cleared.")
