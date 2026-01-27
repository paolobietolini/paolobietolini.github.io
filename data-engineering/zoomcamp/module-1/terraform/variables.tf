variable "credentials" {
  default     = "./secrets/de-terraform-test-keys.json" # You can use export GOOGLE_CREDENTIALS as well or use the Terraform file function
  description = "GCP SA credentials"
}

variable "project" {
  default     = "de-terraform-test"
  description = "GCP Project ID"
}
variable "region" {
  description = "Project Location"
  default     = "europe-central2"
}

variable "location" {
  default     = "EU"
  description = "Project Location"
}
variable "bq_dataset_name" {
  default     = "demo_dataset"
  description = "BQ Dataset Name"

}

variable "bq_location" {
  default     = "EU"
  description = "BQ Location"
}

variable "gcs_bucket_name" {
  default     = "de-terraform-test-tf-bucket"
  description = "GCS Bucket Name"
}

variable "gcs_storage_class" {
  default     = "STANDARD"
  description = "GCS Storage Class"
}
