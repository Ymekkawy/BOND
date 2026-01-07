import streamlit as st
from supabase import create_client
import base64

# --- اتصال مباشر وجاهز برابط مشروعك ---
SUPABASE_URL = "https://lkzyubzuunlnkyaqqwzi.supabase.co"
# انسخ الكود اللي بيبدأ بـ sb_publishable من صورتك وحطه هنا
SUPABASE_KEY = "sb_publishable_GrCY2EOqAWGddZUteIvEzA_O_D0T..." 

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except:
    st.error("Please update your Supabase Key in the code.")

st.set_page_config(page_title="BOND STORE", layout="wide")

# تصميم العنوان
st.markdown('<h1 style="text-align:center; background:black; color:white; padding:20px; border-radius:15px;">BOND STORE</h1>', unsafe_allow_html=True)

# القائمة الجانبية للتنقل
menu = st.sidebar.selectbox("Menu", ["🛒 SHOP", "🏪 SELLER LOGIN", "🛠️ ADMIN"])

# --- 1. صفحة العرض (SHOP) ---
if menu == "🛒 SHOP":
    try:
        res = supabase.table("products").select("*").execute()
        items = res.data
        if not items:
            st.info("The store is currently empty. Merchants must add products first.")
        else:
            for p in items:
                st.markdown('<div style="border:1px solid #ddd; padding:15px; border-radius:15px; margin-bottom:20px;">', unsafe_allow_html=True)
                if p.get('image'):
                    st.image(base64.b64decode(p['image']), use_container_width=True)
                st.subheader(p['name'])
                st.write(f"**Price:** {p['price']} EGP")
                st.markdown(f'<a href="https://wa.me/{p["phone"]}" target="_blank"><button style="width:100%; background:#25D366; color:white; border:none; padding:10px; border-radius:10px; font-weight:bold; cursor:pointer;">Order via WhatsApp</button></a>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
    except:
        st.warning("Store is empty or still initializing...")

# --- 2. دخول التجار (SELLER LOGIN) ---
elif menu == "🏪 SELLER LOGIN":
    st.header("Merchant Access")
    pwd = st.text_input("Enter Merchant Code", type="password")
    
    try:
        # بيجيب الأكواد اللي إنت (الأدمن) سمحت بيها من الجدول
        merchants_res = supabase.table("merchants").select("code").execute()
        allowed_codes = [m['code'] for m in merchants_res.data]
        
        if pwd in allowed_codes:
            st.success("Access Granted!")
            with st.form("add_product"):
                name = st.text_input("Product Name")
                price = st.number_input("Price", min_value=0)
                phone = st.text_input("WhatsApp Number")
                file = st.file_uploader("Upload Image", type=['jpg', 'png'])
                if st.form_submit_button("Publish Now"):
                    if file and name:
                        img_str = base64.b64encode(file.read()).decode()
                        supabase.table("products").insert({"name": name, "price": price, "phone": phone, "image": img_str}).execute()
                        st.success("Product is live!")
                    else: st.error("Please fill all fields.")
        elif pwd:
            st.error("Invalid code. Ask Admin for your code.")
    except:
        st.error("No merchants registered in the system yet. Admin must add a merchant first.")

# --- 3. لوحة تحكم الأدمن (ADMIN - Password: 1515) ---
elif menu == "🛠️ ADMIN":
    st.header("Admin Dashboard")
    if st.text_input("Admin Password", type="password") == "1515":
        # إضافة تاجر
        st.subheader("Manage Merchant Access")
        with st.form("add_m"):
            m_name = st.text_input("Merchant Name")
            m_code = st.text_input("Create Code for this Merchant")
            if st.form_submit_button("Authorize Merchant"):
                try:
                    supabase.table("merchants").insert({"name": m_name, "code": m_code}).execute()
                    st.success(f"Merchant '{m_name}' can now login!")
                except:
                    st.error("Make sure you created the 'merchants' table in Supabase.")

        # عرض ومسح التجار (التحكم في الـ Access)
        try:
            merchants = supabase.table("merchants").select("*").execute().data
            for m in merchants:
                c1, c2 = st.columns([3, 1])
                c1.write(f"👤 {m['name']} (Code: {m['code']})")
                if c2.button("Remove Access", key=f"del_{m['id']}"):
                    supabase.table("merchants").delete().eq("id", m['id']).execute()
                    st.rerun()
        except:
            st.info("No merchants authorized yet.")

        if st.button("Wipe Store Data (Delete Products)"):
            supabase.table("products").delete().neq("id", 0).execute()
            st.success("Cleared.")
