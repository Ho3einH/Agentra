import os
import requests
import streamlit as st

st.set_page_config(
    page_title="Customer Agent",
    page_icon="🤖",
    layout="centered"
)

st.markdown("""
<style>
html, body, [class*="css"] {
    direction: rtl;
    text-align: right;
}
.stChatMessage {
    direction: rtl;
    text-align: right;
}
</style>
""", unsafe_allow_html=True)

st.title("🤖 Customer Agent")
st.caption("محیط آزمایشی تعامل با ایجنت")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("پیامت رو بنویس...")

if prompt:
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("در حال دریافت پاسخ..."):
            try:
                response = requests.post(
                    os.getenv("AGENT_URL", "http://127.0.0.1:8000/message"),
                    json={
                        "customer_id": "gui-user",
                        "message": prompt
                    },
                    timeout=90
                )
                response.raise_for_status()
                answer = response.json()["ai_response"]

            except Exception as e:
                answer = f"خطا در ارتباط با Agent:\n\n{e}"

            st.markdown(answer)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })
