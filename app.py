import streamlit as st
import base64
from github import Github
import json

# --- CONFIGURATION ---
GITHUB_TOKEN = "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" 
REPO_NAME = "ymekkawy/BOND" 

st.set_page_config(page_title="BOND STORE", layout="wide")

def load_data():
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        contents = repo.get_contents("database.json")
        return json.loads(contents.decoded_content.decode())
    except:
        return {"merchants": {"admin": "1515"}, "products": []}

def save_data(data):
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    try:
        contents = repo.get_contents("database.json")
        repo.update_file(contents.path, "Update Data", json.dumps(data, indent=4), contents.sha)
    except:
        repo.create_file("database.json", "Create DB", json.dumps(data, indent=4))

# UI Header
st.markdown('<h1 style="text-align:center; background:black; color:white; padding:20px; border-radius:15px;">BOND STORE</h1>', unsafe_allow_html=True)

data = load_data()
tabs = st.tabs(["🛒 SHOP", "🏪 SELLER LOGIN", "🛠️ ADMIN"])

# --- SHOP (Customer View) ---
with tabs[0]:
    if not data["products"]:
        st.info("No items available.")
    for i, p in enumerate(data["products"]):
        st.markdown('<div style="border:1px solid #ddd; padding:15px; border-radius:15px; margin-bottom:20px;">', unsafe_allow_html=True)
        st.image(base64.b64decode(p['image']), use_container_width=True)
        st.subheader(p['name'])
        st.write(f"Price: {p['price']} EGP")
        with st.expander("ORDER NOW"):
            u_name = st.text_input("Your Name", key=f"user_{i}")
            wa_url = f"https://wa.me/{p['phone']}?text=I want to buy {p['name']}"
            st.markdown(f'<a href="{wa_url}" target="_blank"><button style="width:100%; background:#25D366; color:white; border:none; padding:10px; border-radius:10px; cursor:pointer; font-weight:bold;">Order via WhatsApp</button></a>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- SELLER LOGIN (Protected Area) ---
with tabs[1]:
    st.header("Merchant Login")
    seller_code = st.text_input("Enter your Merchant Code", type="password")
    
    # Check if the code exists in our database
    if seller_code in data["merchants"].values():
        merchant_name = [k for k, v in data["merchants"].items() if v == seller_code][0]
        st.success(f"Welcome back, {merchant_name}!")
        
        with st.form("add_product"):
            st.subheader("Add New Product")
            p_name = st.text_input("Product Name")
            p_price = st.number_input("Price", min_value=0)
            p_phone = st.text_input("Your WhatsApp Number (ex: 2010...)")
            p_img = st.file_uploader("Upload Image", type=['jpg', 'png', 'jpeg'])
            
            if st.form_submit_button("Publish"):
                if p_name and p_phone and p_img:
                    img_str = base64.b64encode(p_img.read()).decode()
                    data["products"].append({"name": p_name, "price": p_price, "phone": p_phone, "image": img_str, "seller": merchant_name})
                    save_data(data)
                    st.success("Product Saved!")
                else: st.error("Please fill all fields!")
    elif seller_code:
        st.error("Invalid Merchant Code. Only authorized sellers can enter.")

# --- ADMIN (Manage Merchants) ---
with tabs[2]:
    if st.text_input("Developer Password", type="password") == "1515":
        st.header("Admin Panel")
        
        # Add new merchants here
        with st.expander("Add New Merchant"):
            new_m_name = st.text_input("Merchant Name")
            new_m_code = st.text_input("Assign a Code")
            if st.button("Authorize Merchant"):
                data["merchants"][new_m_name] = new_m_code
                save_data(data)
                st.success(f"Merchant {new_m_name} added!")

        if st.button("Clear All Products"):
            data["products"] = []
            save_data(data)
            st.warning("All products deleted.")
