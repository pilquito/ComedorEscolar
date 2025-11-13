import sqlite3
import logging
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from werkzeug.security import generate_password_hash
from models import Student, Class, Teacher

import os

# Database path - usar variable de entorno para Docker, o directorio actual como fallback
DATABASE_PATH = os.environ.get('DATABASE_PATH', os.path.join(os.getcwd(), 'cafeteria.db'))
# Asegurar que el directorio existe
os.makedirs(os.path.dirname(DATABASE_PATH) if os.path.dirname(DATABASE_PATH) else '.', exist_ok=True)
DATABASE_FILE = DATABASE_PATH

def get_db_connection():
    """Get database connection with row factory for dict-like access"""
    try:
        conn = sqlite3.connect(DATABASE_FILE, timeout=30)
        conn.row_factory = sqlite3.Row
        # Enable foreign keys and WAL mode for better concurrency
        conn.execute('PRAGMA foreign_keys = ON')
        conn.execute('PRAGMA journal_mode = WAL')
        conn.execute('PRAGMA synchronous = NORMAL')
        return conn
    except Exception as e:
        logging.error(f"Error connecting to database: {e}")
        raise

def verify_database_integrity():
    """Verify database integrity and log status"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if tables exist and have data
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        logging.info(f"Database tables found: {tables}")
        
        # Count records in each main table
        for table in ['students', 'classes', 'teachers', 'daily_meals']:
            if table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                logging.info(f"Table {table} has {count} records")
        
        # Check daily_meals data for today
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("SELECT COUNT(*) FROM daily_meals WHERE date = ?", (today,))
        today_meals = cursor.fetchone()[0]
        logging.info(f"Daily meals for {today}: {today_meals}")
        
        conn.close()
        return True
    except Exception as e:
        logging.error(f"Database integrity check failed: {e}")
        return False

def init_db():
    """Initialize database with required tables"""
    logging.info(f"Initializing database at: {DATABASE_FILE}")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create teachers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teachers (
            teacher_id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            nombre TEXT NOT NULL,
            apellidos TEXT NOT NULL,
            active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create classes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS classes (
            clase_id TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            apellidos TEXT NOT NULL,
            clase_id TEXT NOT NULL,
            tipo_comensal TEXT NOT NULL CHECK (tipo_comensal IN ('FIJO', 'FIJO_DISCONTINUO', 'EXTRA')),
            dias_semana TEXT,
            activo BOOLEAN DEFAULT 1,
            viene_hoy BOOLEAN DEFAULT 0,
            alergias TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (clase_id) REFERENCES classes (clase_id)
        )
    ''')
    
    # Create daily meal records table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_meals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            date TEXT NOT NULL,
            meal_type TEXT NOT NULL CHECK (meal_type IN ('FIJO', 'FIJO_DISCONTINUO', 'EXTRA')),
            eats_today BOOLEAN DEFAULT 1,
            confirmed BOOLEAN DEFAULT 0,
            is_absent BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students (student_id),
            UNIQUE(student_id, date)
        )
    ''')
    
    # Create teacher_classes relationship table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teacher_classes (
            teacher_id TEXT,
            clase_id TEXT,
            assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (teacher_id, clase_id),
            FOREIGN KEY (teacher_id) REFERENCES teachers (teacher_id),
            FOREIGN KEY (clase_id) REFERENCES classes (clase_id)
        )
    ''')
    
    # Insert default teacher if none exists
    cursor.execute('SELECT COUNT(*) FROM teachers')
    if cursor.fetchone()[0] == 0:
        from werkzeug.security import generate_password_hash
        default_password = generate_password_hash('teacher123')
        cursor.execute('''
            INSERT INTO teachers (teacher_id, username, password_hash, nombre, apellidos)
            VALUES (?, ?, ?, ?, ?)
        ''', ('teacher001', 'profesor', default_password, 'Profesor', 'Demo'))
    
    # Add new columns to existing daily_meals table if they don't exist
    try:
        cursor.execute('ALTER TABLE daily_meals ADD COLUMN confirmed BOOLEAN DEFAULT 0')
        cursor.execute('ALTER TABLE daily_meals ADD COLUMN is_absent BOOLEAN DEFAULT 0')
        logging.info("Added confirmation columns to daily_meals table")
    except sqlite3.OperationalError as e:
        # Columns probably already exist
        if "duplicate column name" not in str(e):
            logging.debug(f"Column addition error (probably already exist): {e}")
    
    conn.commit()
    conn.close()
    logging.info("Database initialized successfully")
    
    # Verify database integrity after initialization
    verify_database_integrity()

class StudentDB:
    @staticmethod
    def get_all_students() -> List[Student]:
        """Get all students from database"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM students ORDER BY apellidos, nombre')
        rows = cursor.fetchall()
        conn.close()
        
        students = []
        for row in rows:
            student = Student(
                student_id=row['student_id'],
                nombre=row['nombre'],
                apellidos=row['apellidos'],
                clase_id=row['clase_id'],
                tipo_comensal=row['tipo_comensal'],
                dias_semana=row['dias_semana'],
                activo=bool(row['activo']),
                viene_hoy=bool(row['viene_hoy']),
                alergias=row['alergias'] or "",
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
            students.append(student)
        return students
    
    @staticmethod
    def get_students_by_class(clase_id: str) -> List[Student]:
        """Get all students in a specific class"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM students WHERE clase_id = ? ORDER BY apellidos, nombre', (clase_id,))
        rows = cursor.fetchall()
        conn.close()
        
        students = []
        for row in rows:
            student = Student(
                student_id=row['student_id'],
                nombre=row['nombre'],
                apellidos=row['apellidos'],
                clase_id=row['clase_id'],
                tipo_comensal=row['tipo_comensal'],
                dias_semana=row['dias_semana'],
                activo=bool(row['activo']),
                viene_hoy=bool(row['viene_hoy']),
                alergias=row['alergias'] or "",
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
            students.append(student)
        return students
    
    @staticmethod
    def get_student_by_id(student_id: str) -> Optional[Student]:
        """Get student by ID"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM students WHERE student_id = ?', (student_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Student(
                student_id=row['student_id'],
                nombre=row['nombre'],
                apellidos=row['apellidos'],
                clase_id=row['clase_id'],
                tipo_comensal=row['tipo_comensal'],
                dias_semana=row['dias_semana'],
                activo=bool(row['activo']),
                viene_hoy=bool(row['viene_hoy']),
                alergias=row['alergias'] or "",
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
        return None
    
    @staticmethod
    def create_or_update_student(student: Student) -> bool:
        """Create new student or update existing one"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Check if student exists
            cursor.execute('SELECT student_id FROM students WHERE student_id = ?', (student.student_id,))
            exists = cursor.fetchone()
            
            if exists:
                # Update existing student
                cursor.execute('''
                    UPDATE students 
                    SET nombre = ?, apellidos = ?, clase_id = ?, tipo_comensal = ?, 
                        dias_semana = ?, activo = ?, viene_hoy = ?, alergias = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE student_id = ?
                ''', (student.nombre, student.apellidos, student.clase_id, student.tipo_comensal,
                      student.dias_semana, student.activo, student.viene_hoy, student.alergias,
                      student.student_id))
            else:
                # Create new student
                cursor.execute('''
                    INSERT INTO students (student_id, nombre, apellidos, clase_id, tipo_comensal,
                                        dias_semana, activo, viene_hoy, alergias)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (student.student_id, student.nombre, student.apellidos, student.clase_id,
                      student.tipo_comensal, student.dias_semana, student.activo, 
                      student.viene_hoy, student.alergias))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error creating/updating student: {e}")
            conn.rollback()
            conn.close()
            return False
    
    @staticmethod
    def update_student_attendance(student_id: str, viene_hoy: bool) -> bool:
        """Update student's daily attendance"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE students SET viene_hoy = ?, updated_at = CURRENT_TIMESTAMP
                WHERE student_id = ?
            ''', (viene_hoy, student_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error updating student attendance: {e}")
            conn.rollback()
            conn.close()
            return False
    
    @staticmethod
    def update_student_meal_type(student_id: str, tipo_comensal: str, dias_semana: str = None) -> bool:
        """Update student's meal type and days"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE students SET tipo_comensal = ?, dias_semana = ?, updated_at = CURRENT_TIMESTAMP
                WHERE student_id = ?
            ''', (tipo_comensal, dias_semana, student_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error updating student meal type: {e}")
            conn.rollback()
            conn.close()
            return False

class ClassDB:
    @staticmethod
    def get_all_classes() -> List[Dict[str, Any]]:
        """Get all classes with student counts"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.clase_id, c.nombre,
                   COUNT(s.student_id) as total_students,
                   COUNT(CASE WHEN s.viene_hoy = 1 THEN 1 END) as students_eating_today
            FROM classes c
            LEFT JOIN students s ON c.clase_id = s.clase_id AND s.activo = 1
            GROUP BY c.clase_id, c.nombre
            ORDER BY c.nombre
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        classes = []
        for row in rows:
            classes.append({
                'clase_id': row['clase_id'],
                'nombre': row['nombre'],
                'total_students': row['total_students'],
                'students_eating_today': row['students_eating_today']
            })
        return classes
    
    @staticmethod
    def get_class_by_id(clase_id: str) -> Optional[Dict[str, Any]]:
        """Get class by ID with student counts"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.clase_id, c.nombre,
                   COUNT(s.student_id) as total_students,
                   COUNT(CASE WHEN s.viene_hoy = 1 THEN 1 END) as students_eating_today
            FROM classes c
            LEFT JOIN students s ON c.clase_id = s.clase_id AND s.activo = 1
            WHERE c.clase_id = ?
            GROUP BY c.clase_id, c.nombre
        ''', (clase_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'clase_id': row['clase_id'],
                'nombre': row['nombre'],
                'total_students': row['total_students'],
                'students_eating_today': row['students_eating_today']
            }
        return None
    
    @staticmethod
    def create_class(clase_id: str, nombre: str) -> bool:
        """Create new class"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('INSERT INTO classes (clase_id, nombre) VALUES (?, ?)', (clase_id, nombre))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error creating class: {e}")
            conn.rollback()
            conn.close()
            return False

class DailyMealDB:
    @staticmethod
    def create_daily_meal_record(student_id: str, date: str, meal_type: str, eats_today: bool = True) -> bool:
        """Create or update daily meal record"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO daily_meals (student_id, date, meal_type, eats_today, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (student_id, date, meal_type, eats_today))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error creating daily meal record: {e}")
            conn.rollback()
            conn.close()
            return False
    
    @staticmethod
    def get_daily_meals_by_date(date: str) -> List[Dict[str, Any]]:
        """Get all meal records for a specific date"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT dm.*, s.nombre, s.apellidos, s.clase_id
            FROM daily_meals dm
            JOIN students s ON dm.student_id = s.student_id
            WHERE dm.date = ? AND dm.eats_today = 1
            ORDER BY s.clase_id, s.apellidos, s.nombre
        ''', (date,))
        
        rows = cursor.fetchall()
        conn.close()
        
        meals = []
        for row in rows:
            meals.append({
                'student_id': row['student_id'],
                'nombre': row['nombre'],
                'apellidos': row['apellidos'],
                'clase_id': row['clase_id'],
                'meal_type': row['meal_type'],
                'date': row['date'],
                'eats_today': bool(row['eats_today']),
                'confirmed': bool(row['confirmed']),
                'is_absent': bool(row['is_absent'])
            })
        return meals
    
    @staticmethod
    def get_daily_meal_counts_by_class(date: str) -> Dict[str, Dict[str, int]]:
        """Get meal counts by class for a specific date with confirmation status"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.clase_id, dm.meal_type, 
                   COUNT(*) as total_count,
                   COUNT(CASE WHEN dm.confirmed = 1 AND dm.is_absent = 0 AND s.viene_hoy = 1 THEN 1 END) as confirmed_count,
                   COUNT(CASE WHEN dm.is_absent = 1 OR (s.viene_hoy = 0) THEN 1 END) as absent_count,
                   COUNT(CASE WHEN dm.confirmed = 0 AND s.viene_hoy = 1 AND dm.is_absent = 0 THEN 1 END) as pending_count
            FROM daily_meals dm
            JOIN students s ON dm.student_id = s.student_id
            WHERE dm.date = ?
            GROUP BY s.clase_id, dm.meal_type
        ''', (date,))
        
        rows = cursor.fetchall()
        conn.close()
        
        counts = {}
        for row in rows:
            clase_id = row['clase_id']
            meal_type = row['meal_type']
            
            if clase_id not in counts:
                counts[clase_id] = {
                    'FIJO': {'total': 0, 'confirmed': 0, 'absent': 0, 'pending': 0},
                    'FIJO_DISCONTINUO': {'total': 0, 'confirmed': 0, 'absent': 0, 'pending': 0},
                    'EXTRA': {'total': 0, 'confirmed': 0, 'absent': 0, 'pending': 0},
                    'totals': {'total': 0, 'confirmed': 0, 'absent': 0, 'pending': 0}
                }
            
            counts[clase_id][meal_type] = {
                'total': row['total_count'],
                'confirmed': row['confirmed_count'],
                'absent': row['absent_count'],
                'pending': row['pending_count']
            }
            
            # Update class totals
            counts[clase_id]['totals']['total'] += row['total_count']
            counts[clase_id]['totals']['confirmed'] += row['confirmed_count']
            counts[clase_id]['totals']['absent'] += row['absent_count']
            counts[clase_id]['totals']['pending'] += row['pending_count']
        
        return counts
    
    @staticmethod
    def mark_student_confirmed(student_id: str, date: str, is_absent: bool = False) -> bool:
        """Mark student as confirmed (present) or absent for a specific date"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # For absent students, ensure they still appear in statistics by keeping eats_today = 1
            # but set confirmed = 1 and is_absent = 1
            if is_absent:
                cursor.execute('''
                    UPDATE daily_meals 
                    SET confirmed = 1, is_absent = 1, eats_today = 1, updated_at = CURRENT_TIMESTAMP
                    WHERE student_id = ? AND date = ?
                ''', (student_id, date))
                logging.info(f"Marking student {student_id} as ABSENT for {date}")
            else:
                cursor.execute('''
                    UPDATE daily_meals 
                    SET confirmed = 1, is_absent = 0, updated_at = CURRENT_TIMESTAMP
                    WHERE student_id = ? AND date = ?
                ''', (student_id, date))
                logging.info(f"Marking student {student_id} as PRESENT for {date}")
            
            if cursor.rowcount == 0:
                # No daily meal record found, cannot confirm
                logging.error(f"No daily meal record found for student {student_id} on {date}")
                conn.close()
                return False
            
            # Synchronize with students table - if marked absent, set viene_hoy = 0
            if is_absent:
                cursor.execute('''
                    UPDATE students 
                    SET viene_hoy = 0, updated_at = CURRENT_TIMESTAMP
                    WHERE student_id = ?
                ''', (student_id,))
            else:
                # If confirmed present, set viene_hoy = 1
                cursor.execute('''
                    UPDATE students 
                    SET viene_hoy = 1, updated_at = CURRENT_TIMESTAMP
                    WHERE student_id = ?
                ''', (student_id,))
                
            conn.commit()
            conn.close()
            logging.info(f"Successfully updated student {student_id} confirmation status")
            return True
        except Exception as e:
            logging.error(f"Error marking student confirmation: {e}")
            conn.rollback()
            conn.close()
            return False
    
    @staticmethod
    def get_class_confirmation_status(clase_id: str, date: str) -> Dict[str, int]:
        """Get confirmation status for a specific class and date"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN dm.confirmed = 1 AND dm.is_absent = 0 AND s.viene_hoy = 1 THEN 1 END) as confirmed,
                COUNT(CASE WHEN dm.is_absent = 1 OR (s.viene_hoy = 0) THEN 1 END) as absent,
                COUNT(CASE WHEN dm.confirmed = 0 AND s.viene_hoy = 1 AND dm.is_absent = 0 THEN 1 END) as pending
            FROM daily_meals dm
            JOIN students s ON dm.student_id = s.student_id
            WHERE s.clase_id = ? AND dm.date = ?
        ''', (clase_id, date))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'total': row['total'],
                'confirmed': row['confirmed'],
                'absent': row['absent'],
                'pending': row['pending']
            }
        return {'total': 0, 'confirmed': 0, 'absent': 0, 'pending': 0}
    
    @staticmethod
    def get_student_confirmation_status(student_id: str, date: str) -> Dict[str, any]:
        """Get confirmation status for a specific student and date"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT confirmed, is_absent, eats_today
            FROM daily_meals 
            WHERE student_id = ? AND date = ?
        ''', (student_id, date))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'confirmed': bool(row['confirmed']),
                'is_absent': bool(row['is_absent']),
                'eats_today': bool(row['eats_today']),
                'is_validated': bool(row['confirmed'])  # Student is validated if confirmed (present or absent)
            }
        return {
            'confirmed': False,
            'is_absent': False,
            'eats_today': False,
            'is_validated': False
        }
    
    @staticmethod
    def unlock_student_validation(student_id: str, date: str) -> bool:
        """Unlock student validation to allow modifications"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE daily_meals 
                SET confirmed = 0, updated_at = CURRENT_TIMESTAMP
                WHERE student_id = ? AND date = ?
            ''', (student_id, date))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error unlocking student validation: {e}")
            conn.rollback()
            conn.close()
            return False
    
    @staticmethod
    def update_daily_meal_eats_today(student_id: str, date: str, eats_today: bool) -> bool:
        """Update eats_today status in daily_meals table"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Check if record exists
            cursor.execute('''
                SELECT id FROM daily_meals 
                WHERE student_id = ? AND date = ?
            ''', (student_id, date))
            
            existing_record = cursor.fetchone()
            
            if existing_record:
                # Update existing record
                cursor.execute('''
                    UPDATE daily_meals 
                    SET eats_today = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE student_id = ? AND date = ?
                ''', (eats_today, student_id, date))
            elif eats_today:  # Only create record if marking as eating today
                # Get student info for creating new record
                student = StudentDB.get_student_by_id(student_id)
                if student:
                    cursor.execute('''
                        INSERT INTO daily_meals (student_id, date, meal_type, eats_today, confirmed, is_absent, created_at, updated_at)
                        VALUES (?, ?, ?, ?, 0, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    ''', (student_id, date, student.tipo_comensal, eats_today))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error updating daily meal eats_today status: {e}")
            conn.rollback()
            conn.close()
            return False

class TeacherDB:
    @staticmethod
    def get_teacher_by_username(username: str) -> Optional[Teacher]:
        """Get teacher by username"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM teachers WHERE username = ? AND active = 1', (username,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Teacher(
                teacher_id=row['teacher_id'],
                username=row['username'],
                password_hash=row['password_hash'],
                nombre=row['nombre'],
                apellidos=row['apellidos'],
                active=bool(row['active']),
                created_at=row['created_at']
            )
        return None
    
    @staticmethod
    def get_teacher_by_id(teacher_id: str) -> Optional[Teacher]:
        """Get teacher by ID"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM teachers WHERE teacher_id = ?', (teacher_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Teacher(
                teacher_id=row['teacher_id'],
                username=row['username'],
                password_hash=row['password_hash'],
                nombre=row['nombre'],
                apellidos=row['apellidos'],
                active=bool(row['active']),
                created_at=row['created_at']
            )
        return None
    
    @staticmethod
    def get_all_teachers() -> List[Teacher]:
        """Get all teachers"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM teachers WHERE active = 1 ORDER BY apellidos, nombre')
        teachers = []
        for row in cursor.fetchall():
            teachers.append(Teacher(
                teacher_id=row['teacher_id'],
                username=row['username'],
                password_hash=row['password_hash'],
                nombre=row['nombre'],
                apellidos=row['apellidos'],
                active=bool(row['active']),
                created_at=row['created_at']
            ))
        conn.close()
        return teachers
    
    @staticmethod
    def create_teacher(teacher: Teacher) -> bool:
        """Create a new teacher"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO teachers (teacher_id, username, password_hash, nombre, apellidos, active)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (teacher.teacher_id, teacher.username, teacher.password_hash, 
                  teacher.nombre, teacher.apellidos, teacher.active))
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error creating teacher: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def assign_teacher_to_class(teacher_id: str, clase_id: str) -> bool:
        """Assign teacher to a class"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO teacher_classes (teacher_id, clase_id)
                VALUES (?, ?)
            ''', (teacher_id, clase_id))
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error assigning teacher to class: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def get_teacher_classes(teacher_id: str) -> List[str]:
        """Get classes assigned to a teacher"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT clase_id FROM teacher_classes 
            WHERE teacher_id = ?
        ''', (teacher_id,))
        classes = [row['clase_id'] for row in cursor.fetchall()]
        conn.close()
        return classes

