class BaseAppException(Exception):
    def __init__(self, message, status_code: int = 500):
        self.message = message
        self.status_code = status_code


class AWSServiceError(BaseAppException):
    def __init__(self, message):
        super().__init__(message)


class AuthorisationError(BaseAppException):
    def __init__(self, message, status_code: int = 401):
        super().__init__(message, status_code)


class AuthenticationError(BaseAppException):
    def __init__(self, message, status_code: int = 403):
        super().__init__(message, status_code)


class UserError(BaseAppException):
    def __init__(self, message, status_code: int = 400):
        super().__init__(message, status_code)


class DomainNotEmptyError(BaseAppException):
    def __init__(self, message, status_code: int = 400):
        super().__init__(message, status_code)


class ConflictError(UserError):
    def __init__(self, message, status_code: int = 409):
        super().__init__(message, status_code)


class TooManyRequestsError(UserError):
    def __init__(self, message, status_code: int = 429):
        super().__init__(message, status_code)


class QueryExecutionError(AWSServiceError):
    def __init__(self, message):
        super().__init__(message)


# Could become a generic NotFoundError
class SchemaNotFoundError(UserError):
    def __init__(self, message, status_code: int = 404):
        super().__init__(message, status_code)


# Could just be UserError
class SchemaValidationError(UserError):
    pass

# TODO Pandera: set up column validation error
class ColumnValidationError(UserError):
    pass


class DatasetValidationError(UserError):
    pass


class UnprocessableDatasetError(UserError):
    pass


class InvalidFileUploadError(UserError):
    pass


# Specifically handled in global handler ~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class CredentialsUnavailableError(Exception):
    pass


class NotAuthorisedToViewPageError(Exception):
    pass


# Handled in code to modify behaviour and improve readability ~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class TableAlreadyExistsError(ConflictError):
    pass


class TableCreationError(AWSServiceError):
    pass


class TableDoesNotExistError(Exception):
    pass


class UnsupportedTypeError(Exception):
    pass
