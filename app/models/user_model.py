from dataclasses import dataclass
from typing import Optional, Any

@dataclass
class UserModel:
    userId: int
    name: str
    fullName: str
    email: str
    isadmin: bool
    companyId: int
    companyName: str
    role: Optional[str] = None

    