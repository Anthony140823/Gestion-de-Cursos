"""
Componentes de UI Reutilizables
Componentes visuales modernos para la aplicación
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Any, Optional
from datetime import datetime


def render_metric_card(title: str, value: str, delta: Optional[str] = None, icon: str = "📊"):
    """Renderiza una tarjeta de métrica con estilo"""
    delta_html = f"<p style='color: #28a745; font-size: 14px; margin: 5px 0 0 0;'>↑ {delta}</p>" if delta else ""
    
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px; border-radius: 15px; color: white;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;'>
        <div style='font-size: 36px; margin-bottom: 10px;'>{icon}</div>
        <h3 style='margin: 0; font-size: 16px; opacity: 0.9;'>{title}</h3>
        <p style='margin: 10px 0 0 0; font-size: 32px; font-weight: bold;'>{value}</p>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def render_course_card(course: Dict[str, Any], show_enroll_button: bool = False, on_click_key: str = None):
    """Renderiza una tarjeta de curso atractiva"""
    
    # Determinar color según precio
    if course.get('price', 0) == 0:
        price_color = "#28a745"
        price_text = "GRATIS"
    else:
        price_color = "#1f77b4"
        price_text = f"${course['price']:.2f}"
    
    # Botón de inscripción
    enroll_button = ""
    if show_enroll_button and on_click_key:
        enroll_button = f"""
        <div style='margin-top: 15px;'>
            <button style='background-color: #1f77b4; color: white; border: none;
                          padding: 10px 20px; border-radius: 5px; cursor: pointer;
                          width: 100%; font-weight: bold;'>
                📚 Inscribirse Ahora
            </button>
        </div>
        """
    
    st.markdown(f"""
    <div style='background-color: white; border-radius: 15px; padding: 20px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                border-left: 5px solid {price_color};'>
        <h3 style='color: #2c3e50; margin-top: 0;'>📚 {course['name']}</h3>
        <p style='color: #666; line-height: 1.6;'>{course.get('description', 'Sin descripción')}</p>
        
        <div style='display: flex; justify-content: space-between; align-items: center; margin-top: 15px;'>
            <div>
                <span style='background-color: #e3f2fd; color: #1976d2; padding: 5px 10px;
                            border-radius: 15px; font-size: 12px; font-weight: bold;'>
                    ⏱️ {course.get('duration_days', 0)} días
                </span>
            </div>
            <div>
                <span style='color: {price_color}; font-size: 24px; font-weight: bold;'>
                    {price_text}
                </span>
            </div>
        </div>
        {enroll_button}
    </div>
    """, unsafe_allow_html=True)


def render_progress_bar(progress: float, label: str = "", show_percentage: bool = True):
    """Renderiza una barra de progreso moderna"""
    
    # Determinar color según progreso
    if progress < 30:
        color = "#dc3545"
    elif progress < 70:
        color = "#ffc107"
    else:
        color = "#28a745"
    
    percentage_text = f"{progress:.0f}%" if show_percentage else ""
    
    st.markdown(f"""
    <div style='margin: 10px 0;'>
        <div style='display: flex; justify-content: space-between; margin-bottom: 5px;'>
            <span style='font-weight: bold; color: #2c3e50;'>{label}</span>
            <span style='color: {color}; font-weight: bold;'>{percentage_text}</span>
        </div>
        <div style='background-color: #e0e0e0; border-radius: 10px; height: 20px; overflow: hidden;'>
            <div style='background: linear-gradient(90deg, {color} 0%, {color}dd 100%);
                        width: {progress}%; height: 100%;
                        border-radius: 10px;
                        transition: width 0.5s ease;'>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_circular_progress(progress: float, size: int = 150, label: str = ""):
    """Renderiza un indicador de progreso circular"""
    
    fig = go.Figure(data=[go.Pie(
        values=[progress, 100 - progress],
        hole=0.7,
        marker=dict(colors=['#1f77b4', '#e0e0e0']),
        textinfo='none',
        hoverinfo='skip'
    )])
    
    fig.update_layout(
        showlegend=False,
        height=size,
        width=size,
        margin=dict(l=0, r=0, t=0, b=0),
        annotations=[dict(
            text=f"{progress:.0f}%<br>{label}",
            x=0.5, y=0.5,
            font_size=20,
            showarrow=False
        )]
    )
    
    st.plotly_chart(fig, use_container_width=False)


