import streamlit as st
import requests
import pandas as pd

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Shopify Insights Dashboard", layout="wide")
st.title("🛍️ Shopify Insights Dashboard")
st.caption("Clean, user-friendly tables (with images) — no raw HTML or JSON.")

page = st.sidebar.radio("📌 Navigation", ["Fetch Insights", "Competitors", "Stored Brands"])

def render_brand_tabs(data: dict):
    st.success(f"📌 Showing insights for **{data['brand_name']}**")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        ["📦 Products", "⭐ Hero Products", "📜 Policies", "📞 Contact", "❓ FAQs", "🔗 About & Links"]
    )

    # Products
    with tab1:
        prods = data.get("products", [])
        if prods:
            df = pd.DataFrame(prods)
            # normalize columns that might be missing
            if "image_url" not in df.columns: df["image_url"] = ""
            if "product_url" not in df.columns: df["product_url"] = ""
            if "price" not in df.columns: df["price"] = ""
            if "title" not in df.columns: df["title"] = ""
            st.dataframe(
                df[["image_url", "title", "price", "product_url"]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "image_url": st.column_config.ImageColumn("Image", width="small"),
                    "title": st.column_config.TextColumn("Title"),
                    "price": st.column_config.TextColumn("Price"),
                    "product_url": st.column_config.LinkColumn("Product Link"),
                },
            )
            st.caption(f"Total products shown: {len(df)}")
        else:
            st.info("No products found")

    # Hero Products
    with tab2:
        hero = data.get("hero_products", [])
        if hero:
            dfh = pd.DataFrame(hero)
            if "image_url" not in dfh.columns: dfh["image_url"] = ""
            if "product_url" not in dfh.columns: dfh["product_url"] = ""
            if "title" not in dfh.columns: dfh["title"] = ""
            st.dataframe(
                dfh[["image_url", "title", "product_url"]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "image_url": st.column_config.ImageColumn("Image", width="small"),
                    "title": st.column_config.TextColumn("Title"),
                    "product_url": st.column_config.LinkColumn("Product Link"),
                },
            )
            st.caption(f"Hero products shown: {len(dfh)}")
        else:
            st.info("No hero products found")

    # Policies
    with tab3:
        pol = data.get("policies", {})
        if pol:
            st.table(pd.DataFrame([pol]))
        else:
            st.info("No policies available")

    # Contact & Social
    with tab4:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Contact Details")
            st.table(pd.DataFrame([data.get("contact_details", {})]))
        with col2:
            st.subheader("Social Handles")
            st.table(pd.DataFrame([data.get("social_handles", {})]))

    # FAQs
    with tab5:
        faqs = data.get("faqs", [])
        if faqs:
            st.table(pd.DataFrame(faqs))
        else:
            st.info("No FAQs found")

    # About & Links
    with tab6:
        st.subheader("About the Brand")
        st.write(data.get("about", "N/A"))
        links = data.get("important_links", [])
        if links:
            st.subheader("Important Links")
            st.table(pd.DataFrame(links, columns=["Links"]))
        else:
            st.info("No important links found")

# --------- Pages ---------
if page == "Fetch Insights":
    st.header("🔎 Fetch Brand Insights")
    url = st.text_input("Enter Shopify Store URL", "memy.co.in")
    if st.button("Fetch Insights"):
        try:
            resp = requests.get(f"{BACKEND_URL}/fetch-insights", params={"website_url": url})
            if resp.status_code == 200:
                data = resp.json()
                render_brand_tabs(data)
            else:
                st.error(f"Error {resp.status_code}: {resp.text}")
        except Exception as e:
            st.error(f"❌ Failed to fetch insights: {e}")

elif page == "Competitors":
    st.header("🏆 Competitor Insights")
    url = st.text_input("Enter Shopify Store URL", "memy.co.in")
    if st.button("Fetch Competitors"):
        try:
            resp = requests.get(f"{BACKEND_URL}/fetch-competitors", params={"website_url": url})
            if resp.status_code == 200:
                brands = resp.json()
                for comp in brands:
                    st.markdown(f"### 🏬 {comp['brand_name']}")
                    render_brand_tabs(comp)
                    st.divider()
            else:
                st.error(f"Error {resp.status_code}: {resp.text}")
        except Exception as e:
            st.error(f"❌ Failed to fetch competitors: {e}")

elif page == "Stored Brands":
    st.header("💾 Stored Brands (from MySQL)")
    try:
        resp = requests.get(f"{BACKEND_URL}/brands")
        if resp.status_code == 200:
            brands = resp.json()
            if not brands:
                st.info("No brands stored yet. Fetch some first!")
            else:
                df_list = pd.DataFrame(brands)
                st.dataframe(df_list, use_container_width=True, hide_index=True)
                # Pick by dropdown (no raw IDs to type)
                options = {f"{row['brand_name']} (ID: {row['id']})": row["id"] for row in brands}
                selected = st.selectbox("Select a stored brand to view", list(options.keys()))
                if selected:
                    brand_id = options[selected]
                    detail = requests.get(f"{BACKEND_URL}/brand/{brand_id}")
                    if detail.status_code == 200:
                        data = detail.json()
                        render_brand_tabs(data)
                    else:
                        st.error("❌ Brand not found")
        else:
            st.error(f"Error {resp.status_code}: {resp.text}")
    except Exception as e:
        st.error(f"❌ Failed to connect to backend: {e}")
