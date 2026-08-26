locals {
  bucket_full_name = "${var.bucket_name}-${var.environment}-${random_id.bucket_suffix.hex}"

  common_labels = merge(
    {
      environment = var.environment
      managed_by  = "terraform"
    },
    var.labels
  )
}
