variable "credentials" {
  description = "Path to GCP service account key JSON"
}

variable "project" {
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
  description = "GCS bucket for raw and cleaned data"
}

variable "bq_dataset_name" {
  default     = "reconciliation"
  description = "BigQuery dataset for reconciliation tables"
}
