#!/usr/bin/env python3
"""
Script para gestionar módulos Zephyr con West
Automatiza la adición y actualización de módulos personalizados
"""

import os
import sys
import subprocess
import yaml
import argparse
from pathlib import Path

# Soporte para comando west
try:
    from west.commands import WestCommand
except ImportError:
    WestCommand = object

def run_command(cmd, check=True, capture_output=True):
    """Ejecuta un comando y retorna el resultado"""
    try:
        result = subprocess.run(cmd, shell=True, check=check, 
                              capture_output=capture_output, text=True)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error ejecutando comando: {cmd}")
        print(f"Error: {e}")
        return None

def check_west_workspace():
    """Verifica si estamos en un workspace de West"""
    result = run_command("west list", check=False)
    return result is not None and result.returncode == 0

def get_zephyr_base():
    """Obtiene la ruta base de Zephyr"""
    result = run_command("west list zephyr")
    if result and result.returncode == 0:
        lines = result.stdout.strip().split('\n')
        for line in lines:
            if 'zephyr' in line:
                parts = line.split()
                if len(parts) >= 2:
                    return Path.cwd() / parts[1]  # path column
    return None

def check_module_in_manifest(module_name, zephyr_path):
    """Verifica si el módulo ya está en el manifest"""
    manifest_path = zephyr_path / "west.yml"
    if not manifest_path.exists():
        return False
    
    try:
        with open(manifest_path, 'r') as f:
            manifest = yaml.safe_load(f)
        
        projects = manifest.get('manifest', {}).get('projects', [])
        for project in projects:
            if project.get('name') == module_name:
                return True
        return False
    except Exception as e:
        print(f"Error leyendo manifest: {e}")
        return False

def add_module_to_manifest(module_name, module_path, zephyr_path, url=None):
    """Agrega un módulo al manifest de Zephyr"""
    manifest_path = zephyr_path / "west.yml"
    
    # Crear entrada del módulo
    module_entry = {
        'name': module_name,
        'path': f'zephyr/modules/zephyr/{module_name}',
        'revision': 'main'
    }
    
    if url:
        module_entry['url'] = url
    else:
        module_entry['url'] = f'file://{module_path.absolute()}'
    
    print(f"Agregando módulo {module_name} al manifest...")
    print(f"  Path: {module_entry['path']}")
    print(f"  URL: {module_entry['url']}")
    
    # Aquí podrías modificar el west.yml programáticamente
    # Por seguridad, solo mostramos lo que se agregaría
    print("\nAgrega esta entrada al west.yml de Zephyr:")
    print(f"    - name: {module_name}")
    print(f"      path: {module_entry['path']}")
    print(f"      revision: {module_entry['revision']}")
    print(f"      url: {module_entry['url']}")

def list_available_boards(module_path):
    """Lista los boards disponibles en el módulo"""
    boards_path = module_path / "boards"
    if not boards_path.exists():
        return []
    
    boards = []
    for vendor_dir in boards_path.iterdir():
        if vendor_dir.is_dir():
            for board_dir in vendor_dir.iterdir():
                if board_dir.is_dir():
                    board_yml = board_dir / "board.yml"
                    if board_yml.exists():
                        try:
                            with open(board_yml, 'r') as f:
                                board_info = yaml.safe_load(f)
                            board_name = board_info.get('board', {}).get('name', board_dir.name)
                            boards.append({
                                'name': board_name,
                                'path': str(board_dir),
                                'vendor': vendor_dir.name
                            })
                        except Exception:
                            boards.append({
                                'name': board_dir.name,
                                'path': str(board_dir),
                                'vendor': vendor_dir.name
                            })
    return boards

def test_board_build(board_name, sample_app="hello_world"):
    """Prueba si el board se puede compilar"""
    print(f"\nProbando compilación con board {board_name}...")
    
    # Crear directorio temporal para la prueba
    test_dir = Path("/tmp/zephyr_board_test")
    test_dir.mkdir(exist_ok=True)
    
    os.chdir(test_dir)
    
    # Intentar compilar un sample
    cmd = f"west build -p auto -b {board_name} $ZEPHYR_BASE/samples/{sample_app}"
    result = run_command(cmd, check=False)
    
    if result and result.returncode == 0:
        print(f"✅ Board {board_name} compila correctamente")
        return True
    else:
        print(f"❌ Error compilando board {board_name}")
        if result:
            print(f"Output: {result.stderr}")
        return False

