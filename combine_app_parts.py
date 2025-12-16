"""
Script para combinar todas las partes del app.py mejorado
Ejecutar este script para generar el app.py final
"""

import os

# Archivos a combinar en orden
parts = [
    'app_improved_part1.py',
    'app_improved_part2_admin.py',
    'app_improved_part3_teacher_student.py',
    'app_improved_part4_main.py'
]

output_file = 'app.py'
backup_file = 'app_backup_before_merge.py'

def combine_files():
    """Combina todos los archivos parte en un solo app.py"""
    
    # Hacer backup del app.py actual si existe
    if os.path.exists(output_file):
        print(f"📦 Creando backup: {backup_file}")
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    # Combinar archivos
    print("🔨 Combinando archivos...")
    combined_content = []
    
    for i, part_file in enumerate(parts):
        if not os.path.exists(part_file):
            print(f"❌ Error: No se encontró {part_file}")
            return False
        
        print(f"  ✓ Procesando {part_file}")
        
        with open(part_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remover docstrings de continuación (excepto el primero)
        if i > 0:
            # Remover las primeras líneas de docstring
            lines = content.split('\n')
            # Saltar las primeras líneas que son docstrings
            start_index = 0
            in_docstring = False
            for idx, line in enumerate(lines):
                if '"""' in line:
                    if not in_docstring:
                        in_docstring = True
                    else:
                        start_index = idx + 1
                        break
            
            content = '\n'.join(lines[start_index:])
        
        combined_content.append(content)
    
    # Escribir archivo combinado
    final_content = '\n\n'.join(combined_content)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    print(f"\n✅ Archivo combinado creado: {output_file}")
    print(f"📊 Tamaño: {len(final_content)} caracteres")
    print(f"📄 Líneas: {len(final_content.split(chr(10)))} líneas")
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Combinando partes de app.py mejorado")
    print("=" * 60)
    print()
    
    success = combine_files()
    
    if success:
        print("\n" + "=" * 60)
        print("✨ ¡Proceso completado exitosamente!")
        print("=" * 60)
        print("\n📝 Próximos pasos:")
        print("1. Revisa el archivo app.py generado")
        print("2. Instala dependencias: pip install -r requirements.txt")
        print("3. Configura secrets.toml con tus credenciales")
        print("4. Ejecuta: streamlit run app.py")
        print()
    else:
        print("\n❌ Error en el proceso de combinación")
