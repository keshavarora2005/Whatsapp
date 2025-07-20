import streamlit as st
import pandas as pd
import pywhatkit
import pyautogui
import datetime
import time
import re

# Set Streamlit config
st.set_page_config(page_title="Simple WhatsApp Sender", layout="centered")
st.title("📤 WhatsApp Bulk Sender")

# File uploader
uploaded_file = st.file_uploader("Upload Excel or CSV with 'Name' and 'Phone' columns", type=["xlsx", "csv"])

def clean_phone_number(phone):
    """Clean and format phone number"""
    # Remove all non-digit characters
    phone = re.sub(r'\D', '', str(phone))
    
    # Remove leading zeros
    phone = phone.lstrip('0')
    
    # If it's a 10-digit number, add +91
    if len(phone) == 10:
        return "+91" + phone
    # If it's already 12 digits with country code, format properly
    elif len(phone) == 12 and phone.startswith('91'):
        return "+" + phone
    # If it already has +91, return as is
    elif phone.startswith('+91'):
        return phone
    else:
        return None

def send_whatsapp_message(phone, message):
    """Send WhatsApp message with explicit send action"""
    try:
        # Use pywhatkit to open WhatsApp and type message
        pywhatkit.sendwhatmsg_instantly(
            phone, 
            message, 
            wait_time=15,
            tab_close=False  # Don't close tab automatically
        )
        
        # Wait a moment for the message to be typed
        time.sleep(3)
        
        # Press Enter to send the message
        pyautogui.press('enter')
        
        # Wait a moment for the message to be sent
        time.sleep(2)
        
        # Close the tab
        pyautogui.hotkey('ctrl', 'w')
        
        return True
    except Exception as e:
        st.error(f"Error in send_whatsapp_message: {str(e)}")
        return False

if uploaded_file:
    try:
        # Load data
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # Show preview
        st.success("✅ File uploaded successfully!")
        st.write("**Preview of your data:**")
        st.dataframe(df[["Name", "Phone"]].head())

        # Check required columns
        if "Name" not in df.columns or "Phone" not in df.columns:
            st.error("❌ Missing columns: 'Name' and 'Phone' required.")
        else:
            # Message customization
            st.write("---")
            st.subheader("📝 Message Settings")
            
            custom_message = st.text_area("Type your message below:", value="", height=100)
            st.info("💡 Use {name} in your message to automatically insert the name given in uploaded file ")
            
            # Send button
            st.write("---")
            if st.button("📨 Send WhatsApp Messages", type="primary", use_container_width=True):
                if not custom_message.strip():
                    st.error("Please enter a message before sending.")
                else:
                    success_count = 0
                    error_count = 0

                    # Progress bar
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    for i, row in df.iterrows():
                        name = row["Name"]
                        phone = clean_phone_number(row["Phone"])

                        if not phone:
                            st.error(f"❌ Invalid phone number for {name}: {row['Phone']}")
                            error_count += 1
                            continue

                        # Format message with student name
                        message = custom_message.replace("{name}", name)

                        status_text.text(f"Sending message to {name}...")

                        try:
                            # Use the custom send function
                            if send_whatsapp_message(phone, message):
                                st.success(f"✅ Message sent to {name}")
                                success_count += 1
                            else:
                                st.error(f"❌ Failed to send to {name}")
                                error_count += 1
                            
                            # Update progress
                            progress = (i + 1) / len(df)
                            progress_bar.progress(progress)
                            
                            # Wait between messages
                            time.sleep(10)  # 10 seconds gap
                            
                        except Exception as e:
                            st.error(f"❌ Failed to send to {name}: {str(e)}")
                            error_count += 1
                            continue

                    # Final summary
                    st.write("---")
                    st.success(f"🎉 **Process completed!**")
                    st.write(f"✅ **Success:** {success_count} messages sent")
                    st.write(f"❌ **Errors:** {error_count} messages failed")
                    
                    if error_count > 0:
                        st.warning("⚠️ Some messages failed to send. Please check the error messages above.")

    except Exception as e:
        st.error(f"❌ Error loading file: {str(e)}")
        st.info("💡 Make sure your file has 'Name' and 'Phone' columns with valid data.")

else:
    st.info("📁 Please upload an Excel or CSV file with 'Name' and 'Phone' columns to get started.")
    
