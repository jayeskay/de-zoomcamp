# Module 1 Homework

## Docker & SQL

In this homework we'll prepare the environment and practice with Docker and SQL

### Question 1. Knowing docker tags

Run the command to get information on Docker:

```docker --help```

Now run the command to get help on the "docker build" command:

```docker build --help```

Do the same for "docker run".

Which tag has the following text? - *Automatically remove the container when it exits* 

- `--delete`
- `--rc`
- `--rmc`
- **`--rm`**

#### Explanation

You can find this by searching output of `docker build --help`.

### Question 2. Understanding docker first run 

Run docker with the python:3.9 image in an interactive mode and the entrypoint of bash.

Now check the python modules that are installed (use `pip list`). 

What is version of the package *wheel*?

- **0.42.0**
- 1.0.0
- 23.0.1
- 58.1.0

#### Explanation

You can find this by running an interactive container with `docker run -it --entrypoint=bash python:3.9`, followed by `pip list` to get packages and respective versions.

Alternatively, can also configure Dockerfile as shown, then build image with `docker build -t entrypoint:bash` (arbitrary tag):

```Dockerfile
FROM python:3.9
ENTRYPOINT ["bash"]
```

...and then run `docker run -it entrypoint:bash` and execute `pip list`.

## Prepare Postgres

Run Postgres and load data as shown in the videos. We'll use the green taxi trips from September 2019:

```bash
wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-09.csv.gz
```

You will also need the dataset with zones:

```bash
wget https://s3.amazonaws.com/nyc-tlc/misc/taxi+_zone_lookup.csv
```

Download this data and put it into Postgres (with jupyter notebooks or with a pipeline).

### Question 3. Count records 

How many taxi trips were totally made on September 18th 2019?

Tip: started and finished on 2019-09-18. 

Remember that `lpep_pickup_datetime` and `lpep_dropoff_datetime` columns are in the format timestamp (date and hour+min+sec) and not in date.

- 15767
- **15612**
- 15859
- 89009

#### Explanation

Using the below...

```sql
SELECT
    lpep_pickup_datetime::DATE,
    lpep_dropoff_datetime::DATE,
    COUNT(*)

FROM
    green_taxi_data_201909

WHERE
    lpep_pickup_datetime::DATE = '2019-09-18'
    AND lpep_dropoff_datetime::DATE = '2019-09-18'

GROUP BY
    lpep_pickup_datetime::DATE,
    lpep_dropoff_datetime::DATE;
```

...I get the following:

| lpep_pickup_datetime  | lpep_dropoff_datetime | count |
| ---                   | ---                   | ---   |
| 2019-09-18            | 2019-09-18            | 15612 |

### Question 4. Largest trip for each day

Which was the pick up day with the largest trip distance. Use the pick up time for your calculations.

- 2019-09-18
- 2019-09-16
- **2019-09-26**
- 2019-09-21

#### Explanation

Using the below...

```sql
SELECT
    lpep_pickup_datetime,
    trip_distance

FROM
    green_taxi_data_201909

ORDER BY
    trip_distance DESC

LIMIT 1;
```

...I get the following:

| lpep_pickup_datetime  | trip_distance |
| ---                   | ---           |
| 2019-09-26 19:32:52   | 341.64        |

However, what I think the question is getting at is the overall distance for an entire day:

```sql
SELECT
    lpep_pickup_datetime::DATE,
    SUM(trip_distance)
    
FROM
    green_taxi_data_201909

GROUP BY
    lpep_pickup_datetime::DATE

ORDER BY
    SUM(trip_distance) DESC

LIMIT 1;
```

Thus:

| lpep_pickup_datetime  | trip_distance     |
| ---                   | ---               |
| 2019-09-26            | 58759.9400000002  |

### Question 5. The number of passengers

Consider lpep_pickup_datetime in '2019-09-18' and ignoring Borough has Unknown

Which were the 3 pick up Boroughs that had a sum of total_amount superior to 50000?
 
- **"Brooklyn" "Manhattan" "Queens"**
- "Bronx" "Brooklyn" "Manhattan"
- "Bronx" "Manhattan" "Queens" 
- "Brooklyn" "Queens" "Staten Island"

#### Explanation

I used the following:

```sql
SELECT
    lpep_pickup_datetime::DATE,
    b."Borough",
    SUM(a.total_amount) AS total_amount_sum

FROM
    green_taxi_data_201909 a

    LEFT JOIN taxi_zone_lookup b ON
        a."PULocationID" = b."LocationID"

WHERE
    a.lpep_pickup_datetime::DATE = '2019-09-18'
    AND b."Borough" != 'Unknown'

GROUP BY
    lpep_pickup_datetime::DATE,
    b."Borough"

ORDER BY
    SUM(a.total_amount) DESC

LIMIT 3;
```

This resulted in the following output:

| lpep_pickup_datetime  | Borough   | total_amount_sum  |
| ---                   | ---       | ---               |
| 2019-09-18            | Brooklyn  | 96333.23999999909 |
| 2019-09-18            | Manhattan | 92271.29999999839 |
| 2019-09-18            | Queens    | 78671.70999999884 |

### Question 6. Largest tip

For the passengers picked up in September 2019 in the zone name Astoria which was the drop off zone that had the largest tip? We want the name of the zone, not the id.

Note: it's not a typo, it's `tip`, not `trip`.

- Central Park
- Jamaica
- **JFK Airport**
- Long Island City/Queens Plaza

#### Explanation