def render_status_badge(status: str):
    """Renderiza un badge de estado"""
    
    status_config = {
        'in_progress': {'color': '#ffc107', 'text': 'En Progreso', 'icon': '⏳'},
        'completed': {'color': '#28a745', 'text': 'Completado', 'icon': '✅'},
        'pending': {'color': '#6c757d', 'text': 'Pendiente', 'icon': '⏸️'},
        'approved': {'color': '#28a745', 'text': 'Aprobado', 'icon': '✅'},
        'rejected': {'color': '#dc3545', 'text': 'Rechazado', 'icon': '❌'},
        'graded': {'color': '#17a2b8', 'text': 'Calificado', 'icon': '📝'},
        'submitted': {'color': '#007bff', 'text': 'Enviado', 'icon': '📤'}
    }
    
    config = status_config.get(status, {'color': '#6c757d', 'text': status, 'icon': '❓'})
    
    st.markdown(f"""
    <span style='background-color: {config['color']}; color: white;
                padding: 5px 15px; border-radius: 15px;
                font-size: 12px; font-weight: bold;
                display: inline-block;'>
        {config['icon']} {config['text']}
    </span>
    """, unsafe_allow_html=True)


def render_alert(message: str, alert_type: str = "info"):
    """Renderiza una alerta con estilo"""
    
    alert_config = {
        'success': {'color': '#d4edda', 'border': '#c3e6cb', 'text_color': '#155724', 'icon': '✅'},
        'error': {'color': '#f8d7da', 'border': '#f5c6cb', 'text_color': '#721c24', 'icon': '❌'},
        'warning': {'color': '#fff3cd', 'border': '#ffeaa7', 'text_color': '#856404', 'icon': '⚠️'},
        'info': {'color': '#d1ecf1', 'border': '#bee5eb', 'text_color': '#0c5460', 'icon': 'ℹ️'}
    }
    
    config = alert_config.get(alert_type, alert_config['info'])
    
    st.markdown(f"""
    <div style='background-color: {config['color']}; border: 2px solid {config['border']};
                border-radius: 10px; padding: 15px; margin: 10px 0;
                color: {config['text_color']};'>
        <strong>{config['icon']} {message}</strong>
    </div>
    """, unsafe_allow_html=True)


