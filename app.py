import streamlit as st
from supabase import create_client
import base64

# --- 1. بيانات الربط (تأكد إنها صحيحة 100% من غير مسافات) ---
URL = "https://lkzyubzuunlnkyaqqwzi.supabase.co"
# انسخ الكود اللي بيبدأ بـ sb_publishable وحطه هنا
KEY = "sb_publishable_GrCY2EOqAWGdDZUteIvEzA_O_D0TxQ3" 

try:
    supabase = create_client(URL, KEY)
except Exception as e:
    st.error(f"Error in Connection: {e}")

st.set_page_config(page_title="BOND STORE", layout="wide")
st.markdown('<h1 style="text-align:center; background:black; color:white; padding:20px; border-radius:15px;">BOND STORE</h1>', unsafe_allow_html=True)

menu = st.sidebar.selectbox("Go to:", ["🛒 SHOP", "🏪 SELLER LOGIN", "🛠️ ADMIN"])

# --- ADMIN SECTION (الجزء اللي فيه المشكلة) ---
if menu == "🛠️ ADMIN":
    st.header("Admin Control")
    password = st.text_input("Admin Password", type="password")
    
    if password == "1515":
        st.subheader("Add New Merchant")
        with st.form("merchant_form"):
            m_name = st.text_input("Merchant Name")
            m_code = st.text_input("Merchant Code")
            submit = st.form_submit_button("Authorize")
            
            if submit:
                try:
                    # محاولة الإضافة المباشرة
                    data = {"name": m_name, "code": m_code}
                    response = supabase.table("merchants").insert(data).execute()
                    st.success(f"Done! {m_name} is now a seller.")
                    st.rerun()
                except Exception as error:
                    # لو فشل، هيقولك السبب بالظبط في الموقع
                    st.error(f"Reason of Failure: {error}")
        
        # عرض التجار المسجلين
        try:
            merchants = supabase.table("merchants").select("*").execute().data
            if merchants:
                st.write("Current Merchants:")
                for m in merchants:
                    c1, c2 = st.columns([3, 1])
                    c1.write(f"👤 {m['name']} (Code: {m['code']})")
                    if c2.button("Delete", key=f"del_{m['id']}"):
                        supabase.table("merchants").delete().eq("id", m['id']).execute()
                        st.rerun()
        except:
            st.warning("No merchants found in the database yet.")

