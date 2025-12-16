import streamlit as st
from supabase import create_client
import hashlib

# Configuración
supabase_url = "https://iywapkdxoqvnzityxrwr.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml5d2Fwa2R4b3F2bnppdHl4cndyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE2ODQyODcsImV4cCI6MjA3NzI2MDI4N30.Y6ULElfjC5kMaDL9Ece5caQpFbJChInKHxFThms3i0k"

supabase = create_client(supabase_url, supabase_key)

def hash_password(password):
    """Hash SHA-256 igual que en auth.py"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_users():
    print("🚀 Creando usuarios...")
    
    # Usuario ADMIN
    admin_data = {
        'email': 'admin@educacion.com',
        'password_hash': hash_password('admin'),
        'first_name': 'Admin',
        'last_name': 'Principal', 
        'role': 'admin',
        'is_active': True,
        'requires_password_reset': False
    }
    
    users = [admin_data]
    
    for user in users:
        try:
            # Verificar si el usuario ya existe
            existing = supabase.table('users').select('id').eq('email', user['email']).execute()
            
            if existing.data:
                print(f"⚠️  Usuario {user['email']} ya existe, actualizando...")
                # Actualizar contraseña si existe
                supabase.table('users').update({
                    'password_hash': user['password_hash'],
                    'is_active': True
                }).eq('email', user['email']).execute()
            else:
                print(f"✅ Creando usuario {user['email']}...")
                supabase.table('users').insert(user).execute()
                
        except Exception as e:
            print(f"❌ Error con {user['email']}: {e}")

def test_login(email, password):
    """Probar el login directamente"""
    print(f"\n🔐 Probando login para {email}...")
    
    hashed_input = hash_password(password)
    
    # Buscar usuario
    response = supabase.table('users').select('*').eq('email', email).eq('is_active', True).execute()
    
    if response.data:
        user = response.data[0]
        print(f"   Usuario encontrado: {user['first_name']} {user['last_name']}")
        print(f"   Hash en DB: {user.get('password_hash')}")
        print(f"   Hash input: {hashed_input}")
        print(f"   Coinciden: {user.get('password_hash') == hashed_input}")
        
        if user.get('password_hash') == hashed_input:
            print("   ✅ LOGIN EXITOSO")
        else:
            print("   ❌ CONTRASEÑA INCORRECTA")
    else:
        print("   ❌ USUARIO NO ENCONTRADO")

if __name__ == "__main__":
    create_users()
    
    print("\n" + "="*50)
    print("🧪 PROBANDO CREDENCIALES...")
    print("="*50)
    
    test_login('admin@educacion.com', 'admin')
    
    print("\n🎉 Proceso completado!")