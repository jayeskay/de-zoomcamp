# Module 2: Orchestration

## S3

### Extract: *1_extract_data.py*

Pull data from source DataTalksClub repository: `https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/`

Specifically, the below subset of files (Q4):

- green_tripdata_2020-10.csv.gz
- green_tripdata_2020-11.csv.gz
- green_tripdata_2020-12.csv.gz

### Transform: *2_transform_data.py*

Split `lpep_pickup_datetime` and `lpep_dropoff_datetime` into the following:

- `lpep_pickup_date`
- `lpep_pickup_time`
- `lpep_dropoff_date`
- `lpep_dropoff_time`

Snowflake intakes `datetime[ns]` data types oddly and stores as integer--most effective workaround is the latter column split.

Create assertions:

- No records with passenger count of 0;
- No records with trip distance of 0;
- No records with vendor identifiers other than: 1, 2.

### Load: *3_load_to_s3.py*

Partition files by date:

```python
df_partitioned = df[df['lpep_pickup_date'] == date]
```

Each batch (partition) loaded as .parquet file to S3 location:

- Bucket: `dez2024-dez-mage`
- Key: `ny_taxi/green_taxi_data/green_taxi_data_2020Q4/{PREFIX}_{date.strftime('%Y%m%d')}.parquet`

## Snowflake

### Extract: *4_extract_from_s3.py*

Pull partitioned data from storage location in S3:

- Bucket: `dez2024-dez-mage`
- Key: `ny_taxi/green_taxi_data/green_taxi_data_2020Q4/`

Files are concatenated if found:

```python
for i in contents:
    if '.parquet' in i['Key']:
        df_i = S3.with_config(config).load(BUCKET, i['Key'])                
        df = pd.concat([df, df_i])
```

### Transform: *5_transform_columns.py*

Use regex to conform column names to `snake_case` convention:

```python
data.columns = (re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', col) for col in data.columns)
data.columns = (re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', col) for col in data.columns)
data.columns = (col.lower() for col in data.columns)
```

### Load: *6_load_to_snowflake.py*

Push finalized dataset to Snowflake:

- Database = `DE_ZOOMCAMP`
- Schema = `NY_TAXI`
- Table: `GREEN_TAXI_DATA_2020Q4`