def render_timeline_item(title: str, description: str, date: str, is_completed: bool = False):
    """Renderiza un item de timeline"""
    
    color = "#28a745" if is_completed else "#6c757d"
    icon = "✅" if is_completed else "⏳"
    
    st.markdown(f"""
    <div style='display: flex; margin: 20px 0;'>
        <div style='flex-shrink: 0; width: 40px; height: 40px;
                    background-color: {color}; border-radius: 50%;
                    display: flex; align-items: center; justify-content: center;
                    color: white; font-size: 20px;'>
            {icon}
        </div>
        <div style='margin-left: 20px; flex-grow: 1;'>
            <h4 style='margin: 0; color: #2c3e50;'>{title}</h4>
            <p style='margin: 5px 0; color: #666;'>{description}</p>
            <small style='color: #999;'>{date}</small>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_stat_card_row(stats: List[Dict[str, Any]]):
    """Renderiza una fila de tarjetas de estadísticas"""
    
    cols = st.columns(len(stats))
    
    for col, stat in zip(cols, stats):
        with col:
            render_metric_card(
                title=stat['title'],
                value=stat['value'],
                delta=stat.get('delta'),
                icon=stat.get('icon', '📊')
            )


def render_data_table(data: List[Dict[str, Any]], columns: List[str], title: str = ""):
    """Renderiza una tabla de datos con estilo"""
    
    if title:
        st.markdown(f"### {title}")
    
    if not data:
        render_alert("No hay datos para mostrar", "info")
        return
    
    # Crear tabla HTML
    header_html = "".join([f"<th style='background-color: #1f77b4; color: white; padding: 12px; text-align: left;'>{col}</th>" for col in columns])
    
    rows_html = ""
    for i, row in enumerate(data):
        bg_color = "#f8f9fa" if i % 2 == 0 else "white"
        cells = "".join([f"<td style='padding: 12px; border-bottom: 1px solid #dee2e6;'>{row.get(col, '')}</td>" for col in columns])
        rows_html += f"<tr style='background-color: {bg_color};'>{cells}</tr>"
    
    st.markdown(f"""
    <table style='width: 100%; border-collapse: collapse; border-radius: 10px; overflow: hidden;
                  box-shadow: 0 2px 10px rgba(0,0,0,0.1);'>
        <thead>
            <tr>{header_html}</tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
    """, unsafe_allow_html=True)


def render_exam_timer(time_remaining_seconds: int):
    """Renderiza un temporizador para exámenes"""
    
    minutes = time_remaining_seconds // 60
    seconds = time_remaining_seconds % 60
    
    # Determinar color según tiempo restante
    if time_remaining_seconds > 600:  # Más de 10 minutos
        color = "#28a745"
        bg_color = "#d4edda"
    elif time_remaining_seconds > 300:  # Más de 5 minutos
        color = "#ffc107"
        bg_color = "#fff3cd"
    else:  # Menos de 5 minutos
        color = "#dc3545"
        bg_color = "#f8d7da"
    
    st.markdown(f"""
    <div style='background-color: {bg_color}; border: 2px solid {color};
                border-radius: 10px; padding: 20px; text-align: center;
                margin: 20px 0;'>
        <h2 style='color: {color}; margin: 0; font-size: 48px; font-family: monospace;'>
            ⏱️ {minutes:02d}:{seconds:02d}
        </h2>
        <p style='color: {color}; margin: 10px 0 0 0; font-weight: bold;'>
            Tiempo Restante
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_file_upload_zone(label: str = "Arrastra archivos aquí o haz clic para seleccionar"):
    """Renderiza una zona de carga de archivos con estilo"""
    
    st.markdown(f"""
    <div style='border: 2px dashed #1f77b4; border-radius: 10px;
                padding: 40px; text-align: center; background-color: #f8f9fa;
                transition: all 0.3s ease;'>
        <div style='font-size: 48px; margin-bottom: 10px;'>📁</div>
        <p style='color: #666; margin: 0;'>{label}</p>
    </div>
    """, unsafe_allow_html=True)


def render_grade_display(score: float, max_score: float = 100, passing_score: float = 70):
    """Renderiza la visualización de una calificación"""
    
    percentage = (score / max_score) * 100 if max_score > 0 else 0
    passed = percentage >= passing_score
    
    color = "#28a745" if passed else "#dc3545"
    status_text = "APROBADO" if passed else "REPROBADO"
    icon = "✅" if passed else "❌"
    
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, {color} 0%, {color}dd 100%);
                padding: 30px; border-radius: 15px; color: white;
                text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.2);'>
        <h1 style='margin: 0; font-size: 72px;'>{icon}</h1>
        <h2 style='margin: 10px 0; font-size: 48px;'>{percentage:.1f}%</h2>
        <p style='margin: 0; font-size: 24px; font-weight: bold;'>{status_text}</p>
        <p style='margin: 10px 0 0 0; opacity: 0.9;'>
            Puntuación: {score:.1f} / {max_score:.1f}
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_empty_state(message: str, icon: str = "📭", action_text: str = None):
    """Renderiza un estado vacío"""
    
    action_html = f"<p style='margin-top: 20px;'><strong>{action_text}</strong></p>" if action_text else ""
    
    st.markdown(f"""
    <div style='text-align: center; padding: 60px 20px; color: #999;'>
        <div style='font-size: 72px; margin-bottom: 20px;'>{icon}</div>
        <h3 style='color: #666;'>{message}</h3>
        {action_html}
    </div>
    """, unsafe_allow_html=True)


# Función de prueba
if __name__ == "__main__":
    print("✅ Módulo de componentes UI cargado correctamente")
