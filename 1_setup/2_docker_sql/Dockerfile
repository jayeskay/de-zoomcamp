FROM python:3.9

WORKDIR /app

COPY ingest_data.py ingest_data.py
COPY requirements.txt requirements.txt
COPY green_tripdata_2019-09.csv.gz green_tripdata_2019-09.csv.gz
COPY taxi_zone_lookup.csv taxi_zone_lookup.csv

RUN pip install -r requirements.txt

ENTRYPOINT ["bash"]
