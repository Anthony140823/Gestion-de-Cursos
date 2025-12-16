"""
Sistema de Gestión de Cursos Online - Versión Mejorada
Aplicación principal con UI moderna y arquitectura modular
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import io
import base64
from typing import List, Dict, Any, Optional
from fpdf import FPDF
import requests
import json
from supabase import create_client, Client
import base64
from fpdf import FPDF
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
from auth import init_auth
import os
from typing import Optional, Dict, Any, List
import uuid
from utils.payment_simulator import PaymentSimulator, show_payment_form, show_payment_success, show_payment_failure

# Importar componentes personalizados
from components.ui_components import *
from components.certificate_generator import CertificateGenerator, create_certificate_for_enrollment
from utils.payment_simulator import PaymentSimulator, show_payment_form, show_payment_success, show_payment_failure

# ==================== CONFIGURACIÓN DE LA PÁGINA ====================

st.set_page_config(
    page_title="Sistema de Gestión de Cursos Online",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CSS MODERNO Y MEJORADO ====================

st.markdown("""
<style>
    /* Variables CSS para tema */
    :root {
        --primary-color: #667eea;
        --secondary-color: #764ba2;
        --success-color: #28a745;
        --danger-color: #dc3545;
        --warning-color: #ffc107;
        --info-color: #17a2b8;
        --light-bg: #f8f9fa;
        --dark-text: #2c3e50;
        --border-radius: 15px;
        --box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Ocultar elementos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Estilos generales */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Header principal */
    .main-header {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
        padding: 2rem;
        border-radius: var(--border-radius);
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: var(--box-shadow);
        animation: fadeIn 0.5s ease-in;
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: bold;
    }
    
    /* Badges de rol */
    .role-badge {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: bold;
        display: inline-block;
        margin: 0.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    }
    
    .admin-badge { 
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
        color: white;
    }
    
    .teacher-badge { 
        background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%);
        color: white;
    }
    
    .student-badge { 
        background: linear-gradient(135deg, #45b7d1 0%, #2980b9 100%);
        color: white;
    }
    
    /* Contenedores personalizados */
    .custom-container {
        background-color: white;
        border-radius: var(--border-radius);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: var(--box-shadow);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .custom-container:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }
    
    /* Tarjetas de curso */
    .course-card {
        background: white;
        border-radius: var(--border-radius);
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: var(--box-shadow);
        border-left: 5px solid var(--primary-color);
        transition: all 0.3s ease;
    }
    
    .course-card:hover {
        transform: translateX(10px);
        box-shadow: 0 6px 25px rgba(0,0,0,0.2);
    }
    
    /* Botones mejorados */
    .stButton>button {
        border-radius: 10px;
        font-weight: bold;
        transition: all 0.3s ease;
        border: none;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    
    /* Formularios */
    [data-testid="stForm"] {
        background-color: white;
        padding: 2rem;
        border-radius: var(--border-radius);
        box-shadow: var(--box-shadow);
    }
    
    /* Inputs */
    .stTextInput>div>div>input,
    .stSelectbox>div>div>select,
    .stTextArea>div>div>textarea {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        transition: border-color 0.3s ease;
    }
    
    .stTextInput>div>div>input:focus,
    .stSelectbox>div>div>select:focus,
    .stTextArea>div>div>textarea:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
        font-weight: bold;
    }
    
    /* Métricas */
    [data-testid="stMetric"] {
        background-color: white;
        padding: 1.5rem;
        border-radius: var(--border-radius);
        box-shadow: var(--box-shadow);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--primary-color) 0%, var(--secondary-color) 100%);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: white;
    }
    
    /* Animaciones */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    .animate-fade-in {
        animation: fadeIn 0.5s ease-in;
    }
    
    .animate-slide-in {
        animation: slideIn 0.5s ease-out;
    }
    
    /* Progress bars */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--primary-color) 0%, var(--secondary-color) 100%);
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background-color: var(--light-bg);
        border-radius: 10px;
        font-weight: bold;
    }
    
    /* Alertas personalizadas */
    .custom-alert {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid;
    }
    
    .alert-success {
        background-color: #d4edda;
        border-color: var(--success-color);
        color: #155724;
    }
    
    .alert-error {
        background-color: #f8d7da;
        border-color: var(--danger-color);
        color: #721c24;
    }
    
    .alert-warning {
        background-color: #fff3cd;
        border-color: var(--warning-color);
        color: #856404;
    }
    
    .alert-info {
        background-color: #d1ecf1;
        border-color: var(--info-color);
        color: #0c5460;
    }
    
    /* Loading spinner personalizado */
    .stSpinner > div {
        border-top-color: var(--primary-color) !important;
    }
    
    /* Tablas */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: var(--box-shadow);
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        border: 2px dashed var(--primary-color);
        border-radius: 10px;
        padding: 2rem;
        background-color: var(--light-bg);
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: var(--secondary-color);
        background-color: #e8eaf6;
    }
</style>
""", unsafe_allow_html=True)

# ==================== CONFIGURACIÓN Y INICIALIZACIÓN ====================

from supabase import create_client, Client

@st.cache_resource
def init_supabase():
    """Inicializa cliente de Supabase"""
    supabase_url = st.secrets["SUPABASE_URL"]
    supabase_key = st.secrets["SUPABASE_KEY"]
    return create_client(supabase_url, supabase_key)

def clear_cache():
    """Limpia el caché de Streamlit"""
    st.cache_data.clear()

# Inicializar servicios
supabase = init_supabase()
auth_system = init_auth(supabase)

# URLs de webhooks de n8n
N8N_WEBHOOK_URL = st.secrets["N8N_WEBHOOK_URL"]
N8N_ENROLLMENT_WEBHOOK = st.secrets.get("N8N_ENROLLMENT_WEBHOOK", N8N_WEBHOOK_URL)
N8N_PAYMENT_WEBHOOK = st.secrets.get("N8N_WEBHOOK_PAYMENT", N8N_WEBHOOK_URL)
N8N_VERIFICATION_WEBHOOK = st.secrets.get("N8N_WEBHOOK_VERIFICATION", N8N_WEBHOOK_URL)

# Inicializar generador de certificados
certificate_generator = CertificateGenerator()

def trigger_n8n_workflow(workflow_type: str, data: Dict[str, Any]) -> bool:
    """
    Dispara un workflow de n8n usando la URL específica según el tipo
    
    Args:
        workflow_type: Tipo de workflow (enrollment, exam_correction, certificate_generation, payment)
        data: Datos para el workflow
        
    Returns:
        bool: True si fue exitoso
    """
    payload = {"workflow_type": workflow_type, "data": data}
    
    # Seleccionar URL correcta según el tipo
    if workflow_type == "enrollment":
        webhook_url = N8N_ENROLLMENT_WEBHOOK
    elif workflow_type == "payment":
        webhook_url = N8N_PAYMENT_WEBHOOK
    elif workflow_type == "certificate_generation":
        webhook_url = N8N_WEBHOOK_URL  # Usar la principal para certificados
    else:
        webhook_url = N8N_WEBHOOK_URL  # Default para otros tipos
    
    try:
        # Para pagos, usar onReceived para evitar esperar respuesta y duplicados
        if workflow_type == "payment":
            webhook_url = f"{webhook_url}?responseMode=onReceived"
        
        response = requests.post(webhook_url, json=payload, timeout=30)
        return response.status_code == 200
        
    except Exception as e:
        st.error(f"Error en workflow n8n ({workflow_type}): {e}")
        return False

def safe_supabase_query(query_func):
    """
    Ejecuta una query de Supabase con manejo de errores
    
    Args:
        query_func: Función que ejecuta la query
        
    Returns:
        Resultado de la query o None si hay error
    """
    try:
        return query_func()
    except Exception as e:
        st.error(f"Error en base de datos: {e}")
        return None

# ==================== FUNCIONES AUXILIARES PARA ARCHIVOS ====================

def get_file_extension(filename: str) -> str:
    """Obtiene la extensión de un archivo en minúsculas"""
    return filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

def get_file_type(extension: str) -> str:
    """Clasifica el tipo de archivo para materiales de estudio"""
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

def display_materials_with_download(materials, show_delete=False):
    """Muestra materiales con botones de descarga y opcionalmente eliminación"""
    import base64
    
    if not materials:
        return None
    
    for material in materials:
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.write(f"📄 **{material.get('title', material.get('file_name', 'Sin título'))}**")
            if material.get('file_type') == 'link':
                st.write(f"🔗 Enlace externo")
            else:
                st.write(f"📎 {material.get('file_type', 'Archivo').upper()}")
        
        with col2:
            if material.get('file_type') == 'link':
                if st.button("🔗 Abrir", key=f"open_link_{material['id']}"):
                    st.markdown(f"[Abrir enlace]({material['external_link']})")
            else:
                if st.button("⬇️ Descargar", key=f"download_{material['id']}"):
                    if material.get('file_content_b64'):
                        try:
                            file_data = base64.b64decode(material['file_content_b64'])
                            st.download_button(
                                label="💾 Descargar Archivo",
                                data=file_data,
                                file_name=material.get('file_name', 'archivo'),
                                mime=material.get('mime_type', 'application/octet-stream'),
                                key=f"dl_btn_{material['id']}"
                            )
                        except:
                            st.error("❌ Error al leer el archivo")
        
        if show_delete:
            with col3:
                if st.button("🗑️", key=f"del_material_{material['id']}"):
                    return material['id']
    
    return None

# ==================== FUNCIONES DE DATOS (CACHED) ====================

@st.cache_data(ttl=60)
def get_courses(active_only: bool = True) -> List[Dict[str, Any]]:
    """Obtiene lista de cursos"""
    query = supabase.table('courses').select('*')
    if active_only:
        query = query.eq('is_active', True)
    response = query.order('created_at', desc=True).execute()
    return response.data if response.data else []

@st.cache_data(ttl=60)
def get_users(role: Optional[str] = None) -> List[Dict[str, Any]]:
    """Obtiene lista de usuarios"""
    query = supabase.table('users').select('*').eq('is_active', True)
    if role:
        query = query.eq('role', role)
    response = query.order('created_at', desc=True).execute()
    return response.data if response.data else []

@st.cache_data(ttl=60)
def get_enrollments(student_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Obtiene inscripciones"""
    query = supabase.table('enrollments').select('*, users(*), courses(*)')
    if student_id:
        query = query.eq('student_id', student_id)
    response = query.order('enrollment_date', desc=True).execute()
    return response.data if response.data else []

