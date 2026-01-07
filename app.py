import streamlit as st
from supabase import create_client
import base64

# --- API CONNECTION ---
# ده الرابط بتاع مشروعك اللي جبتهولك
SUPABASE_URL = "https://lkzyubzuunlnkyaqqwzi.supabase.co" 
# انسخ الكود اللي في صورتك (اللي بيبدأ بـ sb_publishable) وحطه هنا
SUPABASE_KEY = "sb_publishable_GrCY2EOqAWGdDZUteIvEzA_O_D0TxQ3"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="BOND STORE", layout="wide")

# Header English
st.markdown('<h1 style="text-align:center; background:black; color:white; padding:20px; border-radius:15px;">BOND STORE</h1>', unsafe_allow_html=True)

tabs = st.tabs(["🛒 SHOP", "🏪 SELLER LOGIN", "🛠️ ADMIN"])

# --- TAB 1: SHOP ---
with tabs[0]:
    try:
        response = supabase.table("products").select("*").execute()
        items = response.data
        if not items:
            st.info("Welcome to BOND! No products added yet.")
        else:
            for p in items:
                st.markdown('<div style="border:1px solid #ddd; padding:15px; border-radius:15px; margin-bottom:20px;">', unsafe_allow_html=True)
                if p.get('image'):
                    st.image(base64.b64decode(p['image']), use_container_width=True)
                st.subheader(p['name'])
                st.write(f"Price: {p['price']} EGP")
                wa_url = f"https://wa.me/{p['phone']}?text=I want to buy {p['name']}"
                st.markdown(f'<a href="{wa_url}" target="_blank"><button style="width:100%; background:#25D366; color:white; border:none; padding:10px; border-radius:10px; font-weight:bold; cursor:pointer;">Order on WhatsApp</button></a>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
    except:
        st.error("Connecting to store...")

# --- TAB 2: SELLER LOGIN ---
with tabs[1]:
    st.header("Merchant Dashboard")
    if st.text_input("Enter Code", type="password") == "1515":
        with st.form("add_p"):
            p_n = st.text_input("Product Name")
            p_p = st.number_input("Price (EGP)", min_value=0)
            p_ph = st.text_input("WhatsApp Number (ex: 2010...)")
            p_i = st.file_uploader("Upload Image", type=['jpg', 'png', 'jpeg'])
            if st.form_submit_button("Publish Now"):
                if p_i and p_ph and p_n:
                    img_str = base64.b64encode(p_i.read()).decode()
                    # حفظ البيانات في Supabase للأبد
                    supabase.table("products").insert({
                        "name": p_n, "price": p_p, "phone": p_ph, "image": img_str
                    }).execute()
                    st.success("Product is live and saved!")
                else: st.error("Please fill all fields!")
