from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class LobApplicationOld(BaseModel):
    """
    Represents a Line of Business (LOB) application configuration.
    
    This model corresponds to the lob_applications table in the database
    and contains configuration for monitoring and error handling.
    """
    
    lob_app_id: int = Field(..., description="Primary key identifier for the LOB application")
    application_name: Optional[str] = Field(None, max_length=100, description="Name of the application")
    lob: Optional[str] = Field(None, max_length=10, description="Line of business identifier")
    auto_resolve: bool = Field(True, description="Whether to automatically resolve issues")
    environment: str = Field(..., max_length=4, description="Environment (e.g., dev, test, prod)")
    git_remote_url: str = Field(..., max_length=255, description="Git repository remote URL")
    lookup_branch_pattern: str = Field(
        "LATEST_RELEASE", 
        max_length=50, 
        description="Pattern for looking up the branch"
    )
    filter_pii: bool = Field(False, description="Whether to filter personally identifiable information")
    created_ts: datetime = Field(..., description="Timestamp when the record was created")
    updated_ts: datetime = Field(..., description="Timestamp when the record was last updated")
    notification_dls: str = Field(..., description="Distribution list for notifications")

    class Config:
        # This allows the model to work with ORM objects
        from_attributes = True
        # Example of how the model should look
        json_schema_extra = {
            "example": {
                "lob_app_id": 1,
                "application_name": "user-service",
                "lob": "retail",
                "auto_resolve": True,
                "environment": "prod",
                "git_remote_url": "https://github.com/company/user-service.git",
                "lookup_branch_pattern": "LATEST_RELEASE",
                "filter_pii": False,
                "created_ts": "2024-01-15T10:30:00Z",
                "updated_ts": "2024-01-15T10:30:00Z",
                "notification_dls": "team-alerts@company.com"
            }
        }


class LobApplicationCreate(BaseModel):
    """
    Model for creating a new LOB application.
    Excludes auto-generated fields like ID and timestamps.
    """
    
    application_name: Optional[str] = Field(None, max_length=100)
    lob: Optional[str] = Field(None, max_length=10)
    auto_resolve: bool = Field(True)
    environment: str = Field(..., max_length=4)
    git_remote_url: str = Field(..., max_length=255)
    lookup_branch_pattern: str = Field("LATEST_RELEASE", max_length=50)
    filter_pii: bool = Field(False)
    notification_dls: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "application_name": "user-service",
                "lob": "retail",
                "auto_resolve": True,
                "environment": "prod",
                "git_remote_url": "https://github.com/company/user-service.git",
                "lookup_branch_pattern": "LATEST_RELEASE",
                "filter_pii": False,
                "notification_dls": "team-alerts@company.com"
            }
        }


class LobApplicationUpdate(BaseModel):
    """
    Model for updating an existing LOB application.
    All fields are optional to allow partial updates.
    """
    
    application_name: Optional[str] = Field(None, max_length=100)
    lob: Optional[str] = Field(None, max_length=10)
    auto_resolve: Optional[bool] = None
    environment: Optional[str] = Field(None, max_length=4)
    git_remote_url: Optional[str] = Field(None, max_length=255)
    lookup_branch_pattern: Optional[str] = Field(None, max_length=50)
    filter_pii: Optional[bool] = None
    notification_dls: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "auto_resolve": False,
                "notification_dls": "updated-team-alerts@company.com"
            }
        }
