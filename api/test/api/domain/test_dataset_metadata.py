from copy import deepcopy
from unittest.mock import Mock

from api.application.services.schema_service import SchemaService
from api.common.config.aws import DATA_BUCKET
from api.domain.dataset_metadata import DatasetMetadata


class TestDatasetMetadata:
    def setup_method(self):
        self.dataset_metadata = DatasetMetadata(
            "layer",
            "domain",
            "DATASET",
            3,
        )

    def test_dataset_location_with_version(self):
        assert self.dataset_metadata.dataset_location() == "data/layer/domain/dataset/3"

    def test_dataset_location_without_version(self):
        assert (
            self.dataset_metadata.dataset_location(with_version=False)
            == "data/layer/domain/dataset"
        )

    def test_raw_data_path(self):
        assert (
            self.dataset_metadata.raw_data_path("filename.csv")
            == "raw_data/layer/domain/dataset/3/filename.csv"
        )

    def test_raw_data_location(self):
        assert (
            self.dataset_metadata.raw_data_location()
            == "raw_data/layer/domain/dataset/3"
        )

    def test_glue_table_prefix(self):
        assert self.dataset_metadata.glue_table_prefix() == "layer_domain_dataset_"

    def test_glue_table_name(self):
        assert self.dataset_metadata.glue_table_name() == "layer_domain_dataset_3"

    def test_s3_path(self):
        assert (
            self.dataset_metadata.s3_path()
            == f"s3://{DATA_BUCKET}/data/layer/domain/dataset/"
        )

    def test_s3_file_location(self):
        assert (
            self.dataset_metadata.s3_file_location()
            == f"s3://{DATA_BUCKET}/data/layer/domain/dataset/3"
        )

    def test_construct_raw_dataset_uploads_location(self):
        assert (
            self.dataset_metadata.construct_raw_dataset_uploads_location()
            == "raw_data/layer/domain/dataset"
        )

    def test_set_version_when_version_not_present(self):
        dataset_metadata = DatasetMetadata("layer", "domain", "dataset")
        schema_service = SchemaService()
        schema_service.get_latest_schema_version = Mock(return_value=11)
        dataset_metadata.set_version(schema_service)
        assert dataset_metadata.version == 11

    def test_set_version_when_version_exists(self):
        original_version = deepcopy(self.dataset_metadata.version)
        self.dataset_metadata.set_version(SchemaService())
        assert original_version == self.dataset_metadata.version

    def test_get_fields(self):
        assert self.dataset_metadata.get_fields() == [
            "layer",
            "domain",
            "dataset",
            "version",
        ]
