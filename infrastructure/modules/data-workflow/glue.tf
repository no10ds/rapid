resource "aws_glue_catalog_database" "catalogue_db" {
  name = "${var.resource-name-prefix}_catalogue_db"
}
