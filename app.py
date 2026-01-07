import streamlit as st
import base64
from github import Github
import json

# --- CONFIGURATION ---
# PUT THE TOKEN YOU COPIED HERE
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
        # Default data if file is missing
        return {"merchants": {"admin": "1515"}, "products": []}

def save_data(data):
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    try:
        contents = repo.get_contents("database.json")
        repo.update_file(contents.path, "Update Data", json.dumps(data, indent=4), contents.sha)
    except:
        repo.create_file("database.json", "Create DB", json.dumps(data, indent=4))

# UI Design
st.markdown('<h1 style="text-align:center; background:black; color:white; padding:20px; border-radius:15px;">BOND STORE</h1>', unsafe_allow_html=True)

data = load_data()
tabs = st.tabs(["🛒 SHOP", "🏪 SELLER LOGIN", "🛠️ ADMIN"])

# --- TAB 1: SHOP ---
with tabs[0]:
    if not data["products"]:
        st.info("No products found.")
    for i, p in enumerate(data["products"]):
        st.markdown('<div style="border:1px solid #ddd; padding:15px; border-radius:15px; margin-bottom:20px;">', unsafe_allow_html=True)
        if "image" in p:
            st.image(base64.b64decode(p['image']), use_container_width=True)
        st.subheader(p['name'])
        st.write(f"Price: {p['price']} EGP")
        with st.expander("ORDER NOW"):
            u_name = st.text_input("Customer Name", key=f"user_{i}")
            wa_url = f"https://wa.me/{p['phone']}?text=Order: {p['name']}"
            st.markdown(f'<a href="{wa_url}" target="_blank"><button style="width:100%; background:#25D366; color:white; border:none; padding:10px; border-radius:10px; cursor:pointer;">Confirm on WhatsApp</button></a>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 2: SELLER LOGIN (Security) ---
with tabs[1]:
    st.header("Seller Access")
    s_code = st.text_input("Enter Merchant Code", type="password")
    
    if s_code in data["merchants"].values():
        m_name = [k for k, v in data["merchants"].items() if v == s_code][0]
        st.success(f"Welcome, {m_name}")
        with st.form("add_p"):
            p_n = st.text_input("Product Name")
            p_p = st.number_input("Price", min_value=0)
            p_ph = st.text_input("WhatsApp Number (ex: 2010...)")
            p_i = st.file_uploader("Product Image", type=['jpg', 'png', 'jpeg'])
            if st.form_submit_button("Post Product"):
                if p_n and p_ph and p_i:
                    img_str = base64.b64encode(p_i.read()).decode()
                    data["products"].append({"name": p_n, "price": p_p, "phone": p_ph, "image": img_str, "seller": m_name})
                    save_data(data)
                    st.success("Product is live!")
    elif s_code:
        st.error("Access Denied: Invalid Code")

# --- TAB 3: ADMIN (Management) ---
with tabs[2]:
    if st.text_input("Admin Password", type="password") == "1515":
        st.header("Admin Control")
        with st.expander("Authorize New Merchant"):
            new_name = st.text_input("Merchant Name")
            new_code = st.text_input("Merchant Code")
            if st.button("Add Merchant"):
                data["merchants"][new_name] = new_code
                save_data(data)
                st.success("Done!")
