terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "7.19.0"
    }
  }
}

provider "google" {
  credentials = file(var.credentials)
  project     = var.project
  region      = var.region
  zone        = var.zone
}

resource "google_storage_bucket" "auto-expire" {
  name          = var.gcs_bucket_name
  location      = var.gcs_location
  force_destroy = true
}

resource "google_bigquery_dataset" "datasets" {
  for_each   = var.bq_datasets
  dataset_id = each.key
  location   = each.value.location
}
