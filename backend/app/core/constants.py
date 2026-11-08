"""Application constants, system role definitions, permissions, and error codes."""

from enum import Enum


class RoleEnum(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MANAGER = "manager"
    DEVELOPER = "developer"


class DocumentStatus(str, Enum):
    DRAFT = "draft"
    PROCESSING = "processing"
    REVIEW_PENDING = "review_pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    GENERATED = "generated"
    ARCHIVED = "archived"


class SourceType(str, Enum):
    UPLOAD = "upload"
    PASTE = "paste"
    MANUAL = "manual"


class SectionType(str, Enum):
    TEXT = "text"
    LIST = "list"
    TABLE = "table"
    HEADING_ONLY = "heading_only"


class ContentSource(str, Enum):
    AI_EXTRACTED = "ai_extracted"
    USER_PROVIDED = "user_provided"
    AI_PLUS_USER = "ai_plus_user"
    SKIPPED = "skipped"


class ReviewStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CHANGES_REQUESTED = "changes_requested"


# Default Role Permissions Matrix
ROLE_PERMISSIONS = {
    RoleEnum.SUPER_ADMIN.value: [
        "*",  # Wildcard access to all features
    ],
    RoleEnum.ADMIN.value: [
        "users:read", "users:write", "users:delete",
        "departments:read", "departments:write", "departments:delete",
        "templates:read", "templates:write", "templates:delete", "templates:publish",
        "documents:read_all", "documents:write_all", "documents:delete_all",
        "admin:stats", "admin:audit_log", "admin:ai_usage",
    ],
    RoleEnum.MANAGER.value: [
        "users:read",
        "departments:read",
        "templates:read",
        "documents:read_department", "documents:write", "documents:read",
        "reviews:read", "reviews:write",
    ],
    RoleEnum.DEVELOPER.value: [
        "templates:read",
        "documents:read_own", "documents:write_own", "documents:delete_own",
        "documents:upload", "documents:generate", "documents:export",
    ],
}


class ErrorCode(str, Enum):
    # Auth
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    INVALID_TOKEN = "INVALID_TOKEN"
    FORBIDDEN = "FORBIDDEN"
    UNAUTHORIZED = "UNAUTHORIZED"
    USER_INACTIVE = "USER_INACTIVE"

    # Validation & Requests
    VALIDATION_ERROR = "VALIDATION_ERROR"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_ALREADY_EXISTS = "RESOURCE_ALREADY_EXISTS"
    INVALID_FILE_TYPE = "INVALID_FILE_TYPE"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"

    # Templates & Sections
    TEMPLATE_NOT_FOUND = "TEMPLATE_NOT_FOUND"
    TEMPLATE_VERSION_NOT_FOUND = "TEMPLATE_VERSION_NOT_FOUND"
    TEMPLATE_SECTION_NOT_FOUND = "TEMPLATE_SECTION_NOT_FOUND"
    SECTION_MANDATORY_CANNOT_SKIP = "SECTION_MANDATORY_CANNOT_SKIP"

    # Documents & Generation
    DOCUMENT_NOT_FOUND = "DOCUMENT_NOT_FOUND"
    DOCUMENT_ALREADY_GENERATED = "DOCUMENT_ALREADY_GENERATED"
    GENERATION_FAILED = "GENERATION_FAILED"
    AI_PROCESSING_FAILED = "AI_PROCESSING_FAILED"

    # System
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"

