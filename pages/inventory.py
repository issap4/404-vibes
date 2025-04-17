import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Conectar a Google Sheets
@st.cache_resource
def connect_to_sheet():
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key("1atwNg78a44JGEkBZ8aZS460Ga5hh5Z0b1XlY7Co8VFc").sheet1
    return sheet

def load_data():
    sheet = connect_to_sheet()
    data = sheet.get_all_records()
    return pd.DataFrame(data)

def save_data(df):
    sheet = connect_to_sheet()
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())

df = load_data()

st.title("🔧 Inventory Management - VIBES🛰️")
st.dataframe(df)

# Agregar nuevo material
st.subheader('➕ Add New Material')
with st.form(key='add_form'):
    material = st.text_input('Material')
    description = st.text_input('Description')
    container = st.text_input('Container')
    location = st.selectbox("Location", ["locker 1", "locker 2", "locker 3", "work-table"])
    shelf = st.selectbox("Shelf", ["top", "bottom", "2nd", "3er", "4th", "5th", "on", "under"])
    amount = st.number_input('Amount', min_value=0)
    keywords = st.text_input('Keywords')
    submit_button = st.form_submit_button(label='Add Material')

    if submit_button:
        new_material = pd.DataFrame({
            'Material': [material],
            'Description': [description],
            'Container': [container],
            'Location': [location],
            'Shelf': [shelf],
            'Amount': [amount],
            'Keywords': [keywords]
        })
        df = pd.concat([df, new_material], ignore_index=True)
        save_data(df)
        st.success('✅ Material successfully added!')

# Modificar material
st.subheader('✏️ Modify Material')
if not df.empty:
    material_to_modify = st.selectbox('Select material to modify', df['Material'].unique())
    selected_material = df[df['Material'] == material_to_modify].iloc[0]

    with st.form(key='modify_form'):
        new_description = st.text_input('Description', value=selected_material['Description'])
        new_container = st.text_input('Container', value=selected_material['Container'])
        new_location = st.selectbox("Location", ["locker 1", "locker 2", "locker 3", "work-table"], index=["locker 1", "locker 2", "locker 3", "work-table"].index(selected_material['Location']))
        new_shelf = st.selectbox("Shelf", ["top", "bottom", "2nd", "3er", "4th", "5th", "on", "under"], index=["top", "bottom", "2nd", "3er", "4th", "5th", "on", "under"].index(selected_material['Shelf']))
        # Obtener el valor numérico correctamente
        try:
            default_amount = int(selected_material['Amount'])
        except (ValueError, TypeError):
            default_amount = 0
        # Input con valor predeterminado seguro
        new_amount = st.number_input('Amount', value=default_amount, min_value=0)
        new_keywords = st.text_input('Keywords', value=selected_material['Keywords'])
        # Botón
        submit_mod = st.form_submit_button(label='Modify Material')

    if submit_mod:
        df.loc[df['Material'] == material_to_modify, ['Description', 'Container', 'Location', 'Shelf', 'Amount', 'Keywords']] = \
            [new_description, new_container, new_location, new_shelf, new_amount, new_keywords]
        save_data(df)
        st.success('✅ Material successfully modified!')

# Eliminar material
st.subheader('❌ Delete Material')
if not df.empty:
    material_to_delete = st.selectbox('Select material to delete', df['Material'].unique())
    if st.button('Delete Material'):
        df = df[df['Material'] != material_to_delete]
        save_data(df)
        st.success('🗑️ Material successfully deleted!')

if st.button("⬅️ Go to Search and Filters"):
    st.switch_page("app.py")
