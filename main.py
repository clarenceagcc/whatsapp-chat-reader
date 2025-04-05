import streamlit as st
import zipfile
import re
import io
import pandas as pd

def parse_whatsapp_chat(text_content):
    messages = []
    for line in io.StringIO(text_content):
        match = re.match(r'\[(\d{2}/\d{2}/\d{2}, \d{2}:\d{2}:\d{2})\] (.*?): (.*)', line)
        if match:
            timestamp_str, sender, content = match.groups()
            messages.append({
                'timestamp': timestamp_str,
                'sender': sender.strip(),
                'content': content.strip()
            })
        else:
            # Handle system messages or other non-standard lines if needed
            pass
    return pd.DataFrame(messages)

def main():
    st.title("WhatsApp Chat Reader")
    st.subheader("Upload a .zip file containing your exported WhatsApp chat (.txt)")

    uploaded_file = st.file_uploader("Choose a .zip file", type="zip")

    if uploaded_file is not None:
        try:
            with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
                txt_files = [f for f in zip_ref.namelist() if f.endswith(".txt")]

                if not txt_files:
                    st.error("No .txt file found inside the uploaded .zip file.")
                    return

                txt_file_name = txt_files[0]
                with zip_ref.open(txt_file_name) as txt_file:
                    text_content = txt_file.read().decode('utf-8', errors='ignore')

                if text_content:
                    st.subheader(f"Chat with: {txt_file_name.split('.')[0]}") # Use filename as chat title
                    chat_df = parse_whatsapp_chat(text_content)

                    if not chat_df.empty:
                        for index, row in chat_df.iterrows():
                            sender = row['sender']
                            timestamp = row['timestamp']
                            content = row['content']

                            if sender == "You":
                                st.markdown(
                                    f"""
                                    <div style="background-color: #DCF8C6; padding: 8px; border-radius: 8px; margin-bottom: 5px; text-align: right; word-break: break-word;">
                                        <span style="font-size: 0.9em; color: #666;">{timestamp}</span><br>
                                        {content}
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )
                            else:
                                st.markdown(
                                    f"""
                                    <div style="background-color: #FFFFFF; border: 1px solid #E0E0E0; padding: 8px; border-radius: 8px; margin-bottom: 5px; text-align: left; word-break: break-word;">
                                        <span style="font-size: 0.8em; color: #0084FF; font-weight: bold;">{sender}</span><br>
                                        <span style="font-size: 0.9em; color: #666;">{timestamp}</span><br>
                                        {content}
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )
                    else:
                        st.warning("No messages found in the chat file or parsing failed.")
                else:
                    st.error("Could not read the content of the .txt file.")

        except zipfile.BadZipFile:
            st.error("Invalid .zip file. Please upload a valid .zip archive.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()