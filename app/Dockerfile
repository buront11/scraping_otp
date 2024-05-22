# ベースイメージを選択
FROM python:3.10

# 必要なパッケージのインストール
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /app
ENV FLASK_APP=app

COPY . /app

EXPOSE 5000

# CMD ["python", "app.py"]
CMD ["uwsgi", "--ini", "/app/app.ini"]