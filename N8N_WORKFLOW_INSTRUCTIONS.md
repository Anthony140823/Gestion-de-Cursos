# Instrucciones Detalladas para Configurar Workflows de n8n

## 📋 Resumen

Este documento contiene instrucciones paso a paso para configurar y mejorar los workflows de n8n para el sistema de gestión de cursos online.

---

## 🔧 Workflow 1: Inscripción de Estudiantes (enrollment)

### Estado Actual
✅ Estructura básica funcional
⚠️ Necesita mejoras en manejo de errores y validaciones

### Mejoras Recomendadas

#### Paso 1: Mejorar el nodo "Procesar Inscripción"

1. Abre el workflow en n8n
2. Haz clic en el nodo "Procesar Inscripción" (Function node)
3. Reemplaza el código con:

```javascript
// Procesar datos de inscripción con validaciones
const enrollmentData = $input.first().json.body.data;

// Validar datos requeridos
if (!enrollmentData.student_id || !enrollmentData.course_id) {
  throw new Error('Faltan datos requeridos: student_id y course_id');
}

// Guardar en base de datos
const enrollment = {
  student_id: enrollmentData.student_id,
  course_id: enrollmentData.course_id,
  enrollment_date: new Date().toISOString(),
  progress_percentage: 0,
  completion_status: 'in_progress'
};

return [{ json: enrollment }];
```

#### Paso 2: Agregar Validación de Duplicados

1. **AGREGAR** un nuevo nodo "Supabase" ANTES de "Guardar Inscripción"
2. Configurar:
   - **Nombre**: "Verificar Inscripción Existente"
   - **Operation**: Get
   - **Table**: enrollments
   - **Filters**: 
     - student_id = `={{ $json.student_id }}`
     - course_id = `={{ $json.course_id }}`

3. **AGREGAR** un nodo "IF" después de "Verificar Inscripción Existente"
4. Configurar:
   - **Nombre**: "¿Ya está inscrito?"
   - **Condition**: `={{ $json.length > 0 }}`
   - **True**: Conectar a un nodo "Stop and Error" con mensaje "El estudiante ya está inscrito en este curso"
   - **False**: Conectar a "Guardar Inscripción"

#### Paso 3: Mejorar el Email de Bienvenida

1. Haz clic en el nodo "Enviar Email Bienvenida"
2. Actualiza el mensaje:

```
Asunto: ¡Bienvenido al curso {{ $('Obtener Info Curso').item.json.name }}!

Mensaje:
Hola {{ $('Obtener Info Estudiante').item.json.first_name }},

¡Te damos la bienvenida al curso {{ $('Obtener Info Curso').item.json.name }}!

📚 Detalles del curso:
- Duración: {{ $('Obtener Info Curso').item.json.duration_days }} días
- Precio: ${{ $('Obtener Info Curso').item.json.price }}

🎯 Próximos pasos:
1. Accede a la plataforma con tu cuenta
2. Explora el contenido del curso
3. Completa las actividades según tu ritmo

¡Mucho éxito en tu aprendizaje!

Equipo de Cursos Online
```

---

## 🔧 Workflow 2: Corrección de Exámenes (exam_correction)

### Estado Actual
✅ Integración con Gemini funcional
⚠️ Necesita validación de respuesta JSON

### Mejoras CRÍTICAS

#### Paso 1: Mejorar el Prompt de Gemini

1. Haz clic en el nodo "Message a model"
2. Actualiza el prompt:

