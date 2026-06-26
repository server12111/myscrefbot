FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY gfhjgffg/ ./gfhjgffg/

RUN mkdir -p gfhjgffg/images

CMD ["python", "gfhjgffg/main.py"]
