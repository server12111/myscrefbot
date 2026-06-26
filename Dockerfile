FROM python:3.11-slim

WORKDIR /app/gfhjgffg

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY gfhjgffg/ .

RUN mkdir -p images

CMD ["python", "main.py"]
