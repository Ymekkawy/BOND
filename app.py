import streamlit as st
from supabase import create_client
import base64

# --- 1. CONNECTION CONFIGURATION ---
# Your project URL
SUPABASE_URL = "https://lkzyubzuunlnkyaqqwzi.supabase.co"
# Paste your ANON PUBLIC KEY here
SUPABASE_KEY = "sb_publishable_GrCY2EOqAWGdDZUteIvEzA_O_D0TxQ3" 

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error(f"Connection Error: {e}")

# Page Setup
st.set_page_config(page_title="BOND STORE", layout="wide")

# Custom CSS for better look
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stRadio > div { background: white; padding: 10px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# Main Title
st.markdown('<h1 style="text-align:center; background:black; color:white; padding:20px; border-radius:15px; margin-bottom:30px;">BOND STORE</h1>', unsafe_allow_html=True)

# Navigation Menu (Horizontal Radio)
menu = st.radio("", ["🛒 SHOP", "🏪 SELLER LOGIN", "🛠️ ADMIN"], horizontal=True)

# --- 2. SHOP SECTION (Public View) ---
if menu == "🛒 SHOP":
    st.subheader("Available Products")
    try:
        # Fetching all products from Supabase
        res = supabase.table("products").select("*").execute()
        items = res.data
        
        if not items:
            st.info("The store is empty. Merchants will add products soon!")
        else:
            # Display items in a clean grid/list
            for p in items:
                with st.container():
                    st.markdown('<div style="border:1px solid #ddd; padding:20px; border-radius:15px; margin-bottom:20px; background:white;">', unsafe_allow_html=True)
                    
                    # Display Image
                    if p.get('image'):
                        try:
                            st.image(base64.b64decode(p['image']), use_container_width=True)
                        except:
                            st.warning("Image loading error.")
                    
                    st.subheader(p['name'])
                    st.write(f"💰 **Price:** {p['price']} EGP")
                    
                    # WhatsApp Order Button
                    wa_url = f"https://wa.me/{p['phone']}"
                    st.markdown(f'<a href="{wa_url}" target="_blank"><button style="width:100%; background:#25D366; color:white; border:none; padding:12px; border-radius:10px; font-weight:bold; cursor:pointer;">Order via WhatsApp</button></a>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading products: {e}")

# --- 3. SELLER LOGIN SECTION ---
elif menu == "🏪 SELLER LOGIN":
    st.header("Merchant Dashboard")
    seller_code = st.text_input("Enter your secret merchant code:", type="password")
    
    if seller_code:
        try:
            # Verify code from 'merchants' table
            m_res = supabase.table("merchants").select("code").execute()
            valid_codes = [m['code'] for m in m_res.data]
            
            if seller_code in valid_codes:
                st.success("Access Granted! Fill in your product details:")
                with st.form("add_item"):
                    p_name = st.text_input("Product Name")
                    p_price = st.number_input("Price (EGP)", min_value=0)
                    p_phone = st.text_input("WhatsApp Number (e.g., 2010...)")
                    p_img = st.file_uploader("Product Image", type=['jpg', 'png', 'jpeg'])
                    
                    if st.form_submit_button("Publish Product"):
                        if p_img and p_name:
                            img_str = base64.b64encode(p_img.read()).decode()
                            # Insert into products table
                            supabase.table("products").insert({
                                "name": p_name, 
                                "price": p_price, 
                                "phone": p_phone, 
                                "image": img_str
                            }).execute()
                            st.success("Success! Your product is now in the SHOP.")
                            st.rerun()
                        else:
                            st.error("Please provide both a name and an image.")
            else:
                st.error("Invalid Code.")
        except Exception as e:
            st.error(f"Authentication Error: {e}")

# --- 4. ADMIN SECTION (Password: 1515) ---
elif menu == "🛠️ ADMIN":
    st.header("Admin Control Panel")
    admin_pass = st.text_input("Enter Admin Password", type="password")
    
    if admin_pass == "1515":
        st.subheader("Manage Merchants")
        with st.form("new_merchant"):
            new_m_name = st.text_input("New Merchant Name")
            new_m_code = st.text_input("Assign Secret Code")
            if st.form_submit_button("Authorize This Merchant"):
                try:
                    # Insert into merchants table
                    supabase.table("merchants").insert({"name": new_m_name, "code": new_m_code}).execute()
                    st.success(f"Merchant '{new_m_name}' is now authorized!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to add merchant: {e}")
        
        # Display and Delete Merchants
        st.divider()
        st.subheader("Current Authorized Merchants")
        try:
            current_m = supabase.table("merchants").select("*").execute().data
            for m in current_m:
                col1, col2 = st.columns([3, 1])
                col1.write(f"👤 {m['name']} (Code: {m['code']})")
                if col2.button("Remove", key=f"m_{m['id']}"):
                    supabase.table("merchants").delete().eq("id", m['id']).execute()
                    st.rerun()
        except:
            st.info("No merchants authorized yet.")
