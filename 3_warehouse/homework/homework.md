# Module 3 Homework

ATTENTION: At the end of the submission form, you will be required to include a link to your GitHub repository or other public code-hosting site. This repository should contain your code for solving the homework. If your solution includes code that is not in file format (such as SQL queries or shell commands), please include these directly in the README file of your repository.

<b><u>Important Note:</b></u> <p> For this homework we will be using the 2022 Green Taxi Trip Record Parquet Files from the New York
City Taxi Data found here: </br> https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page </br>
If you are using orchestration such as Mage, Airflow or Prefect do not load the data into Big Query using the orchestrator.</br> 
Stop with loading the files into a bucket. </br></br>
<u>NOTE:</u> You will need to use the PARQUET option files when creating an External Table</br>

<b>SETUP:</b></br>
Create an external table using the Green Taxi Trip Records Data for 2022. </br>
Create a table in BQ using the Green Taxi Trip Records for 2022 (do not partition or cluster this table). </br>
</p>

## Questions

### Question 1

What is count of records for the 2022 Green Taxi Data??

- 65,623,481
- **840,402**
- 1,936,423
- 253,647

#### Explanantion

Instead of grabbing file download links directly from a GitHub repository, they're parsed using BeatifulSoup HTML parser:

```python
soup = BeautifulSoup(response, features='html.parser')
```

A loop is then executed to rip download links that include "green_tripdata_2022" in the URL:

```python
for i, link in enumerate(soup.findAll('a')):
    href = link.get('href')
    if 'green_tripdata_2022' in href:
        x = pd.read_parquet(href)
```

Once all 2022 files are concatenated into single dataframe, it results in total record count of **840,402**.

See *1_files_for_2022_load.py* for full process.

### Question 2

Write a query to count the distinct number of PULocationIDs for the entire dataset on both the tables. What is the estimated amount of data that will be read when this query is executed on the External Table and the Table?

- **0 MB for the External Table and 6.41MB for the Materialized Table**
- 18.82 MB for the External Table and 47.60 MB for the Materialized Table
- 0 MB for the External Table and 0MB for the Materialized Table
- 2.14 MB for the External Table and 0MB for the Materialized Table

#### Explanation

Dataset is loaded in date partitions as follows (see *green_2020q4_to_gcs_partitioned_2*), resulting in 368 file in total:

```python
for date in data['lpep_pickup_date'].unique():
    df = data[data['lpep_pickup_date']==date]
    pa_table = pa.Table.from_pandas(df)

    object_key = f"{BUCKET_NAME}/{TABLE_NAME}/{TABLE_NAME}_{date}.parquet"

    with pq.ParquetWriter(object_key, pa_table.schema, filesystem=gcs) as w:
        w.write_table(pa_table)
```

While the above did take considerable trial and error, the files were finally loaded as compatible `.parquet` file type, and an **un**partitioned external table was created to read them:

```sql
CREATE OR REPLACE EXTERNAL TABLE `abstract-ring-412516`.ny_taxi.external_green_2022
OPTIONS (
  FORMAT=PARQUET,
  URIS=['gs://dez2024-dez-data-lake/green_taxi_data_2022/*.parquet']
);

```

Executing the above and then running the below query yielded subsequent estimate:

```sql
SELECT COUNT(DISTINCT pu_location_id) FROM `abstract-ring-412516`.ny_taxi.external_green_2022;
```

> This query will process 0 B when run.

The next piece was answered with the following:

```sql
SELECT COUNT(DISTINCT pu_location_id) FROM `abstract-ring-412516`.ny_taxi.green_2022;
```

> This query will process 6.41 MB when run.

### Question 3

How many records have a fare_amount of 0?

- 12,488
- 128,219
- 112
- **1,622**

#### Explanation

This is a simple query:

```sql
SELECT COUNT(*) FROM `abstract-ring-412516`.ny_taxi.green_2022 WHERE fare_amount = 0;
```

### Question 4

What is the best strategy to make an optimized table in Big Query if your query will always order the results by PUlocationID and filter based on lpep_pickup_datetime? (Create a new table with this strategy)

