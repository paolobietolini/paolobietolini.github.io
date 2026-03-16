.PHONY: setup infra generate upload spark-clean create-tables dbt-run dbt-test run-local airflow-up airflow-down run-all destroy help

help:            ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  %-18s %s\n", $$1, $$2}'

setup:           ## Install Python dependencies
	pip install -r data-generator/requirements.txt
	pip install -r dbt/requirements.txt
	pip install pyspark==3.5.*
	cd dbt && dbt deps

infra:           ## Provision GCP resources with Terraform
	cd terraform && terraform init && terraform apply -auto-approve

generate:        ## Generate fake order data locally
	cd data-generator && python generate_orders.py

upload:          ## Upload generated parquet files to GCS
	cd data-generator && python upload_to_gcs.py

spark-clean:     ## Run Spark cleaning jobs locally
	spark-submit --master "local[*]" \
		--jars https://storage.googleapis.com/hadoop-lib/gcs/gcs-connector-hadoop3-latest.jar \
		--conf spark.hadoop.google.cloud.auth.service.account.json.keyfile=$(GOOGLE_APPLICATION_CREDENTIALS) \
		spark/clean_orders.py
	spark-submit --master "local[*]" \
		--jars https://storage.googleapis.com/hadoop-lib/gcs/gcs-connector-hadoop3-latest.jar \
		--conf spark.hadoop.google.cloud.auth.service.account.json.keyfile=$(GOOGLE_APPLICATION_CREDENTIALS) \
		spark/extract_ga4_purchases.py

create-tables:   ## Create BigQuery external tables
	bq query --use_legacy_sql=false --project_id=zmcp-final \
		'CREATE OR REPLACE EXTERNAL TABLE `zmcp-final.reconciliation.ext_orders` OPTIONS (format = "PARQUET", uris = ["gs://zmcp-final-reconciliation-datalake/cleaned/orders/*.parquet"]);'
	bq query --use_legacy_sql=false --project_id=zmcp-final \
		'CREATE OR REPLACE EXTERNAL TABLE `zmcp-final.reconciliation.ext_ga4_purchases` OPTIONS (format = "PARQUET", uris = ["gs://zmcp-final-reconciliation-datalake/cleaned/ga4_purchases/*.parquet"]);'

dbt-run:         ## Run dbt models
	cd dbt && dbt run --profiles-dir .

dbt-test:        ## Run dbt tests
	cd dbt && dbt test --profiles-dir .

run-local:       ## Run the full pipeline locally (no Docker/Airflow)
	$(MAKE) generate
	$(MAKE) upload
	$(MAKE) spark-clean
	$(MAKE) create-tables
	$(MAKE) dbt-run
	$(MAKE) dbt-test
	@echo "\nPipeline complete!"

airflow-up:      ## Start Airflow (Docker Compose)
	cd airflow && docker compose up -d --build

airflow-down:    ## Stop Airflow
	cd airflow && docker compose down

run-all:         ## Trigger the full reconciliation DAG via Airflow
	cd airflow && docker compose exec airflow-webserver \
		airflow dags trigger reconciliation_dag

destroy:         ## Tear down all GCP resources
	cd terraform && terraform destroy -auto-approve
