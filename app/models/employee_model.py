from dataclasses import dataclass
from typing import Optional

@dataclass
class EmployeeModel:
    id: int
    firts_name: str
    last_name: str
    status_id: int
    status: str 
    birth_date: str
    full_name: str = ""
    second_last_name: Optional[str] = None
    middle_name: Optional[str] = None
    work_days: Optional[list] = None
    imageUrl: str = None
    cooworkers: Optional[list] = None