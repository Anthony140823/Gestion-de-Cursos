import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import json
from supabase import create_client, Client
import base64
from fpdf import FPDF
import io
from auth import init_auth
import os
from typing import Optional
import uuid

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Gestión de Cursos Online",
    page_icon="🎓",
    layout="wide"
)

# --- CSS MEJORADO CON ROLES ---
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .role-badge {
        padding: 0.25rem 0.5rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
        display: inline-block;
        margin: 0.25rem;
    }
    .admin-badge { background-color: #ff6b6b; color: white; }
    .teacher-badge { background-color: #4ecdc4; color: white; }
    .student-badge { background-color: #45b7d1; color: white; }
    .custom-container {
        background-color: var(--streamlit-secondary-background-color);
        border: 1px solid var(--streamlit-border-color);
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    .user-info {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    /* Estilo para las tarjetas de métricas */
    [data-testid="stMetric"] {
        background-color: var(--streamlit-secondary-background-color);
        border: 1px solid var(--streamlit-border-color);
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    /* Estilo para los formularios */
    [data-testid="stForm"] {
        background-color: var(--streamlit-secondary-background-color);
        padding: 2rem;
        border-radius: 10px;
        border: 1px solid var(--streamlit-border-color);
    }
    .file-upload-section {
        border: 2px dashed #ccc;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        margin: 10px 0;
    }
    .file-upload-section:hover {
        border-color: #1f77b4;
    }
    .exam-container {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        background-color: #f9f9f9;
    }
    .question-card {
        background-color: white;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .timer-warning {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
    }
    .timer-danger {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
    }
    .feedback-correct {
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
    border-radius: 5px;
    padding: 10px;
    margin: 5px 0;
    }

    .feedback-incorrect {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 10px;
        margin: 5px 0;
    }

    .feedback-explanation {
        background-color: #e2e3e5;
        border: 1px solid #d6d8db;
        border-radius: 5px;
        padding: 10px;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# --- CONFIGURACIÓN SUPABASE Y AUTH ---
@st.cache_resource
def init_supabase():
    supabase_url = st.secrets["SUPABASE_URL"]
    supabase_key = st.secrets["SUPABASE_KEY"]
    return create_client(supabase_url, supabase_key)

supabase = init_supabase()
auth_system = init_auth(supabase)
N8N_WEBHOOK_URL = st.secrets["N8N_WEBHOOK_URL"]

# --- FUNCIONES PARA MANEJO DE ARCHIVOS CON BASE64 ---
def get_file_extension(file_name: str) -> str:
    """Obtiene la extensión del archivo"""
    return os.path.splitext(file_name)[1].lower().replace('.', '')

def get_file_type(extension: str) -> str:
    """Determina el tipo de archivo para la base de datos"""
    document_extensions = ['pdf', 'doc', 'docx', 'txt']
    presentation_extensions = ['ppt', 'pptx']
    spreadsheet_extensions = ['xls', 'xlsx', 'csv']
    image_extensions = ['jpg', 'jpeg', 'png', 'gif']
    
    if extension in document_extensions:
        return 'document'
    elif extension in presentation_extensions:
        return 'presentation'
    elif extension in spreadsheet_extensions:
        return 'spreadsheet'
    elif extension in image_extensions:
        return 'image'
    else:
        return 'other'

def upload_file_base64(file, module_id, title=None):
    """
    Sube archivos guardándolos como base64 en la base de datos
    """
    try:
        if title is None:
            title = file.name
        
        # Verificar tamaño del archivo (límite de 10MB para base64)
        file_size = len(file.getvalue())
        if file_size > 10 * 1024 * 1024:  # 10MB
            st.error("❌ Archivo muy grande. Límite: 10MB")
            return None
        
        # Convertir archivo a base64
        file_content_b64 = base64.b64encode(file.getvalue()).decode('utf-8')
        
        # Obtener tipo de archivo
        file_extension = get_file_extension(file.name)
        file_type = get_file_type(file_extension)
        
        # Guardar en study_materials
        material_data = {
            'module_id': module_id,
            'title': title,
            'file_content_b64': file_content_b64,
            'file_name': file.name,
            'file_size': file_size,
            'file_type': file_type,
            'uploaded_by': st.session_state.user['id']
        }
        
        response = supabase.table('study_materials').insert(material_data).execute()
        
        if response.data:
            st.success(f"✅ Archivo '{file.name}' guardado exitosamente")
            return response.data[0]['id']
        else:
            st.error("❌ Error al guardar en la base de datos")
            return None
            
    except Exception as e:
        st.error(f"❌ Error subiendo archivo: {e}")
        return None

def download_file_base64(material_id):
    """
    Descarga un archivo guardado como base64
    """
    try:
        response = supabase.table('study_materials').select('*').eq('id', material_id).execute()
        
        if response.data and response.data[0].get('file_content_b64'):
            material = response.data[0]
            file_content = base64.b64decode(material['file_content_b64'])
            file_name = material.get('file_name', 'download')
            return file_content, file_name
        return None, None
        
    except Exception as e:
        st.error(f"❌ Error descargando archivo: {e}")
        return None, None

# --- CLASES Y FUNCIONES EXISTENTES ---
class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Reporte de Gestión de Cursos', 0, 1, 'C')
        self.ln(10)
    
    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(5)
    
    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, body)
        self.ln()

def trigger_n8n_workflow(workflow_type, data):
    payload = {"workflow_type": workflow_type, "data": data}
    try:
        response = requests.post(N8N_WEBHOOK_URL, json=payload)
        return response.status_code == 200
    except:
        return False

def clear_cache():
    st.cache_data.clear()

# --- FUNCIONES DE DATOS ---
@st.cache_data(ttl=60)
def get_courses():
    response = supabase.table('courses').select('*').eq('is_active', True).order('created_at', desc=True).execute()
    return response.data

@st.cache_data(ttl=60)
def get_users(role=None):
    query = supabase.table('users').select('*').eq('is_active', True)
    if role:
        query = query.eq('role', role)
    response = query.order('created_at', desc=True).execute()
    return response.data

@st.cache_data(ttl=60)
def get_enrollments():
    response = supabase.table('enrollments').select('*, users(*), courses(*)').order('enrollment_date', desc=True).execute()
    return response.data

@st.cache_data(ttl=60)
def get_exam_results():
    response = supabase.table('exam_results').select('*, exams(title), users(first_name, last_name)').order('completed_at', desc=True).execute()
    return response.data

@st.cache_data(ttl=60)
def get_teacher_assignments(teacher_id=None):
    query = supabase.table('teacher_assignments').select('*, courses(*), users(*)')
    if teacher_id:
        query = query.eq('teacher_id', teacher_id)
    response = query.execute()
    return response.data

@st.cache_data(ttl=60)
def get_study_materials(module_id=None):
    query = supabase.table('study_materials').select('*')
    if module_id:
        query = query.eq('module_id', module_id)
    response = query.order('created_at', desc=True).execute()
    return response.data

@st.cache_data(ttl=60)
def get_assignments(module_id=None):
    query = supabase.table('assignments').select('*')
    if module_id:
        query = query.eq('module_id', module_id)
    response = query.order('created_at', desc=True).execute()
    return response.data

@st.cache_data(ttl=60)
def get_exams(course_id=None, module_id=None):
    """Obtener exámenes - maneja la estructura correcta de la BD"""
    try:
        query = supabase.table('exams').select('*')
        
        if module_id:
            # Filtrar por módulo específico
            query = query.eq('module_id', module_id)
        elif course_id:
            # Filtrar por curso: obtener módulos del curso primero, luego sus exámenes
            modules_response = supabase.table('course_modules')\
                .select('id')\
                .eq('course_id', course_id)\
                .execute()
            
            if modules_response.data:
                module_ids = [module['id'] for module in modules_response.data]
                query = query.in_('module_id', module_ids)
            else:
                return []
        
        response = query.order('created_at', desc=True).execute()
        return response.data
        
    except Exception as e:
        st.error(f"Error al obtener exámenes: {e}")
        return []

@st.cache_data(ttl=60)
def get_exam_questions(exam_id):
    """Obtener preguntas de examen - maneja tanto la estructura nueva como la antigua"""
    try:
        # Primero intentar con la nueva estructura (tabla exam_questions)
        response = supabase.table('exam_questions').select('*').eq('exam_id', exam_id).order('question_order').execute()
        if response.data:
            return response.data
        
        # Si no hay preguntas en la nueva estructura, intentar con la estructura antigua (campo questions en exams)
        exam_response = supabase.table('exams').select('questions').eq('id', exam_id).execute()
        if exam_response.data and exam_response.data[0].get('questions'):
            # Convertir la estructura antigua a la nueva
            old_questions = exam_response.data[0]['questions']
            converted_questions = []
            
            for i, q in enumerate(old_questions):
                if isinstance(q, dict):
                    converted_questions.append({
                        'id': f'temp_{i}',
                        'exam_id': exam_id,
                        'question_type': q.get('type', 'multiple_choice'),
                        'question_text': q.get('question', ''),
                        'correct_answer': json.dumps(q.get('options', [])),
                        'points': q.get('points', 1.0),
                        'question_order': i + 1
                    })
            
            return converted_questions
        
        return []
    except Exception as e:
        st.error(f"Error al obtener preguntas: {e}")
        return []

def migrate_exam_questions(exam_id):
    """Migrar preguntas de la estructura antigua a la nueva"""
    try:
        exam_response = supabase.table('exams').select('questions').eq('id', exam_id).execute()
        if not exam_response.data or not exam_response.data[0].get('questions'):
            return False
        
        old_questions = exam_response.data[0]['questions']
        new_questions = []
        
        for i, q in enumerate(old_questions):
            if isinstance(q, dict):
                question_data = {
                    'exam_id': exam_id,
                    'question_type': q.get('type', 'multiple_choice'),
                    'question_text': q.get('question', ''),
                    'points': q.get('points', 1.0),
                    'question_order': i + 1
                }
                
                # Convertir respuestas según el tipo
                if q.get('type') == 'multiple_choice':
                    options = []
                    for opt in q.get('options', []):
                        options.append({
                            'text': opt.get('text', ''),
                            'is_correct': opt.get('correct', False)
                        })
                    question_data['correct_answer'] = json.dumps(options)
                elif q.get('type') == 'true_false':
                    question_data['correct_answer'] = str(q.get('correct_answer', 'true')).lower()
                else:
                    question_data['correct_answer'] = str(q.get('correct_answer', ''))
                
                new_questions.append(question_data)
        
        # Insertar en la nueva tabla
        for question in new_questions:
            supabase.table('exam_questions').insert(question).execute()
        
        return True
        
    except Exception as e:
        st.error(f"Error en migración de preguntas: {e}")
        return False
    
@st.cache_data(ttl=60)
def get_exam_attempts(exam_id=None, student_id=None):
    query = supabase.table('exam_attempts').select('*')
    if exam_id:
        query = query.eq('exam_id', exam_id)
    if student_id:
        query = query.eq('student_id', student_id)
    
    # Ordenar por fecha de inicio (más reciente primero)
    query = query.order('started_at', desc=True)
    
    try:
        response = query.execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error al obtener intentos de examen: {e}")
        return []

def generate_pdf_report():
    pdf = PDFReport()
    pdf.add_page()
    courses = get_courses()
    users = get_users()
    enrollments = get_enrollments()
    exam_results = get_exam_results()
    
    pdf.chapter_title("Estadísticas Generales")
    stats_text = f"""
    Total de Cursos: {len(courses)}
    Total de Usuarios: {len(users)}
    Total de Inscripciones: {len(enrollments)}
    Tasa de Completación: {len([e for e in enrollments if e.get('completion_status') == 'completed']) / len(enrollments) * 100 if enrollments else 0:.2f}%
    Promedio de Calificaciones: {sum([er.get('score', 0) for er in exam_results if er.get('score')]) / len(exam_results) if exam_results else 0:.2f}
    """
    pdf.chapter_body(stats_text)
    
    pdf.chapter_title("Cursos Más Populares")
    course_enrollments = {}
    for enrollment in enrollments:
        if enrollment.get('courses'):
            course_name = enrollment['courses']['name']
            course_enrollments[course_name] = course_enrollments.get(course_name, 0) + 1
    popular_courses = "\n".join([f"{course}: {count} estudiantes" 
                                 for course, count in sorted(course_enrollments.items(), 
                                 key=lambda x: x[1], reverse=True)[:5]])
    pdf.chapter_body(popular_courses)
    return pdf

STATUS_MAP = {
    "in_progress": "En Progreso",
    "completed": "Completado",
    "pending": "Pendiente"
}

# --- NUEVAS FUNCIONES PARA TAREAS Y EXÁMENES ---
def create_assignment_submission_file(file_content, file_name):
    """
    Guarda un archivo de entrega de tarea como base64
    """
    try:
        file_content_b64 = base64.b64encode(file_content).decode('utf-8')
        file_extension = get_file_extension(file_name)
        file_type = get_file_type(file_extension)
        
        submission_file_data = {
            'file_content_b64': file_content_b64,
            'file_name': file_name,
            'file_type': file_type,
            'uploaded_by': st.session_state.user['id']
        }
        
        response = supabase.table('assignment_submission_files').insert(submission_file_data).execute()
        
        if response.data:
            return response.data[0]['id']
        return None
    except Exception as e:
        st.error(f"Error guardando archivo de entrega: {e}")
        return None

def get_assignment_submission_file(file_id):
    """
    Recupera un archivo de entrega de tarea
    """
    try:
        response = supabase.table('assignment_submission_files').select('*').eq('id', file_id).execute()
        if response.data and response.data[0].get('file_content_b64'):
            file_data = response.data[0]
            file_content = base64.b64decode(file_data['file_content_b64'])
            return file_content, file_data['file_name']
        return None, None
    except Exception as e:
        st.error(f"Error recuperando archivo: {e}")
        return None, None

def check_exam_availability(exam):
    """
    Verifica si un examen está disponible para el estudiante
    """
    try:
        now = datetime.now()
        
        # Debug info
        st.sidebar.write(f"Debug - Exam ID: {exam.get('id')}")
        st.sidebar.write(f"Debug - Activation date: {exam.get('activation_date')}")
        
        activation_date = datetime.fromisoformat(exam['activation_date'].replace('Z', '+00:00')) if exam.get('activation_date') else None
        
        # Verificar fecha de activación
        if activation_date and now < activation_date:
            st.sidebar.write("Debug - Exam not yet available")
            return False, "El examen aún no está disponible"
        
        # Verificar intentos previos
        attempts = get_exam_attempts(exam['id'], st.session_state.user['id'])
        max_attempts = exam.get('max_attempts', 1)
        st.sidebar.write(f"Debug - Attempts: {len(attempts)}/{max_attempts}")
        
        if attempts and len(attempts) >= max_attempts:
            st.sidebar.write("Debug - Max attempts reached")
            return False, "Ya has completado el máximo de intentos permitidos"
        
        st.sidebar.write("Debug - Exam is available")
        return True, "Disponible"
        
    except Exception as e:
        st.sidebar.error(f"Error en check_exam_availability: {e}")
        return False, f"Error: {e}"

def calculate_exam_time_remaining(exam_attempt, exam):
    """
    Calcula el tiempo restante para un examen
    """
    if not exam_attempt or not exam.get('time_limit_minutes'):
        return None
    
    started_at = datetime.fromisoformat(exam_attempt['started_at'].replace('Z', '+00:00'))
    time_limit = timedelta(minutes=exam['time_limit_minutes'])
    end_time = started_at + time_limit
    now = datetime.now()
    
    if now >= end_time:
        return timedelta(0)
    
    return end_time - now

# --- PÁGINAS DE AUTENTICACIÓN ---
def show_login_page():
    st.markdown('<div class="main-header">🎓 Sistema de Gestión de Cursos Online</div>', unsafe_allow_html=True)
    
    if 'require_password_setup' in st.session_state:
        show_password_setup()
        return
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            st.subheader("Iniciar Sesión")
            email = st.text_input("Email")
            password = st.text_input("Contraseña", type="password")
            
            if st.form_submit_button("Ingresar", type="primary"):
                user = auth_system.authenticate_user(email, password)
                if user:
                    st.session_state.user = user
                    st.session_state.token = auth_system.create_jwt_token(user)
                    st.success(f"¡Bienvenido {user['first_name']}!")
                    st.rerun()
                else:
                    if not st.session_state.get('require_password_setup'):
                        st.error("Credenciales incorrectas")
        
        with st.expander("¿No tienes cuenta? Regístrate como estudiante"):
            with st.form("register_form"):
                st.subheader("Registro de Estudiante")
                reg_first_name = st.text_input("Nombre")
                reg_last_name = st.text_input("Apellido")
                reg_email = st.text_input("Email")
                reg_password = st.text_input("Contraseña", type="password")
                reg_confirm_password = st.text_input("Confirmar Contraseña", type="password")
                
                if st.form_submit_button("Registrarse"):
                    if reg_password != reg_confirm_password:
                        st.error("Las contraseñas no coinciden")
                    elif len(reg_password) < 6:
                        st.error("La contraseña debe tener al menos 6 caracteres")
                    else:
                        new_user = auth_system.create_user(
                            reg_email, reg_password, reg_first_name, reg_last_name, 'student'
                        )
                        if new_user:
                            st.success("¡Registro exitoso! Ahora puedes iniciar sesión.")
                        else:
                            st.error("Error en el registro. El email puede estar en uso.")

def show_password_setup():
    st.markdown('<div class="main-header">🔐 Establecer Contraseña</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("password_setup_form"):
            st.subheader("Establece tu contraseña")
            st.info("Como usuario existente, necesitas establecer una contraseña para continuar.")
            
            new_password = st.text_input("Nueva Contraseña", type="password")
            confirm_password = st.text_input("Confirmar Contraseña", type="password")
            
            if st.form_submit_button("Establecer Contraseña", type="primary"):
                if not new_password or not confirm_password:
                    st.error("Por favor completa ambos campos")
                elif new_password != confirm_password:
                    st.error("Las contraseñas no coinciden")
                elif len(new_password) < 6:
                    st.error("La contraseña debe tener al menos 6 caracteres")
                else:
                    user_id = st.session_state.require_password_setup
                    updated_user = auth_system.migrate_existing_user(user_id, new_password)
                    
                    if updated_user:
                        st.success("¡Contraseña establecida exitosamente! Ahora puedes iniciar sesión.")
                        del st.session_state.require_password_setup
                        st.rerun()
                    else:
                        st.error("Error al establecer la contraseña")
        
        if st.button("Volver al Login"):
            if 'require_password_setup' in st.session_state:
                del st.session_state.require_password_setup
            st.rerun()

def show_logout():
    st.sidebar.markdown("---")
    if st.sidebar.button("Cerrar Sesión"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- PÁGINAS POR ROL ---
def show_admin_dashboard():
    st.header("👨‍💼 Dashboard Administrador")
    
    col1, col2, col3, col4 = st.columns(4)
    
    users_count = len(get_users())
    courses_count = len(get_courses())
    teachers_count = len(get_users('teacher'))
    students_count = len(get_users('student'))
    
    with col1:
        st.metric("Total Usuarios", users_count)
    with col2:
        st.metric("Total Cursos", courses_count)
    with col3:
        st.metric("Profesores", teachers_count)
    with col4:
        st.metric("Estudiantes", students_count)
    
    tab1, tab2, tab3, tab4 = st.tabs(["Gestión de Usuarios", "Gestión de Cursos", "Asignar Profesores", "Reportes"])
    
    with tab1:
        st.subheader("Crear Nuevo Usuario")
        with st.form("create_user_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_first_name = st.text_input("Nombre", key="admin_first_name")
                new_last_name = st.text_input("Apellido", key="admin_last_name")
                new_email = st.text_input("Email", key="admin_email")
            with col2:
                new_password = st.text_input("Contraseña", type="password", key="admin_password")
                new_role = st.selectbox("Rol", ["student", "teacher", "admin"], key="admin_role")
            
            if st.form_submit_button("Crear Usuario", type="primary"):
                if not all([new_first_name, new_last_name, new_email, new_password]):
                    st.error("Por favor completa todos los campos")
                elif len(new_password) < 6:
                    st.error("La contraseña debe tener al menos 6 caracteres")
                else:
                    new_user = auth_system.create_user(
                        new_email, new_password, new_first_name, new_last_name, new_role
                    )
                    if new_user:
                        st.success(f"Usuario {new_role} creado exitosamente")
                        clear_cache()
                    else:
                        st.error("Error al crear usuario. El email puede estar en uso.")
        
        st.subheader("Todos los Usuarios")
        users = get_users()
        if users:
            df_data = []
            for user in users:
                df_data.append({
                    'ID': user['id'],
                    'Nombre': user['first_name'],
                    'Apellido': user['last_name'],
                    'Email': user['email'],
                    'Rol': user['role'],
                    'Creado': user['created_at'][:10] if user.get('created_at') else 'N/A'
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("Gestión Completa de Cursos")
        courses = get_courses()
        if courses:
            for course in courses:
                with st.expander(f"📚 {course['name']}", expanded=False):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**Descripción:** {course.get('description', 'Sin descripción')}")
                        st.write(f"**Duración:** {course.get('duration_days', 0)} días")
                        st.write(f"**Precio:** ${course.get('price', 0)}")
                    
                    with col2:
                        if st.button("Editar Curso", key=f"edit_course_{course['id']}"):
                            st.session_state.editing_course_admin = course
                        
                        if st.button("Eliminar", key=f"delete_course_{course['id']}", type="secondary"):
                            try:
                                supabase.table('courses').update({'is_active': False}).eq('id', course['id']).execute()
                                st.success("Curso eliminado")
                                clear_cache()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
        
        with st.form("quick_create_course"):
            st.subheader("Crear Nuevo Curso")
            name = st.text_input("Nombre del Curso")
            description = st.text_area("Descripción")
            
            if st.form_submit_button("Crear Curso Rápido"):
                if name:
                    new_course = {
                        'name': name,
                        'description': description,
                        'price': 0,
                        'duration_days': 30
                    }
                    supabase.table('courses').insert(new_course).execute()
                    st.success("Curso creado")
                    clear_cache()
                    st.rerun()

    with tab3:
        st.subheader("Asignar Profesores a Cursos")
        teachers = get_users('teacher')
        courses = get_courses()
        
        if teachers and courses:
            with st.form("assign_teacher_form"):
                col1, col2 = st.columns(2)
                with col1:
                    selected_teacher = st.selectbox(
                        "Profesor",
                        teachers,
                        format_func=lambda t: f"{t['first_name']} {t['last_name']} ({t['email']})",
                        key="teacher_assign"
                    )
                with col2:
                    selected_course = st.selectbox(
                        "Curso",
                        courses,
                        format_func=lambda c: c['name'],
                        key="course_assign"
                    )
                
                if st.form_submit_button("Asignar Profesor", type="primary"):
                    existing = supabase.table('teacher_assignments')\
                        .select('*')\
                        .eq('teacher_id', selected_teacher['id'])\
                        .eq('course_id', selected_course['id'])\
                        .execute()
                    
                    if existing.data:
                        st.warning("Este profesor ya está asignado a este curso")
                    else:
                        assignment = {
                            'teacher_id': selected_teacher['id'],
                            'course_id': selected_course['id']
                        }
                        try:
                            supabase.table('teacher_assignments').insert(assignment).execute()
                            st.success("Profesor asignado exitosamente")
                            clear_cache()
                        except Exception as e:
                            st.error(f"Error en asignación: {e}")
        else:
            st.info("Necesitas crear profesores y cursos primero")
            
        st.subheader("Asignaciones Existentes")
        assignments = get_teacher_assignments()
        if assignments:
            for assignment in assignments:
                if assignment.get('courses') and assignment.get('users'):
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        st.write(f"**{assignment['users']['first_name']} {assignment['users']['last_name']}** → **{assignment['courses']['name']}**")
                    with col3:
                        if st.button("❌", key=f"remove_assign_{assignment['id']}"):
                            supabase.table('teacher_assignments').delete().eq('id', assignment['id']).execute()
                            st.success("Asignación eliminada")
                            clear_cache()
                            st.rerun()

    with tab4:
        st.subheader("Reportes de Administrador")
        show_reports()

def show_teacher_dashboard():
    st.header("👨‍🏫 Panel del Profesor")
    
    user = st.session_state.user
    st.info(f"Bienvenido, Profesor {user['first_name']} {user['last_name']}")
    
    teacher_assignments = get_teacher_assignments(user['id'])
    
    if not teacher_assignments:
        st.info("No tienes cursos asignados. Contacta al administrador.")
        return
    
    st.subheader("Mis Cursos Asignados")
    
    for assignment in teacher_assignments:
        course = assignment['courses']
        with st.expander(f"📚 {course['name']}", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Gestión de Contenido**")
                if st.button("📁 Gestionar Módulos", key=f"modules_{course['id']}"):
                    st.session_state.current_course = course
                    st.session_state.show_module_management = True
                
                if st.button("📝 Crear Tarea", key=f"assignment_{course['id']}"):
                    st.session_state.current_course = course
                    st.session_state.show_assignment_creation = True
                    
            with col2:
                st.markdown("**Evaluaciones**")
                if st.button("📊 Crear Examen", key=f"exam_{course['id']}"):
                    st.session_state.current_course = course
                    st.session_state.show_exam_creation = True
                
                if st.button("👀 Ver Entregas", key=f"submissions_{course['id']}"):
                    st.session_state.current_course = course
                    st.session_state.show_submissions = True
            
            with col3:
                st.markdown("**Estadísticas**")
                enrollments = supabase.table('enrollments')\
                    .select('*')\
                    .eq('course_id', course['id'])\
                    .execute().data
                
                st.write(f"**Estudiantes inscritos:** {len(enrollments)}")
                completed = len([e for e in enrollments if e.get('completion_status') == 'completed'])
                st.write(f"**Completados:** {completed}")
    
    if st.session_state.get('show_module_management'):
        show_module_management()
    
    if st.session_state.get('show_assignment_creation'):
        show_assignment_creation()
    
    if st.session_state.get('show_exam_creation'):
        show_exam_creation()
    
    if st.session_state.get('show_submissions'):
        show_submissions_management()

def show_student_dashboard():
    st.header("🎓 Mi Aprendizaje")
    
    user = st.session_state.user
    st.info(f"Bienvenido, {user['first_name']} {user['last_name']}")
    
    enrollments = supabase.table('enrollments')\
        .select('*, courses(*)')\
        .eq('student_id', user['id'])\
        .execute().data
    
    if not enrollments:
        st.info("No estás inscrito en ningún curso. Contacta al administrador.")
        return
    
    st.subheader("Mis Cursos")
    
    for enrollment in enrollments:
        course = enrollment['courses']
        with st.expander(f"📖 {course['name']} - Progreso: {enrollment.get('progress_percentage', 0)}%", expanded=True):
            
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**Descripción:** {course.get('description', 'Sin descripción')}")
                st.write(f"**Estado:** {STATUS_MAP.get(enrollment.get('completion_status', 'in_progress'), 'En Progreso')}")
                
                progress = enrollment.get('progress_percentage', 0) or 0
                st.progress(float(progress) / 100)
                st.write(f"Progreso: {progress}%")
            
            with col2:
                if st.button("📚 Contenido", key=f"content_{course['id']}"):
                    st.session_state.current_course = course
                    st.session_state.show_student_content = True
            
            with col3:
                if st.button("📝 Actividades", key=f"activities_{course['id']}"):
                    st.session_state.current_course = course
                    st.session_state.show_student_activities = True
    
    if st.session_state.get('show_student_content'):
        show_student_content()
    
    if st.session_state.get('show_student_activities'):
        show_student_activities()

def check_admin_permissions():
    if 'user' not in st.session_state:
        st.error("No autenticado")
        return False
    
    user_role = st.session_state.user.get('role')
    if user_role != 'admin':
        st.error("🔒 No tienes permisos de administrador para acceder a esta sección")
        st.info("Contacta al administrador del sistema si necesitas acceso")
        return False
    
    return True

def check_teacher_permissions():
    if 'user' not in st.session_state:
        st.error("No autenticado")
        return False
    
    user_role = st.session_state.user.get('role')
    if user_role != 'teacher':
        st.error("🔒 No tienes permisos de profesor para acceder a esta sección")
        return False
    
    return True

def check_teacher_course_access(course_id):
    if not check_teacher_permissions():
        return False
    
    teacher_assignments = get_teacher_assignments(st.session_state.user['id'])
    assigned_course_ids = [assignment['course_id'] for assignment in teacher_assignments if assignment.get('course_id')]
    
    if course_id not in assigned_course_ids:
        st.error("🔒 No tienes acceso a este curso")
        return False
    
    return True

# --- FUNCIONALIDADES ESPECÍFICAS ---
def show_module_management():
    if not check_teacher_permissions():
        return
    
    st.subheader("📁 Gestión de Módulos")
    course = st.session_state.current_course
    
    if not check_teacher_course_access(course['id']):
        return
    
    st.write(f"Curso: **{course['name']}**")
    
    modules = supabase.table('course_modules')\
        .select('*')\
        .eq('course_id', course['id'])\
        .order('module_number')\
        .execute().data
    
    if modules:
        st.write("**Módulos existentes:**")
        for module in modules:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"**Módulo {module['module_number']}:** {module['title']}")
                    if module.get('study_material'):
                        st.write(f"Material: {module['study_material'][:100]}...")
                    st.write(f"**Día de liberación:** {module.get('release_day', 'No definido')}")
                    
                    materials = get_study_materials(module['id'])
                    if materials:
                        st.write("**Archivos:**")
                        for material in materials:
                            file_icon = "📄" if material.get('file_type') == 'document' else "🖼️" if material.get('file_type') == 'image' else "📊"
                            st.write(f"{file_icon} {material['title']}")
                            if material.get('file_content_b64'):
                                file_content, file_name = download_file_base64(material['id'])
                                if file_content:
                                    st.download_button(
                                        label="📥 Descargar",
                                        data=file_content,
                                        file_name=file_name,
                                        mime="application/octet-stream",
                                        key=f"dl_{material['id']}"
                                    )
                
                with col2:
                    if st.button("Editar", key=f"edit_mod_{module['id']}"):
                        st.session_state.editing_module = module
                
                with col3:
                    if st.button("➕ Material", key=f"add_mat_{module['id']}"):
                        st.session_state.adding_material_to = module
    
    with st.form("module_form"):
        st.subheader("Agregar Nuevo Módulo" if not st.session_state.get('editing_module') else "Editar Módulo")
        
        editing_module = st.session_state.get('editing_module')
        
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Título del Módulo", 
                                 value=editing_module.get('title') if editing_module else "")
            module_number = st.number_input("Número de Módulo", 
                                           min_value=1, 
                                           value=editing_module.get('module_number') if editing_module else 1)
        
        with col2:
            release_day = st.number_input(
                "Día de Liberación", 
                min_value=1, 
                max_value=365,
                value=editing_module.get('release_day') if editing_module else 1,
                help="Día en que se libera este módulo (1 = primer día del curso)"
            )
        
        study_material = st.text_area("Material de Estudio (texto)", 
                                     value=editing_module.get('study_material') if editing_module else "")
        
        external_link_value = ""
        if editing_module and 'external_link' in editing_module:
            external_link_value = editing_module.get('external_link', '')
        
        external_link = st.text_input("Enlace externo (opcional)", value=external_link_value)
        
        st.markdown("### 📎 Archivos del Módulo")
        uploaded_files = st.file_uploader(
            "Subir archivos de estudio", 
            type=['pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'txt', 'jpg', 'jpeg', 'png'],
            accept_multiple_files=True,
            key="module_files"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Guardar Módulo", type="primary"):
                module_data = {
                    'course_id': course['id'],
                    'title': title,
                    'module_number': module_number,
                    'release_day': release_day,
                    'study_material': study_material
                }
                
                if external_link and external_link.strip():
                    module_data['external_link'] = external_link.strip()
                
                try:
                    if editing_module:
                        supabase.table('course_modules').update(module_data).eq('id', editing_module['id']).execute()
                        st.success("Módulo actualizado exitosamente")
                        if 'editing_module' in st.session_state:
                            del st.session_state.editing_module
                    else:
                        response = supabase.table('course_modules').insert(module_data).execute()
                        new_module = response.data[0] if response.data else None
                        st.success("Módulo creado exitosamente")
                    
                    # SUBIR ARCHIVOS CON BASE64
                    if uploaded_files and not editing_module and new_module:
                        for uploaded_file in uploaded_files:
                            material_id = upload_file_base64(uploaded_file, new_module['id'])
                            if material_id:
                                st.success(f"✅ '{uploaded_file.name}' guardado correctamente")
                    
                    clear_cache()
                    st.rerun()
                
                except Exception as e:
                    st.error(f"Error al guardar módulo: {e}")
        
        with col2:
            if st.form_submit_button("Cancelar"):
                if 'editing_module' in st.session_state:
                    del st.session_state.editing_module
                st.rerun()
    
    if st.session_state.get('adding_material_to'):
        module = st.session_state.adding_material_to
        with st.form("add_material_form"):
            st.subheader(f"Agregar Material a: Módulo {module['module_number']} - {module['title']}")
            
            material_title = st.text_input("Título del material")
            uploaded_file = st.file_uploader(
                "Seleccionar archivo",
                type=['pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'txt', 'jpg', 'jpeg', 'png'],
                key="additional_material"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Agregar Material", type="primary"):
                    if uploaded_file and material_title:
                        material_id = upload_file_base64(uploaded_file, module['id'], material_title)
                        if material_id:
                            st.success("Material agregado exitosamente")
                            del st.session_state.adding_material_to
                            clear_cache()
                            st.rerun()
                    else:
                        st.error("Por favor completa el título y selecciona un archivo")
            
            with col2:
                if st.form_submit_button("Cancelar"):
                    del st.session_state.adding_material_to
                    st.rerun()
    
    if st.button("Volver al Dashboard"):
        st.session_state.show_module_management = False
        if 'editing_module' in st.session_state:
            del st.session_state.editing_module
        if 'adding_material_to' in st.session_state:
            del st.session_state.adding_material_to
        st.rerun()

def show_assignment_creation():
    if not check_teacher_permissions():
        return
    
    st.subheader("📝 Crear Nueva Tarea")
    course = st.session_state.current_course
    
    if not check_teacher_course_access(course['id']):
        return
    
    with st.form("create_assignment_form"):
        st.write(f"Curso: **{course['name']}**")
        
        title = st.text_input("Título de la Tarea")
        description = st.text_area("Descripción")
        
        due_date = st.date_input("Fecha Límite", min_value=datetime.now().date())
        due_time = st.time_input("Hora Límite", value=datetime.now().time())
        due_datetime = datetime.combine(due_date, due_time)
        
        max_score = st.number_input("Puntaje Máximo", value=100.0, min_value=0.0, max_value=100.0)
        
        st.markdown("### 📎 Archivos Guía (Opcional)")
        guide_files = st.file_uploader(
            "Subir archivos guía para la tarea",
            type=['pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'txt'],
            accept_multiple_files=True,
            key="assignment_guides"
        )
        
        modules = supabase.table('course_modules')\
            .select('*')\
            .eq('course_id', course['id'])\
            .order('module_number')\
            .execute().data
        
        module_options = [None] + modules if modules else [None]
        selected_module = st.selectbox(
            "Asociar a Módulo (opcional)",
            module_options,
            format_func=lambda m: f"Módulo {m['module_number']}: {m['title']}" if m else "Sin módulo específico"
        )
        
        if st.form_submit_button("Crear Tarea", type="primary"):
            if not title:
                st.error("El título es obligatorio")
            else:
                assignment_data = {
                    'module_id': selected_module['id'] if selected_module else None,
                    'title': title,
                    'description': description,
                    'due_date': due_datetime.isoformat(),
                    'max_score': max_score,
                    'created_by': st.session_state.user['id']
                }
                
                try:
                    response = supabase.table('assignments').insert(assignment_data).execute()
                    new_assignment = response.data[0] if response.data else None
                    
                    # Subir archivos guía con base64
                    if guide_files and new_assignment:
                        for guide_file in guide_files:
                            material_id = upload_file_base64(
                                guide_file, 
                                selected_module['id'] if selected_module else None,
                                f"Guía: {guide_file.name}"
                            )
                            if material_id:
                                st.success(f"✅ '{guide_file.name}' subido como guía")
                    
                    st.success("Tarea creada exitosamente")
                    st.session_state.show_assignment_creation = False
                    clear_cache()
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al crear tarea: {e}")
    
    if st.button("Volver al Dashboard"):
        st.session_state.show_assignment_creation = False
        st.rerun()


def show_exam_creation():
    if not check_teacher_permissions():
        return
    
    st.subheader("📊 Crear Nuevo Examen")
    course = st.session_state.current_course
    
    if not check_teacher_course_access(course['id']):
        return
    
    st.write(f"Curso: **{course['name']}**")
    
    with st.form("exam_form"):
        title = st.text_input("Título del Examen")
        description = st.text_area("Descripción del Examen")
        
        col1, col2 = st.columns(2)
        with col1:
            time_limit = st.number_input("Límite de Tiempo (minutos)", min_value=1, value=60)
            max_attempts = st.number_input("Intentos Máximos", min_value=1, value=1)
            passing_score = st.number_input("Puntaje para Aprobar", min_value=0, max_value=20, value=14)
        
        with col2:
            activation_date = st.date_input("Fecha de Activación", min_value=datetime.now().date())
            activation_time = st.time_input("Hora de Activación", value=datetime.now().time())
            activation_datetime = datetime.combine(activation_date, activation_time)
            allow_file_upload = st.checkbox("Permitir subida de archivos")
        
        # Obtener módulos del curso
        modules = supabase.table('course_modules')\
            .select('*')\
            .eq('course_id', course['id'])\
            .order('module_number')\
            .execute().data
        
        selected_module = None
        if modules:
            selected_module = st.selectbox(
                "Asociar a Módulo",
                modules,
                format_func=lambda m: f"Módulo {m['module_number']}: {m['title']}"
            )
        
        if st.form_submit_button("Crear Examen", type="primary"):
            if not title:
                st.error("El título es obligatorio")
            else:
                # Crear datos básicos del examen
                exam_data = {
                    'module_id': selected_module['id'] if selected_module else None,
                    'title': title,
                    'questions': [],  # Campo requerido por la estructura antigua
                    'passing_score': passing_score
                }
                
                # Agregar campos nuevos si existen
                try:
                    # Verificar si la columna course_id existe agregándola condicionalmente
                    exam_data['course_id'] = course['id']
                except:
                    pass  # Si no existe, no la incluimos
                
                try:
                    # Verificar si la columna description existe
                    if description:
                        exam_data['description'] = description
                except:
                    pass
                
                try:
                    # Verificar si la columna time_limit_minutes existe
                    exam_data['time_limit_minutes'] = time_limit
                except:
                    pass
                
                try:
                    # Verificar si la columna max_attempts existe
                    exam_data['max_attempts'] = max_attempts
                except:
                    pass
                
                try:
                    # Verificar si la columna activation_date existe
                    exam_data['activation_date'] = activation_datetime.isoformat()
                except:
                    pass
                
                try:
                    # Verificar si la columna allow_file_upload existe
                    exam_data['allow_file_upload'] = allow_file_upload
                except:
                    pass
                
                try:
                    # Verificar si la columna created_by existe
                    exam_data['created_by'] = st.session_state.user['id']
                except:
                    pass
                
                try:
                    response = supabase.table('exams').insert(exam_data).execute()
                    new_exam = response.data[0] if response.data else None
                    
                    if new_exam:
                        st.success("Examen creado exitosamente")
                        st.session_state.new_exam_id = new_exam['id']
                        st.session_state.show_question_creation = True
                    clear_cache()
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al crear examen: {e}")
                    # Mostrar más detalles del error
                    st.error(f"Detalles del error: {str(e)}")
                    # Mostrar los datos que se intentaron insertar
                    st.info(f"Datos enviados: {exam_data}")
    
    if st.session_state.get('show_question_creation'):
        show_question_creation()
    
    if st.button("Volver al Dashboard"):
        st.session_state.show_exam_creation = False
        if 'show_question_creation' in st.session_state:
            del st.session_state.show_question_creation
        st.rerun()

def reset_question_form():
    """Restablecer el formulario de pregunta cuando cambia el tipo"""
    if 'question_text' in st.session_state:
        st.session_state.question_text = ""
    if 'question_points' in st.session_state:
        st.session_state.question_points = 1.0
    # No resetear options para mantener las opciones existentes

def check_exams_structure():
    """Verificar la estructura actual de la tabla exams"""
    try:
        # Intentar obtener la estructura de exams
        response = supabase.table('exams').select('*').limit(1).execute()
        if response.data:
            first_exam = response.data[0]
            st.sidebar.info("Estructura de exams encontrada")
            st.sidebar.write(f"Columnas: {list(first_exam.keys())}")
            return list(first_exam.keys())
        return []
    except Exception as e:
        st.sidebar.error(f"Error verificando estructura de exams: {e}")
        return []
    
def show_question_creation():
    if not st.session_state.get('new_exam_id'):
        st.error("No hay examen seleccionado")
        return

    exam_id = st.session_state.new_exam_id

    st.subheader("➕ Agregar Preguntas al Examen")

    # Inicializar estado para el tipo de pregunta actual
    if 'current_question_type' not in st.session_state:
        st.session_state.current_question_type = "multiple_choice"

    # Usar un formulario separado solo para seleccionar el tipo de pregunta
    col1, col2 = st.columns([2, 1])
    with col1:
        question_type = st.selectbox(
            "Tipo de Pregunta",
            ["multiple_choice", "true_false", "fill_blank", "open_ended"],
            format_func=lambda x: {
                "multiple_choice": "Opción Múltiple",
                "true_false": "Verdadero/Falso",
                "fill_blank": "Completar Palabras",
                "open_ended": "Pregunta Abierta"
            }[x],
            key="question_type_selector"
        )

    with col2:
        if st.button("🔄 Actualizar Tipo", type="secondary"):
            st.session_state.current_question_type = question_type
            # Limpiar campos específicos del tipo anterior
            if 'options' in st.session_state:
                del st.session_state.options
            st.rerun()

    # Mostrar el tipo actual seleccionado
    st.info(f"**Tipo de pregunta actual:** { {
        'multiple_choice': 'Opción Múltiple',
        'true_false': 'Verdadero/Falso',
        'fill_blank': 'Completar Palabras',
        'open_ended': 'Pregunta Abierta'
    }[st.session_state.current_question_type] }")

    # Formulario principal para la pregunta
    with st.form("question_form", clear_on_submit=True):
        question_text = st.text_area("Texto de la Pregunta", key="question_text")
        points = st.number_input(
            "Puntos",
            min_value=0.0,
            max_value=100.0,
            value=1.0,
            key="question_points"
        )

        # Renderizar campos específicos según el tipo de pregunta actual
        if st.session_state.current_question_type == "multiple_choice":
            st.write("**Opciones:**")

            # Inicializar opciones si no existen
            if 'options' not in st.session_state:
                st.session_state.options = [
                    {"text": "", "is_correct": False} for _ in range(4)
                ]

            # Mostrar opciones
            for i in range(4):
                col1, col2 = st.columns([4, 1])
                with col1:
                    option_text = st.text_input(
                        f"Opción {i + 1}",
                        value=st.session_state.options[i]["text"],
                        key=f"option_text_{i}"
                    )
                    st.session_state.options[i]["text"] = option_text
                with col2:
                    is_correct = st.checkbox(
                        "Correcta",
                        value=st.session_state.options[i]["is_correct"],
                        key=f"option_correct_{i}"
                    )
                    st.session_state.options[i]["is_correct"] = is_correct

            correct_answer = json.dumps(st.session_state.options)

        elif st.session_state.current_question_type == "true_false":
            correct_answer = st.radio(
                "Respuesta Correcta",
                ["true", "false"],
                key="true_false_answer",
                horizontal=True
            )

        elif st.session_state.current_question_type == "fill_blank":
            correct_answer = st.text_input(
                "Respuesta Correcta (texto a completar)",
                key="fill_blank_answer",
                placeholder="Ejemplo: Python"
            )

        else:  # open_ended
            correct_answer = st.text_area(
                "Respuesta Modelo (para corrección)",
                key="open_ended_answer",
                placeholder=(
                    "Describe la respuesta esperada para que la IA pueda "
                    "evaluar las respuestas de los estudiantes..."
                )
            )

        # Botón para agregar pregunta
        col1, col2 = st.columns([1, 1])
        with col1:
            submitted = st.form_submit_button("💾 Agregar Pregunta", type="primary")
        with col2:
            if st.form_submit_button("🔄 Limpiar Formulario"):
                # Limpiar campos específicos
                if 'options' in st.session_state:
                    st.session_state.options = [
                        {"text": "", "is_correct": False} for _ in range(4)
                    ]
                st.rerun()

        if submitted:
            if not question_text or not question_text.strip():
                st.error("El texto de la pregunta es obligatorio")

            elif st.session_state.current_question_type == "multiple_choice":
                # Validar opciones múltiples
                has_correct = any(
                    opt["is_correct"]
                    for opt in st.session_state.options
                    if opt["text"].strip()
                )

                if not has_correct:
                    st.error("Debe haber al menos una opción correcta")

                else:
                    valid_options = all(
                        opt["text"].strip() for opt in st.session_state.options
                    )

                    if not valid_options:
                        st.error("Todas las opciones deben tener texto")
                    else:
                        save_question(
                            exam_id,
                            question_text,
                            st.session_state.current_question_type,
                            correct_answer,
                            points
                        )

            else:
                # Para otros tipos de pregunta, validar respuesta correcta
                if not correct_answer or not correct_answer.strip():
                    st.error("La respuesta correcta es obligatoria")
                else:
                    save_question(
                        exam_id,
                        question_text,
                        st.session_state.current_question_type,
                        correct_answer,
                        points
                    )

    # Mostrar preguntas existentes
    show_existing_questions(exam_id)

    # Botón para finalizar
    st.markdown("---")
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("✅ Finalizar Creación de Examen", type="primary"):
            cleanup_question_creation()

    with col2:
        if st.button("📝 Seguir Agregando Preguntas"):
            st.rerun()

def save_question(exam_id, question_text, question_type, correct_answer, points):
    """Guardar pregunta en la base de datos"""
    try:
        # Obtener el orden actual
        existing_questions = get_exam_questions(exam_id)
        next_order = len(existing_questions) + 1
        
        question_data = {
            'exam_id': exam_id,
            'question_type': question_type,
            'question_text': question_text,
            'correct_answer': correct_answer,
            'points': points,
            'question_order': next_order
        }
        
        supabase.table('exam_questions').insert(question_data).execute()
        st.success("✅ Pregunta agregada exitosamente")
        clear_cache()
        st.rerun()
    except Exception as e:
        st.error(f"❌ Error al agregar pregunta: {e}")

def show_existing_questions(exam_id):
    """Mostrar preguntas existentes del examen"""
    existing_questions = get_exam_questions(exam_id)

    if existing_questions:
        st.markdown("---")
        st.subheader(f"📋 Preguntas Existentes ({len(existing_questions)})")

        for i, question in enumerate(existing_questions, 1):
            with st.expander(
                f"**Pregunta {i}:** {question['question_text'][:80]}...",
                expanded=False
            ):
                col1, col2, col3 = st.columns([3, 1, 1])

                with col1:
                    # Mostrar tipo de pregunta con ícono
                    type_icons = {
                        'multiple_choice': '🔘',
                        'true_false': '✅❌',
                        'fill_blank': '📝',
                        'open_ended': '💬'
                    }
                    icon = type_icons.get(question['question_type'], '❓')

                    st.write(f"**{icon} Tipo:** { {
                        'multiple_choice': 'Opción Múltiple',
                        'true_false': 'Verdadero/Falso',
                        'fill_blank': 'Completar Palabras',
                        'open_ended': 'Pregunta Abierta'
                    }[question['question_type']] }")

                    st.write(f"**📊 Puntos:** {question['points']}")

                    # Mostrar respuesta correcta según el tipo
                    if question['question_type'] == 'multiple_choice':
                        try:
                            options = json.loads(question['correct_answer'])
                            correct_options = [
                                f"**{opt['text']}**"
                                for opt in options
                                if opt.get('is_correct')
                            ]
                            st.write(
                                f"**✅ Respuestas correctas:** {', '.join(correct_options)}"
                            )
                        except Exception:
                            st.write("**⚠️ Error al cargar opciones**")

                    elif question['question_type'] == 'true_false':
                        answer = (
                            "Verdadero"
                            if question['correct_answer'] == 'true'
                            else "Falso"
                        )
                        st.write(f"**✅ Respuesta correcta:** {answer}")

                    else:
                        st.write(
                            f"**✅ Respuesta correcta:** "
                            f"{question['correct_answer'][:100]}"
                            f"{'...' if len(question['correct_answer']) > 100 else ''}"
                        )

                with col3:
                    if st.button(
                        "🗑️ Eliminar",
                        key=f"del_q_{question['id']}",
                        type="secondary"
                    ):
                        try:
                            supabase.table('exam_questions') \
                                .delete() \
                                .eq('id', question['id']) \
                                .execute()

                            st.success("Pregunta eliminada")
                            clear_cache()
                            st.rerun()

                        except Exception as e:
                            st.error(f"Error al eliminar pregunta: {e}")

    else:
        st.info(
            "ℹ️ Aún no hay preguntas en este examen. "
            "Agrega la primera pregunta usando el formulario arriba."
        )

def cleanup_question_creation():
    """Limpiar el estado de creación de preguntas"""
    keys_to_remove = [
        'new_exam_id', 
        'show_question_creation',
        'current_question_type',
        'options',
        'question_text',
        'question_points',
        'true_false_answer', 
        'fill_blank_answer',
        'open_ended_answer'
    ]
    
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]
    
    st.session_state.show_exam_creation = False
    st.success("Examen creado completamente")
    st.rerun()

def show_submissions_management():
    if not check_teacher_permissions():
        return
    
    st.subheader("👀 Gestión de Entregas")
    course = st.session_state.current_course
    
    if not check_teacher_course_access(course['id']):
        return
    
    st.write(f"Curso: **{course['name']}**")
    
    assignments = supabase.table('assignments')\
        .select('*')\
        .execute().data
    
    assignments = [a for a in assignments if a.get('module_id')]
    course_modules = supabase.table('course_modules')\
        .select('id')\
        .eq('course_id', course['id'])\
        .execute().data
    
    module_ids = [module['id'] for module in course_modules]
    assignments = [a for a in assignments if a.get('module_id') in module_ids]
    
    if not assignments:
        st.info("No hay tareas creadas para este curso")
        if st.button("Volver"):
            st.session_state.show_submissions = False
            st.rerun()
        return
    
    for assignment in assignments:
        with st.expander(f"📝 {assignment['title']} - Vence: {assignment['due_date']}"):
            submissions = supabase.table('assignment_submissions')\
                .select('*, users(first_name, last_name)')\
                .eq('assignment_id', assignment['id'])\
                .execute().data
            
            if submissions:
                for submission in submissions:
                    with st.container():
                        col1, col2, col3 = st.columns([3, 1, 1])
                        with col1:
                            student = submission['users']
                            st.write(f"**Estudiante:** {student['first_name']} {student['last_name']}")
                            st.write(f"**Entregado:** {submission['submitted_at']}")
                            st.write(f"**Estado:** {submission.get('status', 'submitted')}")
                        
                        with col2:
                            if submission.get('score') is not None:
                                st.write(f"**Calificación:** {submission['score']}/{assignment['max_score']}")
                            else:
                                st.write("**Por calificar**")
                        
                        with col3:
                            if st.button("Calificar", key=f"grade_{submission['id']}"):
                                st.session_state.grading_submission = submission
                                st.session_state.grading_assignment = assignment
            else:
                st.info("No hay entregas para esta tarea")
    
    if st.session_state.get('grading_submission'):
        show_grading_interface()
    
    if st.button("Volver al Dashboard"):
        st.session_state.show_submissions = False
        if 'grading_submission' in st.session_state:
            del st.session_state.grading_submission
        st.rerun()

def show_grading_interface():
    submission = st.session_state.grading_submission
    assignment = st.session_state.grading_assignment
    
    st.subheader("📊 Calificar Entrega")
    student = submission['users']
    st.write(f"**Estudiante:** {student['first_name']} {student['last_name']}")
    st.write(f"**Tarea:** {assignment['title']}")
    st.write(f"**Entregado:** {submission['submitted_at']}")
    
    # Mostrar archivo de entrega si existe
    if submission.get('file_id'):
        file_content, file_name = get_assignment_submission_file(submission['file_id'])
        if file_content:
            st.download_button(
                label=f"📥 Descargar Entrega: {file_name}",
                data=file_content,
                file_name=file_name,
                mime="application/octet-stream",
                key="download_submission"
            )
    
    with st.form("grading_form"):
        score = st.number_input("Calificación", 
                               min_value=0.0, 
                               max_value=float(assignment['max_score']), 
                               value=float(submission.get('score', 0)))
        feedback = st.text_area("Feedback", value=submission.get('feedback', ''))
        
        if st.form_submit_button("Guardar Calificación", type="primary"):
            update_data = {
                'score': score,
                'feedback': feedback,
                'status': 'graded'
            }
            
            supabase.table('assignment_submissions')\
                .update(update_data)\
                .eq('id', submission['id'])\
                .execute()
            
            st.success("Calificación guardada exitosamente")
            del st.session_state.grading_submission
            del st.session_state.grading_assignment
            clear_cache()
            st.rerun()
    
    if st.button("Cancelar"):
        del st.session_state.grading_submission
        del st.session_state.grading_assignment
        st.rerun()

def show_student_content():
    st.subheader("📚 Contenido del Curso")
    course = st.session_state.current_course
    
    st.write(f"Curso: **{course['name']}**")
    
    modules = supabase.table('course_modules')\
        .select('*')\
        .eq('course_id', course['id'])\
        .order('module_number')\
        .execute().data
    
    if not modules:
        st.info("Este curso no tiene contenido disponible aún.")
        if st.button("Volver"):
            st.session_state.show_student_content = False
            st.rerun()
        return
    
    for module in modules:
        with st.expander(f"📖 Módulo {module['module_number']}: {module['title']}", expanded=False):
            if module.get('study_material'):
                st.write("**Material de estudio:**")
                st.write(module['study_material'])
            
            if module.get('external_link'):
                st.markdown(f"[🔗 Enlace externo]({module['external_link']})")
            
            try:
                materials_response = supabase.table('study_materials')\
                    .select('*')\
                    .eq('module_id', module['id'])\
                    .execute()
                
                materials = materials_response.data if materials_response.data else []
                
                if materials:
                    st.write("---")
                    st.write("**📎 Archivos disponibles:**")
                    
                    for material in materials:
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            file_type = material.get('file_type', 'document')
                            file_icons = {
                                'document': '📄',
                                'image': '🖼️', 
                                'presentation': '📊',
                                'spreadsheet': '📈',
                                'other': '📎'
                            }
                            icon = file_icons.get(file_type, '📎')
                            
                            st.write(f"{icon} **{material['title']}**")
                            if material.get('file_type'):
                                st.caption(f"Tipo: {material['file_type']}")
                        
                        with col2:
                            if material.get('file_content_b64'):
                                file_content, file_name = download_file_base64(material['id'])
                                if file_content:
                                    st.download_button(
                                        label="📥 Descargar",
                                        data=file_content,
                                        file_name=file_name,
                                        mime="application/octet-stream",
                                        key=f"dl_{material['id']}"
                                    )
                
                else:
                    st.info("No hay archivos disponibles para este módulo.")
                    
            except Exception as e:
                st.error(f"Error al cargar archivos: {e}")
    
    if st.button("Volver a Mis Cursos"):
        st.session_state.show_student_content = False
        st.rerun()

def show_student_activities():
    st.subheader("📝 Actividades del Curso")
    course = st.session_state.current_course
    
    st.write(f"Curso: **{course['name']}**")
    
    # Obtener TODOS los exámenes del curso (a través de los módulos)
    exams = get_exams(course_id=course['id'])
    
    # Mostrar exámenes
    st.markdown("### 📊 Exámenes")
    
    if exams:
        user_id = st.session_state.user['id']
        
        for exam in exams:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"**{exam['title']}**")
                    if exam.get('description'):
                        st.write(f"{exam['description'][:100]}...")
                    
                    # Obtener información del módulo
                    if exam.get('module_id'):
                        module_info = supabase.table('course_modules')\
                            .select('title, module_number')\
                            .eq('id', exam['module_id'])\
                            .execute()
                        if module_info.data:
                            module_data = module_info.data[0]
                            st.write(f"**Módulo:** {module_data['module_number']} - {module_data['title']}")
                    
                    # Información del examen
                    st.write(f"**Límite de tiempo:** {exam.get('time_limit_minutes', 0)} minutos")
                    st.write(f"**Intentos permitidos:** {exam.get('max_attempts', 1)}")
                    st.write(f"**Puntaje para aprobar:** {exam.get('passing_score', 14)}")
                
                with col2:
                    # Verificar disponibilidad
                    is_available, message = check_exam_availability(exam)
                    attempts = get_exam_attempts(exam['id'], user_id)
                    
                    if attempts:
                        latest_attempt = attempts[0]
                        status = latest_attempt.get('status', 'unknown')
                        if status == 'submitted':
                            st.write("**Estado:** Completado")
                            if latest_attempt.get('score') is not None:
                                st.write(f"**Calificación:** {latest_attempt['score']}")
                        elif status == 'in_progress':
                            st.write("**Estado:** En progreso")
                        else:
                            st.write(f"**Estado:** {status}")
                    else:
                        st.write(f"**Estado:** {message}")
                
                with col3:
                    if is_available:
                        if attempts and len(attempts) >= exam.get('max_attempts', 1):
                            st.write("✅ Límite alcanzado")
                        elif attempts and any(attempt.get('status') == 'in_progress' for attempt in attempts):
                            # BOTÓN "CONTINUAR" - CORREGIDO
                            if st.button("Continuar", key=f"continue_exam_{exam['id']}"):
                                st.session_state.taking_exam = exam
                                st.session_state.show_exam_interface = True
                                st.rerun()  # IMPORTANTE: forzar rerun
                        else:
                            # BOTÓN "COMENZAR" - CORREGIDO  
                            if st.button("Comenzar", key=f"start_exam_{exam['id']}"):
                                st.session_state.taking_exam = exam
                                st.session_state.show_exam_interface = True
                                st.rerun()  # IMPORTANTE: forzar rerun
                    else:
                        st.write("⏳ No disponible")
    else:
        st.info("No hay exámenes disponibles para este curso.")
    
    # VERIFICAR SI DEBEMOS MOSTRAR LA INTERFAZ DEL EXAMEN
    if st.session_state.get('show_exam_interface') and st.session_state.get('taking_exam'):
        show_exam_interface()

def show_submission_form():
    assignment = st.session_state.submitting_assignment
    
    st.subheader(f"📤 Entregar Tarea: {assignment['title']}")
    
    due_date = datetime.fromisoformat(assignment['due_date'].replace('Z', '+00:00'))
    if datetime.now() > due_date:
        st.error("❌ La fecha límite para esta tarea ya pasó. No se pueden enviar entregas tardías.")
        if st.button("Volver"):
            st.session_state.show_submission_form = False
            if 'submitting_assignment' in st.session_state:
                del st.session_state.submitting_assignment
            st.rerun()
        return
    
    with st.form("submission_form"):
        st.write("**Instrucciones:** Sube tu archivo de entrega")
        st.info(f"Formatos permitidos: PDF, Word, PowerPoint, Excel, TXT")
        st.warning(f"⏰ Fecha límite: {due_date.strftime('%Y-%m-%d %H:%M')}")
        
        uploaded_file = st.file_uploader(
            "Selecciona tu archivo", 
            type=['pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'txt'],
            key="submission_file"
        )
        
        if st.form_submit_button("Enviar Entrega", type="primary"):
            if uploaded_file is not None:
                # Guardar archivo de entrega
                file_id = create_assignment_submission_file(uploaded_file.getvalue(), uploaded_file.name)
                
                if file_id:
                    # Guardar entrega en assignment_submissions
                    submission_data = {
                        'assignment_id': assignment['id'],
                        'student_id': st.session_state.user['id'],
                        'file_id': file_id,
                        'status': 'submitted',
                        'submitted_at': datetime.now().isoformat()
                    }
                    
                    if datetime.now() > due_date:
                        submission_data['status'] = 'late'
                    
                    try:
                        supabase.table('assignment_submissions').insert(submission_data).execute()
                        st.success("¡Entrega enviada exitosamente!")
                        st.session_state.show_submission_form = False
                        del st.session_state.submitting_assignment
                        clear_cache()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al enviar la entrega: {e}")
                else:
                    st.error("Error al guardar el archivo")
            else:
                st.error("Por favor selecciona un archivo para entregar")
    
    if st.button("Cancelar"):
        st.session_state.show_submission_form = False
        if 'submitting_assignment' in st.session_state:
            del st.session_state.submitting_assignment
        st.rerun()

def show_exam_interface():
    if not st.session_state.get('taking_exam'):
        st.error("No hay examen seleccionado")
        return
    
    exam = st.session_state.taking_exam
    user_id = st.session_state.user['id']
    
    # Verificar si ya existe un intento en progreso
    attempts = get_exam_attempts(exam['id'], user_id)
    current_attempt = None
    
    # Buscar intento en progreso o crear uno nuevo
    if attempts:
        for attempt in attempts:
            if attempt.get('status') == 'in_progress':
                current_attempt = attempt
                st.info("📝 Tienes un intento en progreso. Continuando...")
                break
        
        # Si no hay intento en progreso, verificar si se puede crear uno nuevo
        if not current_attempt:
            completed_attempts = len([a for a in attempts if a.get('status') == 'submitted'])
            max_attempts = exam.get('max_attempts', 1)
            
            if completed_attempts >= max_attempts:
                st.error("❌ Ya has completado el máximo de intentos permitidos para este examen.")
                # Mostrar resultados del último intento
                latest_attempt = attempts[0]
                if latest_attempt.get('score') is not None:
                    show_exam_results(latest_attempt, exam)
                st.session_state.show_exam_interface = False
                if 'taking_exam' in st.session_state:
                    del st.session_state.taking_exam
                if st.button("🔙 Volver a Mis Cursos"):
                    st.rerun()
                return
            else:
                # Crear nuevo intento
                attempt_data = {
                    'exam_id': exam['id'],
                    'student_id': user_id,
                    'status': 'in_progress',
                    'started_at': datetime.now().isoformat()
                }
                try:
                    response = supabase.table('exam_attempts').insert(attempt_data).execute()
                    if response.data:
                        current_attempt = response.data[0]
                        st.success("🎯 Nuevo intento de examen iniciado")
                    else:
                        st.error("❌ Error al crear nuevo intento de examen")
                        return
                except Exception as e:
                    # Si hay error de duplicado, buscar el intento existente SIN CACHÉ
                    if "duplicate key" in str(e) or "23505" in str(e):
                        st.warning("⚠️ Recuperando intento existente...")
                        # Limpiar caché primero
                        clear_cache()
                        try:
                            # Buscar directamente sin caché
                            response = supabase.table('exam_attempts')\
                                .select('*')\
                                .eq('exam_id', exam['id'])\
                                .eq('student_id', user_id)\
                                .order('started_at', desc=True)\
                                .limit(1)\
                                .execute()
                            
                            if response.data and len(response.data) > 0:
                                current_attempt = response.data[0]
                                st.info(f"📝 Intento recuperado - Estado: {current_attempt.get('status')}")
                            else:
                                st.error("❌ No se pudo recuperar el intento existente")
                                return
                        except Exception as e2:
                            st.error(f"❌ Error al recuperar intento: {e2}")
                            return
                    else:
                        st.error(f"❌ Error al crear intento: {e}")
                        return
    else:
        # No hay intentos previos visibles, intentar crear uno nuevo
        attempt_data = {
            'exam_id': exam['id'],
            'student_id': user_id,
            'status': 'in_progress',
            'started_at': datetime.now().isoformat()
        }
        try:
            response = supabase.table('exam_attempts').insert(attempt_data).execute()
            if response.data:
                current_attempt = response.data[0]
                st.success("🎯 Intento de examen iniciado")
            else:
                st.error("❌ Error al crear intento de examen")
                return
        except Exception as e:
            # Si hay error de duplicado, buscar el intento existente SIN CACHÉ
            if "duplicate key" in str(e) or "23505" in str(e):
                st.warning("⚠️ Recuperando intento existente...")
                try:
                    # Buscar directamente sin caché
                    response = supabase.table('exam_attempts')\
                        .select('*')\
                        .eq('exam_id', exam['id'])\
                        .eq('student_id', user_id)\
                        .order('started_at', desc=True)\
                        .limit(1)\
                        .execute()
                    
                    if response.data and len(response.data) > 0:
                        current_attempt = response.data[0]
                        st.info(f"📝 Intento recuperado - Estado: {current_attempt.get('status')}")
                    else:
                        st.error("❌ No se pudo recuperar el intento existente")
                        return
                except Exception as e2:
                    st.error(f"❌ Error al recuperar intento: {e2}")
                    return
            else:
                st.error(f"❌ Error al crear intento: {e}")
                return
    
    if not current_attempt:
        st.error("❌ No se pudo iniciar o recuperar el intento de examen")
        st.session_state.show_exam_interface = False
        if 'taking_exam' in st.session_state:
            del st.session_state.taking_exam
        st.rerun()
        return
    
    st.session_state.current_exam_attempt = current_attempt
    
    # Mostrar información del examen
    st.subheader(f"📝 Examen: {exam['title']}")
    
    # Timer
    time_remaining = calculate_exam_time_remaining(current_attempt, exam)
    if time_remaining:
        minutes_remaining = int(time_remaining.total_seconds() // 60)
        seconds_remaining = int(time_remaining.total_seconds() % 60)
        
        if minutes_remaining < 5:
            st.markdown(f'<div class="timer-danger">⏰ Tiempo restante: {minutes_remaining}:{seconds_remaining:02d}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="timer-warning">⏰ Tiempo restante: {minutes_remaining}:{seconds_remaining:02d}</div>', unsafe_allow_html=True)
        
        # Verificar si el tiempo se agotó
        if time_remaining.total_seconds() <= 0:
            st.error("⏰ El tiempo se ha agotado. El examen se enviará automáticamente.")
            submit_exam_attempt(current_attempt, exam, st.session_state.get('exam_answers', {}))
            return
    else:
        st.info("⏰ Examen sin límite de tiempo")
    
    # Obtener preguntas
    questions = get_exam_questions(exam['id'])
    
    if not questions:
        st.error("No hay preguntas en este examen")
        return
    
    # Inicializar respuestas del usuario en session_state si no existen
    if 'exam_answers' not in st.session_state:
        st.session_state.exam_answers = {}
    
    # Formulario de examen - SIN st.form para permitir interactividad
    st.markdown('<div class="exam-container">', unsafe_allow_html=True)
    
    for i, question in enumerate(questions, 1):
        st.markdown(f'<div class="question-card">', unsafe_allow_html=True)
        
        # Mostrar pregunta y puntos claramente
        st.markdown(f"### Pregunta {i} ({question['points']} puntos)")
        st.markdown(f"**{question['question_text']}**")
        st.markdown("---")
        
        question_type = question['question_type']
        question_id = question['id']
        
        # Inicializar respuesta si no existe
        if question_id not in st.session_state.exam_answers:
            st.session_state.exam_answers[question_id] = ""
        
        if question_type == "multiple_choice":
            try:
                options = json.loads(question['correct_answer'])
                choices = [opt['text'] for opt in options if opt.get('text')]
                
                if choices:
                    # Usar radio buttons para opción única
                    current_value = st.session_state.exam_answers.get(question_id, "")
                    default_index = choices.index(current_value) if current_value in choices else 0
                    
                    user_answer = st.radio(
                        "Selecciona una opción:",
                        choices,
                        key=f"q_{question_id}",
                        index=default_index
                    )
                    st.session_state.exam_answers[question_id] = user_answer
                else:
                    st.error("No hay opciones válidas para esta pregunta")
                    
            except Exception as e:
                st.error(f"Error al cargar las opciones: {e}")
                
        elif question_type == "true_false":
            current_value = st.session_state.exam_answers.get(question_id, "verdadero")
            default_index = 0 if current_value.lower() != "falso" else 1
            
            user_answer = st.radio(
                "Selecciona:",
                ["Verdadero", "Falso"],
                key=f"q_{question_id}",
                index=default_index
            )
            st.session_state.exam_answers[question_id] = user_answer.lower()
            
        elif question_type == "fill_blank":
            user_answer = st.text_input(
                "Escribe tu respuesta:",
                value=st.session_state.exam_answers.get(question_id, ""),
                key=f"q_{question_id}"
            )
            st.session_state.exam_answers[question_id] = user_answer
            
        else:  # open_ended
            user_answer = st.text_area(
                "Escribe tu respuesta:",
                value=st.session_state.exam_answers.get(question_id, ""),
                key=f"q_{question_id}",
                height=100
            )
            st.session_state.exam_answers[question_id] = user_answer
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    with col1:
        if not st.session_state.get('confirm_submit'):
            if st.button("📤 Terminar Intento", type="primary", use_container_width=True):
                st.session_state.confirm_submit = True
                st.rerun()
    with col2:
        if st.button("💾 Guardar y Salir", use_container_width=True):
            save_exam_progress(current_attempt, st.session_state.exam_answers)
            st.session_state.show_exam_interface = False
            if 'exam_answers' in st.session_state:
                del st.session_state.exam_answers
            st.success("Progreso guardado. Puedes continuar más tarde.")
            st.rerun()
    
    # Mostrar confirmación de envío si es necesario
    if st.session_state.get('confirm_submit'):
        st.markdown("---")
        st.warning("**⚠️ Confirmar envío del examen**")
        st.info("Esta acción no se puede deshacer. Todas tus respuestas serán enviadas para calificación.")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("✅ Sí, enviar examen definitivamente", type="primary", use_container_width=True):
                submit_exam_attempt(current_attempt, exam, st.session_state.exam_answers)
            if st.button("❌ No, volver al examen", use_container_width=True):
                st.session_state.confirm_submit = False
                st.rerun()

def show_exam_results(attempt, exam):
    """Muestra los resultados y feedback del examen completado"""
    st.subheader("📊 Resultados del Examen")
    
    # Información del examen
    st.write(f"**Examen:** {exam['title']}")
    if attempt.get('completed_at'):
        completed_date = datetime.fromisoformat(attempt['completed_at'].replace('Z', '+00:00'))
        st.write(f"**Completado:** {completed_date.strftime('%Y-%m-%d %H:%M')}")
    
    # Calificación - TODO DE EXAM_ATTEMPTS
    if attempt.get('score') is not None:
        score = attempt['score']
        passing_score = exam.get('passing_score', 14)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Tu Calificación", f"{score:.1f}", 
                     delta=f"{score - passing_score:.1f}" if score >= passing_score else f"{score - passing_score:.1f}")
        with col2:
            st.metric("Puntaje para Aprobar", f"{passing_score}")
        with col3:
            if score >= passing_score:
                st.success("✅ APROBADO")
            else:
                st.error("❌ REPROBADO")
        
        # Barra de progreso visual
        st.progress(min(score / 20.0, 1.0))
        
        # Feedback de la IA - OBTENER DE EXAM_RESULTS
        st.markdown("---")
        st.subheader("💬 Feedback de la IA")
        
        # Buscar feedback detallado en exam_results
        exam_results_data = supabase.table('exam_results')\
            .select('*')\
            .eq('exam_id', exam['id'])\
            .eq('student_id', st.session_state.user['id'])\
            .order('completed_at', desc=True)\
            .limit(1)\
            .execute()
        
        ai_feedback_data = None
        if exam_results_data.data and exam_results_data.data[0].get('feedback'):
            try:
                # Intentar parsear el feedback estructurado de la IA
                feedback_json = exam_results_data.data[0]['feedback']
                if isinstance(feedback_json, str):
                    feedback_json = json.loads(feedback_json)
                
                # Buscar explicaciones detalladas por pregunta
                if isinstance(feedback_json, list):
                    ai_feedback_data = feedback_json
                elif isinstance(feedback_json, dict) and 'answers' in feedback_json:
                    ai_feedback_data = feedback_json['answers']
            except:
                # Si no se puede parsear, mostrar el feedback como texto
                st.info(exam_results_data.data[0]['feedback'])
        
        # Si hay feedback estructurado de la IA, mostrarlo
        if ai_feedback_data:
            st.subheader("🤖 Explicación Detallada por Pregunta")
            
            for i, feedback_item in enumerate(ai_feedback_data, 1):
                with st.expander(f"Pregunta {i}: {feedback_item.get('question_text', '')[:80]}...", expanded=False):
                    # Mostrar explicación de la IA
                    if feedback_item.get('explanation'):
                        st.markdown("**💡 Explicación de la IA:**")
                        st.info(feedback_item['explanation'])
                    
                    # Mostrar respuesta correcta según la IA
                    if feedback_item.get('correct_answer'):
                        st.markdown("**🎯 Respuesta correcta:**")
                        st.success(feedback_item['correct_answer'])
        
        # Si no hay feedback de la IA en exam_results, mostrar el de exam_attempts
        elif attempt.get('ai_feedback'):
            st.info(attempt['ai_feedback'])
        elif attempt.get('feedback'):
            st.info(attempt['feedback'])
        else:
            st.info("No hay feedback de la IA disponible.")
        
        # Detalles por pregunta - TODO DE EXAM_ATTEMPTS
        st.markdown("---")
        st.subheader("📝 Revisión de Respuestas")
        
        # Obtener respuestas del estudiante DE EXAM_ATTEMPTS
        user_answers = {}
        if attempt.get('answers_data'):
            try:
                user_answers = json.loads(attempt['answers_data'])
            except:
                pass
        
        questions = get_exam_questions(exam['id'])
        
        for i, question in enumerate(questions, 1):
            question_id = str(question['id'])
            user_answer = user_answers.get(question_id, "No respondida")
            
            with st.expander(f"Pregunta {i}: {question['question_text'][:80]}...", expanded=False):
                st.write(f"**Pregunta completa:** {question['question_text']}")
                st.write(f"**Puntos:** {question['points']}")
                
                # Mostrar respuesta del estudiante
                st.markdown("**Tu respuesta:**")
                if question['question_type'] == 'multiple_choice':
                    st.write(f"- {user_answer}")
                else:
                    st.write(user_answer)
                
                # Mostrar respuesta correcta
                st.markdown("**Respuesta correcta:**")
                if question['question_type'] == 'multiple_choice':
                    try:
                        options = json.loads(question['correct_answer'])
                        correct_options = [opt['text'] for opt in options if opt.get('is_correct')]
                        for opt in correct_options:
                            st.write(f"- ✓ {opt}")
                    except:
                        st.write(question['correct_answer'])
                elif question['question_type'] == 'true_false':
                    st.write("Verdadero" if question['correct_answer'] == 'true' else "Falso")
                else:
                    st.write(question['correct_answer'])
                
                # Indicador de correcto/incorrecto
                if question['question_type'] == 'multiple_choice':
                    try:
                        options = json.loads(question['correct_answer'])
                        correct_options = [opt['text'] for opt in options if opt.get('is_correct')]
                        if user_answer in correct_options:
                            st.success("✅ Respuesta correcta")
                        else:
                            st.error("❌ Respuesta incorrecta")
                    except:
                        pass
                elif question['question_type'] == 'true_false':
                    correct_answer = "verdadero" if question['correct_answer'] == 'true' else "falso"
                    if str(user_answer).lower() == correct_answer:
                        st.success("✅ Respuesta correcta")
                    else:
                        st.error("❌ Respuesta incorrecta")
                elif question['question_type'] == 'fill_blank':
                    if str(user_answer).lower().strip() == str(question['correct_answer']).lower().strip():
                        st.success("✅ Respuesta correcta")
                    else:
                        st.error("❌ Respuesta incorrecta")
                else:
                    st.info("⏳ Pregunta abierta - calificada por IA")
    
    else:
        st.warning("⏳ El examen está siendo calificado. Los resultados estarán disponibles pronto.")
    
    if st.button("🔙 Volver a Mis Cursos", use_container_width=True):
        st.session_state.show_exam_interface = False
        if 'taking_exam' in st.session_state:
            del st.session_state.taking_exam
        st.rerun()

def submit_exam_attempt(attempt, exam, user_answers=None):
    """Envía el intento de examen para corrección y muestra resultados"""
    try:
        # Preparar datos para n8n
        exam_data = {
            'exam_attempt_id': attempt['id'],
            'exam_id': exam['id'],
            'student_id': st.session_state.user['id'],
            'passing_score': exam.get('passing_score', 14),
            'submission': []
        }
        
        # Obtener preguntas y respuestas
        questions = get_exam_questions(exam['id'])
        for question in questions:
            submission_item = {
                'question_id': question['id'],
                'question_text': question['question_text'],
                'question_type': question['question_type'],
                'correct_answer': question['correct_answer'],
                'student_answer': user_answers.get(str(question['id']), '') if user_answers else '',
                'points': question['points']
            }
            exam_data['submission'].append(submission_item)
        
        # **CORRECIÓN INMEDIATA**
        score, feedback, passed, detailed_feedback = calculate_immediate_score(exam_data, exam)
        
        # **ACTUALIZAR ESTADO DEL INTENTO - ESTO ES LO MÁS IMPORTANTE**
        update_data = {
            'status': 'submitted',
            'submitted_at': datetime.now().isoformat(),
            'answers_data': json.dumps(user_answers) if user_answers else None,
            'score': score,
            'passed': passed
        }
        
        # Agregar campos opcionales solo si existen en la tabla
        try:
            update_data['ai_feedback'] = feedback
        except Exception:
            pass
        
        # Ejecutar la actualización en exam_attempts (FUENTE PRINCIPAL)
        supabase.table('exam_attempts').update(update_data).eq('id', attempt['id']).execute()
        
        # **GUARDAR EN EXAM_RESULTS CON TODOS LOS DATOS NECESARIOS**
        exam_result_data = {
            'exam_id': exam['id'],
            'student_id': st.session_state.user['id'],
            'score': score,
            'passed': passed,
            'completed_at': datetime.now().isoformat(),
            'feedback': json.dumps(detailed_feedback),  # Guardar feedback detallado como JSON
            'answers': json.dumps(user_answers) if user_answers else None  # ¡ESTO ES LO QUE FALTABA!
        }
        
        # Agregar campos opcionales
        try:
            exam_result_data['total_questions'] = len(questions)
            exam_result_data['correct_answers'] = calculate_correct_answers(exam_data, questions)
        except Exception:
            pass
        
        # Insertar en exam_results (SOLO UNA VEZ)
        supabase.table('exam_results').insert(exam_result_data).execute()
        
        # Disparar workflow de n8n para corrección adicional (si es necesario)
        n8n_success = trigger_n8n_workflow('exam_correction', exam_data)
        if n8n_success:
            st.success("✅ Examen enviado para corrección adicional con IA.")
        else:
            st.success("✅ Examen enviado y calificado.")
        
        # **MOSTRAR RESULTADOS INMEDIATAMENTE**
        st.session_state.show_exam_results = True
        st.session_state.last_exam_attempt = {**attempt, **update_data}  # Actualizar con nuevos datos
        st.session_state.last_exam = exam
        st.session_state.exam_detailed_feedback = detailed_feedback  # Guardar feedback detallado
        
        # Limpiar estado
        st.session_state.show_exam_interface = False
        if 'taking_exam' in st.session_state:
            del st.session_state.taking_exam
        if 'current_exam_attempt' in st.session_state:
            del st.session_state.current_exam_attempt
        if 'confirm_submit' in st.session_state:
            del st.session_state.confirm_submit
        if 'exam_answers' in st.session_state:
            del st.session_state.exam_answers
        
        clear_cache()
        st.rerun()
        
    except Exception as e:
        st.error(f"Error al enviar el examen: {e}")
        st.error(f"Detalles del error: {str(e)}")

def calculate_immediate_score(exam_data, exam):
    """Calcula el score inmediato del examen y genera feedback detallado"""
    total_points = 0
    earned_points = 0
    feedback_comments = []
    detailed_feedback = []
    
    passing_score = exam.get('passing_score', 14)
    
    for i, submission in enumerate(exam_data['submission'], 1):
        question_points = submission['points']
        total_points += question_points
        
        # Calcular si la respuesta es correcta según el tipo
        is_correct = False
        explanation = ""
        question_type = submission['question_type']
        
        if question_type == 'multiple_choice':
            try:
                correct_options = json.loads(submission['correct_answer'])
                correct_texts = [opt['text'] for opt in correct_options if opt.get('is_correct')]
                if submission['student_answer'] in correct_texts:
                    earned_points += question_points
                    is_correct = True
                    explanation = f"✅ Seleccionaste la respuesta correcta."
                else:
                    correct_answers = ", ".join(correct_texts)
                    explanation = f"❌ La respuesta correcta era: {correct_answers}"
            except Exception as e:
                explanation = f"⚠️ Error al evaluar la pregunta: {str(e)}"
                
        elif question_type == 'true_false':
            correct_answer = "verdadero" if submission['correct_answer'] == 'true' else "falso"
            if submission['student_answer'].lower() == correct_answer:
                earned_points += question_points
                is_correct = True
                explanation = f"✅ Correcto: identificaste correctamente la afirmación."
            else:
                correct_display = "Verdadero" if correct_answer == "verdadero" else "Falso"
                explanation = f"❌ La respuesta correcta era: {correct_display}"
                
        elif question_type == 'fill_blank':
            if submission['student_answer'].lower().strip() == submission['correct_answer'].lower().strip():
                earned_points += question_points
                is_correct = True
                explanation = f"✅ Completaste correctamente el espacio en blanco."
            else:
                explanation = f"❌ La respuesta correcta era: {submission['correct_answer']}"
                
        else:  # open_ended - dar puntos completos por ahora
            earned_points += question_points
            is_correct = True
            explanation = f"📝 Pregunta abierta - tu respuesta ha sido registrada para revisión adicional."
        
        # Agregar al feedback detallado
        detailed_feedback.append({
            'question_number': i,
            'question_text': submission['question_text'],
            'student_answer': submission['student_answer'],
            'correct_answer': submission['correct_answer'],
            'question_type': question_type,  # Incluir el tipo de pregunta
            'is_correct': is_correct,
            'explanation': explanation,
            'points': question_points,
            'earned_points': question_points if is_correct else 0
        })
        
        feedback_comments.append(f"Pregunta {i}: {explanation}")
    
    # Calcular porcentaje
    score_percentage = (earned_points / total_points * 20) if total_points > 0 else 0
    passed = score_percentage >= passing_score
    
    # Crear feedback consolidado
    feedback_summary = f"""
        **Resultado del Examen: {exam['title']}**

        **Puntuación Obtenida:** {score_percentage:.1f}/20
        **Puntuación para Aprobar:** {passing_score}/20
        **Estado:** {'✅ APROBADO' if passed else '❌ REPROBADO'}

        **Desglose:**
        - Puntos totales posibles: {total_points}
        - Puntos obtenidos: {earned_points}
        - Porcentaje: {score_percentage:.1f}%

        **Resumen por pregunta:**
        """ + "\n".join([f"- {comment}" for comment in feedback_comments])

    return score_percentage, feedback_summary, passed, detailed_feedback

def calculate_correct_answers(exam_data, questions):
    """Calcula el número de respuestas correctas"""
    correct_count = 0
    
    for i, submission in enumerate(exam_data['submission']):
        question = questions[i]
        
        if submission['question_type'] == 'multiple_choice':
            try:
                correct_options = json.loads(submission['correct_answer'])
                correct_texts = [opt['text'] for opt in correct_options if opt.get('is_correct')]
                if submission['student_answer'] in correct_texts:
                    correct_count += 1
            except:
                pass
                
        elif submission['question_type'] == 'true_false':
            correct_answer = "verdadero" if submission['correct_answer'] == 'true' else "falso"
            if submission['student_answer'].lower() == correct_answer:
                correct_count += 1
                
        elif submission['question_type'] == 'fill_blank':
            if submission['student_answer'].lower().strip() == submission['correct_answer'].lower().strip():
                correct_count += 1
                
        else:  # open_ended - contar como correcta por ahora
            correct_count += 1
    
    return correct_count

def save_exam_progress(attempt, user_answers):
    """Guarda el progreso del examen sin enviarlo"""
    try:
        update_data = {
            'answers_data': json.dumps(user_answers) if user_answers else None
        }
        
        supabase.table('exam_attempts').update(update_data).eq('id', attempt['id']).execute()
        st.success("Progreso guardado exitosamente")
    except Exception as e:
        st.error(f"Error al guardar el progreso: {e}")

# Función auxiliar para verificar la estructura de la base de datos
def check_database_structure():
    """Verificar qué tablas y columnas existen"""
    try:
        # Verificar tablas
        tables = ['exam_questions', 'assignment_submission_files', 'exam_attempts', 'exams']
        existing_tables = []
        
        for table in tables:
            try:
                supabase.table(table).select('id').limit(1).execute()
                existing_tables.append(table)
            except:
                pass
        
        st.sidebar.info(f"Tablas existentes: {', '.join(existing_tables)}")
        
        return existing_tables
    except Exception as e:
        st.sidebar.error(f"Error verificando estructura: {e}")
        return []


# --- PÁGINAS ORIGINALES ACTUALIZADAS ---
def show_dashboard():
    st.header("📊 Dashboard Principal")
    
    col1, col2, col3, col4 = st.columns(4)
    courses = get_courses()
    users = get_users()
    enrollments = get_enrollments()
    exam_results = get_exam_results()
    
    with col1:
        st.metric("Total Cursos", len(courses))
    with col2:
        st.metric("Total Usuarios", len(users))
    with col3:
        active_enrollments = len([e for e in enrollments if e.get('completion_status') == 'in_progress'])
        st.metric("Inscripciones Activas", active_enrollments)
    with col4:
        avg_score = sum([er.get('score', 0) for er in exam_results if er.get('score')]) / len(exam_results) if exam_results else 0
        st.metric("Promedio Calificaciones", f"{avg_score:.2f}")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        if enrollments:
            course_data = {}
            for enrollment in enrollments:
                if enrollment.get('courses'):
                    course_name = enrollment['courses']['name']
                    course_data[course_name] = course_data.get(course_name, 0) + 1
            
            if course_data:
                fig = px.pie(values=list(course_data.values()), names=list(course_data.keys()), 
                           title="Distribución de Estudiantes por Curso")
                fig.update_layout(legend_title_text='Cursos')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No hay datos de inscripciones para mostrar.")
        else:
            st.info("No hay datos de inscripciones para mostrar.")
            
    with col2:
        if enrollments:
            status_data = {}
            for enrollment in enrollments:
                status_raw = enrollment.get('completion_status', 'in_progress')
                status_display = STATUS_MAP.get(status_raw, status_raw.capitalize())
                status_data[status_display] = status_data.get(status_display, 0) + 1
            
            if status_data:
                fig = px.bar(x=list(status_data.keys()), y=list(status_data.values()), 
                           title="Estado de Completación de Cursos", 
                           labels={'x':'Estado', 'y':'Cantidad'})
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No hay datos de estado para mostrar.")
        else:
            st.info("No hay datos de inscripciones para mostrar.")
    
    st.subheader("Últimas Inscripciones")
    if enrollments:
        enrollment_data = []
        for e in sorted(enrollments, key=lambda x: x.get('enrollment_date', ''), reverse=True)[:10]:
            if e.get('users') and e.get('courses'):
                enrollment_data.append({
                    'Estudiante': f"{e['users']['first_name']} {e['users']['last_name']}",
                    'Curso': e['courses']['name'],
                    'Fecha': datetime.fromisoformat(e['enrollment_date'].replace('Z', '+00:00')).strftime('%Y-%m-%d') if e.get('enrollment_date') else 'N/A',
                    'Progreso': f"{e.get('progress_percentage', 0)}%",
                    'Estado': STATUS_MAP.get(e.get('completion_status', 'in_progress'), 'En Progreso')
                })
        if enrollment_data:
            st.dataframe(enrollment_data, use_container_width=True, hide_index=True)
        else:
            st.info("No hay inscripciones válidas para mostrar.")
    else:
        st.info("Aún no hay inscripciones.")

def manage_courses():
    if not check_admin_permissions():
        return
    st.header("📚 Gestión de Cursos")
    
    if not auth_system.has_role('admin'):
        st.error("No tienes permisos para acceder a esta sección")
        return
    
    tab1, tab2 = st.tabs(["Listar y Modificar Cursos", "Crear Nuevo Curso"])
    
    with tab1:
        st.subheader("Cursos Activos")
        courses = get_courses()
        if not courses:
            st.info("No hay cursos activos. ¡Crea uno en la pestaña 'Crear Nuevo Curso'!")
            return

        for course in courses:
            with st.container():
                st.markdown('<div class="custom-container">', unsafe_allow_html=True)
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.subheader(course['name'])
                    st.write(f"**Descripción:** {course.get('description', 'Sin descripción')}")
                    st.write(f"**Duración:** {course.get('duration_days', 0)} días | **Precio:** ${course.get('price', 0)}")
                
                with col2:
                    st.write("")
                    if st.button("Editar", key=f"edit_{course['id']}", use_container_width=True):
                        st.session_state.edit_course_id = course['id']
                    if st.button("Eliminar ⛔", key=f"del_{course['id']}", type="secondary", use_container_width=True):
                        try:
                            supabase.table('courses').update({'is_active': False}).eq('id', course['id']).execute()
                            st.success(f"Curso '{course['name']}' desactivado.")
                            clear_cache()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al eliminar: {e}")
                
                if st.session_state.get('edit_course_id') == course['id']:
                    with st.form(key=f"form_edit_{course['id']}"):
                        st.subheader(f"Editando: {course['name']}")
                        edit_name = st.text_input("Nombre", value=course['name'])
                        edit_desc = st.text_area("Descripción", value=course.get('description', ''))
                        col1_edit, col2_edit = st.columns(2)
                        with col1_edit:
                            edit_price = st.number_input("Precio ($)", value=float(course.get('price', 0)), min_value=0.0, step=10.0)
                        with col2_edit:
                            edit_duration = st.number_input("Duración (días)", value=course.get('duration_days', 30), min_value=1, step=1)
                        
                        col1_btn, col2_btn = st.columns(2)
                        with col1_btn:
                            if st.form_submit_button("Guardar Cambios", type="primary"):
                                update_data = {
                                    'name': edit_name, 'description': edit_desc,
                                    'price': edit_price, 'duration_days': edit_duration,
                                    'updated_at': datetime.now().isoformat()
                                }
                                supabase.table('courses').update(update_data).eq('id', course['id']).execute()
                                st.success("¡Curso actualizado!")
                                del st.session_state.edit_course_id
                                clear_cache()
                                st.rerun()
                        with col2_btn:
                            if st.form_submit_button("Cancelar"):
                                del st.session_state.edit_course_id
                                st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.subheader("Crear un Nuevo Curso")
        with st.form("crear_curso"):
            name = st.text_input("Nombre del Curso")
            description = st.text_area("Descripción")
            col1, col2 = st.columns(2)
            with col1:
                price = st.number_input("Precio ($)", min_value=0.0, step=10.0, value=0.0)
            with col2:
                duration = st.number_input("Duración (días)", min_value=1, step=1, value=30)
            
            if st.form_submit_button("Crear Curso", type="primary"):
                if not name:
                    st.error("El nombre del curso es obligatorio")
                else:
                    new_course = {
                        'name': name, 
                        'description': description,
                        'price': price, 
                        'duration_days': duration
                    }
                    supabase.table('courses').insert(new_course).execute()
                    st.success(f"¡Curso '{name}' creado exitosamente!")
                    clear_cache()

def manage_students():
    st.header("👥 Gestión de Estudiantes")
    
    if not check_admin_permissions():
        return
    
    tab1, tab2 = st.tabs(["Listar y Gestionar Estudiantes", "Inscripciones Masivas"])
    
    with tab1:
        st.subheader("Estudiantes Registrados")
        students = get_users('student')
        
        if students:
            # Crear DataFrame interactivo
            df_data = []
            for student in students:
                df_data.append({
                    'ID': student['id'],
                    'Nombre': student['first_name'],
                    'Apellido': student['last_name'],
                    'Email': student['email'],
                    'Fecha Registro': student['created_at'][:10] if student.get('created_at') else 'N/A',
                    'Activo': 'Sí' if student.get('is_active', True) else 'No'
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Acciones por estudiante
            st.subheader("Acciones por Estudiante")
            selected_student_email = st.selectbox(
                "Seleccionar Estudiante",
                [s['email'] for s in students],
                key="student_actions"
            )
            
            selected_student = next((s for s in students if s['email'] == selected_student_email), None)
            
            if selected_student:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    # Editar datos del estudiante
                    if st.button("✏️ Editar Datos", key="edit_student_data"):
                        st.session_state.editing_student_data = selected_student
                
                with col2:
                    # Resetear contraseña
                    if st.button("🔄 Resetear Contraseña", key="reset_student_pass"):
                        st.session_state.resetting_student_password = selected_student
                
                with col3:
                    # Ver inscripciones del estudiante
                    if st.button("📚 Ver Inscripciones", key="view_enrollments"):
                        enrollments = supabase.table('enrollments')\
                            .select('*, courses(*)')\
                            .eq('student_id', selected_student['id'])\
                            .execute().data
                        
                        if enrollments:
                            st.write("**Cursos inscritos:**")
                            for enrollment in enrollments:
                                course = enrollment.get('courses', {})
                                status = STATUS_MAP.get(enrollment.get('completion_status', 'in_progress'), 'En Progreso')
                                st.write(f"- {course.get('name', 'Curso desconocido')} ({status})")
                        else:
                            st.info("El estudiante no está inscrito en ningún curso")
                
                with col4:
                    # Desactivar estudiante
                    if st.button("❌ Desactivar", type="secondary", key="deactivate_student"):
                        supabase.table('users').update({'is_active': False}).eq('id', selected_student['id']).execute()
                        st.success("Estudiante desactivado")
                        clear_cache()
                        st.rerun()
                
                # Formulario de edición de datos del estudiante
                if st.session_state.get('editing_student_data') == selected_student:
                    with st.form("edit_student_data_form"):
                        st.subheader(f"Editando: {selected_student['first_name']} {selected_student['last_name']}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            edit_first_name = st.text_input("Nombre", value=selected_student['first_name'])
                            edit_last_name = st.text_input("Apellido", value=selected_student['last_name'])
                        with col2:
                            edit_email = st.text_input("Email", value=selected_student['email'])
                            st.info("El email no se puede modificar")
                        
                        col1_btn, col2_btn = st.columns(2)
                        with col1_btn:
                            if st.form_submit_button("💾 Guardar Cambios", type="primary"):
                                update_data = {
                                    'first_name': edit_first_name,
                                    'last_name': edit_last_name,
                                    'updated_at': datetime.now().isoformat()
                                }
                                updated_student = auth_system.update_user(selected_student['id'], update_data)
                                if updated_student:
                                    st.success("¡Datos del estudiante actualizados!")
                                    del st.session_state.editing_student_data
                                    clear_cache()
                                    st.rerun()
                                else:
                                    st.error("Error al actualizar los datos")
                        with col2_btn:
                            if st.form_submit_button("❌ Cancelar"):
                                del st.session_state.editing_student_data
                                st.rerun()
                
                # Formulario de reset de contraseña para estudiante
                if st.session_state.get('resetting_student_password') == selected_student:
                    with st.form("reset_student_password_form"):
                        st.subheader(f"Resetear Contraseña: {selected_student['first_name']} {selected_student['last_name']}")
                        
                        reset_option = st.radio(
                            "Opción de reset:",
                            ["Generar contraseña temporal", "Establecer contraseña específica"],
                            key="student_reset_option"
                        )
                        
                        if reset_option == "Establecer contraseña específica":
                            new_password = st.text_input("Nueva contraseña", type="password", key="student_new_pass")
                            confirm_password = st.text_input("Confirmar contraseña", type="password", key="student_confirm_pass")
                        else:
                            new_password = None
                            st.info("Se generará una contraseña temporal automáticamente")
                        
                        col1_btn, col2_btn = st.columns(2)
                        with col1_btn:
                            if st.form_submit_button("🔄 Resetear Contraseña", type="primary"):
                                if reset_option == "Establecer contraseña específica":
                                    if not new_password:
                                        st.error("La contraseña no puede estar vacía")
                                    elif len(new_password) < 6:
                                        st.error("La contraseña debe tener al menos 6 caracteres")
                                    elif new_password != confirm_password:
                                        st.error("Las contraseñas no coinciden")
                                    else:
                                        temp_password = auth_system.reset_user_password(selected_student['id'], new_password)
                                        if temp_password:
                                            st.success("¡Contraseña actualizada exitosamente!")
                                            del st.session_state.resetting_student_password
                                            clear_cache()
                                            st.rerun()
                                else:
                                    temp_password = auth_system.reset_user_password(selected_student['id'])
                                    if temp_password:
                                        st.success(f"¡Contraseña reseteada exitosamente!")
                                        st.info(f"**Contraseña temporal:** `{temp_password}`")
                                        st.warning("⚠️ Copia esta contraseña ahora, no se volverá a mostrar")
                                        del st.session_state.resetting_student_password
                                        clear_cache()
                                        st.rerun()
                        with col2_btn:
                            if st.form_submit_button("❌ Cancelar"):
                                del st.session_state.resetting_student_password
                                st.rerun()
                
                # Inscripción a cursos (mantener esta funcionalidad)
                st.subheader("Inscripción a Cursos")
                courses = get_courses()
                if courses:
                    if st.button("➕ Inscribir a Curso", key="enroll_course"):
                        st.session_state.enrolling_student = selected_student
                
                if st.session_state.get('enrolling_student') == selected_student:
                    with st.form("enroll_student_form"):
                        st.write(f"Inscribir a {selected_student['first_name']} {selected_student['last_name']}")
                        available_courses = get_courses()
                        course_to_enroll = st.selectbox(
                            "Seleccionar Curso",
                            available_courses,
                            format_func=lambda c: c['name']
                        )
                        
                        if st.form_submit_button("Inscribir", type="primary"):
                            enrollment_data = {
                                'student_id': selected_student['id'],
                                'course_id': course_to_enroll['id']
                            }
                            try:
                                supabase.table('enrollments').insert(enrollment_data).execute()
                                st.success(f"Estudiante inscrito en {course_to_enroll['name']}")
                                del st.session_state.enrolling_student
                                clear_cache()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error al inscribir: {e}")
                        
                        if st.form_submit_button("Cancelar"):
                            del st.session_state.enrolling_student
                            st.rerun()
        
        else:
            st.info("No hay estudiantes registrados.")
    
    with tab2:
        st.subheader("Gestión Avanzada")
        st.info("Funciones avanzadas de gestión de estudiantes")

def manage_enrollments():
    if not check_admin_permissions():
        return
    st.header("🎫 Gestión de Inscripciones")
    
    if not auth_system.has_role('admin'):
        st.error("No tienes permisos para acceder a esta sección")
        return
    
    tab1, tab2, tab3 = st.tabs(["Nueva Inscripción", "Acciones de Inscripción", "Resultados de Exámenes"])

    with tab1:
        st.subheader("Inscribir Estudiante a un Curso")
        with st.form("nueva_inscripcion"):
            students = get_users('student')
            courses = get_courses()
            
            if not students or not courses:
                st.warning("Debes crear al menos un estudiante y un curso antes de poder inscribir.")
                return

            col1, col2 = st.columns(2)
            with col1:
                selected_student = st.selectbox(
                    "Estudiante", students,
                    format_func=lambda s: f"{s['first_name']} {s['last_name']}"
                )
            with col2:
                selected_course = st.selectbox(
                    "Curso", courses,
                    format_func=lambda c: c['name']
                )
                
            if st.form_submit_button("Inscribir Estudiante", type="primary"):
                new_enrollment = {
                    'student_id': selected_student['id'],
                    'course_id': selected_course['id']
                }
                if trigger_n8n_workflow('enrollment', new_enrollment):
                    st.success("¡Inscripción procesada exitosamente!")
                    clear_cache()
                else:
                    st.error("Error en el proceso de inscripción. Revisa n8n.")

    with tab2:
        st.subheader("Acciones de Inscripción")
        enrollments = get_enrollments()
        
        if not enrollments:
            st.info("Aún no hay inscripciones para gestionar.")
            return

        enrollment_options = {}
        for e in enrollments:
            if e.get('users') and e.get('courses'):
                label = f"{e['users']['first_name']} {e['users']['last_name']} - {e['courses']['name']}"
                enrollment_options[label] = e
        
        if not enrollment_options:
            st.warning("No hay inscripciones válidas para mostrar.")
            return
            
        selected_label = st.selectbox("Selecciona una Inscripción", enrollment_options.keys())
        selected_enrollment = enrollment_options[selected_label]

        st.info(f"Gestionando a **{selected_enrollment['users']['first_name']}** en **{selected_enrollment['courses']['name']}**.")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="custom-container">', unsafe_allow_html=True)
            st.markdown("#### Generación de Certificado")
            
            status_raw = selected_enrollment.get('completion_status', 'in_progress')
            status_display = STATUS_MAP.get(status_raw, status_raw.capitalize())
            st.write(f"**Estado actual:** {status_display}")
            st.write(f"**Progreso:** {selected_enrollment.get('progress_percentage', 0)}%")
            
            if selected_enrollment.get('progress_percentage', 0) == 100.0:
                if st.button("🎓 Generar Certificado", use_container_width=True):
                    certificate_data = {
                        "enrollment_id": selected_enrollment['id'],
                        "student_name": f"{selected_enrollment['users']['first_name']} {selected_enrollment['users']['last_name']}",
                        "course_name": selected_enrollment['courses']['name']
                    }
                    if trigger_n8n_workflow('certificate_generation', certificate_data):
                        st.success("¡Solicitud de certificado enviada a n8n!")
                        clear_cache()
                    else:
                        st.error("Error al enviar la solicitud a n8n.")
            else:
                st.warning("Progreso debe ser 100% para generar certificado.")
            st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.subheader("Resultados de Exámenes")
        
        # Usar SOLO exam_attempts
        exam_attempts = get_exam_attempts()
        submitted_attempts = [attempt for attempt in exam_attempts if attempt.get('status') == 'submitted']
        
        if not submitted_attempts:
            st.info("Aún no hay resultados de exámenes.")
            return

        result_options = {}
        for attempt in submitted_attempts:
            student_name = f"{attempt['users']['first_name']} {attempt['users']['last_name']}" if attempt.get('users') else "Estudiante Desconocido"
            exam_title = attempt['exams']['title'] if attempt.get('exams') else "Examen Desconocido"
            score = attempt.get('score', 'N/A')
            label = f"{student_name} - {exam_title} (Score: {score})"
            result_options[label] = attempt
            
        selected_result_label = st.selectbox("Selecciona un Resultado", result_options.keys())
        selected_result = result_options[selected_result_label]

        st.markdown(f"### Resultado para {selected_result['users']['first_name'] if selected_result.get('users') else 'Estudiante Desconocido'}")
        st.metric("Puntaje Final", f"{selected_result.get('score', 0)}")
        
        if selected_result.get('passed'):
            st.success("¡Examen Aprobado!")
        else:
            st.error("Examen Reprobado")

def show_reports():
    st.header("📈 Reportes y Estadísticas")
    
    enrollments = get_enrollments()
    exam_results = get_exam_results()
    
    col1, col2 = st.columns(2)
    with col1:
        if enrollments:
            progress_data = [e.get('progress_percentage', 0) for e in enrollments if e.get('progress_percentage') is not None]
            if progress_data:
                fig = px.histogram(progress_data, nbins=20, title="Distribución del Progreso")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No hay datos de progreso para mostrar.")
        else:
            st.info("No hay datos de progreso para mostrar.")
            
    with col2:
        if exam_results:
            scores = [er.get('score', 0) for er in exam_results if er.get('score') is not None]
            if scores:
                fig = px.box(scores, title="Distribución de Calificaciones")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No hay datos de calificaciones para mostrar.")
        else:
            st.info("No hay datos de calificaciones para mostrar.")
    
    st.subheader("Reporte Detallado")
    if st.button("Generar Reporte PDF"):
        pdf = generate_pdf_report()
        pdf_buffer = io.BytesIO(pdf.output(dest='S'))
        
        st.download_button(
            label="Descargar Reporte PDF",
            data=pdf_buffer,
            file_name="reporte_cursos.pdf",
            mime="application/pdf",
            type="primary"
        )

def show_settings():
    st.header("⚙️ Configuración")
    
    st.markdown('<div class="custom-container">', unsafe_allow_html=True)
    st.subheader("Configuración de n8n")
    st.info(f"URL Webhook: {N8N_WEBHOOK_URL}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="custom-container">', unsafe_allow_html=True)
    st.subheader("Información del Sistema")
    st.info("Sistema de Gestión de Cursos Online v2.0")
    st.write("**Roles implementados:** Administrador, Profesor, Estudiante")
    st.write("**Base de datos:** Supabase")
    st.write("**Autenticación:** JWT")
    st.markdown('</div>', unsafe_allow_html=True)


def format_correct_answer(correct_answer, question_type):
    """Formatea la respuesta correcta para que sea legible"""
    try:
        if question_type == 'multiple_choice':
            options = json.loads(correct_answer)
            if isinstance(options, list):
                correct_options = []
                for opt in options:
                    if isinstance(opt, dict):
                        text = opt.get('text', '')
                        is_correct = opt.get('is_correct', False)
                        if is_correct and text:
                            correct_options.append(f"✓ {text}")
                return "\n".join(correct_options) if correct_options else "No hay opciones correctas definidas"
        elif question_type == 'true_false':
            return "Verdadero" if correct_answer == 'true' else "Falso"
        
        # Para otros tipos, devolver el texto directamente
        return str(correct_answer)
    except:
        return str(correct_answer)

def format_student_answer(student_answer, question_type):
    """Formatea la respuesta del estudiante para que sea legible"""
    if question_type == 'multiple_choice':
        return student_answer  # Ya es texto legible
    elif question_type == 'true_false':
        return "Verdadero" if student_answer == 'verdadero' else "Falso"
    else:
        return student_answer

def parse_json_feedback(feedback_text):
    """Intenta parsear el feedback de la IA si está en formato JSON"""
    try:
        # Limpiar el texto de posibles marcadores de código
        clean_text = feedback_text.replace('```json', '').replace('```', '').strip()
        feedback_data = json.loads(clean_text)
        return feedback_data
    except:
        return None

def parse_ai_feedback(feedback_text):
    """
    Parsea el feedback estructurado de la IA que viene de n8n
    """
    try:
        # Si el feedback ya es un diccionario, devolverlo directamente
        if isinstance(feedback_text, dict):
            return feedback_text
        
        # Intentar parsear como JSON
        if isinstance(feedback_text, str):
            # Limpiar el texto de posibles marcadores de código
            clean_text = feedback_text.replace('```json', '').replace('```', '').strip()
            
            # Intentar parsear como JSON
            try:
                feedback_data = json.loads(clean_text)
                return feedback_data
            except:
                # Si no es JSON, intentar extraer información estructurada del texto
                return extract_structured_feedback(feedback_text)
        
        return None
    except Exception as e:
        st.error(f"Error al parsear feedback de la IA: {e}")
        return None

def extract_structured_feedback(feedback_text):
    """
    Intenta extraer información estructurada del feedback de texto plano
    """
    try:
        # Buscar patrones comunes en el feedback
        lines = feedback_text.split('\n')
        structured_data = {'answers': []}
        
        current_question = None
        current_answer = {}
        
        for line in lines:
            line = line.strip()
            
            # Buscar preguntas
            if line.startswith('Pregunta:') or 'Pregunta:' in line:
                if current_question and current_answer:
                    structured_data['answers'].append(current_answer)
                    current_answer = {}
                
                current_question = line.replace('Pregunta:', '').strip()
                current_answer['question'] = current_question
            
            # Buscar explicaciones
            elif line.startswith('Explicación:') or 'Explicación:' in line:
                explanation = line.replace('Explicación:', '').strip()
                current_answer['explanation'] = explanation
            
            # Buscar respuestas correctas
            elif line.startswith('Respuesta correcta:') or 'Respuesta correcta:' in line:
                correct_answer = line.replace('Respuesta correcta:', '').strip()
                current_answer['correct_answer'] = correct_answer
            
            # Buscar respuestas del estudiante
            elif line.startswith('Tu respuesta:') or 'Tu respuesta:' in line:
                student_answer = line.replace('Tu respuesta:', '').strip()
                current_answer['student_answer'] = student_answer
            
            # Determinar si es correcta basado en emojis o texto
            elif '✅' in line or 'Correcto' in line or 'correcta' in line.lower():
                current_answer['is_correct'] = True
            elif '❌' in line or 'Incorrecto' in line or 'incorrecta' in line.lower():
                current_answer['is_correct'] = False
        
        # Agregar la última respuesta
        if current_question and current_answer:
            structured_data['answers'].append(current_answer)
        
        return structured_data if structured_data['answers'] else None
        
    except Exception as e:
        return None

def safe_supabase_query(query_func, *args, max_retries=3, **kwargs):
    """
    Ejecuta una consulta de Supabase con manejo de errores y reintentos
    """
    for attempt in range(max_retries):
        try:
            result = query_func(*args, **kwargs)
            return result
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Backoff exponencial
                import time
                time.sleep(wait_time)
                
                # Intentar reinicializar el cliente en caso de error grave
                if "connection" in str(e).lower() or "socket" in str(e).lower():
                    try:
                        global supabase
                        supabase = init_supabase()
                    except:
                        pass
            else:
                st.error(f"❌ Error de conexión después de {max_retries} intentos: {e}")
                return None
    return None

# --- APLICACIÓN PRINCIPAL ---
def main():
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    # INICIALIZAR ESTADOS PARA EXÁMENES (AGREGAR ESTO)
    if 'taking_exam' not in st.session_state:
        st.session_state.taking_exam = None
    if 'show_exam_interface' not in st.session_state:
        st.session_state.show_exam_interface = False
    if 'current_exam_attempt' not in st.session_state:
        st.session_state.current_exam_attempt = None
    if 'confirm_submit' not in st.session_state:
        st.session_state.confirm_submit = False

    if (st.session_state.get('show_exam_results') and 
        st.session_state.get('last_exam_attempt') and 
        st.session_state.get('last_exam')):
        show_exam_results_after_submission()

    if not auth_system.is_authenticated():
        show_login_page()
        return
    
    user = st.session_state.user

    if auth_system.has_role('admin') or auth_system.has_role('teacher'):
        exams_columns = check_exams_structure()
        if exams_columns:
            st.sidebar.info(f"Columnas en exams: {len(exams_columns)}")

    if auth_system.has_role('admin'):
        check_database_structure()
    
    user = st.session_state.user
    role_badge_class = f"{user['role']}-badge"
    role_display = {
        'admin': 'Administrador',
        'teacher': 'Profesor', 
        'student': 'Estudiante'
    }[user['role']]
    
    st.sidebar.markdown(f"""
    <div class="user-info">
        <h4>👋 Hola, {user['first_name']}</h4>
        <div class="role-badge {role_badge_class}">{role_display}</div>
        <p><small>{user['email']}</small></p>
    </div>
    """, unsafe_allow_html=True)
    
    if auth_system.has_role('admin'):
        menu_options = {
            "Dashboard": "📊",
            "Gestión de Cursos": "📚",
            "Estudiantes": "👥",
            "Inscripciones": "🎫",
            "Reportes": "📈",
            "Configuración": "⚙️"
        }
        pages = {
            "Dashboard": show_admin_dashboard,
            "Gestión de Cursos": manage_courses,
            "Estudiantes": manage_students,
            "Inscripciones": manage_enrollments,
            "Reportes": show_reports,
            "Configuración": show_settings
        }
    elif auth_system.has_role('teacher'):
        menu_options = {
            "Mi Panel": "👨‍🏫",
            "Reportes": "📈",
            "Configuración": "⚙️"
        }
        pages = {
            "Mi Panel": show_teacher_dashboard,
            "Reportes": show_reports,
            "Configuración": show_settings
        }
    else:
        menu_options = {
            "Mi Aprendizaje": "🎓",
            "Configuración": "⚙️"
        }
        pages = {
            "Mi Aprendizaje": show_student_dashboard,
            "Configuración": show_settings
        }
    
    menu = st.sidebar.radio(
        "Menú Principal",
        options=menu_options.keys(),
        format_func=lambda option: f"{menu_options[option]} {option}"
    )
    
    pages[menu]()
    show_logout()
    
def show_exam_results_after_submission():
    """Muestra los resultados inmediatamente después de enviar el examen"""
    attempt = st.session_state.last_exam_attempt
    exam = st.session_state.last_exam
    
    st.subheader("🎓 Resultados del Examen")
    
    # Información del examen
    st.write(f"**Examen:** {exam['title']}")
    st.write(f"**Completado:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # Calificación - TODO DE EXAM_ATTEMPTS
    if attempt.get('score') is not None:
        score = attempt['score']
        passing_score = exam.get('passing_score', 14)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Tu Calificación", f"{score:.1f}/20", 
                     delta=f"{score - passing_score:.1f}" if score >= passing_score else f"{score - passing_score:.1f}",
                     delta_color="normal" if score >= passing_score else "inverse")
        with col2:
            st.metric("Puntaje para Aprobar", f"{passing_score}/20")
        with col3:
            passed = attempt.get('passed', score >= passing_score)
            if passed:
                st.success("✅ **APROBADO**")
            else:
                st.error("❌ **REPROBADO**")
        
        # Barra de progreso visual
        progress_value = min(score / 20.0, 1.0)
        st.progress(progress_value)
        st.write(f"**{score:.1f}/20 puntos** ({progress_value*100:.1f}%)")
    
    # SECCIÓN DE FEEDBACK DETALLADO - EXPLICACIÓN DE LA IA DE EXAM_RESULTS
    st.markdown("---")
    
    # Obtener el feedback completo de la IA desde exam_results
    exam_results_data = safe_supabase_query(
        lambda: supabase.table('exam_results')
        .select('*')
        .eq('exam_id', exam['id'])
        .eq('student_id', st.session_state.user['id'])
        .order('completed_at', desc=True)
        .limit(1)
        .execute()
    )
    
    ai_feedback_data = None
    if exam_results_data and exam_results_data.data:
        latest_result = exam_results_data.data[0]
        
        # **CORRECCIÓN: OBTENER EXPLICACIÓN DIRECTAMENTE DE LA COLUMNA 'answers'**
        if latest_result.get('answers'):
            try:
                # Parsear las respuestas que contienen las explicaciones
                answers_data = latest_result['answers']
                if isinstance(answers_data, str):
                    answers_data = json.loads(answers_data)
                
                # Buscar las explicaciones en la estructura de answers
                if isinstance(answers_data, list):
                    ai_feedback_data = []
                    for answer_item in answers_data:
                        if isinstance(answer_item, dict) and 'explanation' in answer_item:
                            ai_feedback_data.append({
                                'question_text': answer_item.get('question_text', ''),
                                'explanation': answer_item.get('explanation', ''),
                                'correct_answer': answer_item.get('correct_answer', ''),
                                'is_correct': answer_item.get('is_correct')
                            })
                
                # Si no se encontró en answers, intentar con feedback
                if not ai_feedback_data and latest_result.get('feedback'):
                    feedback_data = latest_result['feedback']
                    if isinstance(feedback_data, str):
                        try:
                            feedback_data = json.loads(feedback_data)
                        except:
                            pass
                    
                    if isinstance(feedback_data, list):
                        ai_feedback_data = feedback_data
                    elif isinstance(feedback_data, dict) and 'answers' in feedback_data:
                        ai_feedback_data = feedback_data['answers']
                        
            except Exception as e:
                st.error(f"Error al procesar feedback: {e}")
    
    # Mostrar explicación detallada de la IA SOLO SI EXISTE EN EXAM_RESULTS
    if ai_feedback_data:
        st.subheader("🤖 Explicación Detallada de la IA")
        
        for i, feedback_item in enumerate(ai_feedback_data, 1):
            with st.expander(
                f"Pregunta {i}: {feedback_item.get('question_text', '')[:100]}...", 
                expanded=False
            ):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # Pregunta completa
                    if feedback_item.get('question_text'):
                        st.markdown("**📋 Pregunta:**")
                        st.info(feedback_item['question_text'])
                    
                    # **EXPLICACIÓN DE LA IA - OBTENIDA DIRECTAMENTE DE EXAM_RESULTS**
                    if feedback_item.get('explanation'):
                        st.markdown("**💡 Explicación de la IA:**")
                        st.info(feedback_item['explanation'])
                    
                    # Respuesta correcta según la IA
                    if feedback_item.get('correct_answer'):
                        st.markdown("**🎯 Respuesta correcta:**")
                        st.success(feedback_item['correct_answer'])
                
                with col2:
                    # Estado de la pregunta
                    if feedback_item.get('is_correct') is not None:
                        st.markdown("**📊 Resultado:**")
                        if feedback_item['is_correct']:
                            st.success("✅ Correcta")
                        else:
                            st.error("❌ Incorrecta")
    
    # Si no hay feedback de la IA, mostrar el feedback general de exam_attempts
    elif attempt.get('ai_feedback'):
        st.subheader("💬 Feedback General de la IA")
        st.info(attempt['ai_feedback'])
    
    # DETALLES POR PREGUNTA - TODO DE EXAM_ATTEMPTS
    st.markdown("---")
    st.subheader("📝 Revisión de Respuestas")
    
    # Obtener respuestas del estudiante DE EXAM_ATTEMPTS
    user_answers = {}
    if attempt.get('answers_data'):
        try:
            user_answers = json.loads(attempt['answers_data'])
        except:
            pass
    
    questions = get_exam_questions(exam['id'])
    
    for i, question in enumerate(questions, 1):
        question_id = str(question['id'])
        user_answer = user_answers.get(question_id, "No respondida")
        
        with st.expander(f"Pregunta {i}: {question['question_text'][:80]}...", expanded=False):
            st.write(f"**Pregunta completa:** {question['question_text']}")
            st.write(f"**Puntos:** {question['points']}")
            
            # Mostrar respuesta del estudiante
            st.markdown("**Tu respuesta:**")
            if question['question_type'] == 'multiple_choice':
                st.write(f"- {user_answer}")
            else:
                st.write(user_answer)
            
            # Mostrar respuesta correcta
            st.markdown("**Respuesta correcta:**")
            if question['question_type'] == 'multiple_choice':
                try:
                    options = json.loads(question['correct_answer'])
                    correct_options = [opt['text'] for opt in options if opt.get('is_correct')]
                    for opt in correct_options:
                        st.write(f"- ✓ {opt}")
                except:
                    st.write(question['correct_answer'])
            elif question['question_type'] == 'true_false':
                st.write("Verdadero" if question['correct_answer'] == 'true' else "Falso")
            else:
                st.write(question['correct_answer'])
            
            # Indicador de correcto/incorrecto
            if question['question_type'] == 'multiple_choice':
                try:
                    options = json.loads(question['correct_answer'])
                    correct_options = [opt['text'] for opt in options if opt.get('is_correct')]
                    if user_answer in correct_options:
                        st.success("✅ Respuesta correcta")
                    else:
                        st.error("❌ Respuesta incorrecta")
                except:
                    pass
            elif question['question_type'] == 'true_false':
                correct_answer = "verdadero" if question['correct_answer'] == 'true' else "falso"
                if str(user_answer).lower() == correct_answer:
                    st.success("✅ Respuesta correcta")
                else:
                    st.error("❌ Respuesta incorrecta")
            elif question['question_type'] == 'fill_blank':
                if str(user_answer).lower().strip() == str(question['correct_answer']).lower().strip():
                    st.success("✅ Respuesta correcta")
                else:
                    st.error("❌ Respuesta incorrecta")
            else:
                st.info("⏳ Pregunta abierta - calificada por IA")
    
    # Botón para volver
    st.markdown("---")
    if st.button("🔙 Volver a Mis Cursos", type="primary", use_container_width=True):
        st.session_state.show_exam_results = False
        if 'last_exam_attempt' in st.session_state:
            del st.session_state.last_exam_attempt
        if 'last_exam' in st.session_state:
            del st.session_state.last_exam
        if 'exam_detailed_feedback' in st.session_state:
            del st.session_state.exam_detailed_feedback
        st.rerun()

if __name__ == "__main__":
    main()

# Crear entorno virtual
# python -m venv venv

# Activar entorno virtual 
# .\venv\Scripts\activate 

# instalar los requerimientos
# pip install -r requirements.txt

# Ejecutar Streamlit
# streamlit run app.py