class InstallBoards(WestCommand):
    def __init__(self):
        super().__init__(
            'install-boards',
            'Copia boards/dts/soc desde el módulo a Zephyr (árbol principal)',
            '''
            west install-boards [--zephyr <ruta_zephyr>]
            Por defecto detecta la ruta de Zephyr automáticamente.
            '''
        )

    def do_add_parser(self, parser_adder):
        parser = self._parser = parser_adder.add_parser(
            self.name, help=self.help, description=self.description)
        parser.add_argument('--zephyr', required=False, help='Ruta al árbol Zephyr (opcional)')
        return parser

    def do_run(self, args, unknown_args):
        import shutil
        src_root = Path(__file__).parent
        if args.zephyr:
            zephyr_root = Path(args.zephyr).resolve()
        else:
            # Detectar automáticamente usando west list zephyr
            result = run_command("west list zephyr")
            if result and result.returncode == 0:
                zephyr_path = result.stdout.strip().split()[-1]
                zephyr_root = Path(zephyr_path).resolve()
            else:
                print("No se pudo detectar la ruta de Zephyr. Usa --zephyr <ruta>")
                return
        print(f"Copiando boards, dts y soc desde {src_root} a {zephyr_root}")
        for subdir in ["boards", "dts", "soc"]:
            src = src_root / subdir
            dst = zephyr_root / subdir
            if src.exists():
                if not dst.exists():
                    dst.mkdir(parents=True)
                for item in src.iterdir():
                    dest_item = dst / item.name
                    if item.is_dir():
                        shutil.copytree(item, dest_item, dirs_exist_ok=True)
                    else:
                        shutil.copy2(item, dest_item)
                print(f"✅ Copiado {subdir} a {dst}")
            else:
                print(f"⚠️  No existe {src}, se omite")

def main():
    parser = argparse.ArgumentParser(description="Gestionar módulos Zephyr con West")
    parser.add_argument("--module-path", "-p", type=Path, default=Path.cwd(),
                       help="Ruta al módulo (default: directorio actual)")
    parser.add_argument("--module-name", "-n", default="zephyr-vexriscv",
                       help="Nombre del módulo")
    parser.add_argument("--check", "-c", action="store_true",
                       help="Solo verificar el estado actual")
    parser.add_argument("--test-build", "-t", action="store_true",
                       help="Probar compilación de los boards")
    parser.add_argument("--url", "-u", help="URL del repositorio del módulo")
    
    args = parser.parse_args()
    
    print("🔧 Gestor de módulos Zephyr")
    print("=" * 40)
    
    # Verificar workspace de West
    if not check_west_workspace():
        print("❌ No se detectó un workspace de West válido")
        print("Ejecuta este script desde un workspace de West inicializado")
        sys.exit(1)
    
    print("✅ Workspace de West detectado")
    
    # Obtener ruta de Zephyr
    zephyr_path = get_zephyr_base()
    if not zephyr_path:
        print("❌ No se pudo encontrar la ruta de Zephyr")
        sys.exit(1)
    
    print(f"✅ Zephyr encontrado en: {zephyr_path}")
    
    # Verificar módulo
    module_path = args.module_path.resolve()
    module_yml = module_path / "module.yml"
    
    if not module_yml.exists():
        print(f"❌ No se encontró module.yml en {module_path}")
        sys.exit(1)
    
    print(f"✅ Módulo encontrado en: {module_path}")
    
    # Leer información del módulo
    try:
        with open(module_yml, 'r') as f:
            module_info = yaml.safe_load(f)
        print(f"✅ Módulo: {module_info.get('name', 'sin nombre')}")
    except Exception as e:
        print(f"❌ Error leyendo module.yml: {e}")
        sys.exit(1)
    
    # Verificar si ya está en el manifest
    is_in_manifest = check_module_in_manifest(args.module_name, zephyr_path)
    if is_in_manifest:
        print(f"✅ Módulo {args.module_name} ya está en el manifest")
    else:
        print(f"⚠️  Módulo {args.module_name} NO está en el manifest")
        if not args.check:
            add_module_to_manifest(args.module_name, module_path, zephyr_path, args.url)
    
    # Listar boards disponibles
    boards = list_available_boards(module_path)
    if boards:
        print(f"\n📋 Boards disponibles ({len(boards)}):")
        for board in boards:
            print(f"  - {board['name']} (vendor: {board['vendor']})")
    else:
        print("\n⚠️  No se encontraron boards en el módulo")
    
    # Probar compilación si se solicita
    if args.test_build and boards:
        print("\n🔨 Probando compilación de boards...")
        for board in boards[:2]:  # Solo probar los primeros 2
            test_board_build(board['name'])
    
    print("\n✅ Verificación completada")
    
    if is_in_manifest:
        print(f"\n🎉 Tu board está listo para usar:")
        print(f"   west build -b tang_nano_20k")
        print(f"   (No necesitas -DBOARD_ROOT)")

if __name__ == "__main__":
    main()
