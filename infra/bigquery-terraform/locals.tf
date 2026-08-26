locals {
  common_labels = merge(
    {
      environment = var.environment
      managed_by  = "terraform"
    },
    var.labels
  )
}
