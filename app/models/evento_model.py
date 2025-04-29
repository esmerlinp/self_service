from dataclasses import dataclass
from typing import Optional, Any

@dataclass
class EventoModel:
    type: str
    code: int
    name: str
    date: str
    department: str
    oldPosition: Optional[str] = None
    positionName: Optional[str] = None
    positionDescription: Optional[str] = None
    image: Optional[str] = None
    accion: Optional[str] = None
    
    def get_message(self) -> str:
        
        if self.type == "birthday":
            return f"¡Feliz cumpleaños, {self.name}! 🎉"
        
        elif self.type == "promotion":
            return f"¡Felicidades, {self.name}! Has sido promovido a {self.positionName}."
    
    
        
