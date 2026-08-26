output "bucket_name" {
  description = "The name of the created Cloud Storage bucket."
  value       = google_storage_bucket.this.name
}

output "bucket_url" {
  description = "The gs:// URL of the bucket."
  value       = google_storage_bucket.this.url
}

output "bucket_self_link" {
  description = "The URI of the created bucket."
  value       = google_storage_bucket.this.self_link
}

output "bucket_location" {
  description = "The location of the bucket."
  value       = google_storage_bucket.this.location
}
