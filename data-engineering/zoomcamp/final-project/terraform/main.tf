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

resource "google_bigquery_dataset" "datasets" {
  for_each   = var.bq_datasets
  dataset_id = each.key
  location   = each.value.location
}
