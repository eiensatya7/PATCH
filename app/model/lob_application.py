from pydantic import BaseModel


class LobApplication(BaseModel):
    """
    Represents a Line of Business (LOB) application configuration.

    This model corresponds to the lob_applications table in the database
    and contains configuration for monitoring and error handling.
    """

    lob_app_id: int | None = None  # Auto-incremented primary key
    application_name: str | None = None
    lob: str | None = None
    auto_resolve: bool = True
    environment: str
    git_remote_url: str
    lookup_branch_pattern: str = "LATEST_RELEASE"
    filter_pii: bool = False
    created_ts: str | None = None  # ISO 8601 format string
    updated_ts: str | None = None # ISO 8601 format string
    notification_dls: str
    app_info_actuator_url: str | None = None  # URL for application info actuator
    jira_projects_url: str | None = None  # URL for Jira projects
    app_dynamics_url: str | None = None  # URL for AppDynamics