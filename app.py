import streamlit as st
import base64
from github import Github
import json

# --- CONFIGURATION ---
# Replace with your actual GitHub Token and Repo
GITHUB_TOKEN = "YOUR_GITHUB_TOKEN_HERE" 
REPO_NAME = "ymekkawy/bond" 

st.set_page_config(page_title="BOND STORE", layout="wide")

# Function to load data from GitHub
def load_data():
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        contents = repo.get_contents("database.json")
        return json.loads(contents.decoded_content.decode())
    except Exception:
        # Initial structure if file doesn't exist
        return {"merchants": {}, "products": []}

# Function to save data to GitHub
def save_data(data):
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    try:
        contents = repo.get_contents("database.json")
        repo.update_file(contents.path, "Update Store Data", json.dumps(data, indent=4), contents.sha)
    except Exception:
        repo.create_file("database.json", "Initial database creation", json.dumps(data, indent=4))

st.markdown('<div style="background:black;color:white;padding:20px;text-align:center;font-size:30px;border-radius:0 0 20px 20px;">BOND STORE</div>', unsafe_allow_html=True)

# Load current data
current_data = load_data()

tabs = st.tabs(["🛒 SHOP", "🏪 SELLER", "🛠️ ADMIN"])

# --- 1. SHOP TAB (Customer View) ---
with tabs[0]:
    if not current_data["products"]:
        st.info("The store is currently empty.")
    else:
        for i, p in enumerate(current_data["products"]):
            st.markdown('<div style="border:1px solid #ddd;padding:15px;border-radius:15px;margin-bottom:20px;">', unsafe_allow_html=True)
            # Display the uploaded product image
            if "image" in p:
                st.image(base64.b64decode(p['image']), use_container_width=True)
            st.subheader(p['name'])
            st.write(f"Price: {p['price']} EGP")
            
            with st.expander("ORDER NOW"):
                u_name = st.text_input("Your Name", key=f"user_{i}")
                # WhatsApp link goes to the specific merchant's phone
                order_msg = f"New Order: {p['name']}\nCustomer: {u_name}"
                wa_url = f"https://wa.me/{p['phone']}?text={order_msg.replace(' ', '%20')}"
                st.markdown(f'<a href="{wa_url}" target="_blank"><button style="width:100%;background:#25D366;color:white;border:none;padding:12px;border-radius:10px;cursor:pointer;font-weight:bold;">Confirm via WhatsApp</button></a>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

# --- 2. SELLER TAB (Add Products) ---
with tabs[1]:
    st.header("Seller Dashboard")
    with st.form("seller_form"):
        prod_name = st.text_input("Product Name")
        prod_price = st.number_input("Price (EGP)", min_value=0)
        prod_phone = st.text_input("Your WhatsApp Number (e.g., 2010...)")
        prod_img = st.file_uploader("Upload Product Image", type=['jpg', 'png', 'jpeg'])
        
        if st.form_submit_button("Publish Product"):
            if prod_name and prod_phone and prod_img:
                img_encoded = base64.b64encode(prod_img.read()).decode()
                new_entry = {
                    "name": prod_name,
                    "price": prod_price,
                    "phone": prod_phone,
                    "image": img_encoded
                }
                current_data["products"].append(new_entry)
                save_data(current_data)
                st.success("Product published successfully! It will not be deleted.")
            else:
                st.error("Please fill all fields and upload an image.")

# --- 3. ADMIN TAB (Developer Settings) ---
with tabs[2]:
    if st.text_input("Admin Password", type="password") == "1515":
        st.subheader("Manage Database")
        if st.button("Clear All Data"):
            save_data({"merchants": {}, "products": []})
            st.warning("All data has been wiped.")