# Función adicional para DailyMealDB
def __purge_daily_meals_impl(date: str, clase_id: str = None) -> int:
    """Delete daily meal records for a specific date and optionally class"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if clase_id:
            # Purge specific class for the date
            cursor.execute('''
                DELETE FROM daily_meals 
                WHERE date = ? AND student_id IN (
                    SELECT student_id FROM students WHERE clase_id = ?
                )
            ''', (date, clase_id))
        else:
            # Purge all records for the date
            cursor.execute('DELETE FROM daily_meals WHERE date = ?', (date,))
        
        deleted_count = cursor.rowcount
        conn.commit()
        return deleted_count
        
    except Exception as e:
        logging.error(f"Error purging daily meals: {e}")
        return 0
    finally:
        conn.close()

# Agregar la función a DailyMealDB
DailyMealDB.purge_daily_meals = staticmethod(__purge_daily_meals_impl)

# Función adicional para debug de fechas
def __get_all_dates_with_counts_impl() -> list:
    """Get all dates with meal counts from daily_meals table"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            date,
            COUNT(*) as total_meals,
            COUNT(CASE WHEN eats_today = 1 THEN 1 END) as eating_today,
            COUNT(CASE WHEN confirmed = 1 THEN 1 END) as confirmed,
            COUNT(CASE WHEN is_absent = 1 THEN 1 END) as absent
        FROM daily_meals 
        GROUP BY date 
        ORDER BY date DESC
    ''')
    
    dates = []
    for row in cursor.fetchall():
        dates.append({
            'date': row['date'],
            'total_meals': row['total_meals'],
            'eating_today': row['eating_today'],
            'confirmed': row['confirmed'],
            'absent': row['absent']
        })
    
    conn.close()
    return dates

DailyMealDB.get_all_dates_with_counts = staticmethod(__get_all_dates_with_counts_impl)

# Función para contar registros de un día específico
def __get_meals_count_for_date_impl(date_str: str) -> int:
    """Get count of imported meals for a specific date"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT COUNT(*) as count FROM daily_meals WHERE date = ?', (date_str,))
        result = cursor.fetchone()
        count = result['count'] if result else 0
        print(f"DEBUG: Meals count for {date_str}: {count}")  # Debug log
        return count
    except Exception as e:
        print(f"DEBUG: Error counting meals for {date_str}: {e}")
        return 0
    finally:
        conn.close()

DailyMealDB.get_meals_count_for_date = staticmethod(__get_meals_count_for_date_impl)

# Función para obtener clases con datos del día
def __get_classes_with_daily_data_impl(date_str: str) -> list:
    """Get classes that have imported daily meal data for a specific date"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            c.clase_id,
            c.nombre,
            COUNT(dm.student_id) as total_students,
            COUNT(CASE WHEN dm.confirmed = 1 AND dm.is_absent = 0 THEN 1 END) as students_eating_today
        FROM classes c
        INNER JOIN students s ON c.clase_id = s.clase_id
        INNER JOIN daily_meals dm ON s.student_id = dm.student_id
        WHERE dm.date = ?
        GROUP BY c.clase_id, c.nombre
        ORDER BY c.nombre
    ''', (date_str,))
    
    classes = []
    for row in cursor.fetchall():
        classes.append({
            'clase_id': row['clase_id'],
            'nombre': row['nombre'], 
            'total_students': row['total_students'],
            'students_eating_today': row['students_eating_today']
        })
    
    conn.close()
    return classes

