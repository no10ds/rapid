class SchemaAlreadyExistsException(Exception):
    pass


class JobFailedException(Exception):
    def __init__(self, message, data):
        self.message = message
        self.data = data


class UnableToFetchJobStatusException(Exception):
    def __init__(self, message, data):
        self.message = message
        self.data = data


class DataFrameUploadFailedException(Exception):
    def __init__(self, message, data):
        self.message = message
        self.data = data


class DataFrameUploadValidationException(Exception):
    pass


class DatasetInfoFailedException(Exception):
    def __init__(self, message, data):
        self.message = message
        self.data = data


class DatasetNotFoundException(Exception):
    def __init__(self, message, data):
        self.message = message
        self.data = data


class SchemaGenerationFailedException(Exception):
    def __init__(self, message, data):
        self.message = message
        self.data = data


class SchemaCreateFailedException(Exception):
    def __init__(self, message, data):
        self.message = message
        self.data = data


class SchemaUpdateFailedException(Exception):
    def __init__(self, message, data):
        self.message = message
        self.data = data


class CannotFindCredentialException(Exception):
    pass


class AuthenticationErrorException(Exception):
    pass


class SchemaInitialisationException(Exception):
    pass


class ColumnNotDifferentException(Exception):
    pass


class InvalidPermissionsException(Exception):
    pass


class SubjectAlreadyExistsException(Exception):
    pass


class SubjectNotFoundException(Exception):
    pass


class SubjectDeletionFailedException(Exception):
    pass


class InvalidDomainNameException(Exception):
    pass


class DomainConflictException(Exception):
    pass
