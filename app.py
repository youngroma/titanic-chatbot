import streamlit as st
import requests
import base64
from io import BytesIO
from PIL import Image

st.title("Titanic Chatbot")

question = st.text_input("Ask about Titanic passengers:")

if st.button("Ask"):
    if question:
        response = requests.get(
            "https://titanic-chatbot-production.up.railway.app/ask",
            params={"question": question}
        )

        if response.status_code == 200:
            data = response.json()

            if "image" in data:
                try:
                    image_data = base64.b64decode(data["image"])  
                    image = Image.open(BytesIO(image_data)) 
                    st.image(image, caption="Histogram of Passenger Ages", use_container_width=True)
                except Exception as e:
                    st.error(f"Error decoding or displaying the image: {e}")
            elif "answer" in data:
                st.write(f"Answer: **{data['answer']}**")
        else:
            st.error("Error while receiving response from server.")
    else:
        st.warning("Please enter your question!")

st.markdown("### Example Questions")
st.markdown("- **What percentage of passengers were male on the Titanic?**")
st.markdown("- **Show me a histogram of passenger ages**")
st.markdown("- **What was the average ticket fare?**")
st.markdown("- **How many passengers embarked from each port?**")
