from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class OnboardRequest(BaseModel):
    application_name: Optional[str] = None
    lob: Optional[str] = None
    auto_resolve: bool = True
    environment: str
    git_remote_url: str
    lookup_branch_pattern: str = "LATEST_RELEASE"
    filter_pii: bool = False
    notification_dls: str


