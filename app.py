import streamlit as st
from supabase import create_client
import base64

# --- بياناتك اللي هنربط بيها (تأكد إنها صح) ---
URL = "https://lkzyubzuunlnkyaqqwzi.supabase.co"
# حط هنا الـ anon public key الجديد اللي نسخته
KEY = "sb_publishable_GrCY2EOqAWGdDZUteIvEzA_O_D0TxQ3" 

try:
    supabase = create_client(URL, KEY)
except:
    pass

st.set_page_config(page_title="BOND STORE", layout="wide")

# العنوان
st.markdown('<h1 style="text-align:center; background:black; color:white; padding:20px; border-radius:15px;">BOND STORE</h1>', unsafe_allow_html=True)

# التنقل (horizontal عشان ميهنجش في الجنب)
menu = st.radio("Navigation:", ["🛒 SHOP", "🏪 SELLER LOGIN", "🛠️ ADMIN"], horizontal=True)

# --- 1. SHOP ---
if menu == "🛒 SHOP":
    st.info("Products will appear here once added.")

# --- 2. SELLER LOGIN (دي اللي كانت بيضاء عندك) ---
elif menu == "🏪 SELLER LOGIN":
    st.header("Merchant Entrance")
    # الخانة دي لازم تظهر دلوقتي لأنها بره أي شروط
    seller_code = st.text_input("Please Enter Your Code to Access:", type="password", key="seller_input")
    
    if seller_code:
        try:
            # بيشيك على الكود
            res = supabase.table("merchants").select("code").execute()
            allowed = [r['code'] for r in res.data]
            if seller_code in allowed:
                st.success("Access Granted!")
                with st.form("add_product"):
                    name = st.text_input("Product Name")
                    price = st.number_input("Price")
                    phone = st.text_input("WhatsApp")
                    img = st.file_uploader("Image")
                    if st.form_submit_button("Publish"):
                        img_str = base64.b64encode(img.read()).decode()
                        supabase.table("products").insert({"name": name, "price": price, "phone": phone, "image": img_str}).execute()
                        st.success("Done!")
            else:
                st.error("Invalid Code!")
        except Exception as e:
            st.error(f"Waiting for Admin to add merchants... (Error: {e})")

# --- 3. ADMIN ---
elif menu == "🛠️ ADMIN":
    st.header("Admin Area")
    admin_pass = st.text_input("Password", type="password")
    if admin_pass == "1515":
        m_name = st.text_input("New Merchant Name")
        m_code = st.text_input("New Merchant Code")
        if st.button("Authorize"):
            supabase.table("merchants").insert({"name": m_name, "code": m_code}).execute()
            st.success("Merchant Added!")