DailyMealDB.get_classes_with_daily_data = staticmethod(__get_classes_with_daily_data_impl)

# Función para obtener lista de estudiantes ausentes
def __get_absent_students_impl(date_str: str, clase_id: str = None) -> list:
    """Get list of absent students for a specific date and optionally class"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Debug: Log what we're looking for
    logging.info(f"Looking for absent students on {date_str}" + (f" in class {clase_id}" if clase_id else ""))
    
    if clase_id:
        cursor.execute('''
            SELECT 
                s.student_id,
                s.nombre,
                s.apellidos,
                s.clase_id,
                c.nombre as clase_nombre,
                dm.meal_type,
                dm.eats_today,
                dm.confirmed,
                dm.is_absent
            FROM students s
            INNER JOIN classes c ON s.clase_id = c.clase_id
            INNER JOIN daily_meals dm ON s.student_id = dm.student_id
            WHERE dm.date = ? AND (dm.is_absent = 1 OR s.viene_hoy = 0) AND s.clase_id = ?
            ORDER BY s.apellidos, s.nombre
        ''', (date_str, clase_id))
    else:
        cursor.execute('''
            SELECT 
                s.student_id,
                s.nombre,
                s.apellidos,
                s.clase_id,
                c.nombre as clase_nombre,
                dm.meal_type,
                dm.eats_today,
                dm.confirmed,
                dm.is_absent
            FROM students s
            INNER JOIN classes c ON s.clase_id = c.clase_id
            INNER JOIN daily_meals dm ON s.student_id = dm.student_id
            WHERE dm.date = ? AND (dm.is_absent = 1 OR s.viene_hoy = 0)
            ORDER BY c.nombre, s.apellidos, s.nombre
        ''', (date_str,))
    
    absent_students = []
    for row in cursor.fetchall():
        logging.info(f"Found absent student: {row['student_id']} - {row['apellidos']}, {row['nombre']} - confirmed={row['confirmed']}, is_absent={row['is_absent']}")
        absent_students.append({
            'student_id': row['student_id'],
            'nombre': row['nombre'],
            'apellidos': row['apellidos'],
            'clase_id': row['clase_id'],
            'clase_nombre': row['clase_nombre'],
            'meal_type': row['meal_type'],
            'eats_today': row['eats_today']
        })
    
    logging.info(f"Total absent students found: {len(absent_students)}")
    conn.close()
    return absent_students

DailyMealDB.get_absent_students = staticmethod(__get_absent_students_impl)

# Función para obtener lista de estudiantes confirmados
def __get_confirmed_students_impl(date_str: str, clase_id: str = None) -> list:
    """Get list of confirmed students for a specific date and optionally class"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if clase_id:
        cursor.execute('''
            SELECT 
                s.student_id,
                s.nombre,
                s.apellidos,
                s.clase_id,
                c.nombre as clase_nombre,
                dm.meal_type,
                dm.eats_today
            FROM students s
            INNER JOIN classes c ON s.clase_id = c.clase_id
            INNER JOIN daily_meals dm ON s.student_id = dm.student_id
            WHERE dm.date = ? AND dm.confirmed = 1 AND dm.is_absent = 0 AND s.clase_id = ?
            ORDER BY s.apellidos, s.nombre
        ''', (date_str, clase_id))
    else:
        cursor.execute('''
            SELECT 
                s.student_id,
                s.nombre,
                s.apellidos,
                s.clase_id,
                c.nombre as clase_nombre,
                dm.meal_type,
                dm.eats_today
            FROM students s
            INNER JOIN classes c ON s.clase_id = c.clase_id
            INNER JOIN daily_meals dm ON s.student_id = dm.student_id
            WHERE dm.date = ? AND dm.confirmed = 1 AND dm.is_absent = 0
            ORDER BY c.nombre, s.apellidos, s.nombre
        ''', (date_str,))
    
    confirmed_students = []
    for row in cursor.fetchall():
        confirmed_students.append({
            'student_id': row['student_id'],
            'nombre': row['nombre'],
            'apellidos': row['apellidos'],
            'clase_id': row['clase_id'],
            'clase_nombre': row['clase_nombre'],
            'meal_type': row['meal_type'],
            'eats_today': row['eats_today']
        })
    
    conn.close()
    return confirmed_students

