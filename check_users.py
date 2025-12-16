import streamlit as st
from supabase import create_client

# Configuración
supabase_url = "https://iywapkdxoqvnzityxrwr.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml5d2Fwa2R4b3F2bnppdHl4cndyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE2ODQyODcsImV4cCI6MjA3NzI2MDI4N30.Y6ULElfjC5kMaDL9Ece5caQpFbJChInKHxFThms3i0k"

supabase = create_client(supabase_url, supabase_key)

def check_users():
    print("🔍 Verificando usuarios en la base de datos...")
    
    # Ver todos los usuarios
    response = supabase.table('users').select('*').execute()
    
    if response.data:
        print(f"✅ Se encontraron {len(response.data)} usuarios:")
        for user in response.data:
            print(f"   - {user['email']} ({user['role']}) - Password: {'Sí' if user.get('password_hash') else 'No'}")
    else:
        print("❌ No hay usuarios en la base de datos")

def check_tables():
    print("\n📊 Verificando estructura de la base de datos...")
    
    try:
        # Verificar si existe la tabla users
        response = supabase.table('users').select('id', count='exact').limit(1).execute()
        print("✅ Tabla 'users' existe")
    except Exception as e:
        print(f"❌ Error con tabla 'users': {e}")

if __name__ == "__main__":
    check_tables()
    check_users()