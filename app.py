import streamlit as st
from supabase import create_client
import base64

# --- 1. CONNECTION (Your URL is already here) ---
SUPABASE_URL = "https://lkzyubzuunlnkyaqqwzi.supabase.co"
# Paste your KEY here (the one starting with sb_publishable)
SUPABASE_KEY = "sb_publishable_GrCY2EOqAWGddZUteIvEzA_O_D0T..." 

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except:
    st.error("Check your Supabase Key!")

st.set_page_config(page_title="BOND STORE", layout="wide")

# UI Header
st.markdown('<h1 style="text-align:center; background:black; color:white; padding:20px; border-radius:15px;">BOND STORE</h1>', unsafe_allow_html=True)

# Navigation Menu
menu = st.sidebar.selectbox("Go to:", ["🛒 SHOP", "🏪 SELLER LOGIN", "🛠️ ADMIN"])

# --- 2. SHOP (Customer View) ---
if menu == "🛒 SHOP":
    try:
        res = supabase.table("products").select("*").execute()
        items = res.data
        if not items:
            st.info("Store is empty. Admin needs to authorize sellers first.")
        else:
            for p in items:
                with st.container():
                    st.markdown('<div style="border:1px solid #ddd; padding:15px; border-radius:15px; margin-bottom:20px;">', unsafe_allow_html=True)
                    if p.get('image'):
                        st.image(base64.b64decode(p['image']), use_container_width=True)
                    st.subheader(p['name'])
                    st.write(f"**Price:** {p['price']} EGP")
                    st.markdown(f'<a href="https://wa.me/{p["phone"]}" target="_blank"><button style="width:100%; background:#25D366; color:white; border:none; padding:10px; border-radius:10px; font-weight:bold; cursor:pointer;">Order via WhatsApp</button></a>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
    except:
        st.warning("Store is being initialized...")

# --- 3. SELLER LOGIN (For Merchants) ---
elif menu == "🏪 SELLER LOGIN":
    st.header("Merchant Login")
    pwd = st.text_input("Enter Merchant Code", type="password")
    
    # Validation from database
    try:
        merchants = supabase.table("merchants").select("code").execute().data
        allowed_codes = [m['code'] for m in merchants]
        
        if pwd in allowed_codes:
            st.success("Welcome! Add your product details:")
            with st.form("add_product_form"):
                p_name = st.text_input("Product Name")
                p_price = st.number_input("Price (EGP)", min_value=0)
                p_phone = st.text_input("WhatsApp (ex: 2010...)")
                p_file = st.file_uploader("Product Image", type=['jpg', 'png'])
                if st.form_submit_button("Publish Product"):
                    if p_file and p_name:
                        img_str = base64.b64encode(p_file.read()).decode()
                        supabase.table("products").insert({"name": p_name, "price": p_price, "phone": p_phone, "image": img_str}).execute()
                        st.success("Product is now LIVE!")
                    else: st.error("Please fill all fields.")
        elif pwd:
            st.error("Invalid code. Please contact Admin.")
    except:
        st.error("Admin has not authorized any merchants yet.")

# --- 4. ADMIN (Full Control - Password: 1515) ---
elif menu == "🛠️ ADMIN":
    st.header("Admin Panel")
    admin_pwd = st.text_input("Admin Password", type="password")
    if admin_pwd == "1515":
        # Add Merchant
        st.subheader("Manage Sellers")
        with st.form("add_merchant"):
            m_name = st.text_input("Seller Name")
            m_code = st.text_input("Create Secret Code")
            if st.form_submit_button("Add Seller"):
                supabase.table("merchants").insert({"name": m_name, "code": m_code}).execute()
                st.success(f"Seller '{m_name}' added successfully.")
                st.rerun()

        # View and Remove Merchants
        try:
            current_m = supabase.table("merchants").select("*").execute().data
            for m in current_m:
                col1, col2 = st.columns([3, 1])
                col1.write(f"👤 {m['name']} (Code: {m['code']})")
                if col2.button("Remove Access", key=f"del_{m['id']}"):
                    supabase.table("merchants").delete().eq("id", m['id']).execute()
                    st.rerun()
        except:
            st.info("No sellers found.")

        if st.button("Delete All Products (Wipe Store)"):
            supabase.table("products").delete().neq("id", 0).execute()
            st.success("All products deleted.")
