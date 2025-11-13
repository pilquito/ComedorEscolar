import csv
import io
import logging
import pandas as pd
from datetime import datetime, date
from flask import render_template, request, jsonify, session, redirect, url_for, flash, make_response
from werkzeug.security import check_password_hash
from app import app
from database import StudentDB, ClassDB, TeacherDB, DailyMealDB, get_db_connection
from models import Student

def format_date_spanish(date_obj):
    """Formatea una fecha en español: 28 de agosto de 2025"""
    months_spanish = {
        1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril',
        5: 'mayo', 6: 'junio', 7: 'julio', 8: 'agosto',
        9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
    }
    
    if isinstance(date_obj, str):
        date_obj = datetime.strptime(date_obj, '%Y-%m-%d').date()
    
    day = date_obj.day
    month = months_spanish[date_obj.month]
    year = date_obj.year
    
    return f"{day} de {month} de {year}"

# Registrar el filtro en Jinja2
app.jinja_env.filters['spanish_date'] = format_date_spanish

# Helper function to check if user is logged in
def is_logged_in():
    return 'teacher_id' in session

@app.route('/')
@app.route('/dashboard')
@app.route('/dashboard/<selected_date>')
def index(selected_date=None):
    """Main dashboard route - only shows data if there are imported meals for the selected date"""
    if not is_logged_in():
        return redirect(url_for('login'))
    
    # Use provided date or default to today
    if selected_date:
        try:
            # Validate date format
            datetime.strptime(selected_date, '%Y-%m-%d')
            today = selected_date
        except ValueError:
            flash('Fecha inválida', 'error')
            today = date.today().strftime('%Y-%m-%d')
    else:
        today = date.today().strftime('%Y-%m-%d')
    
    # Check if there are any imported meals for today
    daily_meals_count = DailyMealDB.get_meals_count_for_date(today)
    
    if daily_meals_count == 0:
        # No imported data for today - show empty dashboard
        response = make_response(render_template('dashboard.html',
                                 classes=[],
                                 total_students=0,
                                 total_eating_today=0,
                                 total_confirmed=0,
                                 total_absent=0,
                                 total_pending=0,
                                 today=today,
                                 no_data=True,
                                 message="No hay datos importados para hoy"))
        
        # Add headers to prevent caching
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    
    # Get classes with real imported data for today only
    all_classes = DailyMealDB.get_classes_with_daily_data(today)
    
    # Filter classes based on teacher assignment
    teacher_id = session.get('teacher_id')
    if teacher_id:
        assigned_classes = TeacherDB.get_teacher_classes(teacher_id)
        if assigned_classes:
            # Filter classes to only show assigned ones
            classes = [c for c in all_classes if c['clase_id'] in assigned_classes]
        else:
            # If no classes assigned, show all (for admin teachers)
            classes = all_classes
    else:
        classes = all_classes
    
    # Add confirmation status for each class
    for clase in classes:
        confirmation_status = DailyMealDB.get_class_confirmation_status(clase['clase_id'], today)
        clase['confirmation_status'] = confirmation_status
    
    # Calculate global totals based on daily_meals table only
    total_students = sum(c['total_students'] for c in classes)
    total_eating_today = sum(c['students_eating_today'] for c in classes)
    total_confirmed = sum(c['confirmation_status']['confirmed'] for c in classes)
    total_absent = sum(c['confirmation_status']['absent'] for c in classes)
    total_pending = sum(c['confirmation_status']['pending'] for c in classes)
    
    response = make_response(render_template('dashboard.html', 
                             classes=classes,
                             total_students=total_students,
                             total_eating_today=total_eating_today,
                             total_confirmed=total_confirmed,
                             total_absent=total_absent,
                             total_pending=total_pending,
                             today=today,
                             no_data=False))
    
    # Add headers to prevent caching
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Teacher login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Por favor, introduce usuario y contraseña', 'error')
            return render_template('login.html')
        
        teacher = TeacherDB.get_teacher_by_username(username)
        
        if teacher and check_password_hash(teacher.password_hash, password):
            session['teacher_id'] = teacher.teacher_id
            session['teacher_name'] = f"{teacher.nombre} {teacher.apellidos}"
            flash(f'Bienvenido/a, {teacher.nombre}', 'success')
            return redirect(url_for('index'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout route"""
    session.clear()
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('login'))

@app.route('/classes/<clase_id>')
def class_detail(clase_id):
    """Class detail view with students"""
    if not is_logged_in():
        return redirect(url_for('login'))
    
    class_info = ClassDB.get_class_by_id(clase_id)
    if not class_info:
        flash('Clase no encontrada', 'error')
        return redirect(url_for('index'))
    
    students = StudentDB.get_students_by_class(clase_id)
    today = date.today().strftime('%Y-%m-%d')
    
    # Add confirmation status for each student
    for student in students:
        confirmation_status = DailyMealDB.get_student_confirmation_status(student.student_id, today)
        student.confirmation_status = confirmation_status
    
    return render_template('class_detail.html', 
                         class_info=class_info, 
                         students=students,
                         today=today)

# API Routes
@app.route('/api/classes')
def api_get_classes():
    """API: Get all classes with counts"""
    if not is_logged_in():
        return jsonify({'error': 'Not authenticated'}), 401
    
    classes = ClassDB.get_all_classes()
    return jsonify({'classes': classes})

@app.route('/api/classes/<clase_id>')
def api_get_class_students(clase_id):
    """API: Get students in a specific class"""
    if not is_logged_in():
        return jsonify({'error': 'Not authenticated'}), 401
    
    class_info = ClassDB.get_class_by_id(clase_id)
    if not class_info:
        return jsonify({'error': 'Class not found'}), 404
    
    students = StudentDB.get_students_by_class(clase_id)
    students_data = []
    
    for student in students:
        students_data.append({
            'student_id': student.student_id,
            'nombre': student.nombre,
            'apellidos': student.apellidos,
            'tipo_comensal': student.tipo_comensal,
            'dias_semana': student.dias_semana,
            'activo': student.activo,
            'viene_hoy': student.viene_hoy,
            'alergias': student.alergias
        })
    
    return jsonify({
        'class': class_info,
        'students': students_data
    })

@app.route('/api/students/<student_id>', methods=['PATCH'])
def api_update_student(student_id):
    """API: Update student attendance or meal type"""
    if not is_logged_in():
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    student = StudentDB.get_student_by_id(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    success = True
    
    # Update attendance if provided
    if 'viene_hoy' in data:
        success = StudentDB.update_student_attendance(student_id, data['viene_hoy'])
    
    # Update meal type if provided
    if 'tipo_comensal' in data:
        dias_semana = data.get('dias_semana', student.dias_semana)
        success = success and StudentDB.update_student_meal_type(
            student_id, data['tipo_comensal'], dias_semana
        )
    
    if success:
        return jsonify({'message': 'Student updated successfully'})
    else:
        return jsonify({'error': 'Failed to update student'}), 500

@app.route('/api/import', methods=['POST'])
def api_import_csv():
    """API: Import CSV data (PARTEGEN.CSV format)"""
    if not is_logged_in():
        return jsonify({'error': 'Not authenticated'}), 401
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.lower().endswith('.csv'):
        return jsonify({'error': 'File must be a CSV'}), 400
    
    try:
        # Read CSV content with multiple encoding attempts
        raw_content = file.stream.read()
        content = None
        
        # Try different encodings commonly used in Spanish CSV files
        encodings = ['utf-8', 'iso-8859-1', 'windows-1252', 'cp1252']
        
        for encoding in encodings:
            try:
                content = raw_content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        
        if content is None:
            return jsonify({'error': 'No se pudo leer el archivo. Formato de codificación no soportado.'}), 400
        
        stream = io.StringIO(content, newline=None)
        csv_input = csv.DictReader(stream, delimiter=';')
        
        # Detect file format by checking headers
        headers = csv_input.fieldnames or []
        is_partegen = 'FECHA' in headers and 'CURSO' in headers and 'CODIGO' in headers
        is_partei4a = 'CODIGO' in headers and 'NOMBRE DEL ALUMNO' in headers and 'CURSO' not in headers
        
        if not (is_partegen or is_partei4a):
            return jsonify({
                'error': f'Formato de archivo no reconocido. Se esperaban columnas PARTEGEN o PARTEI4A.\nColumnas encontradas: {", ".join(headers)}\nFormato esperado PARTEGEN: FECHA;CURSO;CODIGO;NOMBRE DEL ALUMNO;FAL;COM;EXT\nFormato esperado PARTEI4A: CODIGO;NOMBRE DEL ALUMNO;FAL;COM;EXT'
            }), 400
        
        filename = file.filename or ''
        imported_count = 0
        updated_count = 0
        errors = []
        
        for row_num, row in enumerate(csv_input, start=2):
            try:
                # Handle both PARTEGEN and PARTEI4A formats
                if is_partegen:
                    # PARTEGEN CSV format: FECHA;CURSO;CODIGO;NOMBRE DEL ALUMNO;FAL;COM;EXT
                    fecha = row.get('FECHA', '').strip()
                    student_id = row.get('CODIGO', '').strip()
                    full_name = row.get('NOMBRE DEL ALUMNO', '').strip()
                    clase_id = row.get('CURSO', '').strip()
                    com_field = row.get('COM', '').strip().lower()
                    ext_field = row.get('EXT', '').strip().lower()
                else:  # PARTEI4A format - single class file
                    # PARTEI4A typically doesn't have FECHA or CURSO columns
                    # Extract from filename or use today's date
                    fecha = ''
                    student_id = row.get('CODIGO', '').strip()
                    full_name = row.get('NOMBRE DEL ALUMNO', '').strip()
                    # For PARTEI4A, extract class from filename (e.g., PARTEI4A -> 4A)
                    if 'PARTEI' in filename.upper():
                        clase_id = filename.upper().replace('PARTEI', '').replace('.CSV', '').replace('.', '') or '4A'
                    else:
                        clase_id = '4A'  # Default class
                    com_field = row.get('COM', '').strip().lower()
                    ext_field = row.get('EXT', '').strip().lower()
                
                # Parse date (format: DDMMYY or DDMYY -> YYYY-MM-DD)
                if fecha and len(fecha) >= 5:
                    try:
                        if len(fecha) == 6:  # DDMMYY
                            day = fecha[:2]
                            month = fecha[2:4]
                            year = '20' + fecha[4:6]
                        elif len(fecha) == 5:  # DDMYY (single digit month)
                            day = fecha[:2]
                            month = '0' + fecha[2:3]  # Add leading zero to month
                            year = '20' + fecha[3:5]
                        else:
                            raise ValueError(f"Formato de fecha no reconocido: {fecha}")
                        
                        # Validate the date
                        import datetime
                        datetime.datetime(int(year), int(month), int(day))
                        import_date = f"{year}-{month}-{day}"
                    except (ValueError, IndexError) as e:
                        errors.append(f"Fila {row_num}: Formato de fecha inválido '{fecha}'. Esperado: DDMMYY o DDMYY. Error: {e}")
                        import_date = date.today().strftime('%Y-%m-%d')
                else:
                    import_date = date.today().strftime('%Y-%m-%d')
                
                # Parse full name (format: APELLIDOS NOMBRES)
                if full_name:
                    name_parts = full_name.split()
                    if len(name_parts) >= 2:
                        # First part is usually apellidos, rest is nombres
                        apellidos = name_parts[0]
                        nombre = ' '.join(name_parts[1:])
                    else:
                        apellidos = full_name
                        nombre = ''
                else:
                    nombre = ''
                    apellidos = ''
                
                # Determine meal type and if eating today based on COM/EXT fields
                eats_today = False
                daily_meal_type = None
                
                if com_field == 'c':  # Comensal continuo
                    tipo_comensal = 'FIJO'
                    eats_today = True
                    daily_meal_type = 'FIJO'
                elif com_field == 'd':  # Discontinuo
                    tipo_comensal = 'FIJO_DISCONTINUO'
                    eats_today = True
                    daily_meal_type = 'FIJO_DISCONTINUO'
                elif 'extra' in ext_field or ext_field == 'e' or ext_field == 'x':
                    tipo_comensal = 'EXTRA'
                    eats_today = True
                    daily_meal_type = 'EXTRA'
                else:
                    # Student exists but doesn't eat today
                    tipo_comensal = 'EXTRA'  # Default for students not eating
                    eats_today = False
                
                dias_semana = None
                alergias = ''
                
                # Skip completely empty rows
                if not any([student_id, full_name, clase_id, com_field, ext_field]):
                    continue  # Skip empty rows silently
                
                if not all([student_id, nombre, apellidos, clase_id]):
                    missing_fields = []
                    if not student_id: missing_fields.append('CODIGO')
                    if not nombre: missing_fields.append('nombre')
                    if not apellidos: missing_fields.append('apellidos')
                    if not clase_id: missing_fields.append('clase')
                    
                    # Show raw row data for debugging
                    raw_data = '; '.join([f"{k}='{v}'" for k, v in row.items() if v.strip()])
                    errors.append(f"Fila {row_num}: Faltan campos obligatorios: {', '.join(missing_fields)}. Datos de la fila: [{raw_data}]")
                    continue
                
                if tipo_comensal not in ['FIJO', 'FIJO_DISCONTINUO', 'EXTRA']:
                    tipo_comensal = 'EXTRA'
                
                # Create or update student
                existing_student = StudentDB.get_student_by_id(student_id)
                
                student = Student(
                    student_id=student_id,
                    nombre=nombre,
                    apellidos=apellidos,
                    clase_id=clase_id,
                    tipo_comensal=tipo_comensal,
                    dias_semana=dias_semana,
                    activo=True,
                    viene_hoy=eats_today,  # Set based on PARTEGEN data
                    alergias=alergias
                )
                
                # Ensure class exists
                if not ClassDB.get_class_by_id(clase_id):
                    ClassDB.create_class(clase_id, f"Clase {clase_id}")
                
                # Create or update student
                if StudentDB.create_or_update_student(student):
                    # Create daily meal record if student eats today
                    if eats_today and daily_meal_type:
                        DailyMealDB.create_daily_meal_record(
                            student_id, import_date, daily_meal_type, True
                        )
                    
                    if existing_student:
                        updated_count += 1
                    else:
                        imported_count += 1
                else:
                    errors.append(f"Fila {row_num}: Error al guardar estudiante {student_id}")
                    
            except Exception as e:
                error_details = f"Error de procesamiento - {str(e)}"
                if 'fecha' in str(e).lower():
                    error_details += " (revisa formato de fecha DDMMYY)"
                
                # Show raw row data for debugging
                try:
                    raw_data = '; '.join([f"{k}='{v.strip()}'" for k, v in row.items() if v and v.strip()])
                    error_details += f". Datos de la fila: [{raw_data}]"
                except:
                    pass
                    
                errors.append(f"Fila {row_num}: {error_details}")
        
        result_data = {
            'message': f'Importación completada: {imported_count} nuevos, {updated_count} actualizados',
            'imported': imported_count,
            'updated': updated_count,
            'errors': errors,
            'file_format': 'PARTEGEN' if is_partegen else 'PARTEI4A',
            'headers_found': list(headers)
        }
        
        return jsonify(result_data)
        
    except Exception as e:
        return jsonify({'error': f'Error al procesar archivo: {str(e)}'}), 500

@app.route('/api/export_original')
def api_export_original_format():
    """API: Export in original PARTEGEN/PARTEI4A format - only when 100% validated"""
    if not is_logged_in():
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        export_date = request.args.get('date', date.today().strftime('%Y-%m-%d'))
        logging.info(f"Attempting export for date: {export_date}")
        
        # Check if 100% is validated
        total_students = 0
        total_validated = 0
        
        # Get all classes with data for this date
        classes = DailyMealDB.get_classes_with_daily_data(export_date)
        
        for clase in classes:
            confirmation_status = DailyMealDB.get_class_confirmation_status(clase['clase_id'], export_date)
            total_students += confirmation_status['total']
            total_validated += confirmation_status['confirmed'] + confirmation_status['absent']
        
        logging.info(f"Export validation check: {total_validated}/{total_students} students validated")
        
        if total_students == 0:
            return jsonify({'error': 'No hay datos para exportar en esta fecha'}), 400
        
        if total_validated < total_students:
            pending_count = total_students - total_validated
            return jsonify({
                'error': f'No se puede exportar: faltan {pending_count} estudiantes por validar. Debe estar el 100% validado.'
            }), 400
        
        # Get all students with their current data
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                s.student_id, s.nombre, s.apellidos, s.clase_id, s.tipo_comensal, 
                s.dias_semana, s.alergias, s.viene_hoy,
                dm.confirmed, dm.is_absent, dm.meal_type, dm.date
            FROM students s
            INNER JOIN daily_meals dm ON s.student_id = dm.student_id
            WHERE dm.date = ?
            ORDER BY s.clase_id, s.apellidos, s.nombre
        ''', (export_date,))
        
        students = cursor.fetchall()
        conn.close()
        
        # Create CSV content in PARTEGEN format
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')
        
        # Header in PARTEGEN format
        writer.writerow(['FECHA', 'CURSO', 'CODIGO', 'NOMBRE DEL ALUMNO', 'FAL', 'COM', 'EXT'])
        
        # Convert export_date to DDMMYY format (same as input)
        try:
            fecha_obj = datetime.strptime(export_date, '%Y-%m-%d')
            fecha_formatted = fecha_obj.strftime('%d%m%y')
        except:
            fecha_formatted = export_date.replace('-', '')
        
        # Data rows
        for student in students:
            # Determine FAL value: "F" if absent, empty if present
            fal = "F" if student['is_absent'] else ""
            
            # Determine COM value based on meal type (same format as input)
            com = ""
            if student['tipo_comensal'] == 'FIJO':
                com = "C"  # C = continuo
            elif student['tipo_comensal'] == 'FIJO_DISCONTINUO':
                com = "D"  # D = discontinuo
            
            # Determine EXT value (same format as input)
            ext = "E" if student['tipo_comensal'] == 'EXTRA' else ""
            
            writer.writerow([
                fecha_formatted,                         # FECHA (DDMMYY)
                student['clase_id'],                     # CURSO
                student['student_id'],                   # CODIGO
                f"{student['apellidos']} {student['nombre']}", # NOMBRE DEL ALUMNO (sin coma)
                fal,                                     # FAL (F if absent)
                com,                                     # COM (c/d)
                ext                                      # EXT (e)
            ])
        
        # Create filename (same as import)
        filename = 'PARTGEN.csv'
        
        # Create response
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        
        return response
        
    except Exception as e:
        logging.error(f"Export original format error: {str(e)}", exc_info=True)
        return jsonify({'error': f'Error al exportar: {str(e)}'}), 500

@app.route('/api/export')
def api_export_csv():
    """API: Export daily attendance CSV with filtering and validation status"""
    if not is_logged_in():
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        # Get filter parameters
        export_date = request.args.get('date', date.today().strftime('%Y-%m-%d'))
        clase_filter = request.args.get('clase')
        
        # Get daily meal records for the date
        daily_meals = DailyMealDB.get_daily_meals_by_date(export_date)
        
        # Filter by class if specified
        if clase_filter:
            daily_meals = [meal for meal in daily_meals if meal.get('clase_id') == clase_filter]
        
        # Group by class and sort by confirmation status
        meals_by_class = {}
        for meal in daily_meals:
            if meal.get('eats_today', False):  # Only students who eat today
                clase_id = meal.get('clase_id')
                if clase_id not in meals_by_class:
                    meals_by_class[clase_id] = {'confirmed': [], 'absent': []}
                
                if meal.get('is_absent', False):
                    meals_by_class[clase_id]['absent'].append(meal)
                elif meal.get('confirmed', False):
                    meals_by_class[clase_id]['confirmed'].append(meal)
                else:
                    # Treat unvalidated as confirmed for export
                    meals_by_class[clase_id]['confirmed'].append(meal)
        
        # Create CSV content
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')
        
        # Header
        writer.writerow([
            'fecha', 'clase_id', 'student_id', 'apellidos', 'nombre', 
            'tipo_comensal', 'estado_validacion', 'alergias'
        ])
        
        # Data rows organized by class
        for clase_id in sorted(meals_by_class.keys()):
            class_data = meals_by_class[clase_id]
            
            # First: confirmed students (present and validated)
            for meal in sorted(class_data['confirmed'], key=lambda x: (x.get('apellidos', ''), x.get('nombre', ''))):
                writer.writerow([
                    format_date_spanish(export_date),
                    meal.get('clase_id', ''),
                    meal.get('student_id', ''),
                    meal.get('apellidos', ''),
                    meal.get('nombre', ''),
                    meal.get('meal_type', ''),
                    'PRESENTE' if meal.get('confirmed') else 'SIN_VALIDAR',
                    meal.get('alergias', '')
                ])
            
            # Then: absent students (at the end of each class)
            for meal in sorted(class_data['absent'], key=lambda x: (x.get('apellidos', ''), x.get('nombre', ''))):
                writer.writerow([
                    format_date_spanish(export_date),
                    meal.get('clase_id', ''),
                    meal.get('student_id', ''),
                    meal.get('apellidos', ''),
                    meal.get('nombre', ''),
                    meal.get('meal_type', ''),
                    'AUSENTE',
                    meal.get('alergias', '')
                ])
        
        # Create filename
        filename_date = export_date.replace('-', '')
        filename_class = f"_{clase_filter}" if clase_filter else ""
        filename = f'comedor_export_{filename_date}{filename_class}.csv'
        
        # Create response
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        
        return response
        
    except Exception as e:
        return jsonify({'error': f'Error al exportar: {str(e)}'}), 500

# AJAX endpoints for frontend functionality
@app.route('/ajax/toggle_attendance', methods=['POST'])
def ajax_toggle_attendance():
    """Toggle student attendance via AJAX"""
    if not is_logged_in():
        return jsonify({'error': 'Not authenticated'}), 401
    
    student_id = request.form.get('student_id')
    viene_hoy = request.form.get('viene_hoy') == 'true'
    
    if not student_id:
        return jsonify({'error': 'Student ID required'}), 400
    
    # Check if student is validated (confirmed) for today
    today = date.today().strftime('%Y-%m-%d')
    confirmation_status = DailyMealDB.get_student_confirmation_status(student_id, today)
    
    # Special handling for validated students being marked as not coming
    if confirmation_status['is_validated'] and not viene_hoy:
        # Mark as absent instead of preventing the change
        logging.info(f"Student {student_id} is validated and being marked as not coming. Marking as absent.")
        if DailyMealDB.mark_student_confirmed(student_id, today, True):  # True = is_absent
            # Also update student table
            StudentDB.update_student_attendance(student_id, viene_hoy)
            logging.info(f"Successfully marked student {student_id} as absent")
            return jsonify({'success': True, 'viene_hoy': viene_hoy, 'marked_absent': True})
        else:
            logging.error(f"Failed to mark student {student_id} as absent")
            return jsonify({'error': 'Error al marcar como ausente'}), 500
    elif confirmation_status['is_validated']:
        return jsonify({'error': 'No se puede modificar - El alumno ya está validado'}), 400
    
    if StudentDB.update_student_attendance(student_id, viene_hoy):
        # Also update daily_meals if record exists
        if not viene_hoy:  # If marking as NOT coming today
            # Set eats_today = 0 in daily_meals to exclude from statistics
            DailyMealDB.update_daily_meal_eats_today(student_id, today, False)
        else:  # If marking as coming today
            # Set eats_today = 1 in daily_meals (or create record if needed)
            DailyMealDB.update_daily_meal_eats_today(student_id, today, True)
            
        return jsonify({'success': True, 'viene_hoy': viene_hoy})
    else:
        return jsonify({'error': 'Failed to update attendance'}), 500

@app.route('/ajax/update_meal_type', methods=['POST'])
def ajax_update_meal_type():
    """Update student meal type via AJAX"""
    if not is_logged_in():
        return jsonify({'error': 'Not authenticated'}), 401
    
    student_id = request.form.get('student_id')
    tipo_comensal = request.form.get('tipo_comensal')
    dias_semana = request.form.get('dias_semana', '')
    
    if not student_id or not tipo_comensal:
        return jsonify({'error': 'Student ID and meal type required'}), 400
    
    if tipo_comensal not in ['FIJO', 'FIJO_DISCONTINUO', 'EXTRA']:
        return jsonify({'error': 'Invalid meal type'}), 400
    
    if StudentDB.update_student_meal_type(student_id, tipo_comensal, dias_semana or None):
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Failed to update meal type'}), 500

@app.route('/ajax/validate_student', methods=['POST'])
def ajax_validate_student():
    """Validate individual student via AJAX"""
    if not is_logged_in():
        return jsonify({'error': 'Not authenticated'}), 401
    
    student_id = request.form.get('student_id')
    is_absent = request.form.get('is_absent') == 'true'
    
    if not student_id:
        return jsonify({'error': 'Student ID required'}), 400
    
    # Verificar que el estudiante existe y su estado
    student = StudentDB.get_student_by_id(student_id)
    if not student:
        return jsonify({'error': 'Estudiante no encontrado'}), 400
    
    # Si se está marcando como ausente, permitir incluso si viene_hoy = false
    if not is_absent and not student.viene_hoy:
        return jsonify({'error': 'Solo se pueden validar como presentes estudiantes marcados como "Viene Hoy = Sí"'}), 400
    
    today = date.today().strftime('%Y-%m-%d')
    
    # Check if daily meal record exists
    confirmation_status = DailyMealDB.get_student_confirmation_status(student_id, today)
    if not confirmation_status['eats_today']:  # No record exists
        # Create daily meal record first
        if not DailyMealDB.create_daily_meal_record(student_id, today, student.tipo_comensal, True):
            return jsonify({'error': 'Error creating meal record'}), 500
    
    logging.info(f"Attempting to validate student {student_id} as {'ABSENT' if is_absent else 'PRESENT'}")
    
    if DailyMealDB.mark_student_confirmed(student_id, today, is_absent):
        logging.info(f"Successfully validated student {student_id} as {'ABSENT' if is_absent else 'PRESENT'}")
        return jsonify({'success': True, 'is_absent': is_absent})
    else:
        logging.error(f"Failed to validate student {student_id} as {'ABSENT' if is_absent else 'PRESENT'}")
        return jsonify({'error': 'Failed to validate student'}), 500

@app.route('/ajax/validate_all_class', methods=['POST'])
def ajax_validate_all_class():
    """Validate all students in a class via AJAX"""
    if not is_logged_in():
        return jsonify({'error': 'Not authenticated'}), 401
    
    class_id = request.form.get('class_id')
    
    if not class_id:
        return jsonify({'error': 'Class ID required'}), 400
    
    today = date.today().strftime('%Y-%m-%d')
    
    # Check if there are imported meals for today first
    daily_meals_count = DailyMealDB.get_meals_count_for_date(today)
    if daily_meals_count == 0:
        return jsonify({'error': f'No hay datos importados para hoy ({today}). Primero importa un archivo CSV con datos del día actual.'}), 400
    
    # Get all students in the class
    students = StudentDB.get_students_by_class(class_id)
    validated_present = 0
    validated_absent = 0
    total_students = 0
    
    for student in students:
        if student.activo:  # Solo estudiantes activos
            total_students += 1
            # Check if student is already validated
            confirmation_status = DailyMealDB.get_student_confirmation_status(student.student_id, today)
            
            if not confirmation_status['is_validated']:
                # Create daily meal record if it doesn't exist
                if not confirmation_status['eats_today']:  # No record exists
                    # Create daily meal record first
                    if DailyMealDB.create_daily_meal_record(student.student_id, today, student.tipo_comensal, True):
                        # Then validate based on attendance
                        if student.viene_hoy:
                            # Mark as present
                            if DailyMealDB.mark_student_confirmed(student.student_id, today, False):
                                validated_present += 1
                        else:
                            # Mark as absent
                            if DailyMealDB.mark_student_confirmed(student.student_id, today, True):
                                validated_absent += 1
                else:
                    # Record exists, just validate based on attendance
                    if student.viene_hoy:
                        # Mark as present
                        if DailyMealDB.mark_student_confirmed(student.student_id, today, False):
                            validated_present += 1
                    else:
                        # Mark as absent  
                        if DailyMealDB.mark_student_confirmed(student.student_id, today, True):
                            validated_absent += 1
    
    if total_students == 0:
        return jsonify({'error': 'No hay estudiantes activos en esta clase.'}), 400
    
    total_validated = validated_present + validated_absent
    return jsonify({
        'success': True, 
        'validated_count': total_validated,
        'validated_present': validated_present,
        'validated_absent': validated_absent,
        'total_students': total_students
    })

@app.route('/ajax/unlock_student', methods=['POST'])
def ajax_unlock_student():
    """Unlock a validated student to allow modifications"""
    if not is_logged_in():
        return jsonify({'error': 'Not authenticated'}), 401
    
    student_id = request.form.get('student_id')
    
    if not student_id:
        return jsonify({'error': 'Student ID required'}), 400
    
    today = date.today().strftime('%Y-%m-%d')
    
    # Check if student is actually validated
    confirmation_status = DailyMealDB.get_student_confirmation_status(student_id, today)
    if not confirmation_status['is_validated']:
        return jsonify({'error': 'El estudiante no está validado'}), 400
    
    # Unlock by setting confirmed = 0
    if DailyMealDB.unlock_student_validation(student_id, today):
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Error al desbloquear estudiante'}), 500

@app.route('/daily-meals')
@app.route('/daily-meals/<meal_date>')
def daily_meals(meal_date=None):
    """View daily meal records"""
    if not is_logged_in():
        return redirect(url_for('login'))
    
    if not meal_date:
        meal_date = date.today().strftime('%Y-%m-%d')
    
    daily_meals = DailyMealDB.get_daily_meals_by_date(meal_date)
    meal_counts = DailyMealDB.get_daily_meal_counts_by_class(meal_date)
    
    # Group meals by class
    meals_by_class = {}
    for meal in daily_meals:
        clase_id = meal['clase_id']
        if clase_id not in meals_by_class:
            meals_by_class[clase_id] = []
        meals_by_class[clase_id].append(meal)
    
    # Calculate totals from the new structure
    total_fijo = sum(counts.get('FIJO', {}).get('total', 0) for counts in meal_counts.values())
    total_discontinuo = sum(counts.get('FIJO_DISCONTINUO', {}).get('total', 0) for counts in meal_counts.values())
    total_extra = sum(counts.get('EXTRA', {}).get('total', 0) for counts in meal_counts.values())
    total_meals = total_fijo + total_discontinuo + total_extra
    
    return render_template('daily_meals.html',
                         meal_date=meal_date,
                         meals_by_class=meals_by_class,
                         meal_counts=meal_counts,
                         total_fijo=total_fijo,
                         total_discontinuo=total_discontinuo,
                         total_extra=total_extra,
                         total_meals=total_meals)

@app.route('/api/daily-meals/<meal_date>')
def api_daily_meals(meal_date):
    """API: Get daily meal records for a specific date"""
    if not is_logged_in():
        return jsonify({'error': 'Not authenticated'}), 401
    
    daily_meals = DailyMealDB.get_daily_meals_by_date(meal_date)
    meal_counts = DailyMealDB.get_daily_meal_counts_by_class(meal_date)
    
    return jsonify({
        'date': meal_date,
        'meals': daily_meals,
        'counts_by_class': meal_counts
    })

@app.route('/ajax/confirm_student', methods=['POST'])
def ajax_confirm_student():
    """Mark student as confirmed (present) via AJAX"""
    if not is_logged_in():
        return jsonify({'error': 'Not authenticated'}), 401
    
    student_id = request.form.get('student_id')
    date = request.form.get('date')
    
    if not student_id or not date:
        return jsonify({'error': 'Student ID and date required'}), 400
    
    if DailyMealDB.mark_student_confirmed(student_id, date, is_absent=False):
        return jsonify({'success': True, 'status': 'confirmed'})
    else:
        return jsonify({'error': 'Failed to confirm student'}), 500

@app.route('/ajax/mark_absent', methods=['POST'])
def ajax_mark_absent():
    """Mark student as absent via AJAX"""
    if not is_logged_in():
        return jsonify({'error': 'Not authenticated'}), 401
    
    student_id = request.form.get('student_id')
    date = request.form.get('date')
    
    if not student_id or not date:
        return jsonify({'error': 'Student ID and date required'}), 400
    
    if DailyMealDB.mark_student_confirmed(student_id, date, is_absent=True):
        return jsonify({'success': True, 'status': 'absent'})
    else:
        return jsonify({'error': 'Failed to mark student as absent'}), 500

@app.route('/ajax/get_class_status', methods=['GET'])
def ajax_get_class_status():
    """Get confirmation status for a class on a specific date"""
    if not is_logged_in():
        return jsonify({'error': 'Not authenticated'}), 401
    
    clase_id = request.args.get('clase_id')
    date = request.args.get('date', date.today().strftime('%Y-%m-%d'))
    
    if not clase_id:
        return jsonify({'error': 'Class ID required'}), 400
    
    status = DailyMealDB.get_class_confirmation_status(clase_id, date)
    return jsonify(status)

@app.route('/config')
def config():
    """Configuration page"""
    if not is_logged_in():
        return redirect(url_for('login'))
    
    classes = ClassDB.get_all_classes()
    return render_template('config.html', classes=classes)

@app.route('/api/purge-day', methods=['POST'])
def api_purge_day():
    """API: Purge data for a specific day and optionally class"""
    if not is_logged_in():
        return jsonify({'error': 'No autorizado'}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Datos requeridos'}), 400
    
    purge_date = data.get('date')
    clase_id = data.get('clase_id')  # Optional, if provided purge only this class
    
    if not purge_date:
        return jsonify({'error': 'Fecha requerida'}), 400
    
    try:
        # Validate date format
        datetime.strptime(purge_date, '%Y-%m-%d')
        
        # Purge daily meal records
        deleted_meals = DailyMealDB.purge_daily_meals(purge_date, clase_id)
        
        message = f'Eliminados {deleted_meals} registros de comidas'
        if clase_id:
            message += f' para la clase {clase_id}'
        message += f' del día {format_date_spanish(purge_date)}'
        
        return jsonify({
            'message': message,
            'deleted_meals': deleted_meals
        })
        
    except ValueError:
        return jsonify({'error': 'Formato de fecha inválido'}), 400
    except Exception as e:
        return jsonify({'error': f'Error al purgar datos: {str(e)}'}), 500


@app.route('/config/purge-students', methods=['POST'])
def purge_students():
    """Purge all students"""
    if not is_logged_in():
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        deleted_count = StudentDB.purge_students()
        return jsonify({
            'message': f'Eliminados {deleted_count} estudiantes de la base de datos',
            'deleted_students': deleted_count
        })
    except Exception as e:
        return jsonify({'error': f'Error al purgar estudiantes: {str(e)}'}), 500

@app.route('/teachers')
def teachers():
    """Teachers management page"""
    if not is_logged_in():
        return redirect(url_for('login'))
    
    teachers = TeacherDB.get_all_teachers()
    classes = ClassDB.get_all_classes()
    
    # Add assigned classes to each teacher
    for teacher in teachers:
        teacher.assigned_classes = TeacherDB.get_teacher_classes(teacher.teacher_id)
    
    return render_template('teachers.html', teachers=teachers, classes=classes)

# === CRUD ROUTES FOR TEACHERS ===

@app.route('/teachers/new', methods=['GET', 'POST'])
def teacher_new():
    """Create new teacher"""
    if not is_logged_in():
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        nombre = request.form.get('nombre')
        apellidos = request.form.get('apellidos')
        
        if not all([username, password, nombre, apellidos]):
            flash('Todos los campos son obligatorios', 'error')
        else:
            try:
                teacher_id = TeacherDB.create_teacher(username, password, nombre, apellidos)
                flash(f'Profesor {nombre} {apellidos} creado exitosamente', 'success')
                return redirect(url_for('teachers'))
            except Exception as e:
                flash(f'Error al crear profesor: {str(e)}', 'error')
    
    return render_template('teacher_form.html', action='create')

@app.route('/teachers/<teacher_id>/edit', methods=['GET', 'POST'])
def teacher_edit(teacher_id):
    """Edit teacher"""
    if not is_logged_in():
        return redirect(url_for('login'))
    
    teacher = TeacherDB.get_teacher_by_id(teacher_id)
    if not teacher:
        flash('Profesor no encontrado', 'error')
        return redirect(url_for('teachers'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')  # Optional
        nombre = request.form.get('nombre')
        apellidos = request.form.get('apellidos')
        active = request.form.get('active') == 'on'
        
        if not all([username, nombre, apellidos]):
            flash('Username, nombre y apellidos son obligatorios', 'error')
        else:
            try:
                update_data = {
                    'username': username,
                    'nombre': nombre,
                    'apellidos': apellidos,
                    'active': active
                }
                if password:  # Only update password if provided
                    update_data['password'] = password
                
                TeacherDB.update_teacher(teacher_id, **update_data)
                flash(f'Profesor {nombre} {apellidos} actualizado exitosamente', 'success')
                return redirect(url_for('teachers'))
            except Exception as e:
                flash(f'Error al actualizar profesor: {str(e)}', 'error')
    
    return render_template('teacher_form.html', action='edit', teacher=teacher)

@app.route('/teachers/<teacher_id>/delete', methods=['POST'])
def teacher_delete(teacher_id):
    """Delete teacher"""
    if not is_logged_in():
        return redirect(url_for('login'))
    
    teacher = TeacherDB.get_teacher_by_id(teacher_id)
    if not teacher:
        flash('Profesor no encontrado', 'error')
        return redirect(url_for('teachers'))
    
    try:
        TeacherDB.delete_teacher(teacher_id)
        flash(f'Profesor {teacher.nombre} {teacher.apellidos} eliminado exitosamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar profesor: {str(e)}', 'error')
    
    return redirect(url_for('teachers'))

@app.route('/teachers/<teacher_id>/archive', methods=['POST'])
def teacher_archive(teacher_id):
    """Archive/unarchive teacher"""
    if not is_logged_in():
        return redirect(url_for('login'))
    
    teacher = TeacherDB.get_teacher_by_id(teacher_id)
    if not teacher:
        flash('Profesor no encontrado', 'error')
        return redirect(url_for('teachers'))
    
    try:
        archive = teacher.active  # If active, archive it
        TeacherDB.archive_teacher(teacher_id, archive)
        action = 'archivado' if archive else 'desarchivado'
        flash(f'Profesor {teacher.nombre} {teacher.apellidos} {action} exitosamente', 'success')
    except Exception as e:
        flash(f'Error al archivar profesor: {str(e)}', 'error')
    
    return redirect(url_for('teachers'))

@app.route('/teachers/<teacher_id>/assign-classes', methods=['GET', 'POST'])
def teacher_assign_classes(teacher_id):
    """Assign classes to teacher"""
    if not is_logged_in():
        return redirect(url_for('login'))
    
    teacher = TeacherDB.get_teacher_by_id(teacher_id)
    if not teacher:
        flash('Profesor no encontrado', 'error')
        return redirect(url_for('teachers'))
    
    if request.method == 'POST':
        selected_classes = request.form.getlist('clase_ids')
        
        try:
            TeacherDB.set_teacher_classes(teacher_id, selected_classes)
            if selected_classes:
                flash(f'Asignadas {len(selected_classes)} clases al profesor {teacher.nombre} {teacher.apellidos}', 'success')
            else:
                flash(f'Se eliminaron todas las asignaciones del profesor {teacher.nombre} {teacher.apellidos}', 'info')
            return redirect(url_for('teachers'))
        except Exception as e:
            flash(f'Error al asignar clases: {str(e)}', 'error')
    
    all_classes = ClassDB.get_all_classes()
    assigned_classes = TeacherDB.get_teacher_classes(teacher_id)
    
    return render_template('teacher_assign_classes.html', 
                         teacher=teacher, 
                         all_classes=all_classes, 
                         assigned_classes=assigned_classes)

@app.route('/students')
def students():
    """Students management page"""
    if not is_logged_in():
        return redirect(url_for('login'))
    
    clase_filter = request.args.get('clase')
    
    # Filter classes based on teacher assignment
    teacher_id = session.get('teacher_id')
    all_classes = ClassDB.get_all_classes()
    if teacher_id:
        assigned_classes = TeacherDB.get_teacher_classes(teacher_id)
        if assigned_classes:
            # Filter classes to only show assigned ones
            classes = [c for c in all_classes if c['clase_id'] in assigned_classes]
            # If class filter is set, make sure it's in assigned classes
            if clase_filter and clase_filter not in assigned_classes:
                clase_filter = None  # Reset filter if not assigned
        else:
            # If no classes assigned, show all (for admin teachers)
            classes = all_classes
    else:
        classes = all_classes
    
    # Get students based on filter and permissions
    if clase_filter:
        students = StudentDB.get_students_by_class(clase_filter)
    else:
        if teacher_id and assigned_classes:
            # Show students from assigned classes only
            all_students = StudentDB.get_all_students()
            students = [s for s in all_students if s.clase_id in assigned_classes]
        else:
            # Show all students (for admin teachers)
            students = StudentDB.get_all_students()
    
    return render_template('students.html', students=students, classes=classes, selected_class=clase_filter)

# === CRUD ROUTES FOR STUDENTS ===

@app.route('/students/new', methods=['GET', 'POST'])
def student_new():
    """Create new student"""
    if not is_logged_in():
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        apellidos = request.form.get('apellidos')
        clase_id = request.form.get('clase_id')
        tipo_comensal = request.form.get('tipo_comensal', 'FIJO')
        dias_semana = ','.join(request.form.getlist('dias_semana'))
        alergias = request.form.get('alergias', '').strip() or None
        
        if not all([nombre, apellidos, clase_id]):
            flash('Nombre, apellidos y clase son obligatorios', 'error')
        else:
            try:
                student_id = StudentDB.create_student(
                    nombre=nombre,
                    apellidos=apellidos,
                    clase_id=clase_id,
                    tipo_comensal=tipo_comensal,
                    dias_semana=dias_semana,
                    alergias=alergias
                )
                flash(f'Estudiante {nombre} {apellidos} creado exitosamente', 'success')
                return redirect(url_for('students'))
            except Exception as e:
                flash(f'Error al crear estudiante: {str(e)}', 'error')
    
    classes = ClassDB.get_all_classes()
    return render_template('student_form.html', action='create', classes=classes)

@app.route('/students/<student_id>/edit', methods=['GET', 'POST'])
def student_edit(student_id):
    """Edit student"""
    if not is_logged_in():
        return redirect(url_for('login'))
    
    student = StudentDB.get_student_by_id(student_id)
    if not student:
        flash('Estudiante no encontrado', 'error')
        return redirect(url_for('students'))
    
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        apellidos = request.form.get('apellidos')
        clase_id = request.form.get('clase_id')
        tipo_comensal = request.form.get('tipo_comensal', 'FIJO')
        dias_semana = ','.join(request.form.getlist('dias_semana'))
        activo = request.form.get('activo') == 'on'
        viene_hoy = request.form.get('viene_hoy') == 'on'
        alergias = request.form.get('alergias', '').strip() or None
        
        if not all([nombre, apellidos, clase_id]):
            flash('Nombre, apellidos y clase son obligatorios', 'error')
        else:
            try:
                StudentDB.update_student(
                    student_id=student_id,
                    nombre=nombre,
                    apellidos=apellidos,
                    clase_id=clase_id,
                    tipo_comensal=tipo_comensal,
                    dias_semana=dias_semana,
                    activo=activo,
                    viene_hoy=viene_hoy,
                    alergias=alergias
                )
                flash(f'Estudiante {nombre} {apellidos} actualizado exitosamente', 'success')
                return redirect(url_for('students'))
            except Exception as e:
                flash(f'Error al actualizar estudiante: {str(e)}', 'error')
    
    classes = ClassDB.get_all_classes()
    return render_template('student_form.html', action='edit', student=student, classes=classes)

@app.route('/students/<student_id>/delete', methods=['POST'])
def student_delete(student_id):
    """Delete student"""
    if not is_logged_in():
        return redirect(url_for('login'))
    
    student = StudentDB.get_student_by_id(student_id)
    if not student:
        flash('Estudiante no encontrado', 'error')
        return redirect(url_for('students'))
    
    try:
        StudentDB.delete_student(student_id)
        flash(f'Estudiante {student.nombre} {student.apellidos} eliminado exitosamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar estudiante: {str(e)}', 'error')
    
    return redirect(url_for('students'))

@app.route('/students/<student_id>/archive', methods=['POST'])
def student_archive(student_id):
    """Archive/unarchive student"""
    if not is_logged_in():
        return redirect(url_for('login'))
    
    student = StudentDB.get_student_by_id(student_id)
    if not student:
        flash('Estudiante no encontrado', 'error')
        return redirect(url_for('students'))
    
    try:
        archive = student.activo  # If active, archive it
        StudentDB.archive_student(student_id, archive)
        action = 'archivado' if archive else 'desarchivado'
        flash(f'Estudiante {student.nombre} {student.apellidos} {action} exitosamente', 'success')
    except Exception as e:
        flash(f'Error al archivar estudiante: {str(e)}', 'error')
    
    return redirect(url_for('students'))

@app.route('/classes')
def classes_manager():
    """Classes management page"""
    if not is_logged_in():
        return redirect(url_for('login'))
    
    classes = ClassDB.get_all_classes()
    
    # Add statistics to each class
    for clase in classes:
        students = StudentDB.get_students_by_class(clase['clase_id'])
        clase['student_count'] = len(students)
        clase['active_students'] = len([s for s in students if s.activo])
    
    return render_template('classes.html', classes=classes)

@app.route('/ausentes')
@app.route('/ausentes/<meal_date>')
@app.route('/ausentes/<meal_date>/<clase_id>')
def ausentes(meal_date=None, clase_id=None):
    """Show list of absent students for a specific date and optionally class"""
    if not is_logged_in():
        return redirect(url_for('login'))
    
    # Use today if no date provided
    if not meal_date:
        meal_date = date.today().strftime('%Y-%m-%d')
    
    try:
        # Validate date format
        datetime.strptime(meal_date, '%Y-%m-%d')
    except ValueError:
        flash('Formato de fecha inválido', 'error')
        return redirect(url_for('index'))
    
    # Get absent students
    absent_students = DailyMealDB.get_absent_students(meal_date, clase_id)
    
    # Get class info if filtering by class
    class_info = None
    if clase_id:
        class_info = ClassDB.get_class_by_id(clase_id)
    
    # Group students by class for better display
    students_by_class = {}
    for student in absent_students:
        class_name = student['clase_nombre']
        if class_name not in students_by_class:
            students_by_class[class_name] = []
        students_by_class[class_name].append(student)
    
    response = make_response(render_template('ausentes.html',
                             absent_students=absent_students,
                             students_by_class=students_by_class,
                             meal_date=meal_date,
                             class_info=class_info,
                             total_absent=len(absent_students)))
    
    # Add headers to prevent caching
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/confirmados')
@app.route('/confirmados/<meal_date>')
@app.route('/confirmados/<meal_date>/<clase_id>')
def confirmados(meal_date=None, clase_id=None):
    """Show list of confirmed students for a specific date and optionally class"""
    if not is_logged_in():
        return redirect(url_for('login'))
    
    # Use today if no date provided
    if not meal_date:
        meal_date = date.today().strftime('%Y-%m-%d')
    
    try:
        # Validate date format
        datetime.strptime(meal_date, '%Y-%m-%d')
    except ValueError:
        flash('Formato de fecha inválido', 'error')
        return redirect(url_for('index'))
    
    # Get confirmed students
    confirmed_students = DailyMealDB.get_confirmed_students(meal_date, clase_id)
    
    # Get class info if filtering by class
    class_info = None
    if clase_id:
        class_info = ClassDB.get_class_by_id(clase_id)
    
    # Group students by class for better display
    students_by_class = {}
    for student in confirmed_students:
        class_name = student['clase_nombre']
        if class_name not in students_by_class:
            students_by_class[class_name] = []
        students_by_class[class_name].append(student)
    
    response = make_response(render_template('confirmados.html',
                             confirmed_students=confirmed_students,
                             students_by_class=students_by_class,
                             meal_date=meal_date,
                             class_info=class_info,
                             total_confirmed=len(confirmed_students)))
    
    # Add headers to prevent caching
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/pendientes')
@app.route('/pendientes/<meal_date>')
@app.route('/pendientes/<meal_date>/<clase_id>')
def pendientes(meal_date=None, clase_id=None):
    """Show list of pending students (not yet validated) for a specific date and optionally class"""
    if not is_logged_in():
        return redirect(url_for('login'))
    
    # Use today if no date provided
    if not meal_date:
        meal_date = date.today().strftime('%Y-%m-%d')
    
    try:
        # Validate date format
        datetime.strptime(meal_date, '%Y-%m-%d')
    except ValueError:
        flash('Formato de fecha inválido', 'error')
        return redirect(url_for('index'))
    
    # Get pending students
    pending_students = DailyMealDB.get_pending_students(meal_date, clase_id)
    
    # Get class info if filtering by class
    class_info = None
    if clase_id:
        class_info = ClassDB.get_class_by_id(clase_id)
    
    # Group students by class for better display
    students_by_class = {}
    for student in pending_students:
        class_name = student['clase_nombre']
        if class_name not in students_by_class:
            students_by_class[class_name] = []
        students_by_class[class_name].append(student)
    
    response = make_response(render_template('pendientes.html',
                             pending_students=pending_students,
                             students_by_class=students_by_class,
                             meal_date=meal_date,
                             class_info=class_info,
                             total_pending=len(pending_students)))
    
    # Add headers to prevent caching
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/api/debug-dates')
def api_debug_dates():
    """Debug: Check what dates are in the database"""
    if not is_logged_in():
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        # Get all dates from daily_meals
        daily_meals = DailyMealDB.get_all_dates_with_counts()
        
        return jsonify({
            'dates_in_db': daily_meals,
            'total_dates': len(daily_meals)
        })
        
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500