```
Eres un asistente de corrección de exámenes y un tutor amigable.

Voy a pasarte una lista de preguntas de un examen, donde cada item incluye:
- question: La pregunta
- correct_answer: La respuesta correcta
- student_answer: La respuesta del estudiante

DATOS DEL EXAMEN:
Puntuación para aprobar: {{ $json.body.data.passing_score }}

PREGUNTAS Y RESPUESTAS:
{{ JSON.stringify($json.body.data.submission) }}

INSTRUCCIONES:
1. Calcula la puntuación final de 0 a 100
2. Determina si aprobó (true/false) comparando con passing_score
3. Para CADA pregunta, genera feedback con:
   - is_correct: true o false
   - explanation: Explicación pedagógica y amigable

IMPORTANTE: Responde ÚNICAMENTE con un objeto JSON válido, sin markdown ni código adicional.

FORMATO DE RESPUESTA (copiar exactamente esta estructura):
{
  "score": <número_de_0_a_100>,
  "passed": <true_o_false>,
  "corrected_by_ai": true,
  "answers": [
    {
      "question": "<copia_la_pregunta>",
      "student_answer": "<copia_respuesta_estudiante>",
      "correct_answer": "<copia_respuesta_correcta>",
      "is_correct": <true_o_false>,
      "explanation": "<explicación_amigable_y_pedagógica>"
    }
  ]
}

EJEMPLO:
{
  "score": 75,
  "passed": true,
  "corrected_by_ai": true,
  "answers": [
    {
      "question": "¿Cuál es la capital de Francia?",
      "student_answer": "París",
      "correct_answer": "París",
      "is_correct": true,
      "explanation": "¡Excelente! París es correctamente la capital de Francia."
    }
  ]
}
```

#### Paso 2: AGREGAR Nodo de Validación JSON

1. **AGREGAR** un nuevo nodo "Code" DESPUÉS de "Message a model"
2. Configurar:
   - **Nombre**: "Validar y Limpiar JSON"
   - **Código**:

```javascript
// Obtener respuesta de Gemini
let responseText = $input.first().json.content.parts[0].text;

// Limpiar markdown si existe
responseText = responseText.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();

// Intentar parsear JSON
let parsedData;
try {
  parsedData = JSON.parse(responseText);
} catch (error) {
  throw new Error(`Error parseando JSON de Gemini: ${error.message}\nRespuesta: ${responseText}`);
}

// Validar estructura requerida
if (!parsedData.score && parsedData.score !== 0) {
  throw new Error('Falta campo requerido: score');
}

if (typeof parsedData.passed !== 'boolean') {
  throw new Error('Falta campo requerido: passed');
}

if (!Array.isArray(parsedData.answers)) {
  throw new Error('Falta campo requerido: answers (debe ser array)');
}

// Validar que score esté en rango válido
if (parsedData.score < 0 || parsedData.score > 100) {
  parsedData.score = Math.max(0, Math.min(100, parsedData.score));
}

// Retornar datos validados
return [{ json: parsedData }];
```

#### Paso 3: Actualizar "Guardar Resultado Examen"

1. Haz clic en el nodo "Guardar Resultado Examen"
2. Actualiza los campos para usar el nodo de validación:
   - **student_id**: `={{ $('Es Corrección Examen?').item.json.body.data.student_id }}`
   - **exam_id**: `={{ $('Es Corrección Examen?').item.json.body.data.exam_id }}`
   - **score**: `={{ $('Validar y Limpiar JSON').item.json.score }}`
   - **answers**: `={{ JSON.stringify($('Validar y Limpiar JSON').item.json.answers) }}`
   - **passed**: `={{ $('Validar y Limpiar JSON').item.json.passed }}`
   - **corrected_by_ai**: `={{ $('Validar y Limpiar JSON').item.json.corrected_by_ai }}`
   - **feedback**: `={{ $('Validar y Limpiar JSON').item.json.answers.map(a => \`Pregunta: ${a.question}\\nExplicación: ${a.explanation}\`).join('\\n\\n') }}`
   - **total_questions**: `={{ $('Validar y Limpiar JSON').item.json.answers.length }}`
   - **correct_answers**: `={{ $('Validar y Limpiar JSON').item.json.answers.filter(a => a.is_correct).length }}`

#### Paso 4: AGREGAR Verificación de Completación de Curso

