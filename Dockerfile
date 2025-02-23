FROM selenium/standalone-chrome:latest

USER seluser
WORKDIR /app

COPY requirements.txt .
RUN sudo pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:$PORT app:app"]