- Cluster on lpep_pickup_datetime, Partition by PUlocationID
- **Partition by lpep_pickup_datetime, Cluster on PUlocationID**
- Partition by lpep_pickup_datetime, Partition by PUlocationID
- Cluster on by lpep_pickup_datetime, Cluster on PUlocationID

#### Explanation

Whereas partitions segregate chunks of data, clusters merely order them. To optimize queries based upon lpep_pickup_datetime column, that requires a `PARTITION BY lpep_pickup_datetime` statement; the clustering can be set using `CLUSTER BY pu_location_id` (note that I converted columns to Snake Case). Full statement:

```sql
CREATE OR REPLACE TABLE `abstract-ring-412516`.ny_taxi.green_2022_partitioned
PARTITION BY lpep_pickup_datetime
CLUSTER BY pu_location_id
AS SELECT * FROM `abstract-ring-412516`.ny_taxi.external_green_2022;
```

*BigQuery didn't like lpep_pickup_datetime, so I used lpep_pickup_date in its place in actuality.*

### Question 5

Write a query to retrieve the distinct PULocationID between lpep_pickup_datetime 06/01/2022 and 06/30/2022 (inclusive). Use the materialized table you created earlier in your FROM clause and note the estimated bytes. Now change the table in the from clause to the partitioned table you created for question 4 and note the estimated bytes processed. What are these values? Choose the answer which most closely matches. 

- 22.82 MB for non-partitioned table and 647.87 MB for the partitioned table
- **12.82 MB for non-partitioned table and 1.12 MB for the partitioned table**
- 5.63 MB for non-partitioned table and 0 MB for the partitioned table
- 10.31 MB for non-partitioned table and 10.31 MB for the partitioned table

#### Explanation

For the non-partitioned table, that's easy enough to check:

```sql
SELECT COUNT(DISTINCT pu_location_id) FROM `abstract-ring-412516`.ny_taxi.green_2022 WHERE lpep_pickup_date BETWEEN '2022-06-01' AND '2022-06-30';
```

> This query will process 12.82 MB when run.

The partiioned table is created as follows, using the existing external_green_2022 table:

```sql
CREATE OR REPLACE TABLE `abstract-ring-412516`.ny_taxi.green_2022_partitioned
PARTITION BY lpep_pickup_date
CLUSTER BY pu_location_id
AS SELECT * FROM `abstract-ring-412516`.ny_taxi.external_green_2022;
```

Once populated, it's a simple enough query:

```sql
SELECT COUNT(DISTINCT pu_location_id) FROM `abstract-ring-412516`.ny_taxi.green_2022_partitioned WHERE lpep_pickup_date BETWEEN '2022-06-01' AND '2022-06-30';
```

> This query will process 1.12 MB when run.

### Question 6

Where is the data stored in the External Table you created?

- Big Query
- **GCP Bucket**
- Big Table
- Container Registry

#### Explanation

This is in the definition of the external table at creation:

```sql
URIS=['gs://dez2024-dez-data-lake/green_taxi_data_2022/*.parquet']
```

This is why there are 0 B returned by the query estimator, as the data itself does not *live* in the table--it's simply presented as one.

### Question 7

It is best practice in Big Query to always cluster your data:

- True
- **False**

#### Explanation

Per [Google Cloud website](https://cloud.google.com/bigquery/docs/clustered-tables),

> When you query a clustered table, you don't receive an accurate query cost estimate before query execution because the number of storage blocks to be scanned is not known before query execution. The final cost is determined after query execution is complete and is based on the specific storage blocks that were scanned.

This is a tricky one. From a performance standpoint, yes, it's better; however, it does render the cost more uncertain. As business are generally going to take cost into consideration, this may not be necessary on all tables--it depends on whether the cost of clustering outweighs the cost of processing. In the vast majority of cases... it will.

### Question 8 (BONUS)

No Points.

Write a `SELECT COUNT(*)` query from the materialized table you created. How many bytes does it estimate will be read? Why?

**0 B**

#### Explanation

`COUNT(*)` returns the number of rows, a number that is already stored in the table metadata at creation; therefore, the table does not need to be parsed again.
