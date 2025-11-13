from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

@dataclass
class Student:
    student_id: str
    nombre: str
    apellidos: str
    clase_id: str
    tipo_comensal: str  # FIJO | FIJO_DISCONTINUO | EXTRA
    dias_semana: Optional[str]  # For discontinuous meal plans (e.g., "1,3,5" for Mon,Wed,Fri)
    activo: bool
    viene_hoy: bool
    alergias: Optional[str] = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class Class:
    clase_id: str
    nombre: str
    total_students: int = 0
    students_eating_today: int = 0
    created_at: Optional[datetime] = None

@dataclass
class Teacher:
    teacher_id: str
    username: str
    password_hash: str
    nombre: str
    apellidos: str
    active: bool = True
    created_at: Optional[datetime] = None
