from fastapi.testclient import TestClient
from main import app, analyze_titanic_data, generate_chart, df

client = TestClient(app)


def test_ask_question_text():
    response = client.get(
        "/ask", params={"question": "What percentage of passengers were male on the Titanic?"}
    )
    assert response.status_code == 200
    assert "answer" in response.json()
    assert "%" in response.json()["answer"]


def test_ask_question_histogram():
    response = client.get(
        "/ask", params={"question": "Show me a histogram of passenger ages"}
    )
    assert response.status_code == 200
    assert "image" in response.json()


def test_analyze_titanic_data_percentage():
    result = analyze_titanic_data("percentage of passengers were male")
    assert isinstance(result, str)
    assert "%" in result


def test_analyze_titanic_data_histogram():
    result = analyze_titanic_data("histogram of passenger ages")
    assert isinstance(result, dict)
    assert "image" in result


def test_analyze_titanic_data_fare():
    result = analyze_titanic_data("average ticket fare")
    assert isinstance(result, str)
    assert "average ticket fare" in result.lower()


def test_analyze_titanic_data_embarked():
    result = analyze_titanic_data("passengers embarked from each port")
    assert isinstance(result, str)
    assert "Embarked counts" in result


def test_generate_chart():
    img_data = generate_chart(df, "Age")
    assert isinstance(img_data, str)
    assert len(img_data) > 0


def test_ask_question_no_param():
    response = client.get("/ask")
    assert response.status_code == 422