1. **AGREGAR** un nodo "Supabase" DESPUÉS de "Guardar Resultado Examen"
2. Configurar:
   - **Nombre**: "Obtener Inscripción del Estudiante"
   - **Operation**: Get
   - **Table**: enrollments
   - **Filters**:
     - student_id = `={{ $('Es Corrección Examen?').item.json.body.data.student_id }}`

3. **AGREGAR** un nodo "Code" después
4. Configurar:
   - **Nombre**: "Verificar si Completó Curso"
   - **Código**:

```javascript
const enrollment = $input.first().json;
const examPassed = $('Validar y Limpiar JSON').item.json.passed;

// Si aprobó el examen y el progreso es 100%, disparar certificado
if (examPassed && enrollment.progress_percentage >= 100) {
  return [{
    json: {
      trigger_certificate: true,
      enrollment_id: enrollment.id,
      student_id: enrollment.student_id,
      course_id: enrollment.course_id
    }
  }];
}

return [{ json: { trigger_certificate: false } }];
```

5. **AGREGAR** un nodo "IF" después
6. Configurar:
   - **Condition**: `={{ $json.trigger_certificate === true }}`
   - **True**: Conectar a un nuevo nodo "HTTP Request" que llame al webhook de certificados
   - **False**: Conectar a "Response Node"

---

## 🔧 Workflow 3: Generación de Certificados (certificate_generation)

### Estado Actual
❌ NO genera PDFs reales
❌ Usa URLs ficticias
❌ No probado

### Implementación COMPLETA Requerida

#### Paso 1: AGREGAR Nodos de Consulta de Datos

**IMPORTANTE:** No necesitas un endpoint HTTP. n8n puede generar el PDF directamente usando Python.

#### Paso 2: Obtener Datos Necesarios

1. **AGREGAR** nodo "Supabase" ANTES de "Generar PDF de Certificado"
2. Configurar:
   - **Nombre**: "Obtener Datos de Inscripción"
   - **Operation**: Get
   - **Table**: enrollments
   - **Filters**: id = `={{ $json.body.data.enrollment_id }}`

3. **AGREGAR** nodo "Supabase"
4. Configurar:
   - **Nombre**: "Obtener Datos del Estudiante"
   - **Operation**: Get
   - **Table**: users
   - **Filters**: id = `={{ $('Obtener Datos de Inscripción').item.json.student_id }}`

5. **AGREGAR** nodo "Supabase"
6. Configurar:
   - **Nombre**: "Obtener Datos del Curso"
   - **Operation**: Get
   - **Table**: courses
   - **Filters**: id = `={{ $('Obtener Datos de Inscripción').item.json.course_id }}`

#### Paso 3: REEMPLAZAR "Generar Certificado" con Código Python

1. **ELIMINAR** el nodo actual "Generar Certificado" (que usa código ficticio)
2. **AGREGAR** nodo "Code" (Python)
3. Configurar:
   - **Nombre**: "Generar Certificado PDF"
   - **Mode**: Run Once for All Items
   - **Código Python**:

