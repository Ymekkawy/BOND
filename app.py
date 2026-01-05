import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from PIL import Image
import io
import base64

# 1. إعدادات الصفحة
st.set_page_config(page_title="BOND STORE", layout="wide")

# 2. الربط بجوجل شيت (ضروري جداً عشان البيانات متمسحش)
conn = st.connection("gsheets", type=GSheetsConnection)

# دالة لتحويل الصورة لكود نصي (عشان تتخزن في الشيت)
def img_to_b64(file):
    img = Image.open(file).convert("RGB")
    img.thumbnail((300, 300))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return base64.b64encode(buf.getvalue()).decode()

# CSS لتحسين شكل الموبايل
st.markdown("""
    <style>
    .main-header { background: black; color: white; padding: 20px; text-align: center; font-size: 25px; border-radius: 15px; }
    .product-card { border: 1px solid #ddd; padding: 10px; border-radius: 15px; margin-bottom: 20px; background: #fff; }
    .stButton > button { width: 100%; border-radius: 10px; height: 45px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-header">BOND STORE</div>', unsafe_allow_html=True)

t1, t2, t3 = st.tabs(["🛒 المتجر", "🏪 لوحة التاجر", "🛠️ المطور"])

# --- 1. صفحة المتجر (الزبائن) ---
with t1:
    try:
        df = conn.read(worksheet="Products")
        if not df.empty:
            for i, row in df.iterrows():
                st.markdown('<div class="product-card">', unsafe_allow_html=True)
                if row['image']:
                    st.image(base64.b64decode(row['image']), use_container_width=True)
                st.subheader(row['name'])
                st.write(f"السعر: {row['price']} EGP")
                
                with st.expander("اطلب الآن"):
                    c_name = st.text_input("اسمك", key=f"cn{i}")
                    # الأوردر هيروح لرقم التاجر اللي هو ضافه بنفسه
                    msg = f"طلب جديد: {row['name']}\nالاسم: {c_name}"
                    wa_url = f"https://wa.me/{row['merchant_phone']}?text={msg.replace(' ', '%20')}"
                    st.markdown(f'<a href="{wa_url}" target="_blank"><button style="background:#25D366;color:white;border:none;width:100%;padding:10px;border-radius:10px;">تأكيد عبر واتساب</button></a>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("لا توجد منتجات حالياً.")
    except:
        st.warning("في انتظار إضافة أول منتج...")

# --- 2. لوحة التاجر (التاجر يضيف بياناته ومنتجاته) ---
with t2:
    st.header("إضافة منتج جديد")
    with st.form("add_product"):
        m_phone = st.text_input("رقم واتسابك (ابدأ بـ 20)", placeholder="2010xxxxxxx")
        p_name = st.text_input("اسم المنتج")
        p_price = st.number_input("السعر", min_value=0)
        p_img = st.file_uploader("ارفع صورة المنتج", type=['jpg', 'png', 'jpeg'])
        
        submit = st.form_submit_button("نشر المنتج في المتجر")
        
        if submit:
            if m_phone and p_name and p_img:
                img_b64 = img_to_b64(p_img)
                # حفظ البيانات في شيت جوجل
                new_data = pd.DataFrame([{"merchant_phone": m_phone, "name": p_name, "price": p_price, "image": img_b64}])
                try:
                    existing_df = conn.read(worksheet="Products")
                    updated_df = pd.concat([existing_df, new_data], ignore_index=True)
                except:
                    updated_df = new_data
                
                conn.update(worksheet="Products", data=updated_df)
                st.success("تم نشر منتجك بنجاح!")
            else:
                st.error("من فضلك أكمل كافة البيانات وارفع الصورة.")

# --- 3. المطور (للمراجعة فقط) ---
with t3:
    if st.text_input("كلمة سر المطور", type="password") == "1515":
        st.write("جميع المنتجات المسجلة في قاعدة البيانات:")
        try:
            df = conn.read(worksheet="Products")
            st.dataframe(df[['merchant_phone', 'name', 'price']])
        except:
            st.write("القاعدة خالية.")
