1. create a new gcp project
`gcloud projects create `zmcp-final`
2. Create a service account 
```bash
gcloud iam service-accounts create sa-zmcp-final \
  --description="Service Account to operate with the ZMCP Final Project" \
  --display-name="ZMCP-final"

gcloud iam service-accounts keys create ./secret_zmcp-final.json \
    --iam-account=sa-zmcp-final@zmcp-final.iam.gserviceaccount.com`
```



2. create a terraform project in terraform/
  2.1 terraform validate
  2.2 terraform apply
  
3. Copy the GA4 dataset from the public Big Query dataset into my project
```sql
  CREATE TABLE `zmcp-final.raw_ga4.events` AS
  SELECT * FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
  WHERE _TABLE_SUFFIX BETWEEN '20201101' AND '20201231'
```
> NB: BigQuery does not allow cross-region CREATE TABLE AS SELECT -- the source and destination must be in the same region. So i had to create a US-based dataset
