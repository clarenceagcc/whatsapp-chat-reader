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
            pass
    return pd.DataFrame(messages)

def display_messages(chat_df, start_index, end_index):
    previous_sender = None
    previous_alignment = None
    for index, row in chat_df.iloc[start_index:end_index].iterrows():
        sender = row['sender']
        timestamp = row['timestamp']
        content = row['content']

        if sender == previous_sender:
            alignment = 'same-sender'
        elif previous_sender is None:
            alignment = 'left'
        elif sender != previous_sender:
            alignment = 'right' if previous_sender == chat_df['sender'].iloc[0] else 'left'

        if alignment == 'right':
            st.markdown(
                f"""
                <div class="message-container right-aligned">
                    <div class="chat-bubble outgoing">
                        <span class="timestamp">{timestamp}</span><br>
                        {content}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        elif alignment == 'left':
            st.markdown(
                f"""
                <div class="message-container left-aligned">
                    <div class="chat-bubble incoming">
                        <span class="sender">{sender}</span><br>
                        <span class="timestamp">{timestamp}</span><br>
                        {content}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        elif alignment == 'same-sender':
            if previous_alignment == 'right':
                st.markdown(
                    f"""
                    <div class="message-container right-aligned">
                        <div class="chat-bubble outgoing continued">
                            <span class="timestamp">{timestamp}</span><br>
                            {content}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div class="message-container left-aligned">
                        <div class="chat-bubble incoming continued">
                            <span class="timestamp">{timestamp}</span><br>
                            {content}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        previous_sender = sender
        previous_alignment = alignment

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
                    st.subheader(f"Chat with: {txt_file_name.split('.')[0]}")
                    chat_df = parse_whatsapp_chat(text_content)

                    if not chat_df.empty:
                        total_messages = len(chat_df)
                        default_display = min(10, total_messages)
                        display_count = st.slider("Messages to Display", 10, total_messages, default_display, step=10)

                        if 'start_index' not in st.session_state:
                            st.session_state['start_index'] = 0
                            st.session_state['end_index'] = display_count

                        if st.button("Load More"):
                            st.session_state['end_index'] = min(st.session_state['end_index'] + 10, total_messages)

                        display_messages(chat_df, st.session_state['start_index'], st.session_state['end_index'])

                        if st.session_state['end_index'] < total_messages:
                            st.info("Scroll down to load more messages.")
                        elif total_messages > 0:
                            st.success("All messages loaded.")

                    else:
                        st.warning("No messages found in the chat file or parsing failed.")
                else:
                    st.error("Could not read the content of the .txt file.")

        except zipfile.BadZipFile:
            st.error("Invalid .zip file. Please upload a valid .zip archive.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

    st.markdown(
        """
        <style>
        .message-container {
            display: flex;
            width: 100%;
            margin-bottom: 3px; /* Reduced margin */
        }

        .left-aligned {
            justify-content: flex-start;
        }

        .right-aligned {
            justify-content: flex-end;
        }

        .chat-bubble {
            padding: 8px 12px;
            border-radius: 8px;
            text-align: left;
            word-break: break-word;
            max-width: 80%;
        }

        .outgoing {
            background-color: #DCF8C6;
            color: #000;
        }

        .incoming {
            background-color: #FFFFFF;
            border: 1px solid #E0E0E0;
            color: #000;
        }

        .timestamp {
            font-size: 0.7em;
            color: #777;
            display: block;
            text-align: right; /* Align timestamp to the right within the bubble */
            margin-top: 2px;
        }

        .sender {
            font-size: 0.75em;
            color: #0084FF;
            font-weight: bold;
            display: block;
            text-align: left;
            margin-bottom: 2px;
        }

        .continued {
            border-radius: 4px; /* Less rounded for continued messages */
            margin-bottom: 1px; /* Even less space for continuation */
        }

        /* Dark mode */
        @media (prefers-color-scheme: dark) {
            body {
                background-color: #121212;
                color: #D3E0E0;
            }
            .outgoing {
                background-color: #2A4F4F;
                color: #D3E0E0;
            }
            .incoming {
                background-color: #1E1E1E;
                border: 1px solid #444;
                color: #D3E0E0;
            }
            .timestamp {
                color: #999;
            }
            .sender {
                color: #64B5F6;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()