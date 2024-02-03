# Module 2 Homework

For the homework, we'll be working with the _green_ taxi dataset located here:

`https://github.com/DataTalksClub/nyc-tlc-data/releases/tag/green/download`

The goal will be to construct an ETL pipeline that loads the data, performs some transformations, and writes the data to a database (and Google Cloud!).

- Create a new pipeline, call it `green_taxi_etl`
- Add a data loader block and use Pandas to read data for the final quarter of 2020 (months `10`, `11`, `12`).
    - You can use the same datatypes and date parsing methods shown in the course.
    - `BONUS`: load the final three months using a for loop and `pd.concat`
- Add a transformer block and perform the following:
    - Remove rows where the passenger count is equal to 0 _or_ the trip distance is equal to zero.
    - Create a new column `lpep_pickup_date` by converting `lpep_pickup_datetime` to a date.
    - Rename columns in Camel Case to Snake Case, e.g. `VendorID` to `vendor_id`.
    - Add three assertions:
        - `vendor_id` is one of the existing values in the column (currently)
        - `passenger_count` is greater than 0
        - `trip_distance` is greater than 0
- Using a Postgres data exporter (SQL or Python), write the dataset to a table called `green_taxi` in a schema `mage`. Replace the table if it already exists.
- Write your data as Parquet files to a bucket in GCP, partioned by `lpep_pickup_date`. Use the `pyarrow` library!
- Schedule your pipeline to run daily at 5AM UTC.

## Questions

### Question 1. Data Loading

Once the dataset is loaded, what's the shape of the data?

- **266,855 rows x 20 columns**
- 544,898 rows x 18 columns
- 544,898 rows x 20 columns
- 133,744 rows x 20 columns

#### Explanation

Concatenating the below `.csv.gz` files after loading to DataFrame results in the total record count selected above:

- green_tripdata_2020-10.csv.gz,
- green_tripdata_2020-11.csv.gz,
- green_tripdata_2020-12.csv.gz

This concatenation is handled by creating empty DataFrame, then adding the individual results from files:

```python
green_taxi_data = pd.concat([green_taxi_data, df])
```

See *1_extract_data.py* for full process.

### Question 2. Data Transformation

Upon filtering the dataset where the passenger count is equal to 0 _or_ the trip distance is equal to zero, how many rows are left?

- 544,897 rows
- 266,855 rows
- **139,370 rows**
- 266,856 rows

#### Explanation

The below assignment in transformation step reduces original input to the selected answer:

```python
data_transformed = data[(data['passenger_count'] > 0) & (data['trip_distance'] > 0) & (data['VendorID'].isin([1, 2]))]
```

The assumption of foreknowledge of vendor IDs (1, 2) is made in this step.

See *2_transform_data.py* for full process.

### Question 3. Data Transformation

Which of the following creates a new column `lpep_pickup_date` by converting `lpep_pickup_datetime` to a date?

- data = data['lpep_pickup_datetime'].date
- data('lpep_pickup_date') = data['lpep_pickup_datetime'].date
- **data['lpep_pickup_date'] = data['lpep_pickup_datetime'].dt.date**
- data['lpep_pickup_date'] = data['lpep_pickup_datetime'].dt().date()

#### Explanation

Pandas Series objects that have been cast to Datetime objects via `pandas.to_datetime()` method are able to have date and time data extracted, as these are just attributes.

The following block proved to be most effective approach for pushing Snowflake-compatible data, as used in *2_transform_data.py*:

```python
data_transformed['lpep_pickup_date'] = data_transformed['lpep_pickup_datetime'].dt.date
data_transformed['lpep_pickup_time'] = data_transformed['lpep_pickup_datetime'].dt.time
data_transformed['lpep_dropoff_date'] = data_transformed['lpep_dropoff_datetime'].dt.date
data_transformed['lpep_dropoff_time'] = data_transformed['lpep_dropoff_datetime'].dt.time
```

Although this does add extra columns, these can be consolidated in Snowflake.

### Question 4. Data Transformation

What are the existing values of `VendorID` in the dataset?

- 1, 2, or 3
- **1 or 2**
- 1, 2, 3, 4
- 1

#### Explanation

Querying dataset for unique vendor IDs yields the options of `NULL`, `1`, and `2`. Originally interpreted question to mean, "Vendor IDs that are not null."

### Question 5. Data Transformation

How many columns need to be renamed to snake case?

- 3
- 6
- 2
- **4**

#### Explanation

Columns and applied convention are as follows:

- VendorID &rarr; vendor_id
- RatecodeID &rarr; ride_id
- PULocationID &rarr; pu_location_id
- DOLocationID &rarr; do_location_id

Used approach from [Stack Overflow](https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case) in *5_transform_columns.py*:

```python
data.columns = (re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', col) for col in data.columns)
data.columns = (re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', col) for col in data.columns)
data.columns = (col.lower() for col in data.columns)
```

### Question 6. Data Exporting

Once exported, how many partitions (folders) are present in Google Cloud?

- **96**
- 56
- 67
- 108

#### Explanation

The partitioning piece is handled by below block when exporting to S3 in *3_load_to_s3.py*:

```python
for date in df['lpep_pickup_date'].unique():
    df_partitioned = df[df['lpep_pickup_date'] == date]

    S3.with_config(ConfigFileLoader(config_path, config_profile)).export(
        df=df_partitioned,
        bucket_name=BUCKET,
        object_key=f"{PREFIX}_{date.strftime('%Y%m%d')}.parquet"
    )
```

This data is then recombined in *4_extract_from_s3.py*, transformed in *5_transform_columns.py*, and finally loaded to Snowflake in *6_load_to_snowflake.py*.
