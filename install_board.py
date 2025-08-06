#!/usr/bin/env python3
"""
Automatically installs a Zephyr board from the local repository.
- Copies boards/vendor/board/
- Copies dts/*/board.dtsi if it exists
- If multiple boards are found, prompts the user to select one
- Detects Zephyr using 'west' or a full disk search
"""

import sys
import os
import shutil
import argparse
import subprocess
from pathlib import Path


def detect_zephyr_base() -> Path:
    # 1. Try using 'west list zephyr'
    try:
        result = subprocess.run("west list zephyr", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            zephyr_path = Path(result.stdout.strip().split()[-1]).resolve()
            if zephyr_path.exists():
                print(f"✅ Zephyr detected via 'west': {zephyr_path}")
                return zephyr_path
    except Exception:
        pass

    print("⚠️ 'west list zephyr' failed. Searching for Zephyr manually...")

    # 2. Search for Zephyr manually on the system
    candidates = []
    search_roots = [Path.home(), Path("/opt"), Path("/usr/local"), Path("/")]
    for root in search_roots:
        for path in root.rglob("zephyr"):
            try:
                if (path / "Kconfig").exists() and (path / "boards").exists():
                    candidates.append(path.resolve())
            except Exception:
                continue

    if not candidates:
        print("❌ No valid Zephyr installation found.")
        sys.exit(1)

    if len(candidates) == 1:
        print(f"✅ Zephyr found at: {candidates[0]}")
        return candidates[0]

    print("⚠️ Multiple Zephyr installations found:")
    for i, c in enumerate(candidates):
        print(f"  [{i+1}] {c}")

    try:
        index = int(input("Select an option (1, 2, ...): ").strip()) - 1
        return candidates[index]
    except Exception:
        print("❌ Invalid selection.")
        sys.exit(1)


def find_all_boards(module_path: Path):
    boards_path = module_path / "boards"
    boards = []
    for vendor_dir in boards_path.glob("*"):
        for board_dir in vendor_dir.glob("*"):
            if board_dir.is_dir():
                boards.append({
                    "vendor": vendor_dir.name,
                    "name": board_dir.name,
                    "path": board_dir
                })
    return boards


def find_dts_file(module_path: Path, board_name: str):
    dts_path = module_path / "dts"
    return next(dts_path.rglob(f"{board_name}.dtsi"), None)


def copy_board(board: dict, zephyr_path: Path):
    dst = zephyr_path / "boards" / board["vendor"] / board["name"]
    print(f"📁 Copying board: {board['path']} → {dst}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(board["path"], dst, dirs_exist_ok=True)
    print("✅ Board copied successfully.")


def copy_dts(dts_file: Path, zephyr_path: Path):
    relative_parts = dts_file.parts[-3:]  # e.g., dts/riscv/board.dtsi
    dst = zephyr_path / Path(*relative_parts)
    print(f"📁 Copying DTS: {dts_file} → {dst}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(dts_file, dst)
    print("✅ DTS copied successfully.")


def main():
    parser = argparse.ArgumentParser(description="Install a Zephyr board from your repo")
    parser.add_argument("-p", "--module-path", type=Path, default=Path(__file__).resolve().parent,
                        help="Path to the Zephyr module (default: script location)")
    parser.add_argument("-z", "--zephyr-path", type=Path,
                        help="Manual path to Zephyr base (auto-detected if omitted)")
    args = parser.parse_args()

    module_path = args.module_path.resolve()
    zephyr_path = args.zephyr_path.resolve() if args.zephyr_path else detect_zephyr_base()

    boards = find_all_boards(module_path)
    if not boards:
        print("❌ No boards found in 'boards/' directory.")
        sys.exit(1)

    if len(boards) > 1:
        print("⚠️ Multiple boards found:")
        for i, b in enumerate(boards):
            print(f"  [{i+1}] {b['name']} (vendor: {b['vendor']})")
        try:
            index = int(input("Select a board to install: ").strip()) - 1
            board = boards[index]
        except Exception:
            print("❌ Invalid selection.")
            sys.exit(1)
    else:
        board = boards[0]
        print(f"🔍 Automatically detected board: {board['name']} (vendor: {board['vendor']})")

    copy_board(board, zephyr_path)

    dts_file = find_dts_file(module_path, board["name"])
    if dts_file:
        copy_dts(dts_file, zephyr_path)
    else:
        print(f"⚠️ No DTS file found for board '{board['name']}'.")

    print("\n✅ Installation completed. You can now build with:")
    print(f"   west build -b {board['name']} samples/hello_world")


if __name__ == "__main__":
    main()
