"""
Simulador de Pasarela de Pagos
Simula un sistema de pagos para inscripciones de cursos
"""

import streamlit as st
import random
import time
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
import uuid


class PaymentSimulator:
    """Simulador de pasarela de pagos para cursos"""
    
    # Métodos de pago disponibles
    PAYMENT_METHODS = {
        'credit_card': {
            'name': '💳 Tarjeta de Crédito',
            'icon': '💳',
            'processing_time': 2,
            'success_rate': 0.95
        },
        'debit_card': {
            'name': '💳 Tarjeta de Débito',
            'icon': '💳',
            'processing_time': 2,
            'success_rate': 0.95
        },
        'paypal': {
            'name': '🅿️ PayPal',
            'icon': '🅿️',
            'processing_time': 1,
            'success_rate': 0.98
        },
        'bank_transfer': {
            'name': '🏦 Transferencia Bancaria',
            'icon': '🏦',
            'processing_time': 3,
            'success_rate': 0.90
        }
    }
    
    # Bancos simulados
    BANKS = [
        'Banco Continental',
        'Banco de Crédito',
        'Interbank',
        'Scotiabank',
        'BBVA'
    ]
    
    @staticmethod
    def generate_transaction_id() -> str:
        """Genera un ID de transacción único"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_part = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        return f"TXN-{timestamp}-{random_part}"
    
    @staticmethod
    def generate_authorization_code() -> str:
        """Genera un código de autorización"""
        return ''.join([str(random.randint(0, 9)) for _ in range(8)])
    
    @staticmethod
    def validate_card_number(card_number: str) -> Tuple[bool, str]:
        """
        Valida número de tarjeta (simulado)
        
        Returns:
            Tuple[bool, str]: (es_válido, mensaje)
        """
        # Remover espacios
        card_number = card_number.replace(' ', '').replace('-', '')
        
        # Verificar longitud
        if len(card_number) != 16:
            return False, "El número de tarjeta debe tener 16 dígitos"
        
        # Verificar que sean solo números
        if not card_number.isdigit():
            return False, "El número de tarjeta debe contener solo dígitos"
        
        # Simulación: tarjetas que empiezan con 4 son válidas (Visa)
        # Tarjetas que empiezan con 5 son válidas (Mastercard)
        if card_number[0] not in ['4', '5']:
            return False, "Número de tarjeta no válido"
        
        return True, "Tarjeta válida"
    
    @staticmethod
    def validate_cvv(cvv: str) -> Tuple[bool, str]:
        """Valida CVV"""
        if len(cvv) not in [3, 4]:
            return False, "El CVV debe tener 3 o 4 dígitos"
        
        if not cvv.isdigit():
            return False, "El CVV debe contener solo dígitos"
        
        return True, "CVV válido"
    
    @staticmethod
    def validate_expiry_date(month: str, year: str) -> Tuple[bool, str]:
        """Valida fecha de expiración"""
        try:
            month_int = int(month)
            year_int = int(year)
            
            if month_int < 1 or month_int > 12:
                return False, "Mes inválido"
            
            current_year = datetime.now().year % 100  # Últimos 2 dígitos
            current_month = datetime.now().month
            
            if year_int < current_year:
                return False, "Tarjeta expirada"
            
            if year_int == current_year and month_int < current_month:
                return False, "Tarjeta expirada"
            
            return True, "Fecha válida"
            
        except ValueError:
            return False, "Formato de fecha inválido"
    
    @staticmethod
    def process_payment(
        amount: float,
        payment_method: str,
        payment_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Procesa un pago simulado
        
        Args:
            amount: Monto a pagar
            payment_method: Método de pago
            payment_details: Detalles del pago
            
        Returns:
            Dict con resultado del pago
        """
        # Obtener configuración del método de pago
        method_config = PaymentSimulator.PAYMENT_METHODS.get(payment_method)
        
        if not method_config:
            return {
                'success': False,
                'message': 'Método de pago no válido',
                'transaction_id': None
            }
        
        # Simular tiempo de procesamiento
        processing_time = method_config['processing_time']
        
        # Simular procesamiento con barra de progreso
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i in range(100):
            time.sleep(processing_time / 100)
            progress_bar.progress(i + 1)
            
            if i < 30:
                status_text.text("🔄 Validando información...")
            elif i < 60:
                status_text.text("🔄 Procesando pago...")
            elif i < 90:
                status_text.text("🔄 Confirmando transacción...")
            else:
                status_text.text("✅ Finalizando...")
        
        progress_bar.empty()
        status_text.empty()
        
        # Simular éxito/fallo basado en tasa de éxito
        success = random.random() < method_config['success_rate']
        
        if success:
            transaction_id = PaymentSimulator.generate_transaction_id()
            auth_code = PaymentSimulator.generate_authorization_code()
            
            return {
                'success': True,
                'message': '¡Pago procesado exitosamente!',
                'transaction_id': transaction_id,
                'authorization_code': auth_code,
                'amount': amount,
                'payment_method': payment_method,
                'timestamp': datetime.now().isoformat(),
                'status': 'approved'
            }
        else:
            # Simular diferentes tipos de error
            error_messages = [
                'Fondos insuficientes',
                'Tarjeta rechazada por el banco',
                'Error de comunicación con el banco',
                'Transacción cancelada por seguridad'
            ]
            
            return {
                'success': False,
                'message': random.choice(error_messages),
                'transaction_id': None,
                'status': 'rejected'
            }


