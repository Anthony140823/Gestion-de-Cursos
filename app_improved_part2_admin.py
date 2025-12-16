"""
Sistema de Gestión de Cursos Online - Parte 2
Dashboards completos para Admin, Profesor y Estudiante
"""

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
            # Aquí iría la lógica para generar PDF con reportlab
            st.success("✅ Reporte generado (funcionalidad pendiente)")

# ==================== CONTINUARÁ EN PARTE 3 ====================
