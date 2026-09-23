# diet-recommendation-fastapi-streamlit

Diet Recommendation system with LLM pipeline embedding RAG feature using fastapi in backend and streamlit in frontend

## Installtion and running process

```
python -m venv venv
pip install fastapi uvicorn requests streamlit matplotlib pandas numpy google-genai python-dotenv pytest httpx
pip freeze > requirements.txt
pip install -r requirements.txt
pip list
python main_backend.py
streamlit run main_frontend.py

```

## DOCKER Specifics

```

docker-compose up --build


```
