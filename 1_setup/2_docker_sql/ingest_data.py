from sqlalchemy import create_engine
import pandas as pd

engine = create_engine('postgresql://postgres:postgres@pg-database:5432/ny_taxi')

# Import raw data as; use chunking due to file size
green_taxi_data_201909_iter = pd.read_csv(
    filepath_or_buffer='green_tripdata_2019-09.csv.gz',
    compression='gzip',
    iterator=True,
    chunksize=100000
)

# Imoprt location lookup detail (for JOIN)
taxi_zone_lookup = pd.read_csv('taxi_zone_lookup.csv')

counter = 0

with engine.connect() as conn:
    for chunk in green_taxi_data_201909_iter:
        if counter == 0:
            chunk.to_sql(name='green_taxi_data_201909', if_exists='replace', index=False, con=conn)
            print(f"EXECUTING REPLACE FOR counter = {counter}")

        else:
            chunk.to_sql(name='green_taxi_data_201909', if_exists='append', index=False, con=conn)
            print(f"EXECUTING APPEND FOR counter = {counter}")

        counter += 1

    taxi_zone_lookup.to_sql(name='taxi_zone_lookup', if_exists='replace', index=False, con=conn)
