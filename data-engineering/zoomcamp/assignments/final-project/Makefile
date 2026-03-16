.PHONY: setup infra generate airflow-up airflow-down run-all destroy help

help:            ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  %-16s %s\n", $$1, $$2}'

setup:           ## Install Python dependencies
	pip install -r data-generator/requirements.txt
	pip install -r dbt/requirements.txt

infra:           ## Provision GCP resources with Terraform
	cd terraform && terraform init && terraform apply -auto-approve

generate:        ## Generate fake order data locally
	cd data-generator && python generate_orders.py

upload:          ## Upload generated parquet files to GCS
	cd data-generator && python upload_to_gcs.py

airflow-up:      ## Start Airflow (Docker Compose)
	cd airflow && docker compose up -d --build

airflow-down:    ## Stop Airflow
	cd airflow && docker compose down

run-all:         ## Trigger the full reconciliation DAG
	cd airflow && docker compose exec airflow-webserver \
		airflow dags trigger reconciliation_dag

dbt-run:         ## Run dbt models manually (outside Airflow)
	cd dbt && dbt run --profiles-dir .

dbt-test:        ## Run dbt tests manually (outside Airflow)
	cd dbt && dbt test --profiles-dir .

destroy:         ## Tear down all GCP resources
	cd terraform && terraform destroy -auto-approve