@st.cache_data(ttl=60)
def get_subscriptions(student_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Obtiene suscripciones/pagos"""
    query = supabase.table('subscriptions').select('*, users(*), courses(*)')
    if student_id:
        query = query.eq('student_id', student_id)
    response = query.order('created_at', desc=True).execute()
    return response.data if response.data else []

@st.cache_data(ttl=60)
def get_course_modules(course_id: str) -> List[Dict[str, Any]]:
    """Obtiene módulos de un curso"""
    response = supabase.table('course_modules')\
        .select('*')\
        .eq('course_id', course_id)\
        .order('module_number')\
        .execute()
    return response.data if response.data else []

@st.cache_data(ttl=60)
def get_exams(course_id: Optional[str] = None, module_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Obtiene exámenes"""
    query = supabase.table('exams').select('*')
    
    if module_id:
        query = query.eq('module_id', module_id)
    elif course_id:
        # Obtener módulos del curso primero
        modules = get_course_modules(course_id)
        if modules:
            module_ids = [m['id'] for m in modules]
            query = query.in_('module_id', module_ids)
        else:
            return []
    
    response = query.order('created_at', desc=True).execute()
    return response.data if response.data else []

@st.cache_data(ttl=60)
def get_certificates(student_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Obtiene certificados"""
    query = supabase.table('certificates').select('*, enrollments(*, courses(*), users(*))')
    if student_id:
        query = query.eq('enrollments.student_id', student_id)
    response = query.order('issue_date', desc=True).execute()
    return response.data if response.data else []

# ==================== FUNCIONES DE AUTENTICACIÓN ====================

def show_login_page():
    """Muestra la página de inicio de sesión"""
    
    # Header
    st.markdown("""
    <div class="main-header animate-fade-in">
        <h1>🎓 Sistema de Gestión de Cursos Online</h1>
        <p style='font-size: 1.2rem; margin-top: 1rem;'>Aprende, Crece, Destaca</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Verificar si necesita setup de contraseña
    if 'require_password_setup' in st.session_state:
        show_password_setup()
        return
    
    # Tabs para login y registro
    tab1, tab2 = st.tabs(["🔐 Iniciar Sesión", "📝 Registrarse"])
    
    with tab1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login_form"):
                st.subheader("Iniciar Sesión")
                email = st.text_input("📧 Email", placeholder="tu@email.com")
                password = st.text_input("🔒 Contraseña", type="password", placeholder="••••••••")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    login_btn = st.form_submit_button("Ingresar", type="primary", use_container_width=True)
                
                if login_btn:
                    if not email or not password:
                        st.error("❌ Por favor completa todos los campos")
                    else:
                        with st.spinner("Verificando credenciales..."):
                            user = auth_system.authenticate_user(email, password)
                            if user:
                                st.session_state.user = user
                                st.session_state.token = auth_system.create_jwt_token(user)
                                st.success(f"✅ ¡Bienvenido {user['first_name']}!")
                                st.balloons()
                                st.rerun()
                            else:
                                if not st.session_state.get('require_password_setup'):
                                    st.error("❌ Credenciales incorrectas")
    
    with tab2:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("register_form"):
                st.subheader("Registro de Estudiante")
                st.info("💡 Regístrate para acceder a nuestros cursos")
                
                reg_first_name = st.text_input("Nombre", placeholder="Juan")
                reg_last_name = st.text_input("Apellido", placeholder="Pérez")
                reg_email = st.text_input("Email", placeholder="juan@email.com")
                reg_password = st.text_input("Contraseña", type="password", placeholder="Mínimo 6 caracteres")
                reg_confirm_password = st.text_input("Confirmar Contraseña", type="password", placeholder="Repite tu contraseña")
                
                register_btn = st.form_submit_button("Crear Cuenta", type="primary", use_container_width=True)
                
                if register_btn:
                    # Validaciones
                    if not all([reg_first_name, reg_last_name, reg_email, reg_password, reg_confirm_password]):
                        st.error("❌ Por favor completa todos los campos")
                    elif reg_password != reg_confirm_password:
                        st.error("❌ Las contraseñas no coinciden")
                    elif len(reg_password) < 6:
                        st.error("❌ La contraseña debe tener al menos 6 caracteres")
                    else:
                        with st.spinner("Creando cuenta..."):
                            new_user = auth_system.create_user(
                                reg_email, reg_password, reg_first_name, reg_last_name, 'student'
                            )
                            if new_user:
                                st.success("✅ ¡Registro exitoso! Ahora puedes iniciar sesión.")
                                st.balloons()
                            else:
                                st.error("❌ Error en el registro. El email puede estar en uso.")

def show_password_setup():
    """Muestra formulario para establecer contraseña"""
    
    st.markdown("""
    <div class="main-header">
        <h1>🔐 Establecer Contraseña</h1>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("password_setup_form"):
            st.subheader("Establece tu contraseña")
            st.info("Como usuario existente, necesitas establecer una contraseña para continuar.")
            
            new_password = st.text_input("Nueva Contraseña", type="password")
            confirm_password = st.text_input("Confirmar Contraseña", type="password")
            
            if st.form_submit_button("Establecer Contraseña", type="primary", use_container_width=True):
                if not new_password or not confirm_password:
                    st.error("❌ Por favor completa ambos campos")
                elif new_password != confirm_password:
                    st.error("❌ Las contraseñas no coinciden")
                elif len(new_password) < 6:
                    st.error("❌ La contraseña debe tener al menos 6 caracteres")
                else:
                    user_id = st.session_state.require_password_setup
                    updated_user = auth_system.migrate_existing_user(user_id, new_password)
                    
                    if updated_user:
                        st.success("✅ ¡Contraseña establecida exitosamente! Ahora puedes iniciar sesión.")
                        del st.session_state.require_password_setup
                        st.rerun()
                    else:
                        st.error("❌ Error al establecer la contraseña")
        
        if st.button("← Volver al Login"):
            if 'require_password_setup' in st.session_state:
                del st.session_state.require_password_setup
            st.rerun()

def show_logout():
    """Muestra botón de cerrar sesión en sidebar"""
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ==================== CONTINUARÁ EN PARTE 2 ====================
# Este archivo será completado con las funciones de dashboard y páginas específicas



# ==================== CONTINUACIÓN DE app_improved_part1.py ====================

# ==================== DASHBOARD DE ADMINISTRADOR ====================

def show_admin_dashboard():
    """Dashboard completo del administrador"""
    
    st.markdown("""
    <div class="main-header animate-fade-in">
        <h1>👨‍💼 Panel de Administración</h1>
        <span class="role-badge admin-badge">ADMINISTRADOR</span>
    </div>
    """, unsafe_allow_html=True)
    
    user = st.session_state.user
    st.markdown(f"### Bienvenido, {user['first_name']} {user['last_name']}")
    
    # Métricas principales
    users_count = len(get_users())
    courses_count = len(get_courses())
    students_count = len(get_users('student'))
    teachers_count = len(get_users('teacher'))
    enrollments = get_enrollments()
    subscriptions = get_subscriptions()
    
    # Calcular ingresos totales
    total_revenue = sum([s.get('amount_paid', 0) for s in subscriptions if s.get('payment_status') == 'approved'])
    
    # Mostrar métricas con componentes personalizados
    stats = [
        {'title': 'Total Usuarios', 'value': str(users_count), 'icon': '👥', 'delta': f'+{students_count} estudiantes'},
        {'title': 'Cursos Activos', 'value': str(courses_count), 'icon': '📚'},
        {'title': 'Inscripciones', 'value': str(len(enrollments)), 'icon': '🎓'},
        {'title': 'Ingresos Totales', 'value': f'${total_revenue:.2f}', 'icon': '💰', 'delta': f'{len(subscriptions)} pagos'}
    ]
    
    render_stat_card_row(stats)
    
    # Tabs principales
    tabs = st.tabs([
        "👥 Usuarios",
        "📚 Cursos",
        "👨‍🏫 Profesores",
        "💳 Pagos",
        "📊 Reportes"
    ])
    
    with tabs[0]:  # Gestión de Usuarios
        show_admin_users_management()
    
    with tabs[1]:  # Gestión de Cursos
        show_admin_courses_management()
    
    with tabs[2]:  # Asignación de Profesores
        show_admin_teacher_assignments()
    
    with tabs[3]:  # Dashboard de Pagos
        show_admin_payments_dashboard()
    
    with tabs[4]:  # Reportes
        show_admin_reports()

def show_admin_users_management():
    """Gestión de usuarios para admin"""
    
    st.subheader("Gestión de Usuarios")
    
    # Crear nuevo usuario
    with st.expander("➕ Crear Nuevo Usuario", expanded=False):
        with st.form("create_user_admin"):
            col1, col2 = st.columns(2)
            
            with col1:
                first_name = st.text_input("Nombre")
                last_name = st.text_input("Apellido")
                email = st.text_input("Email")
            
            with col2:
                password = st.text_input("Contraseña", type="password")
                role = st.selectbox("Rol", ["student", "teacher", "admin"])
                st.info("💡 El usuario recibirá estas credenciales por email")
            
            if st.form_submit_button("Crear Usuario", type="primary", use_container_width=True):
                if not all([first_name, last_name, email, password]):
                    st.error("❌ Completa todos los campos")
                elif len(password) < 6:
                    st.error("❌ La contraseña debe tener al menos 6 caracteres")
                else:
                    new_user = auth_system.create_user(email, password, first_name, last_name, role)
                    if new_user:
                        st.success(f"✅ Usuario {role} creado exitosamente")
                        clear_cache()
                        st.rerun()
                    else:
                        st.error("❌ Error al crear usuario. El email puede estar en uso.")
    
    # Lista de usuarios
    st.markdown("### Todos los Usuarios")
    
    users = get_users()
    
    if users:
        # Filtros
        col1, col2, col3 = st.columns(3)
        with col1:
            role_filter = st.selectbox("Filtrar por Rol", ["Todos", "admin", "teacher", "student"])
        with col2:
            search_term = st.text_input("🔍 Buscar por nombre o email")
        
        # Aplicar filtros
        filtered_users = users
        if role_filter != "Todos":
            filtered_users = [u for u in filtered_users if u['role'] == role_filter]
        if search_term:
            filtered_users = [u for u in filtered_users if 
                            search_term.lower() in u['first_name'].lower() or
                            search_term.lower() in u['last_name'].lower() or
                            search_term.lower() in u['email'].lower()]
        
        # Mostrar usuarios en tarjetas
        for user in filtered_users:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    st.markdown(f"**{user['first_name']} {user['last_name']}**")
                    st.caption(user['email'])
                
                with col2:
                    render_status_badge(user['role'])
                
                with col3:
                    st.caption(f"Creado: {user['created_at'][:10]}")
                
                with col4:
                    if st.button("🔧", key=f"edit_user_{user['id']}", help="Editar usuario"):
                        st.session_state.editing_user = user
                
                st.markdown("---")
    else:
        render_empty_state("No hay usuarios registrados", "👥", "Crea el primer usuario arriba")

def show_admin_courses_management():
    """Gestión de cursos para admin"""
    
    st.subheader("Gestión de Cursos")
    
    # Crear nuevo curso
    with st.expander("➕ Crear Nuevo Curso", expanded=False):
        with st.form("create_course_admin"):
            name = st.text_input("Nombre del Curso")
            description = st.text_area("Descripción")
            
            col1, col2 = st.columns(2)
            with col1:
                price = st.number_input("Precio ($)", min_value=0.0, step=0.01, value=0.0)
            with col2:
                duration_days = st.number_input("Duración (días)", min_value=1, value=30)
            
            if st.form_submit_button("Crear Curso", type="primary", use_container_width=True):
                if not name:
                    st.error("❌ El nombre del curso es requerido")
                else:
                    new_course = {
                        'name': name,
                        'description': description,
                        'price': price,
                        'duration_days': duration_days,
                        'is_active': True
                    }
                    
                    result = safe_supabase_query(
                        lambda: supabase.table('courses').insert(new_course).execute()
                    )
                    
                    if result and result.data:
                        st.success("✅ Curso creado exitosamente")
                        clear_cache()
                        st.rerun()
    
    # Lista de cursos
    st.markdown("### Cursos Existentes")
    
    if 'editing_course' in st.session_state:
        show_edit_course_form()
    else:
        courses = get_courses(active_only=False)
        
        if courses:
            for course in courses:
                with st.expander(f"📚 {course['name']}", expanded=False):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**Descripción:** {course.get('description', 'Sin descripción')}")
                        st.write(f"**Precio:** ${course.get('price', 0):.2f}")
                        st.write(f"**Duración:** {course.get('duration_days', 0)} días")
                        st.write(f"**Estado:** {'✅ Activo' if course.get('is_active') else '❌ Inactivo'}")
                        
                        # Estadísticas del curso
                        course_enrollments = [e for e in get_enrollments() if e.get('course_id') == course['id']]
                        st.write(f"**Inscritos:** {len(course_enrollments)} estudiantes")
                    
                    with col2:
                        if st.button("✏️ Editar", key=f"edit_course_{course['id']}", use_container_width=True):
                            st.session_state.editing_course = course
                            st.rerun()
                        
                        if course.get('is_active'):
                            if st.button("🚫 Desactivar", key=f"deactivate_{course['id']}", use_container_width=True):
                                safe_supabase_query(
                                    lambda: supabase.table('courses').update({'is_active': False}).eq('id', course['id']).execute()
                                )
                                st.success("Curso desactivado")
                                clear_cache()
                                st.rerun()
                        else:
                            if st.button("✅ Activar", key=f"activate_{course['id']}", use_container_width=True):
                                safe_supabase_query(
                                    lambda: supabase.table('courses').update({'is_active': True}).eq('id', course['id']).execute()
                                )
                                st.success("Curso activado")
                                clear_cache()
                                st.rerun()
        else:
            render_empty_state("No hay cursos creados", "📚", "Crea el primer curso arriba")

def show_edit_course_form():
    """Formulario para editar curso"""
    course = st.session_state.editing_course
    
    st.markdown(f"### ✏️ Editando: {course['name']}")
    
    with st.form("edit_course_form"):
        name = st.text_input("Nombre del Curso", value=course['name'])
        description = st.text_area("Descripción", value=course.get('description', ''))
        
        col1, col2 = st.columns(2)
        with col1:
            price = st.number_input("Precio ($)", min_value=0.0, step=0.01, value=float(course.get('price', 0)))
        with col2:
            duration_days = st.number_input("Duración (días)", min_value=1, value=int(course.get('duration_days', 30)))
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.form_submit_button("💾 Guardar Cambios", type="primary", use_container_width=True):
                updated_course = {
                    'name': name,
                    'description': description,
                    'price': price,
                    'duration_days': duration_days
                }
                
                result = safe_supabase_query(
                    lambda: supabase.table('courses').update(updated_course).eq('id', course['id']).execute()
                )
                
                if result:
                    st.success("✅ Curso actualizado exitosamente")
                    del st.session_state.editing_course
                    clear_cache()
                    st.rerun()
        
        with col_btn2:
            if st.form_submit_button("❌ Cancelar", use_container_width=True):
                del st.session_state.editing_course
                st.rerun()

def show_admin_teacher_assignments():
    """Asignación de profesores a cursos"""
    
    st.subheader("Asignar Profesores a Cursos")
    
    teachers = get_users('teacher')
    courses = get_courses()
    
    if teachers and courses:
        with st.form("assign_teacher"):
            col1, col2 = st.columns(2)
            
            with col1:
                selected_teacher = st.selectbox(
                    "Profesor",
                    teachers,
                    format_func=lambda t: f"{t['first_name']} {t['last_name']} ({t['email']})"
                )
            
            with col2:
                selected_course = st.selectbox(
                    "Curso",
                    courses,
                    format_func=lambda c: c['name']
                )
            
            if st.form_submit_button("Asignar Profesor", type="primary", use_container_width=True):
                # Verificar si ya existe
                existing = safe_supabase_query(
                    lambda: supabase.table('teacher_assignments')
                    .select('*')
                    .eq('teacher_id', selected_teacher['id'])
                    .eq('course_id', selected_course['id'])
                    .execute()
                )
                
                if existing and existing.data:
                    st.warning("⚠️ Este profesor ya está asignado a este curso")
                else:
                    assignment = {
                        'teacher_id': selected_teacher['id'],
                        'course_id': selected_course['id']
                    }
                    
                    result = safe_supabase_query(
                        lambda: supabase.table('teacher_assignments').insert(assignment).execute()
                    )
                    
                    if result:
                        st.success("✅ Profesor asignado exitosamente")
                        clear_cache()
                        st.rerun()
        
        # Mostrar asignaciones existentes
        st.markdown("### Asignaciones Actuales")
        
        assignments_response = safe_supabase_query(
            lambda: supabase.table('teacher_assignments').select('*, users(*), courses(*)').execute()
        )
        
        if assignments_response and assignments_response.data:
            for assignment in assignments_response.data:
                if assignment.get('users') and assignment.get('courses'):
                    col1, col2, col3 = st.columns([3, 3, 1])
                    
                    with col1:
                        st.write(f"👨‍🏫 **{assignment['users']['first_name']} {assignment['users']['last_name']}**")
                    
                    with col2:
                        st.write(f"📚 {assignment['courses']['name']}")
                    
                    with col3:
                        if st.button("❌", key=f"remove_{assignment['id']}", help="Eliminar asignación"):
                            safe_supabase_query(
                                lambda: supabase.table('teacher_assignments').delete().eq('id', assignment['id']).execute()
                            )
                            st.success("Asignación eliminada")
                            clear_cache()
                            st.rerun()
        else:
            st.info("No hay asignaciones todavía")
    else:
        if not teachers:
            st.warning("⚠️ No hay profesores registrados. Crea usuarios con rol 'teacher' primero.")
        if not courses:
            st.warning("⚠️ No hay cursos creados. Crea cursos primero.")

def show_admin_payments_dashboard():
    """Dashboard de pagos y transacciones"""
    
    st.subheader("💳 Dashboard de Pagos")
    
    subscriptions = get_subscriptions()
    
    if subscriptions:
        # Métricas de pagos
        approved_payments = [s for s in subscriptions if s.get('payment_status') == 'approved']
        pending_payments = [s for s in subscriptions if s.get('payment_status') == 'pending']
        
        total_revenue = sum([s.get('amount_paid', 0) for s in approved_payments])
        avg_payment = total_revenue / len(approved_payments) if approved_payments else 0
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            render_metric_card("Total Ingresos", f"${total_revenue:.2f}", icon="💰")
        with col2:
            render_metric_card("Pagos Aprobados", str(len(approved_payments)), icon="✅")
        with col3:
            render_metric_card("Pagos Pendientes", str(len(pending_payments)), icon="⏳")
        with col4:
            render_metric_card("Pago Promedio", f"${avg_payment:.2f}", icon="📊")
        
        # Gráfico de ingresos por curso
        st.markdown("### Ingresos por Curso")
        
        course_revenue = {}
        for sub in approved_payments:
            if sub.get('courses'):
                course_name = sub['courses']['name']
                course_revenue[course_name] = course_revenue.get(course_name, 0) + sub.get('amount_paid', 0)
        
        if course_revenue:
            fig = px.bar(
                x=list(course_revenue.keys()),
                y=list(course_revenue.values()),
                labels={'x': 'Curso', 'y': 'Ingresos ($)'},
                title="Ingresos por Curso"
            )
            fig.update_traces(marker_color='#667eea')
            st.plotly_chart(fig, use_container_width=True)
        
        # Tabla de transacciones
        st.markdown("### Historial de Transacciones")
        
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            status_filter = st.selectbox("Estado", ["Todos", "approved", "pending", "rejected"])
        
        filtered_subs = subscriptions
        if status_filter != "Todos":
            filtered_subs = [s for s in filtered_subs if s.get('payment_status') == status_filter]
        
        # Mostrar transacciones
        for sub in filtered_subs[:20]:  # Mostrar últimas 20
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                
                with col1:
                    if sub.get('users'):
                        st.write(f"**{sub['users']['first_name']} {sub['users']['last_name']}**")
                
                with col2:
                    if sub.get('courses'):
                        st.write(f"📚 {sub['courses']['name']}")
                
                with col3:
                    st.write(f"💰 ${sub.get('amount_paid', 0):.2f}")
                    render_status_badge(sub.get('payment_status', 'pending'))
                
                with col4:
                    st.caption(sub.get('created_at', '')[:10])
                
                st.markdown("---")
    else:
        render_empty_state("No hay transacciones registradas", "💳", "Los pagos aparecerán aquí")

def show_admin_reports():
    """Reportes y estadísticas para admin"""
    
    st.subheader("📊 Reportes y Estadísticas")
    
    # Obtener datos
    users = get_users()
    courses = get_courses()
    enrollments = get_enrollments()
    subscriptions = get_subscriptions()
    
    # Gráfico de usuarios por rol
    st.markdown("### Distribución de Usuarios")
    
    role_counts = {}
    for user in users:
        role = user.get('role', 'unknown')
        role_counts[role] = role_counts.get(role, 0) + 1
    
    fig = px.pie(
        values=list(role_counts.values()),
        names=list(role_counts.keys()),
        title="Usuarios por Rol"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Gráfico de inscripciones en el tiempo
    st.markdown("### Inscripciones en el Tiempo")
    
    if enrollments:
        enrollment_dates = [e.get('enrollment_date', '')[:10] for e in enrollments]
        date_counts = {}
        for date in enrollment_dates:
            date_counts[date] = date_counts.get(date, 0) + 1
        
        fig = px.line(
            x=list(date_counts.keys()),
            y=list(date_counts.values()),
            labels={'x': 'Fecha', 'y': 'Inscripciones'},
            title="Inscripciones Diarias"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Botón para exportar reporte
    if st.button("📥 Exportar Reporte Completo (PDF)", use_container_width=True):
        with st.spinner("Generando reporte..."):
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()

            # Título
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, 'Reporte de Gestion de Cursos', 0, 1, 'C')
            pdf.ln(4)

            # Fecha de generación
            pdf.set_font("Arial", '', 11)
            generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
            pdf.cell(0, 8, f"Generado: {generated_at}", 0, 1)
            pdf.ln(3)

            # Resumen general
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 8, "Resumen General", 0, 1)
            pdf.set_font("Arial", '', 11)
            pdf.cell(0, 6, f"Total usuarios: {len(users)}", 0, 1)
            pdf.cell(0, 6, f"Cursos activos: {len(courses)}", 0, 1)
            pdf.cell(0, 6, f"Inscripciones totales: {len(enrollments)}", 0, 1)

            total_revenue = sum([
                s.get('amount_paid', 0) for s in subscriptions
                if s.get('payment_status') == 'approved'
            ])
            pdf.cell(0, 6, f"Ingresos totales: ${total_revenue:.2f}", 0, 1)
            pdf.ln(4)

            # Usuarios por rol
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 8, "Usuarios por rol", 0, 1)
            pdf.set_font("Arial", '', 11)
            for role, count in role_counts.items():
                pdf.cell(0, 6, f"- {role}: {count}", 0, 1)
            pdf.ln(4)

            # Cursos e inscripciones
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 8, "Cursos e inscripciones", 0, 1)
            pdf.set_font("Arial", '', 11)
            for course in courses:
                course_enrolls = [
                    e for e in enrollments if e.get('course_id') == course['id']
                ]
                pdf.cell(
                    0,
                    6,
                    f"- {course['name']} | Inscritos: {len(course_enrolls)} | Precio: ${course.get('price', 0):.2f}",
                    0,
                    1,
                )

            pdf_bytes = pdf.output(dest='S').encode('latin-1')

            st.success("✅ Reporte generado. Puedes descargarlo abajo.")
            st.download_button(
                "💾 Descargar PDF de Reporte",
                data=pdf_bytes,
                file_name=f"reporte_admin_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

# ==================== CONTINUARÁ EN PARTE 3 ====================



# ==================== DASHBOARD DE PROFESOR ====================

def show_teacher_dashboard():
    """Dashboard completo del profesor"""
    
    st.markdown("""
    <div class="main-header animate-fade-in">
        <h1>👨‍🏫 Panel del Profesor</h1>
        <span class="role-badge teacher-badge">PROFESOR</span>
    </div>
    """, unsafe_allow_html=True)
    
    user = st.session_state.user
    st.markdown(f"### Bienvenido, Profesor {user['first_name']} {user['last_name']}")
    
    # Obtener cursos asignados
    assignments_response = safe_supabase_query(
        lambda: supabase.table('teacher_assignments')
        .select('*, courses(*)')
        .eq('teacher_id', user['id'])
        .execute()
    )
    
    teacher_assignments = assignments_response.data if assignments_response and assignments_response.data else []
    
    if not teacher_assignments:
        render_empty_state(
            "No tienes cursos asignados",
            "📚",
            "Contacta al administrador para que te asigne cursos"
        )
        return
    
    # Métricas del profesor
    total_students = 0
    total_modules = 0
    total_exams = 0
    
    for assignment in teacher_assignments:
        course_id = assignment['course_id']
        enrollments = [e for e in get_enrollments() if e.get('course_id') == course_id]
        total_students += len(enrollments)
        total_modules += len(get_course_modules(course_id))
        total_exams += len(get_exams(course_id=course_id))
    
    stats = [
        {'title': 'Cursos Asignados', 'value': str(len(teacher_assignments)), 'icon': '📚'},
        {'title': 'Total Estudiantes', 'value': str(total_students), 'icon': '👥'},
        {'title': 'Módulos Creados', 'value': str(total_modules), 'icon': '📁'},
        {'title': 'Exámenes Activos', 'value': str(total_exams), 'icon': '📝'}
    ]
    
    render_stat_card_row(stats)
    
    # Tabs con navegación persistente
    current_tab = st.session_state.get('current_tab', 0)
    tab_names = [
        "📚 Mis Cursos",
        "📁 Gestión de Módulos", 
        "📝 Exámenes",
        "📤 Tareas",
        "👥 Estudiantes"
    ]
    
    tabs = st.tabs(tab_names)
    
    # Verificar si venimos de un botón que quiere cambiar de tab
    if st.session_state.get('selected_course') and st.session_state.get('current_tab'):
        target_tab = st.session_state.current_tab
        tab_index = tab_names.index(target_tab) if target_tab in tab_names else 0
        # Preseleccionar el curso correspondiente si viene de botón
        if target_tab == "📁 Gestión de Módulos":
            st.session_state.preselected_course = st.session_state.selected_course
        elif target_tab == "📝 Exámenes":
            st.session_state.preselected_course = st.session_state.selected_course
        # Limpiar estado
        st.session_state.pop('selected_course', None)
        st.session_state.pop('current_tab', None)
    
    with tabs[0]:  # Mis Cursos
        show_teacher_courses(teacher_assignments)
    
    with tabs[1]:  # Gestión de Módulos
        show_teacher_modules(teacher_assignments)
    
    with tabs[2]:  # Exámenes
        show_teacher_exams(teacher_assignments)
    
    with tabs[3]:  # Tareas
        show_teacher_assignments_tab(teacher_assignments)
    
    with tabs[4]:  # Estudiantes
        show_teacher_students(teacher_assignments)

def show_teacher_courses(teacher_assignments):
    """Muestra cursos del profesor"""
    
    st.subheader("Mis Cursos Asignados")
    
    for assignment in teacher_assignments:
        course = assignment['courses']
        
        # Obtener estadísticas del curso
        enrollments = [e for e in get_enrollments() if e.get('course_id') == course['id']]
        modules = get_course_modules(course['id'])
        
        with st.expander(f"📚 {course['name']}", expanded=True):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Descripción:** {course.get('description', 'Sin descripción')}")
                st.write(f"**Duración:** {course.get('duration_days', 0)} días")
                st.write(f"**Precio:** ${course.get('price', 0):.2f}")
                
                # Estadísticas
                st.markdown("#### Estadísticas")
                col_stat1, col_stat2, col_stat3 = st.columns(3)
                
                with col_stat1:
                    st.metric("Estudiantes", len(enrollments))
                with col_stat2:
                    st.metric("Módulos", len(modules))
                with col_stat3:
                    completed = len([e for e in enrollments if e.get('completion_status') == 'completed'])
                    st.metric("Completados", completed)
            
            with col2:
                if st.button("📁 Gestionar Módulos", key=f"manage_modules_{course['id']}", use_container_width=True):
                    st.session_state.selected_course = course
                    st.session_state.current_tab = "📁 Gestión de Módulos"
                    st.rerun()
                
                if st.button("📝 Crear Examen", key=f"create_exam_{course['id']}", use_container_width=True):
                    st.session_state.selected_course = course
                    st.session_state.current_tab = "📝 Exámenes"
                    st.rerun()

def show_teacher_modules(teacher_assignments):
    """Gestión de módulos del curso"""
    
    st.subheader("Gestión de Módulos")
    
    # Seleccionar curso
    courses = [a['courses'] for a in teacher_assignments]
    
    # Preseleccionar curso si viene de botón
    if st.session_state.get('preselected_course'):
        preselected = st.session_state.preselected_course
        selected_course = st.selectbox(
            "Selecciona un curso",
            courses,
            format_func=lambda c: c['name'],
            index=courses.index(preselected) if preselected in courses else 0
        )
        st.session_state.pop('preselected_course', None)  # Limpiar después de usar
    else:
        selected_course = st.selectbox(
            "Selecciona un curso",
            courses,
            format_func=lambda c: c['name']
        )
    
    if selected_course:
        modules = get_course_modules(selected_course['id'])
        
        # Crear nuevo módulo
        with st.expander("➕ Crear Nuevo Módulo", expanded=False):
            with st.form("create_module"):
                module_number = st.number_input("Número de Módulo", min_value=1, value=len(modules) + 1)
                title = st.text_input("Título del Módulo")
                content_url = st.text_input("URL del Contenido (opcional)")
                external_link = st.text_input("Enlace Externo (opcional)")
                study_material = st.text_area("Material de Estudio")
                release_day = st.number_input("Día de Liberación", min_value=1, value=1)
                
                if st.form_submit_button("Crear Módulo", type="primary"):
                    if not title:
                        st.error("❌ El título es requerido")
                    else:
                        new_module = {
                            'course_id': selected_course['id'],
                            'module_number': module_number,
                            'title': title,
                            'content_url': content_url if content_url else None,
                            'external_link': external_link if external_link else None,
                            'study_material': study_material,
                            'release_day': release_day
                        }
                        
                        result = safe_supabase_query(
                            lambda: supabase.table('course_modules').insert(new_module).execute()
                        )
                        
                        if result:
                            st.success("✅ Módulo creado exitosamente")
                            clear_cache()
                            st.rerun()
        
        # Mostrar módulos existentes
        st.markdown("### Módulos del Curso")
        
        if modules:
            for module in modules:
                with st.expander(f"📁 Módulo {module['module_number']}: {module['title']}", expanded=False):
                    st.write(f"**Contenido:** {module.get('study_material', 'Sin contenido')}")
                    if module.get('content_url'):
                        st.write(f"**URL:** {module['content_url']}")
                    if module.get('external_link'):
                        st.write(f"**Enlace Externo:** {module['external_link']}")
                    st.write(f"**Día de Liberación:** {module.get('release_day', 1)}")
                    
                    # Materiales de estudio
                    materials_response = safe_supabase_query(
                        lambda: supabase.table('study_materials')
                        .select('*')
                        .eq('module_id', module['id'])
                        .order('created_at', desc=True)
                        .execute()
                    )
                    
                    materials = materials_response.data if materials_response and materials_response.data else []
                    
                    if materials:
                        st.markdown("**Materiales:**")
                        deleted_material = display_materials_with_download(materials, show_delete=True)
                        if deleted_material:
                            safe_supabase_query(
                                lambda: supabase.table('study_materials').delete().eq('id', deleted_material).execute()
                            )
                            st.success("Material eliminado")
                            clear_cache()
                            st.rerun()
                    
                    # Botones de acción
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📤 Subir Material", key=f"upload_material_{module['id']}"):
                            st.session_state.uploading_to_module = module['id']
                            st.rerun()
                    
                    with col2:
                        if st.button("🗑️ Eliminar Módulo", key=f"delete_module_{module['id']}"):
                            safe_supabase_query(
                                lambda: supabase.table('course_modules').delete().eq('id', module['id']).execute()
                            )
                            st.success("Módulo eliminado")
                            clear_cache()
                            st.rerun()
                    
                    # Formulario de subida de material para este módulo
                    if st.session_state.get('uploading_to_module') == module['id']:
                        st.markdown("---")
                        st.markdown("#### 📤 Subir Material a este Módulo")
                        with st.form(f"upload_material_form_{module['id']}") as form:
                            material_title = st.text_input("Título del material")
                            uploaded_files = st.file_uploader(
                                "Selecciona archivos",
                                type=[
                                    'jpg', 'jpeg', 'png', 'gif',
                                    'pdf', 'doc', 'docx',
                                    'xls', 'xlsx',
                                    'ppt', 'pptx',
                                    'txt',
                                ],
                                accept_multiple_files=True,
                            )
                            external_link = st.text_input("Enlace externo (opcional)")

                            submitted = st.form_submit_button("Guardar Materiales", type="primary")
                            if submitted:
                                if not uploaded_files and not external_link:
                                    st.error("Debes subir al menos un archivo o proporcionar un enlace")
                                else:
                                    if uploaded_files:
                                        for up_file in uploaded_files:
                                            title = material_title or up_file.name
                                            upload_file_base64(up_file, module['id'], title)

                                    if external_link:
                                        link_data = {
                                            'module_id': module['id'],
                                            'title': material_title or external_link,
                                            'file_type': 'link',
                                            'external_link': external_link,
                                            'uploaded_by': st.session_state.user['id'] if 'user' in st.session_state else None,
                                        }
                                        safe_supabase_query(
                                            lambda: supabase.table('study_materials').insert(link_data).execute()
                                        )

                                    st.success("Material(es) guardado(s) correctamente")
                                    st.session_state.uploading_to_module = None
                                    clear_cache()
                                    st.rerun()
        else:
            render_empty_state("No hay módulos creados", "📁", "Crea el primer módulo arriba")

def show_teacher_exams(teacher_assignments):
    """Gestión de exámenes"""
    
    # Verificar si estamos editando preguntas o viendo resultados
    if st.session_state.get('editing_exam'):
        show_exam_question_editor(st.session_state.editing_exam)
        return
    
    if st.session_state.get('viewing_exam_results'):
        show_exam_results(st.session_state.viewing_exam_results)
        return
    
    st.subheader("Gestión de Exámenes")
    
    # Seleccionar curso
    courses = [a['courses'] for a in teacher_assignments]
    
    # Preseleccionar curso si viene de botón
    if st.session_state.get('preselected_course'):
        preselected = st.session_state.preselected_course
        selected_course = st.selectbox(
            "Selecciona un curso",
            courses,
            format_func=lambda c: c['name'],
            key="exam_course_select",
            index=courses.index(preselected) if preselected in courses else 0
        )
        st.session_state.pop('preselected_course', None)  # Limpiar después de usar
    else:
        selected_course = st.selectbox(
            "Selecciona un curso",
            courses,
            format_func=lambda c: c['name'],
            key="exam_course_select"
        )
    
    if selected_course:
        modules = get_course_modules(selected_course['id'])
        
        if not modules:
            st.warning("⚠️ Debes crear módulos primero antes de crear exámenes")
            return
        
        # Crear nuevo examen
        with st.expander("➕ Crear Nuevo Examen", expanded=False):
            with st.form("create_exam"):
                selected_module = st.selectbox(
                    "Módulo",
                    modules,
                    format_func=lambda m: f"Módulo {m['module_number']}: {m['title']}"
                )
                
                title = st.text_input("Título del Examen")
                description = st.text_area("Descripción")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    passing_score = st.number_input("Nota Mínima (sobre 20)", min_value=0.0, max_value=20.0, value=14.0)
                with col2:
                    time_limit = st.number_input("Tiempo Límite (minutos)", min_value=1, value=60)
                with col3:
                    max_attempts = st.number_input("Intentos Máximos", min_value=1, value=1)
                
                st.markdown("#### Preguntas del Examen")
                st.info("💡 Las preguntas se crearán después de crear el examen")
                
                if st.form_submit_button("Crear Examen", type="primary"):
                    if not title:
                        st.error("❌ El título es requerido")
                    else:
                        new_exam = {
                            'module_id': selected_module['id'],
                            'title': title,
                            'description': description,
                            'questions': [],  # Array vacío para cumplir constraint NOT NULL
                            'passing_score': passing_score,
                            'time_limit_minutes': time_limit,
                            'max_attempts': max_attempts,
                            'created_by': st.session_state.user['id']
                        }
                        
                        result = safe_supabase_query(
                            lambda: supabase.table('exams').insert(new_exam).execute()
                        )
                        
                        if result and result.data:
                            st.success("✅ Examen creado exitosamente")
                            st.session_state.editing_exam = result.data[0]
                            clear_cache()
                            st.rerun()
        
        # Mostrar exámenes existentes
        st.markdown("### Exámenes del Curso")
        
        exams = get_exams(course_id=selected_course['id'])
        
        if exams:
            for exam in exams:
                with st.expander(f"📝 {exam['title']}", expanded=False):
                    st.write(f"**Descripción:** {exam.get('description', 'Sin descripción')}")
                    st.write(f"**Nota Mínima:** {exam.get('passing_score', 14)}/20")
                    st.write(f"**Tiempo Límite:** {exam.get('time_limit_minutes', 60)} minutos")
                    st.write(f"**Intentos Máximos:** {exam.get('max_attempts', 1)}")
                    
                    # Obtener preguntas
                    questions_response = safe_supabase_query(
                        lambda: supabase.table('exam_questions')
                        .select('*')
                        .eq('exam_id', exam['id'])
                        .order('question_order')
                        .execute()
                    )
                    
                    questions = questions_response.data if questions_response and questions_response.data else []
                    st.write(f"**Preguntas:** {len(questions)}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("➕ Agregar Preguntas", key=f"add_questions_{exam['id']}"):
                            st.session_state.editing_exam = exam
                            st.rerun()
                    
                    with col2:
                        if st.button("📊 Ver Resultados", key=f"view_results_{exam['id']}"):
                            st.session_state.viewing_exam_results = exam
                            st.rerun()
        else:
            render_empty_state("No hay exámenes creados", "", "Crea el primer examen arriba")

def show_exam_question_editor(exam):
    """Editor de preguntas para examen"""
    st.markdown(f"### 📝 Editando Preguntas del Examen: {exam['title']}")
    
    # Obtener preguntas existentes
    questions_response = safe_supabase_query(
        lambda: supabase.table('exam_questions')
        .select('*')
        .eq('exam_id', exam['id'])
        .order('question_order')
        .execute()
    )
    
    questions = questions_response.data if questions_response and questions_response.data else []
    
    # Mostrar preguntas existentes
    if questions:
        st.markdown("#### Preguntas Existentes")
        for i, question in enumerate(questions):
            with st.expander(f"Pregunta {i+1}: {question['question_text'][:50]}...", expanded=False):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"**Tipo:** {question['question_type']}")
                    st.write(f"**Pregunta:** {question['question_text']}")
                    st.write(f"**Respuesta:** {question['correct_answer']}")
                    st.write(f"**Puntos:** {question.get('points', 1.0)}")
                with col2:
                    if st.button("🗑️", key=f"delete_q_{question['id']}"):
                        safe_supabase_query(
                            lambda: supabase.table('exam_questions').delete().eq('id', question['id']).execute()
                        )
                        st.success("Pregunta eliminada")
                        clear_cache()
                        st.rerun()
    
    # Agregar nueva pregunta
    with st.expander("➕ Agregar Nueva Pregunta", expanded=True):
        # Selector de tipo FUERA del formulario para que sea dinámico
        question_type = st.selectbox(
            "Tipo de Pregunta", 
            ["Opción Múltiple", "Verdadero/Falso", "Respuesta Corta", "Ensayo"],
            key="question_type_selector"
        )
        
        # Ahora el formulario con campos que dependen del tipo
        with st.form("add_question_form"):
            question_text = st.text_area("Texto de la Pregunta", height=100)
            
            # Campos específicos según el tipo de pregunta
            if question_type == "Opción Múltiple":
                st.markdown("**Opciones de Respuesta**")
                options = st.text_area(
                    "Opciones (una por línea)", 
                    placeholder="Opción A\nOpción B\nOpción C\nOpción D",
                    height=120
                )
                correct_answer = st.text_input("Respuesta Correcta", placeholder="Escribe exactamente la opción correcta")
                
                if options:
                    options_list = [opt.strip() for opt in options.split('\n') if opt.strip()]
                else:
                    options_list = []
                question_type_db = "multiple_choice"
                
            elif question_type == "Verdadero/Falso":
                correct_answer = st.selectbox("Respuesta Correcta", ["Verdadero", "Falso"])
                options_list = ["Verdadero", "Falso"]
                question_type_db = "true_false"
                
            elif question_type == "Respuesta Corta":
                correct_answer = st.text_input(
                    "Respuesta Modelo/Clave", 
                    placeholder="Respuesta esperada (para referencia del profesor)"
                )
                options_list = []
                question_type_db = "short_answer"
                
            else:  # Ensayo
                correct_answer = st.text_area(
                    "Criterios de Evaluación / Respuesta Modelo",
                    placeholder="Describe los criterios o puntos clave que debe incluir la respuesta",
                    height=120
                )
                options_list = []
                question_type_db = "essay"
            
            points = st.number_input("Puntos", min_value=0.5, value=1.0, step=0.5)
            question_order = len(questions) + 1
            
            if st.form_submit_button("Agregar Pregunta", type="primary"):
                if not question_text or not correct_answer:
                    st.error("❌ La pregunta y la respuesta son requeridas")
                elif question_type == "Opción Múltiple" and not options_list:
                    st.error("❌ Debes agregar al menos una opción")
                elif question_type == "Opción Múltiple" and correct_answer not in options_list:
                    st.error("❌ La respuesta correcta debe ser una de las opciones listadas")
                else:
                    question_data = {
                        'exam_id': exam['id'],
                        'question_type': question_type_db,
                        'question_text': question_text,
                        'correct_answer': correct_answer,
                        'options': json.dumps(options_list) if options_list else None,
                        'points': points,
                        'question_order': question_order
                    }
                    
                    result = safe_supabase_query(
                        lambda: supabase.table('exam_questions').insert(question_data).execute()
                    )
                    
                    if result:
                        st.success("✅ Pregunta agregada exitosamente")
                        clear_cache()
                        st.rerun()
    
    # Botón para volver
    if st.button("← Volver a Exámenes"):
        st.session_state.pop('editing_exam', None)
        st.rerun()


def show_exam_results(exam):
    """Muestra resultados de examen"""
    st.markdown(f"### 📊 Resultados del Examen: {exam['title']}")
    
    # Obtener resultados
    results_response = safe_supabase_query(
        lambda: supabase.table('exam_results')
        .select('*, users(*)')
        .eq('exam_id', exam['id'])
        .order('completed_at', desc=True)
        .execute()
    )
    
    results = results_response.data if results_response and results_response.data else []
    
    if results:
        # Estadísticas generales
        total_students = len(results)
        passed_students = len([r for r in results if r.get('passed', False)])
        avg_score = sum([r.get('score', 0) for r in results]) / total_students if total_students > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Estudiantes", total_students)
        with col2:
            st.metric("Aprobados", f"{passed_students}/{total_students}")
        with col3:
            st.metric("Promedio", f"{avg_score:.1f}")
        
        # Lista detallada
        st.markdown("#### Resultados Detallados")
        for result in results:
            with st.expander(f"👤 {result['users']['first_name']} {result['users']['last_name']} - {result.get('score', 0)}/100", expanded=False):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Email:** {result['users']['email']}")
                    st.write(f"**Fecha:** {result.get('completed_at', '')[:19]}")
                    st.write(f"**Estado:** {'✅ Aprobado' if result.get('passed', False) else '❌ Reprobado'}")
                    if result.get('feedback'):
                        st.write(f"**Feedback:** {result['feedback']}")
                with col2:
                    st.write(f"**Nota:** {result.get('score', 0)}/100")
    else:
        st.info("No hay resultados registrados para este examen")
    
    # Botón para volver
    if st.button("← Volver a Exámenes"):
        st.session_state.pop('viewing_exam_results', None)
        st.rerun()

def show_teacher_assignments_tab(teacher_assignments):
    """Gestión de tareas del profesor (creación y listado básico)"""

    st.subheader("Gestión de Tareas")

    # Seleccionar curso y módulo
    courses = [a['courses'] for a in teacher_assignments]
    selected_course = st.selectbox(
        "Selecciona un curso",
        courses,
        format_func=lambda c: c['name'],
        key="assignment_course_select",
    )

    if not selected_course:
        return

    modules = get_course_modules(selected_course['id'])
    if not modules:
        st.info("No hay módulos en este curso. Crea módulos primero.")
        return

    # Crear nueva tarea
    with st.expander("➕ Crear Nueva Tarea", expanded=False):
        with st.form("create_assignment_form"):
            selected_module = st.selectbox(
                "Módulo",
                modules,
                format_func=lambda m: f"Módulo {m['module_number']}: {m['title']}",
            )
            title = st.text_input("Título de la tarea")
            description = st.text_area("Descripción")

            col1, col2 = st.columns(2)
            with col1:
                due_date = st.date_input("Fecha de entrega", value=datetime.now().date())
            with col2:
                due_time = st.time_input("Hora de entrega", value=datetime.now().time())

            max_score = st.number_input("Puntaje máximo", min_value=0.0, value=20.0)
            guide_files = st.file_uploader(
                "Archivos guía (opcional)",
                type=[
                    'jpg', 'jpeg', 'png', 'gif',
                    'pdf', 'doc', 'docx',
                    'xls', 'xlsx',
                    'ppt', 'pptx',
                    'txt',
                ],
                accept_multiple_files=True,
            )

            if st.form_submit_button("Crear Tarea", type="primary"):
                if not title:
                    st.error("El título es obligatorio")
                else:
                    due_datetime = datetime.combine(due_date, due_time)
                    assignment_data = {
                        'module_id': selected_module['id'],
                        'title': title,
                        'description': description,
                        'due_date': due_datetime.isoformat(),
                        'max_score': max_score,
                        'created_by': st.session_state.user['id'],
                    }

                    response = safe_supabase_query(
                        lambda: supabase.table('assignments').insert(assignment_data).execute()
                    )
                    new_assignment = response.data[0] if response and response.data else None

                    # Subir archivos guía como materiales del módulo
                    if guide_files and new_assignment:
                        for guide_file in guide_files:
                            upload_file_base64(
                                guide_file,
                                selected_module['id'],
                                f"Guía: {guide_file.name}",
                            )

                    st.success("Tarea creada exitosamente")
                    clear_cache()
                    st.rerun()

    # Listar tareas existentes del curso
    st.markdown("### Tareas del Curso")
    assignments_response = safe_supabase_query(
        lambda: supabase.table('assignments')
        .select('*, course_modules(*)')
        .execute()
    )

    assignments = assignments_response.data if assignments_response and assignments_response.data else []
    if assignments:
        # Filtrar por módulos del curso seleccionado
        module_ids = [m['id'] for m in modules]
        course_assignments = [a for a in assignments if a.get('module_id') in module_ids]

        if course_assignments:
            for assignment in course_assignments:
                module_info = assignment.get('course_modules')
                module_label = (
                    f"Módulo {module_info.get('module_number')}: {module_info.get('title')}"
                    if module_info
                    else "Módulo"
                )
                with st.expander(f"📝 {assignment['title']} - {module_label}", expanded=False):
                    st.write(assignment.get('description', ''))
                    st.write(f"**Fecha límite:** {assignment.get('due_date', '')}")
                    st.write(f"**Puntaje máximo:** {assignment.get('max_score', 20)}")

                    # Contar entregas
                    submissions_resp = safe_supabase_query(
                        lambda: supabase.table('assignment_submissions')
                        .select('id, status')
                        .eq('assignment_id', assignment['id'])
                        .execute()
                    )
                    submissions = (
                        submissions_resp.data
                        if submissions_resp and submissions_resp.data
                        else []
                    )
                    st.write(f"**Entregas:** {len(submissions)}")
        else:
            st.info("No hay tareas creadas para este curso.")
    else:
        st.info("No hay tareas registradas todavía.")

def show_teacher_students(teacher_assignments):
    """Vista de estudiantes del profesor"""
    
    st.subheader("Mis Estudiantes")
    
    # Obtener todos los estudiantes de los cursos del profesor
    all_students = {}
    
    for assignment in teacher_assignments:
        course = assignment['courses']
        enrollments = [e for e in get_enrollments() if e.get('course_id') == course['id']]
        
        for enrollment in enrollments:
            if enrollment.get('users'):
                student = enrollment['users']
                student_id = student['id']
                
                if student_id not in all_students:
                    all_students[student_id] = {
                        'student': student,
                        'courses': [],
                        'progress': []
                    }
                
                all_students[student_id]['courses'].append(course['name'])
                all_students[student_id]['progress'].append(enrollment.get('progress_percentage', 0))
    
    if all_students:
        for student_id, data in all_students.items():
            student = data['student']
            avg_progress = sum(data['progress']) / len(data['progress']) if data['progress'] else 0
            
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 2])
                
                with col1:
                    st.write(f"**{student['first_name']} {student['last_name']}**")
                    st.caption(student['email'])
                
                with col2:
                    st.write(f"📚 Cursos: {', '.join(data['courses'][:2])}")
                    if len(data['courses']) > 2:
                        st.caption(f"+{len(data['courses']) - 2} más")
                
                with col3:
                    render_progress_bar(avg_progress, "Progreso Promedio")
                
                st.markdown("---")
    else:
        render_empty_state("No hay estudiantes inscritos", "👥")

# ==================== DASHBOARD DE ESTUDIANTE ====================

def show_student_dashboard():
    """Dashboard completo del estudiante"""
    
    st.markdown("""
    <div class="main-header animate-fade-in">
        <h1>🎓 Mi Aprendizaje</h1>
        <span class="role-badge student-badge">ESTUDIANTE</span>
    </div>
    """, unsafe_allow_html=True)
    
    user = st.session_state.user
    st.markdown(f"### Bienvenido, {user['first_name']} {user['last_name']}")
    
    if 'viewing_course' in st.session_state:
        show_student_course_content(st.session_state.viewing_course)
        return

    # Tabs principales
    tabs = st.tabs([
        "🛒 Catálogo de Cursos",
        "📚 Mis Cursos",
        "📤 Tareas",
        "📝 Exámenes",
        "🎓 Certificados",
        "💳 Mis Pagos"
    ])
    
    with tabs[0]:  # Catálogo
        show_student_course_catalog()
        
        # Proceso de pago si se está comprando un curso
        if st.session_state.get('purchasing_course'):
            show_student_checkout()
    
    with tabs[1]:  # Mis Cursos
        show_student_my_courses()
    
    with tabs[2]:  # Tareas
        show_student_assignments()
    
    with tabs[3]:  # Exámenes
        show_student_exams()
    
    with tabs[4]:  # Certificados
        show_student_certificates()
    
    with tabs[5]:  # Pagos
        show_student_payments()

def show_student_course_content(course):
    """Muestra el contenido del curso al estudiante"""
    st.button("← Volver a Mis Cursos", on_click=lambda: st.session_state.pop('viewing_course', None))
    
    st.markdown(f"""
    <div class="main-header animate-fade-in">
        <h1>📚 {course['name']}</h1>
        <p>{course.get('description', '')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Obtener inscripción
    enrollment = next((e for e in get_enrollments(st.session_state.user['id']) if e['course_id'] == course['id']), None)
    
    if not enrollment:
        st.error("No estás inscrito en este curso")
        return
        
    # Obtener módulos
    modules = get_course_modules(course['id'])
    
    # Obtener progreso guardado
    completed_items = enrollment.get('completed_items', []) or []
    if isinstance(completed_items, str):
        try:
            completed_items = json.loads(completed_items)
        except:
            completed_items = []
            
    # Calcular progreso total
    total_items = 0
    completed_count = 0
    
    col_content, col_sidebar = st.columns([3, 1])
    
    with col_content:
        st.subheader("Contenido del Curso")
        
        for module in modules:
            with st.expander(f"📁 Módulo {module['module_number']}: {module['title']}", expanded=True):
                st.write(module.get('study_material', ''))
                
                if module.get('content_url'):
                    st.markdown(f"**[🔗 Ver Contenido]({module['content_url']})**")
                
                # Materiales
                materials = safe_supabase_query(
                    lambda: supabase.table('study_materials').select('*').eq('module_id', module['id']).execute()
                ).data or []
                
                if materials:
                    st.markdown("**Materiales del módulo:**")
                    display_materials_with_download(materials, show_delete=False)
                
                for material in materials:
                    item_id = f"mat_{material['id']}"
                    total_items += 1
                    is_completed = item_id in completed_items
                    if is_completed:
                        completed_count += 1
                        
                    if st.checkbox(f"📄 {material['title']}", value=is_completed, key=f"check_{item_id}"):
                        if not is_completed:
                            completed_items.append(item_id)
                            update_progress(enrollment['id'], completed_items)
                            st.rerun()
                    else:
                        if is_completed:
                            completed_items.remove(item_id)
                            update_progress(enrollment['id'], completed_items)
                            st.rerun()
                
                # Exámenes del módulo
                exams = get_exams(module_id=module['id'])
                for exam in exams:
                    item_id = f"exam_{exam['id']}"
                    total_items += 1
                    
                    # Verificar si el examen fue aprobado
                    exam_results = safe_supabase_query(
                        lambda: supabase.table('exam_results')
                        .select('*')
                        .eq('exam_id', exam['id'])
                        .eq('student_id', st.session_state.user['id'])
                        .eq('passed', True)
                        .execute()
                    ).data
                    
                    is_passed = len(exam_results) > 0
                    if is_passed:
                        completed_count += 1
                        if item_id not in completed_items:
                            completed_items.append(item_id)
                            update_progress(enrollment['id'], completed_items)
                    
                    st.markdown(f"**📝 Examen: {exam['title']}**")
                    if is_passed:
                        st.success("✅ Aprobado")
                    else:
                        if st.button("Realizar Examen", key=f"take_exam_btn_{exam['id']}"):
                            st.session_state.taking_exam = exam
                            st.rerun()

    with col_sidebar:
        st.markdown("### Tu Progreso")
        progress = (completed_count / total_items * 100) if total_items > 0 else 0
        render_progress_bar(progress, f"{int(progress)}%")
        
        if progress >= 100:
            st.success("¡Curso Completado!")
            if not enrollment.get('certificate_issued'):
                if st.button("🎓 Solicitar Certificado", use_container_width=True):
                    trigger_n8n_workflow('certificate_generation', {
                        'enrollment_id': enrollment['id'],
                        'student_id': st.session_state.user['id'],
                        'course_id': course['id']
                    })
                    st.success("Certificado solicitado")

def update_progress(enrollment_id, completed_items):
    """Actualiza el progreso del estudiante"""
    # Calcular porcentaje (simplificado, idealmente basado en total de items del curso)
    # Aquí solo actualizamos la lista de items completados
    # El porcentaje real se debería recalcular basado en el total de items del curso
    
    # Obtener curso para saber total de items
    enrollment = safe_supabase_query(
        lambda: supabase.table('enrollments').select('course_id').eq('id', enrollment_id).single().execute()
    ).data
    
    if enrollment:
        course_id = enrollment['course_id']
        modules = get_course_modules(course_id)
        total_items = 0
        for m in modules:
            mats = safe_supabase_query(lambda: supabase.table('study_materials').select('id').eq('module_id', m['id']).execute()).data or []
            exams = get_exams(module_id=m['id'])
            total_items += len(mats) + len(exams)
            
        progress_percentage = (len(completed_items) / total_items * 100) if total_items > 0 else 0
        
        safe_supabase_query(
            lambda: supabase.table('enrollments').update({
                'completed_items': json.dumps(completed_items),
                'progress_percentage': progress_percentage,
                'completion_status': 'completed' if progress_percentage >= 100 else 'in_progress'
            }).eq('id', enrollment_id).execute()
        )
        # Limpiar caché para que el nuevo progreso se refleje inmediatamente
        clear_cache()


def show_student_course_catalog():
    """Catálogo público de cursos para comprar"""
    
    st.subheader("🛒 Catálogo de Cursos")
    st.markdown("Explora y compra cursos para comenzar tu aprendizaje")
    
    # Obtener cursos disponibles
    all_courses = get_courses()
    
    # Obtener cursos ya inscritos
    my_enrollments = get_enrollments(student_id=st.session_state.user['id'])
    enrolled_course_ids = [e.get('course_id') for e in my_enrollments]
    
    # Filtrar cursos no inscritos
    available_courses = [c for c in all_courses if c['id'] not in enrolled_course_ids]
    
    if available_courses:
        # Filtros
        col1, col2 = st.columns([2, 1])
        with col1:
            search = st.text_input("🔍 Buscar cursos", placeholder="Nombre del curso...")
        with col2:
            price_filter = st.selectbox("Precio", ["Todos", "Gratis", "De Pago"])
        
        # Aplicar filtros
        filtered_courses = available_courses
        if search:
            filtered_courses = [c for c in filtered_courses if search.lower() in c['name'].lower()]
        if price_filter == "Gratis":
            filtered_courses = [c for c in filtered_courses if c.get('price', 0) == 0]
        elif price_filter == "De Pago":
            filtered_courses = [c for c in filtered_courses if c.get('price', 0) > 0]
        
        # Mostrar cursos
        for course in filtered_courses:
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"### 📚 {course['name']}")
                    st.write(course.get('description', 'Sin descripción'))
                    
                    col_info1, col_info2 = st.columns(2)
                    with col_info1:
                        st.caption(f"⏱️ Duración: {course.get('duration_days', 0)} días")
                    with col_info2:
                        if course.get('price', 0) == 0:
                            st.caption("💚 GRATIS")
                        else:
                            st.caption(f"💰 ${course.get('price', 0):.2f}")
                
                with col2:
                    if course.get('price', 0) == 0:
                        # Inscripción gratuita directa
                        if st.button("📚 Inscribirse Gratis", key=f"enroll_free_{course['id']}", use_container_width=True):
                            # Crear inscripción directamente
                            new_enrollment = {
                                'student_id': st.session_state.user['id'],
                                'course_id': course['id'],
                                'progress_percentage': 0,
                                'completion_status': 'in_progress'
                            }
                            
                            result = safe_supabase_query(
                                lambda: supabase.table('enrollments').insert(new_enrollment).execute()
                            )
                            
                            if result:
                                st.success("✅ ¡Inscrito exitosamente!")
                                clear_cache()
                                st.rerun()
                    else:
                        # Proceso de pago
                        if st.button("💳 Comprar Curso", key=f"buy_{course['id']}", use_container_width=True):
                            st.session_state.purchasing_course = course
                            st.rerun()
                
                st.markdown("---")
        
        if not filtered_courses:
            render_empty_state("No se encontraron cursos", "🔍", "Intenta con otros filtros")
    else:
        st.success("🎉 ¡Ya estás inscrito en todos los cursos disponibles!")

def show_student_checkout():
    """Proceso de checkout y pago"""
    
    course = st.session_state.purchasing_course
    
    st.markdown("---")
    st.markdown("## 💳 Proceso de Pago")
    
    # Mostrar formulario de pago
    payment_result = show_payment_form(course)
    
    if payment_result:
        if payment_result['success']:
            # Pago exitoso
            show_payment_success(payment_result, course)

            # Delegar creación de suscripción e inscripción a n8n
            trigger_n8n_workflow('payment', {
                'student_id': st.session_state.user['id'],
                'course_id': course['id'],
                'transaction_id': payment_result['transaction_id'],
                'amount': course['price'],
                'payment_method': payment_result['payment_method']
            })
            
            clear_cache()
            
            if st.button("✅ Ir a Mis Cursos", type="primary", use_container_width=True):
                del st.session_state.purchasing_course
                st.rerun()
        else:
            # Pago fallido
            show_payment_failure(payment_result)
            
            if st.button("🔄 Intentar Nuevamente", use_container_width=True):
                st.rerun()
            
            if st.button("← Volver al Catálogo"):
                del st.session_state.purchasing_course
                st.rerun()

def show_student_my_courses():
    """Cursos inscritos del estudiante"""
    
    st.subheader("📚 Mis Cursos")
    
    enrollments = get_enrollments(student_id=st.session_state.user['id'])
    
    if enrollments:
        for enrollment in enrollments:
            if enrollment.get('courses'):
                course = enrollment['courses']
                progress = enrollment.get('progress_percentage', 0)
                
                with st.expander(f"📖 {course['name']} - {progress}%", expanded=False):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**Descripción:** {course.get('description', 'Sin descripción')}")
                        
                        # Barra de progreso
                        render_progress_bar(progress, "Progreso del Curso")
                        
                        # Estado
                        status = enrollment.get('completion_status', 'in_progress')
                        render_status_badge(status)
                    
                    with col2:
                        if st.button("📚 Ver Contenido", key=f"view_content_{course['id']}", use_container_width=True):
                            st.session_state.viewing_course = course
                            st.rerun()
                        
                        if progress >= 100 and not enrollment.get('certificate_issued'):
                            if st.button("🎓 Solicitar Certificado", key=f"request_cert_{enrollment['id']}", use_container_width=True):
                                # Trigger generación de certificado
                                trigger_n8n_workflow('certificate_generation', {
                                    'enrollment_id': enrollment['id'],
                                    'student_id': st.session_state.user['id'],
                                    'course_id': course['id']
                                })
                                st.success("✅ Certificado solicitado. Recibirás un email cuando esté listo.")
    else:
        render_empty_state(
            "No estás inscrito en ningún curso",
            "📚",
            "Explora el catálogo y compra tu primer curso"
        )

def show_student_exams():
    """Exámenes disponibles para el estudiante"""
    
    if 'taking_exam' in st.session_state:
        take_exam(st.session_state.taking_exam)
        return

    st.subheader("📝 Mis Exámenes")
    
    enrollments = get_enrollments(student_id=st.session_state.user['id'])
    
    if enrollments:
        for enrollment in enrollments:
            course = enrollment['courses']
            exams = get_exams(course_id=course['id'])
            
            if exams:
                st.markdown(f"### {course['name']}")
                for exam in exams:
                    with st.container():
                        col1, col2, col3 = st.columns([3, 2, 2])
                        with col1:
                            st.write(f"**{exam['title']}**")
                            st.caption(f"Duración: {exam['time_limit_minutes']} min | Min: {exam['passing_score']}/20")
                        
                        with col2:
                            # Verificar estado
                            results_response = safe_supabase_query(
                                lambda: supabase.table('exam_results')
                                .select('*')
                                .eq('exam_id', exam['id'])
                                .eq('student_id', st.session_state.user['id'])
                                .order('id', desc=True)
                                .execute()
                            )
                            results = results_response.data if results_response and results_response.data else []
                            
                            if results:
                                last_result = results[0]
                                if last_result['passed']:
                                    st.success(f"✅ Aprobado ({last_result['score']}/100)")
                                else:
                                    st.error(f"❌ No Aprobado ({last_result['score']}/100)")

                                # Mostrar feedback detallado generado por IA (Gemini)
                                feedback_text = last_result.get('feedback')
                                if feedback_text:
                                    with st.expander("Ver feedback del examen"):
                                        st.markdown(feedback_text.replace("\n", "  \n"))
                            else:
                                st.info("Pendiente")
                        
                        with col3:
                            if not results or (not results[0]['passed'] and len(results) < exam['max_attempts']):
                                if st.button("📝 Realizar", key=f"take_exam_list_{exam['id']}"):
                                    st.session_state.taking_exam = exam
                                    st.rerun()
            st.markdown("---")
    else:
        render_empty_state("No tienes exámenes pendientes", "📝")

def take_exam(exam):
    """Interfaz para realizar examen"""
    st.button("← Volver", on_click=lambda: st.session_state.pop('taking_exam', None))
    
    st.markdown(f"## 📝 {exam['title']}")
    st.markdown(exam.get('description', ''))
    
    # Obtener preguntas
    questions = safe_supabase_query(
        lambda: supabase.table('exam_questions').select('*').eq('exam_id', exam['id']).order('question_order').execute()
    ).data or []
    
    if not questions:
        st.warning("Este examen no tiene preguntas aún.")
        return
        
    with st.form("exam_submission"):
        answers = []
        for q in questions:
            st.markdown(f"**{q['question_text']}**")
            
            # Asumiendo preguntas de opción múltiple almacenadas en JSON o texto simple
            # Si 'options' es un campo JSON en la tabla exam_questions
            options = q.get('options')
            if isinstance(options, str):
                try:
                    options = json.loads(options)
                except:
                    options = []
            
            if options:
                answer = st.radio("Selecciona una respuesta:", options, key=f"q_{q['id']}")
            else:
                answer = st.text_area("Tu respuesta:", key=f"q_{q['id']}")
            
            answers.append({
                'question_id': q['id'],
                'question': q['question_text'],
                'student_answer': answer,
                'correct_answer': q.get('correct_answer') # Esto no debería enviarse al frontend en un caso real seguro, pero para simulación está bien
            })
            st.markdown("---")
            
        if st.form_submit_button("Enviar Examen", type="primary"):
            with st.spinner("Calificando..."):
                # Calcular nota preliminar (si es posible) o enviar a n8n
                score = 0
                correct_count = 0
                
                # Preparar datos para n8n
                submission_data = {
                    'exam_id': exam['id'],
                    'student_id': st.session_state.user['id'],
                    'passing_score': exam['passing_score'] * 5, # Convertir a escala 100
                    'submission': answers
                }
                
                # Trigger n8n workflow
                trigger_n8n_workflow('exam_correction', submission_data)
                
                st.success("✅ Examen enviado para corrección. Recibirás los resultados pronto.")
                del st.session_state.taking_exam
                st.rerun()

def show_student_certificates():
    """Certificados del estudiante"""
    
    st.subheader("🎓 Mis Certificados")
    
    # Obtener certificados del estudiante
    certs_response = safe_supabase_query(
        lambda: supabase.table('certificates')
        .select('*, enrollments(*, courses(*))')
        .execute()
    )
    
    if certs_response and certs_response.data:
        # Filtrar certificados del estudiante actual
        my_certs = [c for c in certs_response.data 
                   if c.get('enrollments') and 
                   c['enrollments'].get('student_id') == st.session_state.user['id']]
        
        if my_certs:
            for cert in my_certs:
                course = cert['enrollments']['courses']
                
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"### 🎓 {course['name']}")
                        st.write(f"**Fecha de Emisión:** {cert.get('issue_date', '')[:10]}")
                        st.write(f"**Código de Verificación:** `{cert.get('verification_code')}`")
                    
                    with col2:
                        if st.button("📥 Descargar", key=f"download_cert_{cert['id']}", use_container_width=True):
                            # Generar PDF del certificado al vuelo
                            student_name = f"{st.session_state.user['first_name']} {st.session_state.user['last_name']}"
                            course_name = course['name']
                            verification_code = cert.get('verification_code', '')
                            completion_date = cert['enrollments'].get('enrollment_date', '')[:10]

                            # Crear PDF con diseño tipo certificado
                            pdf = FPDF(orientation='L', unit='mm', format='A4')
                            pdf.add_page()

                            # Colores y configuración inicial
                            pdf.set_auto_page_break(auto=False, margin=0)

                            # Borde exterior
                            pdf.set_draw_color(100, 100, 160)
                            pdf.set_line_width(1.5)
                            pdf.rect(8, 8, 281, 190)

                            # Borde interior
                            pdf.set_draw_color(180, 180, 220)
                            pdf.set_line_width(0.8)
                            pdf.rect(14, 14, 269, 178)

                            # Título principal
                            pdf.set_xy(0, 28)
                            pdf.set_font('Arial', 'B', 30)
                            pdf.set_text_color(40, 40, 80)
                            pdf.cell(0, 12, 'CERTIFICADO DE FINALIZACIÓN', 0, 1, 'C')

                            # Subtítulo
                            pdf.set_font('Arial', '', 14)
                            pdf.set_text_color(80, 80, 120)
                            pdf.ln(4)
                            pdf.cell(0, 8, 'Se certifica que', 0, 1, 'C')

                            # Nombre del estudiante
                            pdf.ln(2)
                            pdf.set_font('Arial', 'B', 24)
                            pdf.set_text_color(20, 20, 60)
                            pdf.cell(0, 12, student_name, 0, 1, 'C')

                            # Texto descriptivo del curso
                            pdf.ln(6)
                            pdf.set_font('Arial', '', 14)
                            pdf.set_text_color(60, 60, 90)
                            pdf.multi_cell(0, 8,
                                f'Ha completado satisfactoriamente el curso "{course_name}", '
                                'demostrando compromiso y dedicación en su proceso de aprendizaje.',
                                0, 'C'
                            )

                            # Información adicional (fecha)
                            pdf.ln(6)
                            pdf.set_font('Arial', '', 12)
                            pdf.set_text_color(80, 80, 110)
                            pdf.cell(0, 8, f'Fecha de emisión: {completion_date}', 0, 1, 'C')

                            # Línea de firma y texto
                            pdf.set_y(150)
                            pdf.set_draw_color(120, 120, 160)
                            pdf.set_line_width(0.5)
                            pdf.line(60, 150, 140, 150)
                            pdf.line(160, 150, 240, 150)

                            pdf.set_font('Arial', 'B', 12)
                            pdf.set_text_color(40, 40, 80)
                            pdf.set_xy(60, 152)
                            pdf.cell(80, 6, 'Director Académico', 0, 0, 'C')
                            pdf.set_xy(160, 152)
                            pdf.cell(80, 6, 'Coordinador de Cursos', 0, 0, 'C')

                            # Código de verificación en el pie
                            pdf.set_y(178)
                            pdf.set_font('Arial', '', 9)
                            pdf.set_text_color(120, 120, 120)
                            pdf.cell(0, 5, f'Código de Verificación: {verification_code}', 0, 1, 'C')
                            pdf.cell(0, 4, 'Este certificado puede verificarse en la plataforma de Cursos Online.', 0, 1, 'C')

                            pdf_data = pdf.output(dest='S')
                            # fpdf2 puede devolver str o bytearray según versión; normalizar a bytes
                            if isinstance(pdf_data, str):
                                pdf_bytes = pdf_data.encode('latin-1')
                            else:
                                pdf_bytes = bytes(pdf_data)

                            st.download_button(
                                "💾 Guardar PDF",
                                pdf_bytes,
                                file_name=f"certificado_{course_name}.pdf",
                                mime="application/pdf"
                            )
                    
                    st.markdown("---")
        else:
            render_empty_state(
                "Aún no tienes certificados",
                "🎓",
                "Completa tus cursos para obtener certificados"
            )
    else:
        render_empty_state("No hay certificados disponibles", "🎓")

def show_student_payments():
    """Historial de pagos del estudiante"""
    
    st.subheader("💳 Historial de Pagos")
    
    subscriptions = get_subscriptions(student_id=st.session_state.user['id'])
    
    if subscriptions:
        total_spent = sum([s.get('amount_paid', 0) for s in subscriptions if s.get('payment_status') == 'approved'])
        
        st.metric("Total Gastado", f"${total_spent:.2f}")
        
        st.markdown("### Transacciones")
        
        for sub in subscriptions:
            if sub.get('courses'):
                course = sub['courses']
                
                with st.container():
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.write(f"**{course['name']}**")
                    
                    with col2:
                        st.write(f"💰 ${sub.get('amount_paid', 0):.2f}")
                        render_status_badge(sub.get('payment_status', 'pending'))
                    
                    with col3:
                        st.caption(sub.get('created_at', '')[:10])
                    
                    st.markdown("---")
    else:
        render_empty_state("No hay transacciones", "💳", "Tus pagos aparecerán aquí")

# ==================== CONTINUARÁ EN PARTE 4 (MAIN) ====================



# ==================== FUNCIÓN PRINCIPAL ====================

def main():
    """Función principal de la aplicación"""
    
    # Verificar autenticación
    if not auth_system.is_authenticated():
        show_login_page()
        return
    
    # Usuario autenticado - mostrar sidebar
    user = st.session_state.user
    
    # Sidebar con información del usuario
    with st.sidebar:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
                    padding: 1rem; border-radius: 10px; margin-bottom: 1rem;'>
            <h3 style='color: white; margin: 0;'>👤 {user['first_name']} {user['last_name']}</h3>
            <p style='color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0;'>{user['email']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Badge de rol
        role_badges = {
            'admin': '<span class="role-badge admin-badge">ADMINISTRADOR</span>',
            'teacher': '<span class="role-badge teacher-badge">PROFESOR</span>',
            'student': '<span class="role-badge student-badge">ESTUDIANTE</span>'
        }
        st.markdown(role_badges.get(user['role'], ''), unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navegación según rol
        if user['role'] == 'admin':
            st.markdown("### 🎛️ Panel de Control")
            st.caption("Gestión completa del sistema")
        elif user['role'] == 'teacher':
            st.markdown("### 👨‍🏫 Mis Herramientas")
            st.caption("Gestión de cursos y estudiantes")
        else:  # student
            st.markdown("### 🎓 Mi Aprendizaje")
            st.caption("Cursos y certificados")
        
        # Botón de cerrar sesión
        show_logout()
    
    # Mostrar dashboard según rol
    if user['role'] == 'admin':
        show_admin_dashboard()
    elif user['role'] == 'teacher':
        show_teacher_dashboard()
    else:  # student
        show_student_dashboard()

def show_student_assignments():
    """Muestra las tareas del estudiante con opción para subir archivos"""
    st.subheader("📤 Mis Tareas")
    
    # Obtener cursos inscritos
    enrollments = get_enrollments(student_id=st.session_state.user['id'])
    
    if not enrollments:
        st.info("No estás inscrito en ningún curso")
        return
    
    for enrollment in enrollments:
        course = enrollment['courses']
        
        # Obtener tareas del curso
        assignments_response = safe_supabase_query(
            lambda: supabase.table('assignments')
            .select('*, course_modules(*)')
            .execute()
        )
        
        assignments = assignments_response.data if assignments_response and assignments_response.data else []
        
        # Filtrar tareas por módulos del curso
        course_assignments = []
        modules = get_course_modules(course['id'])
        module_ids = [m['id'] for m in modules]
        
        for assignment in assignments:
            if assignment.get('module_id') in module_ids:
                course_assignments.append(assignment)
        
        if course_assignments:
            st.markdown(f"### 📚 {course['name']}")
            
            for assignment in course_assignments:
                module_info = assignment.get('course_modules')
                module_label = (
                    f"Módulo {module_info.get('module_number')}: {module_info.get('title')}"
                    if module_info
                    else "Módulo"
                )
                
                with st.expander(f"📝 {assignment['title']} - {module_label}", expanded=False):
                    st.write(assignment.get('description', ''))
                    st.write(f"**Fecha límite:** {assignment.get('due_date', '')}")
                    st.write(f"**Puntaje máximo:** {assignment.get('max_score', 20)}")
                    
                    # Verificar si ya entregó la tarea
                    submission_response = safe_supabase_query(
                        lambda: supabase.table('assignment_submissions')
                        .select('*')
                        .eq('assignment_id', assignment['id'])
                        .eq('student_id', st.session_state.user['id'])
                        .execute()
                    )
                    
                    submission = submission_response.data[0] if submission_response and submission_response.data else None
                    
                    if submission:
                        st.success(f"✅ Entregado el {submission.get('submitted_at', '')[:10]}")
                        st.write(f"**Estado:** {submission.get('status', 'pendiente')}")
                        
                        # Mostrar archivos entregados
                        if submission.get('files'):
                            st.markdown("**Archivos entregados:**")
                            display_materials_with_download(submission['files'], show_delete=False)
                    else:
                        # Formulario para entregar tarea
                        with st.form(f"submit_assignment_{assignment['id']}"):
                            st.markdown("#### 📤 Entregar Tarea")
                            
                            submitted_files = st.file_uploader(
                                "Selecciona archivos",
                                type=[
                                    'jpg', 'jpeg', 'png', 'gif',
                                    'pdf', 'doc', 'docx',
                                    'xls', 'xlsx',
                                    'ppt', 'pptx',
                                    'txt',
                                ],
                                accept_multiple_files=True,
                                key=f"files_{assignment['id']}"
                            )
                            
                            comments = st.text_area("Comentarios (opcional)")
                            
                            if st.form_submit_button("📤 Entregar Tarea", type="primary"):
                                if not submitted_files:
                                    st.error("Debes subir al menos un archivo")
                                else:
                                    # Guardar archivos como materiales
                                    saved_files = []
                                    for file in submitted_files:
                                        file_id = upload_file_base64(file, assignment['module_id'], file.name)
                                        if file_id:
                                            saved_files.append(file_id)
                                    
                                    if saved_files:
                                        # Crear registro de entrega
                                        submission_data = {
                                            'assignment_id': assignment['id'],
                                            'student_id': st.session_state.user['id'],
                                            'files': saved_files,
                                            'comments': comments,
                                            'status': 'entregado',
                                            'submitted_at': datetime.now().isoformat()
                                        }
                                        
                                        result = safe_supabase_query(
                                            lambda: supabase.table('assignment_submissions').insert(submission_data).execute()
                                        )
                                        
                                        if result:
                                            st.success("✅ Tarea entregada exitosamente")
                                            clear_cache()
                                            st.rerun()
        else:
            st.info(f"No hay tareas asignadas para el curso {course['name']}")

# ==================== PUNTO DE ENTRADA ====================

if __name__ == "__main__":
    main()


# streamlit run app.py

# Activar entorno virtual (si usas uno)
# .\venv\Scripts\activate

# Instalar dependencias
# pip install -r requirements.txt