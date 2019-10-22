FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7-alpine3.8

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
ADD ./backend/listener/ ./

CMD python listener.py