I used the following, which uses an inner join to filter for Astoria pickup zone, then lists the dropoff zones and individual (not summed) tip amounts, with the latter in descending order:

```sql
SELECT
    b."Zone" AS pickup_zone,
    c."Zone" AS dropoff_zone,
    a.tip_amount

FROM
    green_taxi_data_201909 a

    INNER JOIN taxi_zone_lookup b ON
        a."PULocationID" = b."LocationID"
        AND b."Zone" = 'Astoria'

    INNER JOIN taxi_zone_lookup c ON
        a."DOLocationID" = c."LocationID"

ORDER BY
    a.tip_amount DESC

LIMIT 3;
```

This resulted in the following output:

|pickup_zone|dropoff_zone|tip_amount|
|---|---|---|
|Astoria|JFK Airport|62.31|
|Astoria|Woodside|30.0|
|Astoria|Kips Bay|28.0|

## Terraform

In this section homework we'll prepare the environment by creating resources in GCP with Terraform.

In your VM on GCP/Laptop/GitHub Codespace install Terraform. Copy the files from the course repo [here](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/week_1_basics_n_setup/1_terraform_gcp/terraform) to your VM/Laptop/GitHub Codespace.

Modify the files as necessary to create a GCP Bucket and Big Query Dataset.

### Question 7. Creating Resources

After updating the main.tf and variable.tf files run:

```bash
terraform apply
```

Paste the output of this command into the homework submission form.

#### Explanation

I built out the infrastrucutre in AWS rather than GCP, as that's what I'm using for the course.

```terraform
aws_s3_bucket.data-lake-bucket: Refreshing state... [id=dez2024-dez-data-lake]
aws_s3_bucket_versioning.bucket_versioning: Refreshing state... [id=dez2024-dez-data-lake]

Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
  + create

Terraform will perform the following actions:

  # aws_redshift_cluster.redshift-cluster will be created
  + resource "aws_redshift_cluster" "redshift-cluster" {
      + allow_version_upgrade               = true
      + apply_immediately                   = false
      + aqua_configuration_status           = (known after apply)
      + arn                                 = (known after apply)
      + automated_snapshot_retention_period = 1
      + availability_zone                   = (known after apply)
      + cluster_identifier                  = "dez-redshift-cluster"
      + cluster_namespace_arn               = (known after apply)
      + cluster_nodes                       = (known after apply)
      + cluster_parameter_group_name        = (known after apply)
      + cluster_public_key                  = (known after apply)
      + cluster_revision_number             = (known after apply)
      + cluster_subnet_group_name           = (known after apply)
      + cluster_type                        = "single-node"
      + cluster_version                     = "1.0"
      + database_name                       = "dez_db"
      + default_iam_role_arn                = (known after apply)
      + dns_name                            = (known after apply)
      + encrypted                           = false
      + endpoint                            = (known after apply)
      + enhanced_vpc_routing                = (known after apply)
      + iam_roles                           = (known after apply)
      + id                                  = (known after apply)
      + kms_key_id                          = (known after apply)
      + maintenance_track_name              = "current"
      + manage_master_password              = true
      + manual_snapshot_retention_period    = -1
      + master_password_secret_arn          = (known after apply)
      + master_password_secret_kms_key_id   = (known after apply)
      + master_username                     = "dez"
      + node_type                           = "dc2.large"
      + number_of_nodes                     = 1
      + port                                = 5439
      + preferred_maintenance_window        = (known after apply)
      + publicly_accessible                 = true
      + skip_final_snapshot                 = false
      + tags_all                            = (known after apply)
      + vpc_security_group_ids              = (known after apply)
    }

Plan: 1 to add, 0 to change, 0 to destroy.

Do you want to perform these actions?
  Terraform will perform the actions described above.
  Only 'yes' will be accepted to approve.

  Enter a value: yes

aws_redshift_cluster.redshift-cluster: Creating...
aws_redshift_cluster.redshift-cluster: Still creating... [10s elapsed]
aws_redshift_cluster.redshift-cluster: Still creating... [20s elapsed]
aws_redshift_cluster.redshift-cluster: Still creating... [30s elapsed]
aws_redshift_cluster.redshift-cluster: Still creating... [40s elapsed]
aws_redshift_cluster.redshift-cluster: Still creating... [50s elapsed]
aws_redshift_cluster.redshift-cluster: Still creating... [1m0s elapsed]
aws_redshift_cluster.redshift-cluster: Still creating... [1m10s elapsed]
aws_redshift_cluster.redshift-cluster: Still creating... [1m20s elapsed]
aws_redshift_cluster.redshift-cluster: Still creating... [1m30s elapsed]
aws_redshift_cluster.redshift-cluster: Still creating... [1m40s elapsed]
aws_redshift_cluster.redshift-cluster: Still creating... [1m50s elapsed]
aws_redshift_cluster.redshift-cluster: Still creating... [2m0s elapsed]
aws_redshift_cluster.redshift-cluster: Still creating... [2m10s elapsed]
aws_redshift_cluster.redshift-cluster: Still creating... [2m20s elapsed]
aws_redshift_cluster.redshift-cluster: Still creating... [2m30s elapsed]
aws_redshift_cluster.redshift-cluster: Creation complete after 2m31s [id=dez-redshift-cluster]

Apply complete! Resources: 1 added, 0 changed, 0 destroyed.
```

## Submitting the solutions

* Form for submitting: https://courses.datatalks.club/de-zoomcamp-2024/homework/hw01
* You can submit your homework multiple times. In this case, only the last submission will be used. 

Deadline: 29 January, 23:00 CET