DailyMealDB.get_confirmed_students = staticmethod(__get_confirmed_students_impl)

# Función para obtener lista de estudiantes pendientes de validar
def __get_pending_students_impl(date_str: str, clase_id: str = None) -> list:
    """Get list of pending students (not yet validated) for a specific date and optionally class"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if clase_id:
        cursor.execute('''
            SELECT 
                s.student_id,
                s.nombre,
                s.apellidos,
                s.clase_id,
                c.nombre as clase_nombre,
                dm.meal_type,
                dm.eats_today
            FROM students s
            INNER JOIN classes c ON s.clase_id = c.clase_id
            INNER JOIN daily_meals dm ON s.student_id = dm.student_id
            WHERE dm.date = ? AND dm.confirmed = 0 AND s.viene_hoy = 1 AND dm.is_absent = 0 AND s.clase_id = ?
            ORDER BY s.apellidos, s.nombre
        ''', (date_str, clase_id))
    else:
        cursor.execute('''
            SELECT 
                s.student_id,
                s.nombre,
                s.apellidos,
                s.clase_id,
                c.nombre as clase_nombre,
                dm.meal_type,
                dm.eats_today
            FROM students s
            INNER JOIN classes c ON s.clase_id = c.clase_id
            INNER JOIN daily_meals dm ON s.student_id = dm.student_id
            WHERE dm.date = ? AND dm.confirmed = 0 AND s.viene_hoy = 1 AND dm.is_absent = 0
            ORDER BY c.nombre, s.apellidos, s.nombre
        ''', (date_str,))
    
    pending_students = []
    for row in cursor.fetchall():
        pending_students.append({
            'student_id': row['student_id'],
            'nombre': row['nombre'],
            'apellidos': row['apellidos'],
            'clase_id': row['clase_id'],
            'clase_nombre': row['clase_nombre'],
            'meal_type': row['meal_type'],
            'eats_today': row['eats_today']
        })
    
    conn.close()
    return pending_students

DailyMealDB.get_pending_students = staticmethod(__get_pending_students_impl)

# === FUNCIONES CRUD PARA PROFESORES ===

def __create_teacher_impl(username: str, password: str, nombre: str, apellidos: str) -> str:
    """Create a new teacher"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    teacher_id = str(uuid.uuid4())
    password_hash = generate_password_hash(password)
    
    cursor.execute('''
        INSERT INTO teachers (teacher_id, username, password_hash, nombre, apellidos, active)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (teacher_id, username, password_hash, nombre, apellidos, True))
    
    conn.commit()
    conn.close()
    return teacher_id

def __update_teacher_impl(teacher_id: str, username: str = None, password: str = None, 
                         nombre: str = None, apellidos: str = None, active: bool = None) -> bool:
    """Update teacher information"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    updates = []
    params = []
    
    if username is not None:
        updates.append('username = ?')
        params.append(username)
    if password is not None:
        updates.append('password_hash = ?')
        params.append(generate_password_hash(password))
    if nombre is not None:
        updates.append('nombre = ?')
        params.append(nombre)
    if apellidos is not None:
        updates.append('apellidos = ?')
        params.append(apellidos)
    if active is not None:
        updates.append('active = ?')
        params.append(active)
    
    if not updates:
        conn.close()
        return False
    
    params.append(teacher_id)
    
    cursor.execute(f'''
        UPDATE teachers 
        SET {', '.join(updates)}
        WHERE teacher_id = ?
    ''', params)
    
    result = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return result

def __delete_teacher_impl(teacher_id: str) -> bool:
    """Delete teacher permanently"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM teachers WHERE teacher_id = ?', (teacher_id,))
    
    result = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return result

def __archive_teacher_impl(teacher_id: str, archive: bool = True) -> bool:
    """Archive/unarchive teacher (set active = False/True)"""
    return __update_teacher_impl(teacher_id, active=not archive)

def __purge_teachers_impl() -> int:
    """Delete all teachers (dangerous operation)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM teachers')
    count = cursor.fetchone()[0]
    
    cursor.execute('DELETE FROM teachers')
    
    conn.commit()
    conn.close()
    return count

# Añadir las funciones a TeacherDB
TeacherDB.create_teacher = staticmethod(__create_teacher_impl)
TeacherDB.update_teacher = staticmethod(__update_teacher_impl)
TeacherDB.delete_teacher = staticmethod(__delete_teacher_impl)
TeacherDB.archive_teacher = staticmethod(__archive_teacher_impl)
TeacherDB.purge_teachers = staticmethod(__purge_teachers_impl)

# === FUNCIONES CRUD PARA ESTUDIANTES ===

def __create_student_impl(nombre: str, apellidos: str, clase_id: str, tipo_comensal: str = 'FIJO',
                         dias_semana: str = 'LUNES,MARTES,MIÉRCOLES,JUEVES,VIERNES', 
                         alergias: str = None) -> str:
    """Create a new student"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    student_id = str(uuid.uuid4())
    
    cursor.execute('''
        INSERT INTO students (student_id, nombre, apellidos, clase_id, tipo_comensal, 
                             dias_semana, activo, viene_hoy, alergias)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (student_id, nombre, apellidos, clase_id, tipo_comensal, dias_semana, 
          True, True, alergias))
    
    conn.commit()
    conn.close()
    return student_id

