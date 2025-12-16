"""
Sistema de Gestión de Cursos Online - Parte 3
Dashboards de Profesor y Estudiante
"""

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
    
    # Tabs
    tabs = st.tabs([
        "📚 Mis Cursos",
        "📁 Gestión de Módulos",
        "📝 Exámenes",
        "📤 Tareas",
        "👥 Estudiantes"
    ])
    
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
                    st.session_state.show_module_editor = True
                
                if st.button("📝 Crear Examen", key=f"create_exam_{course['id']}", use_container_width=True):
                    st.session_state.selected_course = course
                    st.session_state.show_exam_creator = True

def show_teacher_modules(teacher_assignments):
    """Gestión de módulos del curso"""
    
    st.subheader("Gestión de Módulos")
    
    # Seleccionar curso
    courses = [a['courses'] for a in teacher_assignments]
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
                        .execute()
                    )
                    
                    materials = materials_response.data if materials_response and materials_response.data else []
                    
                    if materials:
                        st.markdown("**Materiales:**")
                        for material in materials:
                            st.write(f"📄 {material.get('title', material.get('file_name', 'Sin título'))}")
                    
                    # Botones de acción
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📤 Subir Material", key=f"upload_material_{module['id']}"):
                            st.session_state.uploading_to_module = module['id']
                    
                    with col2:
                        if st.button("🗑️ Eliminar Módulo", key=f"delete_module_{module['id']}"):
                            safe_supabase_query(
                                lambda: supabase.table('course_modules').delete().eq('id', module['id']).execute()
                            )
                            st.success("Módulo eliminado")
                            clear_cache()
                            st.rerun()
        else:
            render_empty_state("No hay módulos creados", "📁", "Crea el primer módulo arriba")

def show_teacher_exams(teacher_assignments):
    """Gestión de exámenes"""
    
    st.subheader("Gestión de Exámenes")
    
    # Seleccionar curso
    courses = [a['courses'] for a in teacher_assignments]
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
                    
                    with col2:
                        if st.button("📊 Ver Resultados", key=f"view_results_{exam['id']}"):
                            st.session_state.viewing_exam_results = exam
        else:
            render_empty_state("No hay exámenes creados", "📝", "Crea el primer examen arriba")

def show_teacher_assignments_tab(teacher_assignments):
    """Gestión de tareas"""
    
    st.subheader("Gestión de Tareas")
    st.info("💡 Funcionalidad de tareas - Implementación similar a exámenes")
    # Aquí iría la implementación completa de tareas

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
    
    # Tabs principales
    tabs = st.tabs([
        "🛒 Catálogo de Cursos",
        "📚 Mis Cursos",
        "📝 Exámenes",
        "🎓 Certificados",
        "💳 Mis Pagos"
    ])
    
    with tabs[0]:  # Catálogo
        show_student_course_catalog()
    
    with tabs[1]:  # Mis Cursos
        show_student_my_courses()
    
    with tabs[2]:  # Exámenes
        show_student_exams()
    
    with tabs[3]:  # Certificados
        show_student_certificates()
    
    with tabs[4]:  # Pagos
        show_student_payments()

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

# Proceso de pago
if st.session_state.get('purchasing_course'):
    show_student_checkout()

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
            
            # Registrar suscripción
            subscription = {
                'student_id': st.session_state.user['id'],
                'course_id': course['id'],
                'amount_paid': course['price'],
                'payment_status': 'approved',
                'transaction_id': payment_result['transaction_id']
            }
            
            safe_supabase_query(
                lambda: supabase.table('subscriptions').insert(subscription).execute()
            )
            
            # Crear inscripción automáticamente
            enrollment = {
                'student_id': st.session_state.user['id'],
                'course_id': course['id'],
                'progress_percentage': 0,
                'completion_status': 'in_progress'
            }
            
            safe_supabase_query(
                lambda: supabase.table('enrollments').insert(enrollment).execute()
            )
            
            # Trigger workflow de n8n
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
    
    st.subheader("📝 Mis Exámenes")
    st.info("💡 Funcionalidad de exámenes para estudiantes")
    # Implementación completa de exámenes

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
                            # Descargar certificado
                            if cert.get('certificate_content_b64'):
                                pdf_bytes = base64.b64decode(cert['certificate_content_b64'])
                                st.download_button(
                                    "💾 Guardar PDF",
                                    pdf_bytes,
                                    file_name=f"certificado_{course['name']}.pdf",
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