```python
import base64
import io
from datetime import datetime
import random
import string

# Importar reportlab para generar PDF
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

# Obtener datos de los nodos anteriores
student = $('Obtener Datos del Estudiante').first().json
course = $('Obtener Datos del Curso').first().json
enrollment = $('Obtener Datos de Inscripción').first().json

# Generar código de verificación único
timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=9))
verification_code = f"CERT-{timestamp}-{random_part}"

# Crear buffer para el PDF
buffer = io.BytesIO()

# Crear canvas
c = canvas.Canvas(buffer, pagesize=A4)
page_width, page_height = A4
margin = 0.75 * inch

# Dibujar borde decorativo
c.setStrokeColor(HexColor('#1f77b4'))
c.setLineWidth(3)
c.rect(margin - 10, margin - 10, page_width - 2 * (margin - 10), page_height - 2 * (margin - 10))

c.setStrokeColor(HexColor('#4a90e2'))
c.setLineWidth(1)
c.rect(margin, margin, page_width - 2 * margin, page_height - 2 * margin)

# Título principal
c.setFont("Helvetica-Bold", 36)
c.setFillColor(HexColor('#1f77b4'))
title = "CERTIFICADO DE FINALIZACIÓN"
title_width = c.stringWidth(title, "Helvetica-Bold", 36)
c.drawString((page_width - title_width) / 2, page_height - 2 * inch, title)

# Subtítulo
c.setFont("Helvetica", 14)
c.setFillColor(HexColor('#666666'))
subtitle = "Este documento certifica que"
subtitle_width = c.stringWidth(subtitle, "Helvetica", 14)
c.drawString((page_width - subtitle_width) / 2, page_height - 2.5 * inch, subtitle)

# Nombre del estudiante
student_name = f"{student['first_name']} {student['last_name']}"
c.setFont("Helvetica-Bold", 28)
c.setFillColor(HexColor('#2c3e50'))
name_width = c.stringWidth(student_name, "Helvetica-Bold", 28)
c.drawString((page_width - name_width) / 2, page_height - 3.5 * inch, student_name)

# Línea decorativa
c.setStrokeColor(HexColor('#1f77b4'))
c.setLineWidth(2)
line_start = (page_width - name_width) / 2 - 20
line_end = (page_width + name_width) / 2 + 20
c.line(line_start, page_height - 3.7 * inch, line_end, page_height - 3.7 * inch)

# Información del curso
c.setFont("Helvetica", 14)
c.setFillColor(HexColor('#666666'))
text1 = "ha completado satisfactoriamente el curso"
text1_width = c.stringWidth(text1, "Helvetica", 14)
c.drawString((page_width - text1_width) / 2, page_height - 4.3 * inch, text1)

# Nombre del curso
course_name = course['name']
c.setFont("Helvetica-Bold", 18)
c.setFillColor(HexColor('#1f77b4'))
course_width = c.stringWidth(course_name, "Helvetica-Bold", 18)
c.drawString((page_width - course_width) / 2, page_height - 4.8 * inch, course_name)

# Fecha de completación
completion_date = datetime.now().strftime("%d/%m/%Y")
c.setFont("Helvetica", 12)
c.setFillColor(HexColor('#666666'))
date_text = f"Fecha de finalización: {completion_date}"
date_width = c.stringWidth(date_text, "Helvetica", 12)
c.drawString((page_width - date_width) / 2, page_height - 5.3 * inch, date_text)

# Líneas de firma
y_position = page_height - 7 * inch

# Firma izquierda
left_x = page_width / 4
c.setStrokeColor(HexColor('#000000'))
c.setLineWidth(1)
c.line(left_x - 80, y_position, left_x + 80, y_position)
c.setFont("Helvetica", 10)
c.setFillColor(HexColor('#000000'))
director_text = "Director Académico"
director_width = c.stringWidth(director_text, "Helvetica", 10)
c.drawString(left_x - director_width / 2, y_position - 20, director_text)

# Firma derecha
right_x = 3 * page_width / 4
c.line(right_x - 80, y_position, right_x + 80, y_position)
instructor_text = "Instructor del Curso"
instructor_width = c.stringWidth(instructor_text, "Helvetica", 10)
c.drawString(right_x - instructor_width / 2, y_position - 20, instructor_text)

# Código de verificación
c.setFont("Helvetica-Bold", 10)
c.setFillColor(HexColor('#1f77b4'))
code_text = f"Código: {verification_code}"
c.drawString(margin + 20, margin + 20, code_text)

# Marca de agua
c.saveState()
c.setFont("Helvetica", 60)
c.setFillColorRGB(0.9, 0.9, 0.9, alpha=0.3)
c.rotate(45)
c.drawString(3 * inch, 0, "CERTIFICADO OFICIAL")
c.restoreState()

# Finalizar PDF
c.showPage()
c.save()

# Obtener bytes del PDF y convertir a base64
buffer.seek(0)
pdf_bytes = buffer.getvalue()
pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')

# Retornar datos para guardar
return {
    'json': {
        'enrollment_id': enrollment['id'],
        'certificate_content_b64': pdf_base64,
        'verification_code': verification_code,
        'student_name': student_name,
        'course_name': course_name,
        'completion_date': completion_date,
        'student_email': student['email']
    }
}
```

