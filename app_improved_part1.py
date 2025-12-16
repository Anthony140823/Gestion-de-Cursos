"""
Sistema de Gestión de Cursos Online - Versión Mejorada
Aplicación principal con UI moderna y arquitectura modular
"""

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
from typing import Optional, Dict, Any, List
import uuid

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

@st.cache_resource
def init_supabase():
    """Inicializa cliente de Supabase"""
    supabase_url = st.secrets["SUPABASE_URL"]
    supabase_key = st.secrets["SUPABASE_KEY"]
    return create_client(supabase_url, supabase_key)

# Inicializar servicios
supabase = init_supabase()
auth_system = init_auth(supabase)
N8N_WEBHOOK_URL = st.secrets["N8N_WEBHOOK_URL"]

# Inicializar generador de certificados
certificate_generator = CertificateGenerator()

# ==================== FUNCIONES AUXILIARES ====================

def clear_cache():
    """Limpia el caché de Streamlit"""
    st.cache_data.clear()

def trigger_n8n_workflow(workflow_type: str, data: Dict[str, Any]) -> bool:
    """
    Dispara un workflow de n8n
    
    Args:
        workflow_type: Tipo de workflow (enrollment, exam_correction, certificate_generation, payment)
        data: Datos para el workflow
        
    Returns:
        bool: True si fue exitoso
    """
    payload = {"workflow_type": workflow_type, "data": data}
    try:
        response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=30)
        return response.status_code == 200
    except Exception as e:
        st.error(f"Error en workflow n8n: {e}")
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
