from fastapi import FastAPI
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, Tool, AgentType
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import os
from dotenv import load_dotenv
import uvicorn
from functools import lru_cache

load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(openai_api_key=openai_key)

df = pd.read_csv("titanic.csv")

# Инструменты для LangChain
tools = [
    Tool(
        name="Titanic Data Analysis",
        func=lambda query: analyze_titanic_data(query),
        description="Use this tool to analyze the Titanic dataset and answer questions related to the dataset.",
    ),
]

# Инициализация агента
agent = initialize_agent(tools, llm, agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True, return_only_outputs=True)

app = FastAPI()

# Функция для генерации графиков
def generate_chart(df, column):
    plt.figure(figsize=(8, 4))
    sns.histplot(df[column], bins=20, kde=True)
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')


@lru_cache(maxsize=50)  # Храним 50 последних запросов в кэше
def cached_agent_response(query):
    return agent.invoke(query)


def analyze_titanic_data(query):
    # Обрабатываем простые вопросы напрямую
    if "percentage of passengers were male" in query:
        male_percentage = df[df["Sex"] == "male"].shape[0] / df.shape[0] * 100
        return f"{male_percentage:.2f}% of passengers were male."

    elif "histogram of passenger ages" in query:
        img_data = generate_chart(df, "Age")
        return {"image": img_data}

    elif "average ticket fare" in query:
        avg_fare = df["Fare"].mean()
        return f"The average ticket fare was {avg_fare:.2f}"

    elif "passengers embarked from each port" in query:
        embarked_counts = df["Embarked"].value_counts().to_dict()
        return f"Embarked counts: {embarked_counts}"

    # Если запрос сложный, используем кэш
    try:
        response = agent.invoke(query)

        # Проверяем тип данных
        if isinstance(response, dict):
            return response.get("output", "I couldn't find an answer.")
        elif isinstance(response, list):
            return " ".join(str(item) for item in response)
        elif isinstance(response, str):
            return response

        return "I couldn't process the response properly."

    except Exception as e:
        return f"Sorry, I couldn't understand that. Error: {str(e)}"

    return "Sorry, I couldn't understand that."


@app.get("/ask")
def ask_question(question: str):
    try:
        response = analyze_titanic_data(question)
        # Проверяем, является ли ответ словарем с изображением
        if isinstance(response, dict) and "image" in response:
            return response  # Возвращаем изображение как строку base64
        else:
            return {"answer": response}  # Возвращаем текстовый ответ
    except Exception as e:
        return {"answer": f"Error: {str(e)}"}

# Запуск FastAPI сервера
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
