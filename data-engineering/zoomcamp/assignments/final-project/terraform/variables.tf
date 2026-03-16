variable "credentials" {
  default     = "~/.secrets/zmcp-final-5928b2c488d2.json"
  description = "Path to GCP service account key JSON"
}

variable "project" {
  default     = "zmcp-final"
  description = "GCP Project ID"
}

variable "region" {
  default     = "us-central1"
  description = "GCP region"
}

variable "location" {
  default     = "US"
  description = "Location for GCS and BigQuery (must be US to query GA4 public dataset)"
}

variable "gcs_bucket_name" {
  default     = "zmcp-final-reconciliation-datalake"
  description = "GCS bucket for raw and cleaned data"
}

variable "bq_dataset_name" {
  default     = "reconciliation"
  description = "BigQuery dataset for reconciliation tables"
}
