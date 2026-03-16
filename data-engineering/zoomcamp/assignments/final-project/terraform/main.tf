terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 7.16"
    }
  }
}

provider "google" {
  credentials = file(var.credentials)
  project     = var.project
  region      = var.region
}

# Data Lake bucket
resource "google_storage_bucket" "datalake" {
  name          = var.gcs_bucket_name
  location      = var.location
  force_destroy = true

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }

  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "AbortIncompleteMultipartUpload"
    }
  }
}

# BigQuery dataset (US location to join with GA4 public dataset)
resource "google_bigquery_dataset" "reconciliation" {
  dataset_id = var.bq_dataset_name
  location   = var.location

  delete_contents_on_destroy = true
}
