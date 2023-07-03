BASE_API_PATH = "/api"
BASE_REGEX = "^[a-zA-Z0-9_-]"
FILENAME_WITH_TIMESTAMP_REGEX = r"[a-zA-Z0-9:_\-]+.csv$"

CONTENT_ENCODING = "utf-8"
# https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types
VALID_FILE_MIME_TYPES = ["text/csv", "application/octest-stream"]
VALID_FILE_EXTENSIONS = ["csv", "parquet"]

TAG_KEYS_REGEX = BASE_REGEX + "{1,128}$"
TAG_VALUES_REGEX = BASE_REGEX + "{0,256}$"

COLUMN_NAME_REGEX = "[^a-z0-9_]+"
LOWERCASE_REGEX = r"^[a-z0-9_\-]+$"
LOWERCASE_ROUTE_DESCRIPTION = "Please note this parameter needs to be lowercase"

DATE_FORMAT_REGEX = "(%[Ymd][/-]%[Ymd][/-]%[Ymd]|%[Ym][/-]%[Ym])"

EMAIL_REGEX = (
    r"([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\"([]!#-[^-~ \t]|"
    r"(\\[\t -~]))+\")@([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\[[\t -Z^-~]*])"
)

USERNAME_REGEX = "[a-zA-Z][a-zA-Z0-9@._-]{2,127}"

DEFAULT_JOB_EXPIRY_DAYS = 1
UPLOAD_JOB_EXPIRY_DAYS = 7
QUERY_JOB_EXPIRY_DAYS = 1

QUERY_RESULTS_LINK_EXPIRY_SECONDS = 86400

MB_1 = 1024 * 1024
CHUNK_SIZE = 50
CHUNK_SIZE_MB = MB_1 * CHUNK_SIZE
PARQUET_CHUNK_SIZE = 10000
DATASET_QUERY_LIMIT = 100_000
