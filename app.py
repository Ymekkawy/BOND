import streamlit as st
from supabase import create_client
import base64

# --- الاتصال (تأكد من الـ Key والـ URL) ---
URL = "https://lkzyubzuunlnkyaqqwzi.supabase.co"
KEY = "sb_publishable_GrCY2EOqAWGdDZUteIvEzA_O_D0TxQ3" 

try:
    supabase = create_client(URL, KEY)
except Exception as e:
    st.error(f"Connection Failed: {e}")

st.set_page_config(page_title="BOND STORE", layout="wide")

st.markdown('<h1 style="text-align:center; background:black; color:white; padding:15px; border-radius:15px;">BOND STORE</h1>', unsafe_allow_html=True)

# قائمة التنقل (عشان متهنجش)
menu = st.radio("", ["🛒 SHOP", "🏪 SELLER LOGIN", "🛠️ ADMIN"], horizontal=True)

# --- 1. SHOP ---
if menu == "🛒 SHOP":
    try:
        items = supabase.table("products").select("*").execute().data
        if not items: st.info("Store is currently empty.")
        else:
            cols = st.columns(3)
            for idx, p in enumerate(items):
                with cols[idx % 3]:
                    st.markdown('<div style="border:1px solid #ddd; padding:10px; border-radius:10px; background:white;">', unsafe_allow_html=True)
                    if p.get('image'):
                        st.markdown(f'<img src="data:image/png;base64,{p["image"]}" style="width:100%; height:180px; object-fit:cover; border-radius:10px;">', unsafe_allow_html=True)
                    st.subheader(p['name'])
                    st.write(f"💰 {p['price']} EGP")
                    
                    if p.get('status') == "Sold Out":
                        st.error("SOLD OUT")
                    else:
                        with st.expander(f"Order Now"):
                            with st.form(f"ord_{p['id']}"):
                                c_name = st.text_input("Name")
                                c_addr = st.text_input("Address")
                                c_phone = st.text_input("Phone")
                                c_pay = st.selectbox("Payment", ["Cash", "InstaPay"])
                                if st.form_submit_button("Confirm Order"):
                                    # إرسال الطلب
                                    order_data = {
                                        "customer_name": c_name, "address": c_addr, "phone": c_phone,
                                        "payment_method": c_pay, "product_name": p['name'], "merchant_code": p.get('merchant_code')
                                    }
                                    supabase.table("orders").insert(order_data).execute()
                                    st.success("✅ Order Sent!")
                    st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Shop Error: {e}")

# --- 2. SELLER LOGIN ---
elif menu == "🏪 SELLER LOGIN":
    code = st.text_input("Merchant Code", type="password")
    if code:
        try:
            m_res = supabase.table("merchants").select("code").execute().data
            if code in [m['code'] for m in m_res]:
                t1, t2 = st.tabs(["Products", "Orders"])
                with t1:
                    with st.expander("Add Product"):
                        with st.form("new_p"):
                            n = st.text_input("Name"); pr = st.number_input("Price")
                            ph = st.text_input("WhatsApp Number"); img = st.file_uploader("Image")
                            if st.form_submit_button("Publish"):
                                img_str = base64.b64encode(img.read()).decode()
                                supabase.table("products").insert({"name":n, "price":pr, "phone":ph, "image":img_str, "status":"Available", "merchant_code":code}).execute()
                                st.rerun()
                    # عرض منتجات التاجر فقط
                    my_items = supabase.table("products").select("*").eq("merchant_code", code).execute().data
                    for i in my_items:
                        c1, c2, c3 = st.columns([2,1,1])
                        c1.write(f"{i['name']} ({i['status']})")
                        if c2.button("Sold Out", key=f"s_{i['id']}"):
                            supabase.table("products").update({"status":"Sold Out"}).eq("id", i['id']).execute(); st.rerun()
                        if c3.button("Delete", key=f"d_{i['id']}"):
                            supabase.table("products").delete().eq("id", i['id']).execute(); st.rerun()
                with t2:
                    st.subheader("Your Orders")
                    # عرض الطلبات بالترتيب
                    orders = supabase.table("orders").select("*").eq("merchant_code", code).order("id", desc=True).execute().data
                    for o in orders:
                        st.info(f"📦 {o['product_name']} | 👤 {o['customer_name']} | 🏠 {o['address']} | 📞 {o['phone']}")
                        if st.button("Delete Order", key=f"del_o_{o['id']}"):
                            supabase.table("orders").delete().eq("id", o['id']).execute(); st.rerun()
            else: st.error("Wrong Code")
        except Exception as e: st.error(f"Error: {e}")

# --- 3. ADMIN ---
elif menu == "🛠️ ADMIN":
    if st.text_input("Admin Password", type="password") == "1515":
        m_n = st.text_input("Name"); m_c = st.text_input("Code")
        if st.button("Add"):
            supabase.table("merchants").insert({"name":m_n, "code":m_c}).execute()
            st.success("Merchant Added!")
