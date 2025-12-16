"""
Generador de Certificados con PDF
Genera certificados profesionales en PDF con código QR de verificación
"""

import io
import qrcode
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.utils import ImageReader
from datetime import datetime
import base64
from typing import Optional, Dict, Any


class CertificateGenerator:
    """Generador de certificados en PDF con diseño profesional"""
    
    def __init__(self):
        self.page_width, self.page_height = A4
        self.margin = 0.75 * inch
        
    def generate_qr_code(self, verification_code: str) -> ImageReader:
        """Genera código QR para verificación del certificado"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        
        # URL de verificación (ajustar según tu dominio)
        verification_url = f"https://tu-dominio.com/verify/{verification_code}"
        qr.add_data(verification_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir a ImageReader
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        return ImageReader(img_buffer)
    
    def draw_border(self, c: canvas.Canvas):
        """Dibuja un borde decorativo en el certificado"""
        # Borde exterior
        c.setStrokeColor(HexColor('#1f77b4'))
        c.setLineWidth(3)
        c.rect(
            self.margin - 10,
            self.margin - 10,
            self.page_width - 2 * (self.margin - 10),
            self.page_height - 2 * (self.margin - 10)
        )
        
        # Borde interior
        c.setStrokeColor(HexColor('#4a90e2'))
        c.setLineWidth(1)
        c.rect(
            self.margin,
            self.margin,
            self.page_width - 2 * self.margin,
            self.page_height - 2 * self.margin
        )
    
    def draw_header(self, c: canvas.Canvas):
        """Dibuja el encabezado del certificado"""
        # Título principal
        c.setFont("Helvetica-Bold", 36)
        c.setFillColor(HexColor('#1f77b4'))
        title = "CERTIFICADO DE FINALIZACIÓN"
        title_width = c.stringWidth(title, "Helvetica-Bold", 36)
        c.drawString(
            (self.page_width - title_width) / 2,
            self.page_height - 2 * inch,
            title
        )
        
        # Subtítulo
        c.setFont("Helvetica", 14)
        c.setFillColor(HexColor('#666666'))
        subtitle = "Este documento certifica que"
        subtitle_width = c.stringWidth(subtitle, "Helvetica", 14)
        c.drawString(
            (self.page_width - subtitle_width) / 2,
            self.page_height - 2.5 * inch,
            subtitle
        )
    
    def draw_student_name(self, c: canvas.Canvas, student_name: str):
        """Dibuja el nombre del estudiante"""
        c.setFont("Helvetica-Bold", 28)
        c.setFillColor(HexColor('#2c3e50'))
        name_width = c.stringWidth(student_name, "Helvetica-Bold", 28)
        c.drawString(
            (self.page_width - name_width) / 2,
            self.page_height - 3.5 * inch,
            student_name
        )
        
        # Línea decorativa bajo el nombre
        c.setStrokeColor(HexColor('#1f77b4'))
        c.setLineWidth(2)
        line_start = (self.page_width - name_width) / 2 - 20
        line_end = (self.page_width + name_width) / 2 + 20
        c.line(
            line_start,
            self.page_height - 3.7 * inch,
            line_end,
            self.page_height - 3.7 * inch
        )
    
    def draw_course_info(self, c: canvas.Canvas, course_name: str, completion_date: str):
        """Dibuja información del curso"""
        c.setFont("Helvetica", 14)
        c.setFillColor(HexColor('#666666'))
        
        # Texto de completación
        text1 = "ha completado satisfactoriamente el curso"
        text1_width = c.stringWidth(text1, "Helvetica", 14)
        c.drawString(
            (self.page_width - text1_width) / 2,
            self.page_height - 4.3 * inch,
            text1
        )
        
        # Nombre del curso
        c.setFont("Helvetica-Bold", 18)
        c.setFillColor(HexColor('#1f77b4'))
        course_width = c.stringWidth(course_name, "Helvetica-Bold", 18)
        c.drawString(
            (self.page_width - course_width) / 2,
            self.page_height - 4.8 * inch,
            course_name
        )
        
        # Fecha de completación
        c.setFont("Helvetica", 12)
        c.setFillColor(HexColor('#666666'))
        date_text = f"Fecha de finalización: {completion_date}"
        date_width = c.stringWidth(date_text, "Helvetica", 12)
        c.drawString(
            (self.page_width - date_width) / 2,
            self.page_height - 5.3 * inch,
            date_text
        )
    
    def draw_verification_section(self, c: canvas.Canvas, verification_code: str, qr_image: ImageReader):
        """Dibuja la sección de verificación con QR"""
        # Código QR
        qr_size = 1.2 * inch
        qr_x = self.page_width - self.margin - qr_size - 20
        qr_y = self.margin + 20
        
        c.drawImage(
            qr_image,
            qr_x,
            qr_y,
            width=qr_size,
            height=qr_size
        )
        
        # Texto de verificación
        c.setFont("Helvetica", 8)
        c.setFillColor(HexColor('#666666'))
        verify_text = "Escanea para verificar"
        verify_width = c.stringWidth(verify_text, "Helvetica", 8)
        c.drawString(
            qr_x + (qr_size - verify_width) / 2,
            qr_y - 15,
            verify_text
        )
        
        # Código de verificación
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(HexColor('#1f77b4'))
        code_text = f"Código: {verification_code}"
        c.drawString(
            self.margin + 20,
            self.margin + 20,
            code_text
        )
    
    def draw_signatures(self, c: canvas.Canvas):
        """Dibuja las líneas de firma"""
        y_position = self.page_height - 7 * inch
        
        # Firma izquierda (Director)
        left_x = self.page_width / 4
        c.setStrokeColor(black)
        c.setLineWidth(1)
        c.line(left_x - 80, y_position, left_x + 80, y_position)
        
        c.setFont("Helvetica", 10)
        c.setFillColor(black)
        director_text = "Director Académico"
        director_width = c.stringWidth(director_text, "Helvetica", 10)
        c.drawString(left_x - director_width / 2, y_position - 20, director_text)
        
        # Firma derecha (Instructor)
        right_x = 3 * self.page_width / 4
        c.line(right_x - 80, y_position, right_x + 80, y_position)
        
        instructor_text = "Instructor del Curso"
        instructor_width = c.stringWidth(instructor_text, "Helvetica", 10)
        c.drawString(right_x - instructor_width / 2, y_position - 20, instructor_text)
    
    def generate_certificate(
        self,
        student_name: str,
        course_name: str,
        completion_date: str,
        verification_code: str
    ) -> bytes:
        """
        Genera el certificado completo en PDF
        
        Args:
            student_name: Nombre completo del estudiante
            course_name: Nombre del curso
            completion_date: Fecha de completación (formato: DD/MM/YYYY)
            verification_code: Código único de verificación
            
        Returns:
            bytes: PDF generado como bytes
        """
        # Crear buffer para el PDF
        buffer = io.BytesIO()
        
        # Crear canvas
        c = canvas.Canvas(buffer, pagesize=A4)
        
        # Generar código QR
        qr_image = self.generate_qr_code(verification_code)
        
        # Dibujar elementos del certificado
        self.draw_border(c)
        self.draw_header(c)
        self.draw_student_name(c, student_name)
        self.draw_course_info(c, course_name, completion_date)
        self.draw_signatures(c)
        self.draw_verification_section(c, verification_code, qr_image)
        
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
        
        # Obtener bytes del PDF
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_certificate_base64(
        self,
        student_name: str,
        course_name: str,
        completion_date: str,
        verification_code: str
    ) -> str:
        """
        Genera el certificado y lo retorna como string base64
        
        Returns:
            str: PDF en formato base64
        """
        pdf_bytes = self.generate_certificate(
            student_name,
            course_name,
            completion_date,
            verification_code
        )
        return base64.b64encode(pdf_bytes).decode('utf-8')


def create_certificate_for_enrollment(
    enrollment_data: Dict[str, Any],
    student_data: Dict[str, Any],
    course_data: Dict[str, Any],
    verification_code: str
) -> str:
    """
    Función helper para crear certificado desde datos de inscripción
    
    Args:
        enrollment_data: Datos de la inscripción
        student_data: Datos del estudiante
        course_data: Datos del curso
        verification_code: Código de verificación único
        
    Returns:
        str: PDF en base64
    """
    generator = CertificateGenerator()
    
    student_name = f"{student_data['first_name']} {student_data['last_name']}"
    course_name = course_data['name']
    
    # Formatear fecha
    completion_date = datetime.now().strftime("%d/%m/%Y")
    
    return generator.generate_certificate_base64(
        student_name=student_name,
        course_name=course_name,
        completion_date=completion_date,
        verification_code=verification_code
    )


# Función de prueba
if __name__ == "__main__":
    # Prueba de generación de certificado
    generator = CertificateGenerator()
    
    pdf_bytes = generator.generate_certificate(
        student_name="Juan Pérez García",
        course_name="Desarrollo Web Full Stack con Python",
        completion_date="01/12/2025",
        verification_code="CERT-2025-ABC123XYZ"
    )
    
    # Guardar para prueba
    with open("certificado_prueba.pdf", "wb") as f:
        f.write(pdf_bytes)
    
    print("✅ Certificado de prueba generado: certificado_prueba.pdf")
