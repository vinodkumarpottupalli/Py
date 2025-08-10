import streamlit as st
from src.utils.utils import read_config, applogger
from src.utils.process import process, read_data

log = applogger(read_config())

st.title("Streamlit Project !!")

re_button = False

def disable():
    st.session_state.disabled = True

if "disabled" not in st.session_state:
    st.session_state.disabled = False

with st.form("myform", clear_on_submit=True):
    name = st.text_input("Data", placeholder="Enter something", key="name")
    submitted = st.form_submit_button("Submit", on_click=disable, disabled=st.session_state.disabled)

    if submitted:
        log.info("Form submitted...")
        st.info("Processing...............")
        process()
        re_button = True
        st.info("you have entered: " + st.session_state.name)

if re_button:
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="Download",
            data = read_data(),
            file_name="my_data.csv",
            mime="text/csv"
        )

    with col2:
        if st.button("Refresh Data"):
            #Reset the all the values
            st.session_state.disabled = False
            st.rerun()
