import streamlit as st
import pandas as pd
import gspread
import json
import os
from google.oauth2.service_account import Credentials

# Conexión a Google Sheets
@st.cache_resource
def connect_to_sheet():
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    creds_json = os.getenv("GOOGLE_CREDS_JSON")
    creds_dict = json.loads(creds_json)
    creds = Credentials.from_service_account_info(creds_dict)
    client = gspread.authorize(creds)
    sheet = client.open_by_key("1atwNg78a44JGEkBZ8aZS460Ga5hh5Z0b1XlY7Co8VFc").sheet1
    return sheet

@st.cache_data
def load_data():
    sheet = connect_to_sheet()
    data = sheet.get_all_records()
    return pd.DataFrame(data)

df = load_data()

st.title("🔬404 Material - VIBES🛰️")
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
search_term = st.text_input("🔍Search material or keyword:", "")

location_filter = st.selectbox("📍 Filter by Location:", ["All"] + sorted(df["Location"].dropna().unique().tolist()))
shelf_filter = st.selectbox("🗄️ Filter by Shelf:", ["All"] + sorted(df["Shelf"].dropna().unique().tolist()))

filtered_df = df[df.apply(lambda row: search_term.lower() in str(row.to_list()).lower(), axis=1)]

if location_filter != "All":
    filtered_df = filtered_df[filtered_df["Location"] == location_filter]

if shelf_filter != "All":
    filtered_df = filtered_df[filtered_df["Shelf"] == shelf_filter]

st.write(f"📋 Material {len(filtered_df)} was found:")
if not filtered_df.empty:
    st.dataframe(filtered_df)
else:
    st.warning("⚠️ No Material was found.")

if not filtered_df.empty:
    st.download_button(
        "📥 Save search results in a CSV file",
        filtered_df.to_csv(index=False).encode("utf-8"),
        "materiales_filtrados.csv",
        "text/csv"
    )

if st.button("➡️ Go to Inventory Management"):
    st.switch_page("pages/inventory.py")
