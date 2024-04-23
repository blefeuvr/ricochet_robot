FROM python:3.10

WORKDIR /app

RUN apt-get update && apt-get install -y python3-opencv

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "api:app"]