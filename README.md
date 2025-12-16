# 🎓 Sistema de Gestión de Cursos Online - Versión Mejorada

## 📋 Descripción

Sistema completo de gestión de cursos online con:
- ✨ Interfaz moderna y atractiva
- 💳 Sistema de pagos simulado
- 🎓 Generación automática de certificados PDF
- 📊 Dashboards para Admin, Profesores y Estudiantes
- 🤖 Integración con n8n para automatización
- 🔐 Sistema de autenticación robusto

---

## 🚀 Inicio Rápido

### 1. Instalación de Dependencias

```bash
# Activar entorno virtual (si usas uno)
.\venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configuración

Crea un archivo `.streamlit/secrets.toml` con:

```toml
SUPABASE_URL = "tu-url-de-supabase"
SUPABASE_KEY = "tu-key-de-supabase"
N8N_WEBHOOK_URL = "tu-url-webhook-n8n"
JWT_SECRET = "tu-secret-key-para-jwt"
```

### 3. Ejecutar Aplicación

```bash
streamlit run app.py
```

---

## 📁 Estructura del Proyecto

```
gestion_cursos/
├── app.py                          # Aplicación principal (GENERADA)
├── auth.py                         # Sistema de autenticación
├── requirements.txt                # Dependencias
│
├── components/                     # Componentes reutilizables
│   ├── __init__.py
│   ├── certificate_generator.py   # Generador de certificados PDF
│   └── ui_components.py           # Componentes de UI
│
├── utils/                          # Utilidades
│   ├── __init__.py
│   └── payment_simulator.py       # Simulador de pagos
│
├── N8N_WORKFLOW_INSTRUCTIONS.md   # Guía para configurar n8n
├── IMPLEMENTATION_STATUS.md        # Estado del proyecto
└── README.md                       # Este archivo
```

---

## 👥 Roles y Funcionalidades

### 🔴 Administrador

**Acceso completo al sistema:**
- ✅ Gestión de usuarios (crear, editar, desactivar)
- ✅ Gestión de cursos (crear, editar, activar/desactivar)
- ✅ Asignación de profesores a cursos
- ✅ Dashboard de pagos con gráficos
- ✅ Reportes y estadísticas
- ✅ Exportación de datos

**Credenciales de prueba:**
- Email: `admin@cursos.com`
- Password: `admin123`

### 🟢 Profesor

**Gestión de cursos asignados:**
- ✅ Ver cursos asignados
- ✅ Crear y gestionar módulos
- ✅ Crear exámenes con preguntas
- ✅ Subir materiales de estudio
- ✅ Ver estudiantes inscritos
- ✅ Calificar tareas y exámenes

**Credenciales de prueba:**
- Email: `profesor@cursos.com`
- Password: `profesor123`

### 🔵 Estudiante

**Experiencia de aprendizaje completa:**
- ✅ Catálogo de cursos con búsqueda y filtros
- ✅ Compra de cursos con pasarela de pagos simulada
- ✅ Inscripción gratuita a cursos sin costo
- ✅ Ver contenido de cursos inscritos
- ✅ Realizar exámenes con timer
- ✅ Descargar certificados al completar cursos
- ✅ Historial de pagos

**Credenciales de prueba:**
- Email: `estudiante@cursos.com`
- Password: `estudiante123`

---

## 💳 Sistema de Pagos (Simulado)

### Métodos de Pago Disponibles

1. **💳 Tarjeta de Crédito/Débito**
   - Validación de número de tarjeta
   - Validación de CVV
   - Validación de fecha de expiración
   - Tasa de éxito: 95%

2. **🅿️ PayPal**
   - Simulación de login
   - Tasa de éxito: 98%

3. **🏦 Transferencia Bancaria**
   - Selección de banco
   - Tasa de éxito: 90%

### Tarjetas de Prueba

Para probar el sistema de pagos, usa:

```
Número de Tarjeta: 4532 0151 1283 0366 (Visa)
Número de Tarjeta: 5425 2334 3010 9903 (Mastercard)
CVV: 123
Fecha: 12/26
```

---

## 🎓 Sistema de Certificados

### Características

- ✅ Generación automática de PDF profesional
- ✅ Diseño con bordes decorativos y gradientes
- ✅ Código QR de verificación
- ✅ Marca de agua de seguridad
- ✅ Código de verificación único
- ✅ Almacenamiento en base64 en Supabase

### Flujo de Generación

1. Estudiante completa curso (100% progreso)
2. Solicita certificado desde dashboard
3. Sistema dispara workflow de n8n
4. n8n genera PDF con datos del estudiante y curso
5. Certificado se guarda en BD
6. Estudiante recibe email con enlace de descarga
7. Certificado disponible para descarga en dashboard

### Verificación de Certificados

Los certificados pueden verificarse:
- Escaneando el código QR
- Ingresando el código de verificación en página pública
- Verificando en base de datos

---

## 🤖 Integración con n8n

### Workflows Implementados

1. **Inscripción de Estudiantes**
   - Validación de duplicados
   - Registro en BD
   - Email de bienvenida

2. **Corrección de Exámenes**
   - Integración con Gemini AI
   - Validación de respuestas JSON
   - Feedback detallado
   - Trigger automático de certificados

3. **Generación de Certificados**
   - Obtención de datos
   - Generación de PDF
   - Almacenamiento en BD
   - Notificación por email

4. **Procesamiento de Pagos**
   - Registro de transacción
   - Creación automática de inscripción
   - Email de confirmación

5. **Verificación de Certificados**
   - Búsqueda por código
   - Retorno de datos completos

### Configuración

Sigue las instrucciones detalladas en: **[N8N_WORKFLOW_INSTRUCTIONS.md](N8N_WORKFLOW_INSTRUCTIONS.md)**

---

## 🗄️ Base de Datos (Supabase)

### Tablas Principales

- `users` - Usuarios del sistema (admin, teacher, student)
- `courses` - Cursos disponibles
- `course_modules` - Módulos de cada curso
- `enrollments` - Inscripciones de estudiantes
- `subscriptions` - Pagos y suscripciones
- `exams` - Exámenes
- `exam_questions` - Preguntas de exámenes
- `exam_attempts` - Intentos de examen
- `exam_results` - Resultados con feedback de IA
- `certificates` - Certificados emitidos
- `teacher_assignments` - Asignación de profesores
- `study_materials` - Materiales de estudio
- `assignments` - Tareas
- `assignment_submissions` - Entregas de tareas

### Políticas RLS

Asegúrate de configurar las políticas de Row Level Security en Supabase para:
- Permitir lectura pública de cursos
- Restringir escritura solo a roles autorizados
- Permitir a estudiantes ver solo sus propios datos

---

## 🎨 Características de UI/UX

### Diseño Moderno

- ✨ Gradientes y animaciones CSS
- 🎨 Paleta de colores profesional
- 📱 Diseño responsive
- 🌓 Tema claro optimizado
- 💫 Transiciones suaves
- 🎯 Componentes reutilizables

### Componentes Personalizados

- Tarjetas de métricas con iconos
- Tarjetas de cursos con hover effects
- Barras de progreso (lineales y circulares)
- Badges de estado
- Alertas personalizadas
- Timelines
- Tablas de datos
- Temporizador de exámenes
- Visualización de calificaciones

---

## 🧪 Testing

### Flujo de Prueba Completo

#### 1. Como Administrador

```
1. Login como admin
2. Crear un curso nuevo
3. Crear un usuario profesor
4. Asignar profesor al curso
5. Ver dashboard de pagos
6. Generar reporte
```

#### 2. Como Profesor

```
1. Login como profesor
2. Ver cursos asignados
3. Crear módulo en curso
4. Subir material de estudio
5. Crear examen con preguntas
6. Ver estudiantes inscritos
```

#### 3. Como Estudiante

```
1. Registrarse como nuevo estudiante
2. Explorar catálogo de cursos
3. Comprar curso con tarjeta de prueba
4. Ver curso inscrito
5. Realizar examen
6. Solicitar certificado (si completó 100%)
7. Descargar certificado
```

### Comandos de Prueba n8n

Ver sección de testing en: **[N8N_WORKFLOW_INSTRUCTIONS.md](N8N_WORKFLOW_INSTRUCTIONS.md)**

---

## 📊 Métricas y Reportes

### Dashboard de Admin

- Total de usuarios por rol
- Cursos activos
- Inscripciones totales
- Ingresos totales
- Gráfico de usuarios por rol (pie chart)
- Gráfico de inscripciones en el tiempo (line chart)
- Gráfico de ingresos por curso (bar chart)

### Dashboard de Profesor

- Cursos asignados
- Total de estudiantes
- Módulos creados
- Exámenes activos
- Progreso promedio de estudiantes

### Dashboard de Estudiante

- Cursos inscritos
- Progreso por curso
- Certificados obtenidos
- Total gastado en cursos

---

## 🔧 Solución de Problemas

### Error: "Module not found"

```bash
pip install -r requirements.txt
```

### Error: "Supabase connection failed"

Verifica que `.streamlit/secrets.toml` esté configurado correctamente.

### Error: "n8n webhook not responding"

1. Verifica que n8n esté ejecutándose
2. Verifica la URL del webhook en secrets.toml
3. Revisa los logs de n8n

### Certificados no se generan

1. Verifica que el workflow de n8n esté configurado
2. Revisa las instrucciones en N8N_WORKFLOW_INSTRUCTIONS.md
3. Verifica que el estudiante tenga 100% de progreso

### Pagos no se registran

1. Verifica que la tabla `subscriptions` exista
2. Verifica que el workflow de pagos esté configurado
3. Revisa los logs de la aplicación

---

## 📚 Documentación Adicional

- **[N8N_WORKFLOW_INSTRUCTIONS.md](N8N_WORKFLOW_INSTRUCTIONS.md)** - Configuración detallada de workflows
- **[IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md)** - Estado del proyecto
- **[implementation_plan.md](.gemini/antigravity/brain/.../implementation_plan.md)** - Plan de implementación

---

## 🤝 Contribución

Este es un proyecto académico. Para mejoras:

1. Crea un branch
2. Implementa mejoras
3. Documenta cambios
4. Crea pull request

---

## 📝 Notas Importantes

> **⚠️ IMPORTANTE**: Este sistema usa un simulador de pagos. NO procesa pagos reales. Para producción, integra con Stripe, PayPal u otra pasarela real.

> **🔐 SEGURIDAD**: Cambia todas las credenciales de prueba antes de desplegar en producción.

> **🗄️ BASE DE DATOS**: Asegúrate de configurar correctamente las políticas RLS en Supabase.

> **🤖 N8N**: Los workflows deben configurarse manualmente siguiendo las instrucciones.

---

## 📄 Licencia

Proyecto académico - Universidad Nacional de Trujillo

---

## 👨‍💻 Autor

**Anthony**  
Ingeniería de Software - Ciclo 8  
Universidad Nacional de Trujillo

---

## 🎉 ¡Gracias!

Si tienes preguntas o encuentras problemas, revisa la documentación o contacta al administrador del sistema.

**¡Feliz aprendizaje! 🚀**
