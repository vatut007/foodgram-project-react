FROM python:3.7-slim
WORKDIR /app
COPY requirements.txt /app
RUN apt update && \
    apt upgrade -y && \
    apt -y install python3-pip python3-cffi python3-brotli libpango-1.0-0 libpangoft2-1.0-0
RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt --no-cache-dir
COPY foodgram/ /app
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ] 