**Nota:** Si n8n no tiene reportlab instalado, puedes usar una versión simplificada con fpdf2:

```python
import base64
import io
from datetime import datetime
import random
import string
from fpdf import FPDF

# Obtener datos
student = $('Obtener Datos del Estudiante').first().json
course = $('Obtener Datos del Curso').first().json
enrollment = $('Obtener Datos de Inscripción').first().json

# Generar código de verificación
timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=9))
verification_code = f"CERT-{timestamp}-{random_part}"

# Crear PDF simple
pdf = FPDF()
pdf.add_page()

# Título
pdf.set_font('Arial', 'B', 24)
pdf.cell(0, 20, 'CERTIFICADO DE FINALIZACIÓN', 0, 1, 'C')

# Nombre del estudiante
pdf.set_font('Arial', 'B', 18)
student_name = f"{student['first_name']} {student['last_name']}"
pdf.cell(0, 20, student_name, 0, 1, 'C')

# Curso
pdf.set_font('Arial', '', 14)
pdf.cell(0, 10, 'Ha completado satisfactoriamente el curso:', 0, 1, 'C')
pdf.set_font('Arial', 'B', 16)
pdf.cell(0, 15, course['name'], 0, 1, 'C')

# Fecha
pdf.set_font('Arial', '', 12)
completion_date = datetime.now().strftime("%d/%m/%Y")
pdf.cell(0, 10, f'Fecha: {completion_date}', 0, 1, 'C')

# Código de verificación
pdf.ln(20)
pdf.set_font('Arial', 'B', 10)
pdf.cell(0, 10, f'Código de Verificación: {verification_code}', 0, 1, 'L')

# Convertir a base64
pdf_bytes = pdf.output(dest='S').encode('latin-1')
pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')

# Retornar datos
return {
    'json': {
        'enrollment_id': enrollment['id'],
        'certificate_content_b64': pdf_base64,
        'verification_code': verification_code,
        'student_name': student_name,
        'course_name': course_name,
        'completion_date': completion_date,
        'student_email': student['email']
    }
}
```

#### Paso 4: Actualizar "Guardar Certificado"

1. Haz clic en el nodo "Guardar Certificado" (Supabase)
2. Actualiza los campos para usar los datos del nodo Python:
   - **Table**: certificates
   - **Operation**: Insert
   - **enrollment_id**: `={{ $('Generar Certificado PDF').item.json.enrollment_id }}`
   - **certificate_content_b64**: `={{ $('Generar Certificado PDF').item.json.certificate_content_b64 }}`
   - **verification_code**: `={{ $('Generar Certificado PDF').item.json.verification_code }}`
   - **issue_date**: `={{ new Date().toISOString() }}`

**Nota:** El campo `certificate_url` puede ser NULL ya que el PDF está almacenado en base64.

#### Paso 5: AGREGAR Email de Notificación

1. **AGREGAR** nodo "Gmail" DESPUÉS de "Guardar Certificado"
2. Configurar:
   - **Nombre**: "Enviar Certificado por Email"
   - **To**: `={{ $('Generar Certificado PDF').item.json.student_email }}`
   - **Subject**: `¡Felicitaciones! Has completado {{ $('Generar Certificado PDF').item.json.course_name }}`
   - **Message**:

