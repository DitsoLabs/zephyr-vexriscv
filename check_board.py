#!/usr/bin/env python3
"""
Script simple para verificar si tu board está disponible en West
"""

import subprocess
import sys

def run_cmd(cmd):
    """Ejecuta un comando y retorna el output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return None

def main():
    print("🔍 Verificando disponibilidad de Tang Nano 20K...")
    
    # Verificar si West está disponible
    if not run_cmd("which west"):
        print("❌ West no está instalado o no está en PATH")
        sys.exit(1)
    
    # Verificar workspace
    if not run_cmd("west list"):
        print("❌ No estás en un workspace de West")
        sys.exit(1)
    
    print("✅ West workspace detectado")
    
    # Verificar si el board está disponible
    boards_output = run_cmd("west boards")
    if boards_output and "tang_nano_20k" in boards_output:
        print("✅ Board tang_nano_20k está disponible")
        print("\n🎉 Puedes compilar con:")
        print("   west build -b tang_nano_20k")
        print("   (Sin necesidad de -DBOARD_ROOT)")
    else:
        print("❌ Board tang_nano_20k NO está disponible")
        print("\n🔧 Posibles soluciones:")
        print("1. Verificar que el módulo esté en west.yml")
        print("2. Ejecutar: west update")
        print("3. Usar -DBOARD_ROOT si no está como módulo")
    
    # Mostrar todos los boards disponibles que contengan "tang" o "nano"
    print("\n📋 Boards relacionados encontrados:")
    if boards_output:
        for line in boards_output.split('\n'):
            if 'tang' in line.lower() or 'nano' in line.lower():
                print(f"  {line}")

if __name__ == "__main__":
    main()
