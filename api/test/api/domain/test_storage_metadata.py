from api.common.config.aws import DATA_BUCKET
from api.domain.storage_metadata import StorageMetaData


class TestStorageMetaData:
    def setup_method(self):
        self.dataset_meta_data = StorageMetaData(
            "DOMAIN",
            "DATASET",
            3,
            "Some test base description",
        )

    def test_file_location(self):
        assert self.dataset_meta_data.file_location() == "data/DOMAIN/DATASET/3"

    def test_dataset_location(self):
        assert self.dataset_meta_data.dataset_location() == "data/DOMAIN/DATASET"

    def test_raw_data_location(self):
        assert (
            self.dataset_meta_data.raw_data_path("filename.csv")
            == "raw_data/DOMAIN/DATASET/3/filename.csv"
        )

    def test_glue_table_prefix(self):
        assert self.dataset_meta_data.glue_table_prefix() == "DOMAIN_DATASET_"

    def test_glue_table_name(self):
        assert self.dataset_meta_data.glue_table_name() == "DOMAIN_DATASET_3"

    def test_s3_path(self):
        assert (
            self.dataset_meta_data.s3_path()
            == f"s3://{DATA_BUCKET}/data/DOMAIN/DATASET/"
        )

    def test_construct_dataset_location(self):
        assert (
            self.dataset_meta_data.construct_dataset_location() == "data/DOMAIN/DATASET"
        )

    def test_construct_raw_dataset_uploads_location(self):
        assert (
            self.dataset_meta_data.construct_raw_dataset_uploads_location()
            == "raw_data/DOMAIN/DATASET"
        )

    def test_construct_schema_dataset_location(self):
        assert (
            self.dataset_meta_data.construct_schema_dataset_location("PROTECTED")
            == "data/schemas/PROTECTED/DOMAIN/DATASET"
        )