```
¡Felicitaciones {{ $('Generar Certificado PDF').item.json.student_name }}!

Has completado exitosamente el curso:
{{ $('Generar Certificado PDF').item.json.course_name }}

🎓 Tu certificado está listo para descargar.

Código de Verificación: {{ $('Generar Certificado PDF').item.json.verification_code }}

Puedes descargar tu certificado desde tu dashboard de estudiante en la plataforma.

Para verificar la autenticidad de tu certificado, usa el código de verificación en nuestra página de verificación.

¡Felicitaciones por tu logro!

Equipo de Cursos Online
```

**Nota:** El PDF está almacenado en base64 en la base de datos. El estudiante puede descargarlo desde su dashboard en la aplicación Streamlit.

---

## 🔧 Workflow 4: NUEVO - Procesamiento de Pagos

### Crear Nuevo Workflow

#### Paso 1: Crear Webhook

1. **AGREGAR** nodo "Webhook"
2. Configurar:
   - **Nombre**: "Webhook Pago"
   - **HTTP Method**: POST
   - **Path**: webhook-payment
   - **Response Mode**: Response Node

#### Paso 2: Validar Pago

1. **AGREGAR** nodo "Code"
2. Configurar:
   - **Nombre**: "Procesar Datos de Pago"
   - **Código**:

```javascript
const paymentData = $input.first().json.body.data;

// Validar datos requeridos
if (!paymentData.student_id || !paymentData.course_id || !paymentData.transaction_id) {
  throw new Error('Faltan datos requeridos del pago');
}

// Preparar registro de suscripción
const subscription = {
  student_id: paymentData.student_id,
  course_id: paymentData.course_id,
  amount_paid: paymentData.amount,
  payment_status: 'approved',
  subscription_start: new Date().toISOString(),
  subscription_end: null, // o calcular según duración del curso
  transaction_id: paymentData.transaction_id,
  payment_method: paymentData.payment_method
};

return [{ json: subscription }];
```

#### Paso 3: Guardar Suscripción

1. **AGREGAR** nodo "Supabase"
2. Configurar:
   - **Nombre**: "Guardar Suscripción"
   - **Operation**: Insert
   - **Table**: subscriptions
   - **Data**: Auto-map from input

#### Paso 4: Crear Inscripción Automática

1. **AGREGAR** nodo "Code"
2. Configurar:
   - **Nombre**: "Preparar Inscripción"
   - **Código**:

```javascript
const subscription = $input.first().json;

const enrollment = {
  student_id: subscription.student_id,
  course_id: subscription.course_id,
  enrollment_date: new Date().toISOString(),
  progress_percentage: 0,
  completion_status: 'in_progress'
};

return [{ json: enrollment }];
```

3. **AGREGAR** nodo "Supabase"
4. Configurar:
   - **Nombre**: "Crear Inscripción"
   - **Operation**: Insert
   - **Table**: enrollments

#### Paso 5: Enviar Confirmación

1. **AGREGAR** nodos para obtener datos del estudiante y curso (similar a workflow de inscripción)
2. **AGREGAR** nodo "Gmail" para enviar confirmación de pago e inscripción

---

## 🔧 Workflow 5: NUEVO - Verificación de Certificados

### Crear Nuevo Workflow

#### Paso 1: Crear Webhook

1. **AGREGAR** nodo "Webhook"
2. Configurar:
   - **Nombre**: "Webhook Verificación"
   - **HTTP Method**: GET
   - **Path**: verify-certificate/:code
   - **Response Mode**: Response Node

#### Paso 2: Buscar Certificado

1. **AGREGAR** nodo "Supabase"
2. Configurar:
   - **Nombre**: "Buscar Certificado"
   - **Operation**: Get
   - **Table**: certificates
   - **Filters**: verification_code = `={{ $('Webhook Verificación').item.json.params.code }}`

#### Paso 3: Validar Existencia

1. **AGREGAR** nodo "IF"
2. Configurar:
   - **Condition**: `={{ $json.length > 0 }}`
   - **True**: Continuar con obtención de datos
   - **False**: Retornar error 404

#### Paso 4: Obtener Datos Completos

