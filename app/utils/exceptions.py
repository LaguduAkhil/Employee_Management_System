"""Custom exceptions for the application."""


class AppException(Exception):
    """Base exception for the application."""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AuthenticationError(AppException):
    """Raised when authentication fails."""
    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(message, 401)


class InvalidCredentialsError(AppException):
    """Raised when credentials are invalid."""
    def __init__(self, message: str = "Invalid email or password"):
        super().__init__(message, 401)


class AuthorizationError(AppException):
    """Raised when user doesn't have permission."""
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, 403)


class UserAlreadyExistsError(AppException):
    """Raised when user already exists."""
    def __init__(self, message: str = "User already exists"):
        super().__init__(message, 409)


class EmployeeNotFoundError(AppException):
    """Raised when employee is not found."""
    def __init__(self, message: str = "Employee not found"):
        super().__init__(message, 404)


class EmployeeAlreadyExistsError(AppException):
    """Raised when employee already exists."""
    def __init__(self, message: str = "Employee already exists"):
        super().__init__(message, 409)


class DepartmentNotFoundError(AppException):
    """Raised when department is not found."""
    def __init__(self, message: str = "Department not found"):
        super().__init__(message, 404)


class DepartmentAlreadyExistsError(AppException):
    """Raised when department already exists."""
    def __init__(self, message: str = "Department already exists"):
        super().__init__(message, 409)


class LeaveNotFoundError(AppException):
    """Raised when leave request is not found."""
    def __init__(self, message: str = "Leave request not found"):
        super().__init__(message, 404)


class AttendanceNotFoundError(AppException):
    """Raised when attendance record is not found."""
    def __init__(self, message: str = "Attendance record not found"):
        super().__init__(message, 404)


class InvalidInputError(AppException):
    """Raised when input is invalid."""
    def __init__(self, message: str = "Invalid input"):
        super().__init__(message, 400)


class TokenExpiredError(AppException):
    """Raised when JWT token is expired."""
    def __init__(self, message: str = "Token expired"):
        super().__init__(message, 401)


class InvalidTokenError(AppException):
    """Raised when JWT token is invalid."""
    def __init__(self, message: str = "Invalid token"):
        super().__init__(message, 401)
