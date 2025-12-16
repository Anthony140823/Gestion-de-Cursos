import streamlit as st
import hashlib
import jwt
import datetime
from supabase import create_client
import secrets
import string

# Configuración JWT - SOLO usar st.secrets.get() en el código, NO en el .toml
JWT_SECRET = st.secrets.get("JWT_SECRET", "fallback-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"

class AuthSystem:
    def __init__(self, supabase_client):
        self.supabase = supabase_client
    
    def generate_temp_password(self, length=12):
        """Generar contraseña temporal"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def hash_password(self, password):
        """Hash de contraseña usando SHA-256"""
        if not password:
            return None
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password, hashed):
        """Verificar contraseña"""
        if not hashed:  # Si no tiene contraseña (usuarios migrados)
            return False
        return self.hash_password(password) == hashed
    
    def create_user(self, email, password, first_name, last_name, role='student'):
        """Crear nuevo usuario"""
        try:
            hashed_password = self.hash_password(password)
            user_data = {
                'email': email,
                'password_hash': hashed_password,
                'first_name': first_name,
                'last_name': last_name,
                'role': role,
                'requires_password_reset': False
            }
            response = self.supabase.table('users').insert(user_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            st.error(f"Error creando usuario: {e}")
            return None
    
    def update_user(self, user_id, update_data):
        """Actualizar datos del usuario (excluyendo contraseña)"""
        try:
            # Remover campos que no deben actualizarse directamente
            update_data.pop('password_hash', None)
            update_data.pop('email', None)  # El email no se puede cambiar fácilmente
            
            response = self.supabase.table('users').update(update_data).eq('id', user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            st.error(f"Error actualizando usuario: {e}")
            return None
    
    def reset_user_password(self, user_id, new_password=None):
        """Resetear contraseña de usuario"""
        try:
            if new_password is None:
                new_password = self.generate_temp_password()
            
            hashed_password = self.hash_password(new_password)
            update_data = {
                'password_hash': hashed_password,
                'requires_password_reset': True
            }
            response = self.supabase.table('users').update(update_data).eq('id', user_id).execute()
            
            if response.data:
                return new_password  # Retornar la nueva contraseña (temporal)
            return None
        except Exception as e:
            st.error(f"Error reseteando contraseña: {e}")
            return None
    
    def migrate_existing_user(self, user_id, password):
        """Migrar usuario existente agregando contraseña"""
        try:
            hashed_password = self.hash_password(password)
            update_data = {
                'password_hash': hashed_password,
                'requires_password_reset': False
            }
            response = self.supabase.table('users').update(update_data).eq('id', user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            st.error(f"Error migrando usuario: {e}")
            return None
    
    def authenticate_user(self, email, password):
        """Autenticar usuario"""
        try:
            response = self.supabase.table('users').select('*').eq('email', email).eq('is_active', True).execute()
            
            if not response.data:
                return None
                
            user = response.data[0]
            
            # Si el usuario no tiene contraseña (migrado)
            if not user.get('password_hash'):
                st.info("Usuario migrado. Por favor, establece tu contraseña.")
                st.session_state.require_password_setup = user['id']
                return None
            
            # Verificar contraseña
            if self.verify_password(password, user['password_hash']):
                return user
            
            return None
        except Exception as e:
            st.error(f"Error en autenticación: {e}")
            return None
    
    def create_jwt_token(self, user_data):
        """Crear JWT token"""
        payload = {
            'user_id': user_data['id'],
            'email': user_data['email'],
            'role': user_data['role'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    def verify_jwt_token(self, token):
        """Verificar JWT token"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def get_current_user(self):
        """Obtener usuario actual desde session_state"""
        return st.session_state.get('user')
    
    def is_authenticated(self):
        """Verificar si el usuario está autenticado"""
        return 'user' in st.session_state and st.session_state.user is not None
    
    def has_role(self, required_role):
        """Verificar si el usuario actual tiene el rol requerido"""
        if 'user' not in st.session_state or not st.session_state.user:
            return False
        return st.session_state.user.get('role') == required_role

    def has_any_role(self, roles):
        """Verificar si el usuario actual tiene alguno de los roles requeridos"""
        if 'user' not in st.session_state or not st.session_state.user:
            return False
        return st.session_state.user.get('role') in roles

def init_auth(supabase_client):
    return AuthSystem(supabase_client)