def __update_student_impl(student_id: str, nombre: str = None, apellidos: str = None, 
                         clase_id: str = None, tipo_comensal: str = None,
                         dias_semana: str = None, activo: bool = None, 
                         viene_hoy: bool = None, alergias: str = None) -> bool:
    """Update student information"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    updates = []
    params = []
    
    if nombre is not None:
        updates.append('nombre = ?')
        params.append(nombre)
    if apellidos is not None:
        updates.append('apellidos = ?')
        params.append(apellidos)
    if clase_id is not None:
        updates.append('clase_id = ?')
        params.append(clase_id)
    if tipo_comensal is not None:
        updates.append('tipo_comensal = ?')
        params.append(tipo_comensal)
    if dias_semana is not None:
        updates.append('dias_semana = ?')
        params.append(dias_semana)
    if activo is not None:
        updates.append('activo = ?')
        params.append(activo)
    if viene_hoy is not None:
        updates.append('viene_hoy = ?')
        params.append(viene_hoy)
    if alergias is not None:
        updates.append('alergias = ?')
        params.append(alergias)
    
    if not updates:
        conn.close()
        return False
    
    updates.append('updated_at = CURRENT_TIMESTAMP')
    params.append(student_id)
    
    cursor.execute(f'''
        UPDATE students 
        SET {', '.join(updates)}
        WHERE student_id = ?
    ''', params)
    
    result = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return result

def __delete_student_impl(student_id: str) -> bool:
    """Delete student permanently"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Also delete related daily_meals records
    cursor.execute('DELETE FROM daily_meals WHERE student_id = ?', (student_id,))
    cursor.execute('DELETE FROM students WHERE student_id = ?', (student_id,))
    
    result = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return result

