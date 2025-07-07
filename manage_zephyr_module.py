#!/usr/bin/env python3
"""
Script to manage Zephyr modules with West.
Automates the addition and update of custom modules.
"""

import os
import sys
import subprocess
import yaml
import argparse
from pathlib import Path

# West command support
try:
    from west.commands import WestCommand
except ImportError:
    WestCommand = object

def run_command(cmd, check=True, capture_output=True):
    """Execute a command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, check=check, 
                              capture_output=capture_output, text=True)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {cmd}")
        print(f"Error: {e}")
        return None

def check_west_workspace():
    """Check if we're in a West workspace"""
    result = run_command("west list", check=False)
    return result is not None and result.returncode == 0

def get_zephyr_base():
    """Get the base path of Zephyr"""
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
    """Check if the module is already in the manifest"""
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
        print(f"Error reading manifest: {e}")
        return False

def add_module_to_manifest(module_name, module_path, zephyr_path, url=None):
    """Add a module to Zephyr's manifest"""
    manifest_path = zephyr_path / "west.yml"
    
    module_entry = {
        'name': module_name,
        'path': f'zephyr/modules/zephyr/{module_name}',
        'revision': 'main'
    }
    
    if url:
        module_entry['url'] = url
    else:
        module_entry['url'] = f'file://{module_path.absolute()}'
    
    print(f"Adding module {module_name} to manifest...")
    print(f"  Path: {module_entry['path']}")
    print(f"  URL: {module_entry['url']}")
    
    # For safety, we only show what should be added
    print("\nAdd this entry to Zephyr's west.yml:")
    print(f"    - name: {module_name}")
    print(f"      path: {module_entry['path']}")
    print(f"      revision: {module_entry['revision']}")
    print(f"      url: {module_entry['url']}")

def list_available_boards(module_path):
    """List available boards in the module"""
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
    """Test if a board can be built"""
    print(f"\nTesting build for board {board_name}...")
    
    test_dir = Path("/tmp/zephyr_board_test")
    test_dir.mkdir(exist_ok=True)
    
    os.chdir(test_dir)
    
    cmd = f"west build -p auto -b {board_name} $ZEPHYR_BASE/samples/{sample_app}"
    result = run_command(cmd, check=False)
    
    if result and result.returncode == 0:
        print(f"✅ Board {board_name} built successfully")
        return True
    else:
        print(f"❌ Error building board {board_name}")
        if result:
            print(f"Output: {result.stderr}")
        return False

class InstallBoards(WestCommand):
    def __init__(self):
        super().__init__(
            'install-boards',
            'Copy boards/dts from the module to the main Zephyr tree',
            '''
            west install-boards [--zephyr <zephyr_path>]
            By default, the Zephyr workspace root is detected automatically.
            '''
        )

    def do_add_parser(self, parser_adder):
        parser = self._parser = parser_adder.add_parser(
            self.name, help=self.help, description=self.description)
        parser.add_argument('--zephyr', required=False, help='Path to the Zephyr tree (optional)')
        return parser

    def do_run(self, args, unknown_args):
        import shutil
        src_root = Path(__file__).parent
        if args.zephyr:
            zephyr_root = Path(args.zephyr).resolve()
        else:
            result = run_command("west topdir")
            if result and result.returncode == 0:
                zephyr_root = (Path(result.stdout.strip()).resolve() / "zephyr")
            else:
                print("Could not detect the Zephyr workspace root. Use --zephyr <path>")
                return
        print(f"Copying boards and dts from {src_root} to {zephyr_root}")
        for subdir in ["boards", "dts"]:
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
                print(f"✅ Copied {subdir} to {dst}")
            else:
                print(f"⚠️  {src} does not exist, skipping")

def main():
    parser = argparse.ArgumentParser(description="Manage Zephyr modules with West")
    parser.add_argument("--module-path", "-p", type=Path, default=Path.cwd(),
                       help="Path to the module (default: current directory)")
    parser.add_argument("--module-name", "-n", default="zephyr-vexriscv",
                       help="Module name")
    parser.add_argument("--check", "-c", action="store_true",
                       help="Only check current status")
    parser.add_argument("--test-build", "-t", action="store_true",
                       help="Test board builds")
    parser.add_argument("--url", "-u", help="Module repository URL")
    
    args = parser.parse_args()
    
    print("🔧 Zephyr Module Manager")
    print("=" * 40)
    
    if not check_west_workspace():
        print("❌ No valid West workspace detected")
        print("Run this script from a properly initialized West workspace")
        sys.exit(1)
    
    print("✅ West workspace detected")
    
    zephyr_path = get_zephyr_base()
    if not zephyr_path:
        print("❌ Could not find Zephyr base path")
        sys.exit(1)
    
    print(f"✅ Zephyr found at: {zephyr_path}")
    
    module_path = args.module_path.resolve()
    module_yml = module_path / "module.yml"
    
    if not module_yml.exists():
        print(f"❌ module.yml not found in {module_path}")
        sys.exit(1)
    
    print(f"✅ Module found at: {module_path}")
    
    try:
        with open(module_yml, 'r') as f:
            module_info = yaml.safe_load(f)
        print(f"✅ Module: {module_info.get('name', 'unnamed')}")
    except Exception as e:
        print(f"❌ Error reading module.yml: {e}")
        sys.exit(1)
    
    is_in_manifest = check_module_in_manifest(args.module_name, zephyr_path)
    if is_in_manifest:
        print(f"✅ Module {args.module_name} is already in the manifest")
    else:
        print(f"⚠️  Module {args.module_name} is NOT in the manifest")
        if not args.check:
            add_module_to_manifest(args.module_name, module_path, zephyr_path, args.url)
    
    boards = list_available_boards(module_path)
    if boards:
        print(f"\n📋 Available boards ({len(boards)}):")
        for board in boards:
            print(f"  - {board['name']} (vendor: {board['vendor']})")
    else:
        print("\n⚠️  No boards found in module")
    
    if args.test_build and boards:
        print("\n🔨 Testing board builds...")
        for board in boards[:2]:  # Only test first 2
            test_board_build(board['name'])
    
    print("\n✅ Verification completed")
    
    if is_in_manifest:
        print(f"\n🎉 Your board is ready to use:")
        print(f"   west build -b tang_nano_20k")
        print(f"   (No need to use -DBOARD_ROOT)")

if __name__ == "__main__":
    main()
