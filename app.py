import streamlit as st
import requests
import base64
from io import BytesIO
from PIL import Image

# Заголовок
st.title("Titanic Chatbot")

# Поле ввода для пользователя
question = st.text_input("Ask about Titanic passengers:")

# Кнопка для отправки запроса
if st.button("Ask"):
    if question:
        # Отправка запроса на FastAPI сервер
        response = requests.get("https://titanic-chatbot-production.up.railway.app/ask", params={"question": question})

        if response.status_code == 200:
            data = response.json()

            # Проверяем, пришло ли изображение или текст
            if "image" in data:
                # Декодируем изображение из Base64
                try:
                    image_data = base64.b64decode(data["image"])  # Декодируем из base64
                    image = Image.open(BytesIO(image_data))  # Преобразуем в изображение
                    st.image(image, caption="Histogram of Passenger Ages", use_container_width=True)
                except Exception as e:
                    st.error(f"Error decoding or displaying the image: {e}")
            elif "answer" in data:
                # Если пришел текстовый ответ
                st.write(f"Answer: **{data['answer']}**")
        else:
            st.error("Error while receiving response from server.")
    else:
        st.warning("Please enter your question!")

# Пример вопросов для бота
st.markdown("### Example Questions")
st.markdown("- **What percentage of passengers were male on the Titanic?**")
st.markdown("- **Show me a histogram of passenger ages**")
st.markdown("- **What was the average ticket fare?**")
st.markdown("- **How many passengers embarked from each port?**")
