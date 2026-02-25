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
    raw_backend   = { location = "EU" }
    raw_ga4       = { location = "US" }
    raw_ecommerce = { location = "EU" }
  }
}