def __archive_student_impl(student_id: str, archive: bool = True) -> bool:
    """Archive/unarchive student (set activo = False/True)"""
    return __update_student_impl(student_id, activo=not archive)

def __purge_students_impl() -> int:
    """Delete all students (dangerous operation)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM students')
    count = cursor.fetchone()[0]
    
    cursor.execute('DELETE FROM daily_meals')  # Delete related records first
    cursor.execute('DELETE FROM students')
    
    conn.commit()
    conn.close()
    return count

# Añadir las funciones a StudentDB
StudentDB.create_student = staticmethod(__create_student_impl)
StudentDB.update_student = staticmethod(__update_student_impl)
StudentDB.delete_student = staticmethod(__delete_student_impl)
StudentDB.archive_student = staticmethod(__archive_student_impl)
StudentDB.purge_students = staticmethod(__purge_students_impl)

# === FUNCIONES DE ASIGNACIÓN PROFESOR-CLASE ===

def __assign_teacher_to_class_impl(teacher_id: str, clase_id: str) -> bool:
    """Assign teacher to a class"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if assignment already exists
    cursor.execute(
        'SELECT COUNT(*) FROM teacher_classes WHERE teacher_id = ? AND clase_id = ?',
        (teacher_id, clase_id)
    )
    
    if cursor.fetchone()[0] > 0:
        conn.close()
        return False  # Assignment already exists
    
    # Create assignment
    cursor.execute(
        'INSERT INTO teacher_classes (teacher_id, clase_id) VALUES (?, ?)',
        (teacher_id, clase_id)
    )
    
    conn.commit()
    conn.close()
    return True

