# Credentials
variable "credentials" {
  default     = "../secrets/secret_zcmp-final.json"
  description = "GCP Service Account secrets"
}

# Project
variable "project" {
  default     = "zmcp-final"
  description = "GCP Project ID"
}
variable "region" {
  description = "Project Location"
  default     = "europe-west1"
}

variable "zone" {
  default     = "EU"
  description = "Project Location"
}


# Big Query
variable "bq_location" {
  default     = "EU"
}
variable "bq_datasets" {
  type = map(object({
    location = string
  }))
  default = {
    raw_backend = { location = "EU" }
    raw_ga4     = { location = "US" }
  }
}

# Google Cloud Storage
variable "gcs_location" {
  default = "EU"
  description = "GCS Location"     
}

variable "gcs_bucket_name" {
  default     = "raw_backend_data"
  description = "GCS Bucket Name"
}

variable "gcs_storage_class" {
  default     = "STANDARD"
  description = "GCS Storage Class"
}

