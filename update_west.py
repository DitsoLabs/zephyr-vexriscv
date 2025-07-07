#!/usr/bin/env python3
"""
Script para sincronizar y actualizar módulos West
"""

import subprocess
import sys
import os

def run_cmd(cmd, check=True):
    """Ejecuta un comando y muestra el output en tiempo real"""
    print(f"🔧 Ejecutando: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=check)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🔄 Actualizando workspace West...")
    
    # Cambiar al directorio del workspace Zephyr si no estamos ahí
    zephyr_project = os.environ.get('ZEPHYR_BASE', '/home/fabian/zephyrproject')
    if os.path.exists(zephyr_project):
        os.chdir(zephyr_project)
        print(f"📁 Cambiando a: {zephyr_project}")
    
    # Actualizar todos los módulos
    if not run_cmd("west update"):
        print("❌ Error actualizando módulos")
        sys.exit(1)
    
    print("✅ Módulos actualizados")
    
    # Verificar boards disponibles
    print("\n📋 Verificando boards disponibles...")
    if run_cmd("west boards | grep -i tang", check=False):
        print("✅ Boards Tang encontrados")
    else:
        print("⚠️  No se encontraron boards Tang")
    
    # Intentar compilar un ejemplo simple
    print("\n🔨 Probando compilación...")
    test_cmd = "west build -p auto -b tang_nano_20k $ZEPHYR_BASE/samples/hello_world"
    if run_cmd(test_cmd, check=False):
        print("✅ Compilación exitosa!")
        print("\n🎉 Tu board tang_nano_20k está funcionando correctamente")
    else:
        print("❌ Error en compilación")
        print("Verifica la configuración del módulo")

if __name__ == "__main__":
    main()
