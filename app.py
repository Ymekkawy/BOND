import streamlit as st
from supabase import create_client
import base64

# --- API CONNECTION ---
SUPABASE_URL = "https://lkzyubzuunlnkyaqqwzi.supabase.co" 
SUPABASE_KEY = "sb_publishable_GrCY2EOqAWGdDZUteIvEzA_O_D0TxQ3"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="BOND STORE", layout="wide")

# Header
st.markdown('<h1 style="text-align:center; background:black; color:white; padding:20px; border-radius:15px;">BOND STORE</h1>', unsafe_allow_html=True)

# Tabs Navigation
menu = st.radio("", ["🛒 SHOP", "🏪 SELLER LOGIN", "🛠️ ADMIN"], horizontal=True)

# --- 1. SHOP ---
if menu == "🛒 SHOP":
    try:
        response = supabase.table("products").select("*").execute()
        items = response.data
        if not items:
            st.info("Store is empty.")
        else:
            for p in items:
                st.markdown('<div style="border:1px solid #ddd; padding:15px; border-radius:15px; margin-bottom:20px;">', unsafe_allow_html=True)
                if p.get('image'):
                    st.image(base64.b64decode(p['image']), use_container_width=True)
                st.subheader(p['name'])
                st.write(f"Price: {p['price']} EGP")
                st.markdown(f'<a href="https://wa.me/{p["phone"]}" target="_blank"><button style="width:100%; background:#25D366; color:white; border:none; padding:10px; border-radius:10px; font-weight:bold;">Order on WhatsApp</button></a>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
    except:
        st.error("Connecting...")

# --- 2. SELLER LOGIN ---
elif menu == "🏪 SELLER LOGIN":
    st.header("Seller Access")
    pwd = st.text_input("Enter Merchant Code", type="password")
    if pwd == "1515":
        st.success("Access Granted")
        with st.form("add_form"):
            p_n = st.text_input("Product Name")
            p_p = st.number_input("Price", min_value=0)
            p_ph = st.text_input("WhatsApp Number")
            p_i = st.file_uploader("Upload Image", type=['jpg', 'png'])
            if st.form_submit_button("Publish"):
                if p_i:
                    img_str = base64.b64encode(p_i.read()).decode()
                    supabase.table("products").insert({"name": p_n, "price": p_p, "phone": p_ph, "image": img_str}).execute()
                    st.success("Done!")

# --- 3. ADMIN ---
elif menu == "🛠️ ADMIN":
    st.header("Admin Dashboard")
    admin_pwd = st.text_input("Enter Admin Password", type="password")
    if admin_pwd == "1515":
        if st.button("Wipe All Data"):
            supabase.table("products").delete().neq("id", 0).execute()
            st.success("Database Cleared.")
