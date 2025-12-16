"""
Sistema de Gestión de Cursos Online - Parte 4 (MAIN)
Función principal y enrutamiento
"""

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

# ==================== PUNTO DE ENTRADA ====================

if __name__ == "__main__":
    main()
