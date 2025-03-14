import os
import sys
import streamlit as st
from main import run

st.set_page_config(page_title="ERP Research and Outreach Automation", layout="wide")
st.title("ERP Research and Outreach Automation")

# Add input fields for the company information
with st.form("company_info"):
    company_name = st.text_input("Company Name")
    siren = st.text_input("SIREN Number")
    city = st.text_input("City")
    activity_type = st.text_input("Activity Type")
    website_url = st.text_input("Website URL")
    
    submitted = st.form_submit_button("Run Analysis")
    
    if submitted:
        if not all([company_name, siren, city, activity_type, website_url]):
            st.error("Please fill in all fields")
        else:
            with st.spinner("Running analysis..."):
                try:
                    inputs = {
                        "company_name": company_name,
                        "siren": siren,
                        "city": city,
                        "activity_type": activity_type,
                        "website_url": website_url
                    }
                    result = run(inputs)
                    st.success("Analysis completed!")
                    st.write(result)
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    st.exception(e) 