FROM python:3.9

WORKDIR /app
COPY pipeline.py pipeline.py
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "pipeline.py"]