def show_payment_form(course_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Muestra el formulario de pago para un curso
    
    Args:
        course_data: Datos del curso a pagar
        
    Returns:
        Dict con resultado del pago o None si no se completó
    """
    st.markdown("### 💳 Información de Pago")
    
    # Mostrar resumen del curso
    with st.container():
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 20px; border-radius: 10px; color: white; margin-bottom: 20px;'>
            <h3 style='margin: 0; color: white;'>📚 {course_data['name']}</h3>
            <p style='margin: 10px 0 0 0; font-size: 24px; font-weight: bold;'>
                ${course_data['price']:.2f}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Seleccionar método de pago
    payment_method = st.selectbox(
        "Método de Pago",
        options=list(PaymentSimulator.PAYMENT_METHODS.keys()),
        format_func=lambda x: PaymentSimulator.PAYMENT_METHODS[x]['name']
    )
    
    payment_details = {}
    
    # Formulario según método de pago
    if payment_method in ['credit_card', 'debit_card']:
        st.markdown("#### Datos de la Tarjeta")
        
        col1, col2 = st.columns(2)
        with col1:
            card_holder = st.text_input("Titular de la Tarjeta", key="card_holder")
            card_number = st.text_input(
                "Número de Tarjeta",
                max_chars=19,
                placeholder="1234 5678 9012 3456",
                key="card_number"
            )
        
        with col2:
            col_month, col_year, col_cvv = st.columns(3)
            with col_month:
                expiry_month = st.text_input("Mes", max_chars=2, placeholder="MM", key="exp_month")
            with col_year:
                expiry_year = st.text_input("Año", max_chars=2, placeholder="YY", key="exp_year")
            with col_cvv:
                cvv = st.text_input("CVV", max_chars=4, type="password", key="cvv")
        
        payment_details = {
            'card_holder': card_holder,
            'card_number': card_number,
            'expiry_month': expiry_month,
            'expiry_year': expiry_year,
            'cvv': cvv
        }
        
        # Validaciones
        if st.button("💳 Procesar Pago", type="primary", use_container_width=True):
            # Validar campos
            if not all([card_holder, card_number, expiry_month, expiry_year, cvv]):
                st.error("❌ Por favor completa todos los campos")
                return None
            
            # Validar tarjeta
            valid_card, card_msg = PaymentSimulator.validate_card_number(card_number)
            if not valid_card:
                st.error(f"❌ {card_msg}")
                return None
            
            # Validar CVV
            valid_cvv, cvv_msg = PaymentSimulator.validate_cvv(cvv)
            if not valid_cvv:
                st.error(f"❌ {cvv_msg}")
                return None
            
            # Validar fecha
            valid_date, date_msg = PaymentSimulator.validate_expiry_date(expiry_month, expiry_year)
            if not valid_date:
                st.error(f"❌ {date_msg}")
                return None
            
            # Procesar pago
            result = PaymentSimulator.process_payment(
                amount=course_data['price'],
                payment_method=payment_method,
                payment_details=payment_details
            )
            
            return result
    
    elif payment_method == 'paypal':
        st.markdown("#### Cuenta PayPal")
        
        paypal_email = st.text_input("Email de PayPal", key="paypal_email")
        paypal_password = st.text_input("Contraseña", type="password", key="paypal_password")
        
        payment_details = {
            'email': paypal_email,
            'password': paypal_password
        }
        
        if st.button("🅿️ Pagar con PayPal", type="primary", use_container_width=True):
            if not all([paypal_email, paypal_password]):
                st.error("❌ Por favor completa todos los campos")
                return None
            
            result = PaymentSimulator.process_payment(
                amount=course_data['price'],
                payment_method=payment_method,
                payment_details=payment_details
            )
            
            return result
    
    elif payment_method == 'bank_transfer':
        st.markdown("#### Transferencia Bancaria")
        
        bank = st.selectbox("Banco", PaymentSimulator.BANKS, key="bank")
        account_number = st.text_input("Número de Cuenta", key="account_number")
        
        payment_details = {
            'bank': bank,
            'account_number': account_number
        }
        
        if st.button("🏦 Realizar Transferencia", type="primary", use_container_width=True):
            if not all([bank, account_number]):
                st.error("❌ Por favor completa todos los campos")
                return None
            
            result = PaymentSimulator.process_payment(
                amount=course_data['price'],
                payment_method=payment_method,
                payment_details=payment_details
            )
            
            return result
    
    return None


def show_payment_success(payment_result: Dict[str, Any], course_data: Dict[str, Any]):
    """Muestra mensaje de pago exitoso"""
    st.success("✅ ¡Pago procesado exitosamente!")
    
    st.markdown(f"""
    <div style='background-color: #d4edda; border: 2px solid #c3e6cb; 
                border-radius: 10px; padding: 20px; margin: 20px 0;'>
        <h3 style='color: #155724; margin-top: 0;'>✅ Confirmación de Pago</h3>
        <p><strong>Curso:</strong> {course_data['name']}</p>
        <p><strong>Monto:</strong> ${payment_result['amount']:.2f}</p>
        <p><strong>ID de Transacción:</strong> {payment_result['transaction_id']}</p>
        <p><strong>Código de Autorización:</strong> {payment_result['authorization_code']}</p>
        <p><strong>Fecha:</strong> {datetime.fromisoformat(payment_result['timestamp']).strftime('%d/%m/%Y %H:%M:%S')}</p>
        <p><strong>Estado:</strong> <span style='color: #28a745; font-weight: bold;'>APROBADO</span></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.balloons()


def show_payment_failure(payment_result: Dict[str, Any]):
    """Muestra mensaje de pago fallido"""
    st.error(f"❌ {payment_result['message']}")
    
    st.markdown("""
    <div style='background-color: #f8d7da; border: 2px solid #f5c6cb; 
                border-radius: 10px; padding: 20px; margin: 20px 0;'>
        <h3 style='color: #721c24; margin-top: 0;'>❌ Pago Rechazado</h3>
        <p>Tu pago no pudo ser procesado. Por favor:</p>
        <ul>
            <li>Verifica que los datos ingresados sean correctos</li>
            <li>Asegúrate de tener fondos suficientes</li>
            <li>Contacta a tu banco si el problema persiste</li>
            <li>Intenta con otro método de pago</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)


# Función de prueba
if __name__ == "__main__":
    print("✅ Módulo de simulación de pagos cargado correctamente")
    
    # Prueba de validación de tarjeta
    valid, msg = PaymentSimulator.validate_card_number("4532015112830366")
    print(f"Validación de tarjeta: {valid} - {msg}")
    
    # Prueba de generación de ID
    txn_id = PaymentSimulator.generate_transaction_id()
    print(f"ID de transacción generado: {txn_id}")