1. **AGREGAR** nodos "Supabase" para obtener:
   - Enrollment
   - Student
   - Course

#### Paso 5: Retornar Respuesta

1. **AGREGAR** nodo "Response Node"
2. Configurar respuesta JSON con todos los datos del certificado

---

## ✅ Checklist de Verificación

Después de implementar todos los cambios:

### Workflow de Inscripción
- [ ] Validación de duplicados funciona
- [ ] Email de bienvenida se envía correctamente
- [ ] Datos se guardan en Supabase
- [ ] Manejo de errores implementado

### Workflow de Corrección de Exámenes
- [ ] Gemini retorna JSON válido
- [ ] Validación de JSON funciona
- [ ] Resultados se guardan correctamente
- [ ] Trigger de certificado funciona cuando corresponde

### Workflow de Certificados
- [ ] PDF se genera correctamente
- [ ] Código de verificación es único
- [ ] Certificado se guarda en BD
- [ ] Email de notificación se envía

### Workflow de Pagos
- [ ] Pago se registra en subscriptions
- [ ] Inscripción se crea automáticamente
- [ ] Email de confirmación se envía

### Workflow de Verificación
- [ ] Búsqueda por código funciona
- [ ] Retorna datos correctos
- [ ] Maneja certificados no encontrados

---

## 🔍 Testing

### Cómo Probar Cada Workflow

#### 1. Probar Inscripción
```bash
curl -X POST https://tu-n8n-url/webhook/webhook-enrollment \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_type": "enrollment",
    "data": {
      "student_id": "uuid-del-estudiante",
      "course_id": "uuid-del-curso"
    }
  }'
```

#### 2. Probar Corrección de Examen
```bash
curl -X POST https://tu-n8n-url/webhook/webhook-enrollment \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_type": "exam_correction",
    "data": {
      "student_id": "uuid-del-estudiante",
      "exam_id": "uuid-del-examen",
      "passing_score": 14,
      "submission": [
        {
          "question": "¿Cuál es la capital de Francia?",
          "correct_answer": "París",
          "student_answer": "París"
        }
      ]
    }
  }'
```

#### 3. Probar Generación de Certificado
```bash
curl -X POST https://tu-n8n-url/webhook/webhook-enrollment \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_type": "certificate_generation",
    "data": {
      "enrollment_id": "uuid-de-inscripcion",
      "student_id": "uuid-del-estudiante",
      "course_id": "uuid-del-curso"
    }
  }'
```

---

## 📝 Notas Importantes

> **IMPORTANTE**: Antes de hacer cambios en producción, prueba cada workflow en un entorno de desarrollo.

> **BACKUP**: Exporta tus workflows actuales antes de hacer modificaciones.

> **CREDENCIALES**: Asegúrate de que todas las credenciales (Supabase, Gmail, etc.) estén configuradas correctamente.

> **VARIABLES DE ENTORNO**: Configura las variables necesarias en n8n (URLs, tokens, etc.).

---

## 🆘 Solución de Problemas

### Error: "JSON parse error"
- Verifica que Gemini esté retornando JSON válido
- Revisa el nodo "Validar y Limpiar JSON"
- Chequea los logs de n8n para ver la respuesta exacta

### Error: "Duplicate key value"
- Asegúrate de que la validación de duplicados esté funcionando
- Verifica los filtros en las consultas de Supabase

### Error: "Permission denied"
- Revisa las políticas RLS en Supabase
- Verifica que las credenciales tengan los permisos necesarios

### Certificado no se genera
- Verifica que el endpoint de generación de PDF esté funcionando
- Chequea los logs del servidor de la aplicación
- Asegúrate de que todos los datos necesarios estén presentes

---

## 📚 Recursos Adicionales

- [Documentación de n8n](https://docs.n8n.io/)
- [Documentación de Supabase](https://supabase.com/docs)
- [API de Gemini](https://ai.google.dev/docs)

---

**Última actualización**: 2025-12-01
**Versión**: 1.0
