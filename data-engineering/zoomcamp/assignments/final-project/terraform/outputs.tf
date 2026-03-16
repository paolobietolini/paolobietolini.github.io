output "gcs_bucket_name" {
  value       = google_storage_bucket.datalake.name
  description = "Data lake bucket name"
}

output "gcs_bucket_url" {
  value       = google_storage_bucket.datalake.url
  description = "Data lake bucket URL"
}

output "bq_dataset_id" {
  value       = google_bigquery_dataset.reconciliation.dataset_id
  description = "BigQuery dataset ID"
}
