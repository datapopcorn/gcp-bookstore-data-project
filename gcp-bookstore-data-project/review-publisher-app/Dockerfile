FROM python:3.8-slim-buster

EXPOSE 8051

RUN apt-get update && apt-get install -y \
    build-essential \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /gcp_bookstore_app

COPY . /gcp_bookstore_app

RUN pip install -r requirements.txt

ENTRYPOINT ["streamlit", "run", "review_publisher_app.py", "--server.port=8051", "--server.address=0.0.0.0"]