def __remove_teacher_from_class_impl(teacher_id: str, clase_id: str) -> bool:
    """Remove teacher assignment from a class"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        'DELETE FROM teacher_classes WHERE teacher_id = ? AND clase_id = ?',
        (teacher_id, clase_id)
    )
    
    result = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return result

def __get_teacher_classes_impl(teacher_id: str) -> List[str]:
    """Get classes assigned to a teacher"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        'SELECT clase_id FROM teacher_classes WHERE teacher_id = ?',
        (teacher_id,)
    )
    
    classes = [row['clase_id'] for row in cursor.fetchall()]
    conn.close()
    return classes

def __set_teacher_classes_impl(teacher_id: str, clase_ids: List[str]) -> bool:
    """Set all classes for a teacher (replaces existing assignments)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Remove all existing assignments
        cursor.execute('DELETE FROM teacher_classes WHERE teacher_id = ?', (teacher_id,))
        
        # Add new assignments
        for clase_id in clase_ids:
            cursor.execute(
                'INSERT INTO teacher_classes (teacher_id, clase_id) VALUES (?, ?)',
                (teacher_id, clase_id)
            )
        
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        return False
    finally:
        conn.close()

# Añadir funciones a las clases
TeacherDB.assign_teacher_to_class = staticmethod(__assign_teacher_to_class_impl)
TeacherDB.remove_teacher_from_class = staticmethod(__remove_teacher_from_class_impl)
TeacherDB.get_teacher_classes = staticmethod(__get_teacher_classes_impl)
TeacherDB.set_teacher_classes = staticmethod(__set_teacher_classes_impl)
