import streamlit as st
import os
from datetime import datetime
from main import run
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import yaml
from string import Template

def load_config():
    """Load email configuration from config file and environment variables"""
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'email_config.yaml')
    if not os.path.exists(config_path):
        st.error(f"Email configuration file not found at {config_path}")
        return {}

    with open(config_path, 'r') as f:
        config_template = f.read()
    
    # Replace environment variables
    template = Template(config_template)
    config_str = template.safe_substitute(
        SMTP_USERNAME=os.getenv('SMTP_USERNAME', ''),
        SMTP_PASSWORD=os.getenv('SMTP_PASSWORD', '')
    )
    
    return yaml.safe_load(config_str)

def validate_email_config():
    """Validate email configuration"""
    config = load_config()
    missing = []
    
    if not config.get('smtp_username'):
        missing.append('SMTP_USERNAME environment variable')
    if not config.get('smtp_password'):
        missing.append('SMTP_PASSWORD environment variable')
    
    if missing:
        st.error(f"Missing email configuration: {', '.join(missing)}")
        st.info("""
        To set up email sending:
        1. Go to your Google Account settings
        2. Enable 2-Step Verification if not already enabled
        3. Go to Security → App Passwords
        4. Create a new app password for 'Mail'
        5. Set the environment variables:
           ```
           export SMTP_USERNAME="your-email@gmail.com"
           export SMTP_PASSWORD="your-16-digit-app-password"
           ```
        """)
        return False
    return True

def send_email(to_email, subject, body, attachments=None):
    """Send email with attachments"""
    if not validate_email_config():
        raise ValueError("Invalid email configuration")
    
    config = load_config()
    
    msg = MIMEMultipart()
    msg['From'] = config['smtp_username']
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    # Attach files
    if attachments:
        for filepath in attachments:
            try:
                with open(filepath, 'rb') as f:
                    part = MIMEApplication(f.read(), Name=os.path.basename(filepath))
                    part['Content-Disposition'] = f'attachment; filename="{os.path.basename(filepath)}"'
                    msg.attach(part)
            except Exception as e:
                st.warning(f"Failed to attach {filepath}: {str(e)}")

    # Send email
    try:
        with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
            server.starttls()
            server.login(config['smtp_username'], config['smtp_password'])
            server.send_message(msg)
    except smtplib.SMTPAuthenticationError:
        raise ValueError("""
        Email authentication failed. Please check your App Password configuration.
        Go to Google Account → Security → App Passwords to generate a new password.
        """)
    except Exception as e:
        raise ValueError(f"Failed to send email: {str(e)}")

def main():
    st.title("CrewAI ERP Research Tool")
    
    # Add email configuration status
    with st.sidebar:
        st.subheader("Email Configuration")
        if validate_email_config():
            st.success("Email configuration is valid")
        
    with st.form("input_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input("Company Name", help="Enter the target company name")
            siren = st.text_input("SIREN Number", help="Enter the company's SIREN number")
            city = st.text_input("City", help="Enter the company's city")
            
        with col2:
            activity_type = st.text_input("Activity Type", help="Enter the company's main activity")
            website_url = st.text_input("Website URL", help="Enter the company's website")
            receiver_email = st.text_input("Receiver Email", help="Enter the email address to receive the report")

        submit = st.form_submit_button("Start Research")

        if submit:
            if not all([company_name, siren, city, activity_type, website_url, receiver_email]):
                st.error("Please fill in all fields")
                return

            if not validate_email_config():
                return

            with st.spinner("Running research..."):
                try:
                    # Create inputs dictionary
                    inputs = {
                        "company_name": company_name,
                        "siren": siren,
                        "city": city,
                        "activity_type": activity_type,
                        "website_url": website_url
                    }

                    # Run the crew
                    output_dir = run(inputs)

                    # Get all files in the output directory
                    attachments = []
                    for root, _, files in os.walk(output_dir):
                        for file in files:
                            if file.endswith('.md'):
                                attachments.append(os.path.join(root, file))

                    if not attachments:
                        st.warning("No output files were generated")
                        return

                    # Send email with attachments
                    send_email(
                        to_email=receiver_email,
                        subject=f"Research Results for {company_name}",
                        body=f"Please find attached the research results for {company_name}.",
                        attachments=attachments
                    )

                    st.success("Research completed and results sent by email!")
                    
                    # Display results in the interface
                    st.subheader("Generated Reports")
                    for attachment in attachments:
                        with open(attachment, 'r') as f:
                            st.markdown(f.read())

                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 