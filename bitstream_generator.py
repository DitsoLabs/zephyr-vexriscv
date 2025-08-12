#!/usr/bin/env python3
#
# Copyright (c) 2025, Fabian Alvarez [SantaCRC] (contact@fabianalvarez.dev)
#
"""
CLI tool to build and load the SoC on the Tang Nano 20K.
Exposes arguments for selecting `device`, `variant`, `toolchain`, UART baudrate, build actions
(`--build`, `--load`, `--flash`), and network/TFTP, SPI, and RootFS settings.
Example:
    python make.py --toolchain gowin --build --load --uart-baudrate 115200
"""
import logging
import os
import re
import argparse
import shutil
from litex.soc.integration.builder import Builder
from litex.soc.cores.cpu.vexriscv_smp import VexRiscvSMP
from litepcie.software import generate_litepcie_software
from misc.boards import Board
from misc.soc_linux import SoCLinux

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# -------------------------------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------------------------------

def camel_to_snake(name):
    """Convert CamelCase to snake_case."""
    name = re.sub(r'(?<=[a-z])(?=[A-Z])', '_', name)
    return name.lower()

def get_board():
    """Discover available board classes."""
    board_classes_local = {}
    for obj_name, obj in globals().items():
        snake_name = camel_to_snake(obj_name)
        if isinstance(obj, type) and issubclass(obj, Board) and obj is not Board:
            board_classes_local[snake_name] = obj
    return board_classes_local

board_classes = get_board()

# -------------------------------------------------------------------------------------------------
# Build
# -------------------------------------------------------------------------------------------------

def log_soc_constants(constants, build_dir):
    """Log SoC constants to file."""
    for key, value in constants.items():
        with open(os.path.join(build_dir, "logs", "soc_constants.log"), "a", encoding="utf-8") as file:
            file.write(f"{key}: {value}\n")

def add_optional_interfaces(soc, board, args):
    """Add optional interfaces based on board capabilities."""
    if "spisdcard" in board.soc_capabilities:
        soc.add_spi_sdcard()
    if "sdcard" in board.soc_capabilities:
        soc.add_sdcard()
    if "ethernet" in board.soc_capabilities:
        soc.configure_ethernet(remote_ip=args.remote_ip)
    if "rgb_led" in board.soc_capabilities:
        soc.add_rgb_led()
    if "switches" in board.soc_capabilities:
        soc.add_switches()
    if "spi" in board.soc_capabilities:
        soc.add_spi(args.spi_data_width, args.spi_clk_freq)
    if "i2c" in board.soc_capabilities:
        soc.add_i2c()

def setup_soc(board, args):
    """Setup SoC and board parameters."""
    soc_kwargs = Board.soc_kwargs.copy()
    if args.with_wishbone_memory:
        soc_kwargs["l2_size"] = max(soc_kwargs.get("l2_size", 0), 2048)
    else:
        args.with_wishbone_memory = soc_kwargs.get("l2_size", 0) != 0
    if "usb_host" in board.soc_capabilities:
        args.with_coherent_dma = True
    VexRiscvSMP.args_read(args)
    if args.device is not None:
        soc_kwargs["device"] = args.device
    if args.variant is not None:
        soc_kwargs["variant"] = args.variant
    if args.toolchain is not None:
        soc_kwargs["toolchain"] = args.toolchain
    soc_kwargs["uart_baudrate"] = int(args.uart_baudrate)
    if "crossover" in board.soc_capabilities:
        soc_kwargs["uart_name"] = "crossover"
    if "usb_fifo" in board.soc_capabilities:
        soc_kwargs["uart_name"] = "usb_fifo"
    if "usb_acm" in board.soc_capabilities:
        soc_kwargs["uart_name"] = "usb_acm"
    if "leds" in board.soc_capabilities:
        soc_kwargs["with_led_chaser"] = True
    if "ethernet" in board.soc_capabilities:
        soc_kwargs["with_ethernet"] = True
    if "pcie" in board.soc_capabilities:
        soc_kwargs["with_pcie"] = True
    if "spiflash" in board.soc_capabilities:
        soc_kwargs["with_spi_flash"] = True
    if "sata" in board.soc_capabilities:
        soc_kwargs["with_sata"] = True
    if "video_terminal" in board.soc_capabilities:
        soc_kwargs["with_video_terminal"] = True
    if "framebuffer" in board.soc_capabilities:
        soc_kwargs["with_video_framebuffer"] = True
    if "usb_host" in board.soc_capabilities:
        soc_kwargs["with_usb_host"] = True
    if "ps_ddr" in board.soc_capabilities:
        soc_kwargs["with_ps_ddr"] = True
    soc = SoCLinux(board.soc_cls, **soc_kwargs)
    board.platform = soc.platform
    for key, value in board.soc_constants.items():
        soc.add_constant(key, value)
    identifier = {
        "sipeed_tang_nano_20k": "Sipeed Tang Nano 20K Linux SoC by Fabian Alvarez (SantaCRC)"
    }
    soc.constants['CONFIG_IDENTIFIER'] = identifier["sipeed_tang_nano_20k"]
    return soc

def build_and_generate(soc, board_name, args):
    """Build SoC, generate device tree, boot config, PCIe driver, and docs."""
    build_dir = os.path.join("build", board_name)
    os.makedirs(os.path.join(build_dir, "logs"), exist_ok=True)
    log_soc_constants(soc.constants, build_dir)
    builder = Builder(
        soc,
        output_dir=build_dir,
        bios_console="lite",
        csr_json=os.path.join(build_dir, "csr.json"),
        csr_csv=os.path.join(build_dir, "csr.csv")
    )
    builder.build(run=args.build, build_name=board_name)
    soc.generate_dts(board_name, args.rootfs)
    soc.compile_dts(board_name, args.fdtoverlays)
    soc.combine_dtb(board_name, args.fdtoverlays)
    shutil.copyfile(
        f"software/boot_{args.rootfs}.json", "software/boot.json"
    )
    if "pcie" in soc.constants.get('CONFIG_IDENTIFIER', ''):
        generate_litepcie_software(soc, os.path.join(builder.output_dir, "driver"))
    if args.load:
        board = board_classes[board_name]()
        board.load(filename=builder.get_bitstream_filename(mode="sram"))
    if args.flash:
        board = board_classes[board_name]()
        board.flash(filename=builder.get_bitstream_filename(mode="flash"))
    if args.doc:
        soc.generate_doc(board_name)

def main():
    """Main entry point for bitstream generation and board programming."""
    description = (
        "Zephyr on Tang Nano 20k by SantaCRC\n\n"
    )
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--device", default=None, help="FPGA device.")
    parser.add_argument("--variant", default=None, help="FPGA board variant.")
    parser.add_argument("--toolchain", default=None, help="Toolchain used to build.")
    parser.add_argument("--uart-baudrate", default=115.2e3, type=float, help="UART baudrate.")
    parser.add_argument("--build", action="store_true", help="Build bitstream.")
    parser.add_argument("--load", action="store_true", help="Load bitstream (to SRAM).")
    parser.add_argument("--flash", action="store_true", help="Flash bitstream/images (to Flash).")
    parser.add_argument("--doc", action="store_true", help="Build documentation.")
    parser.add_argument("--local-ip", default="192.168.1.50", help="Local IP address.")
    parser.add_argument("--remote-ip", default="192.168.1.100", help="Remote IP address of TFTP server.")
    parser.add_argument("--spi-data-width", default=8, type=int, help="SPI data width (max bits per xfer).")
    parser.add_argument("--spi-clk-freq", default=1_000_000, type=int, help="SPI clock frequency.")
    parser.add_argument("--fdtoverlays", default="", help="Device Tree overlays to apply.")
    parser.add_argument("--rootfs", default="mmcblk0p2", choices=["ram0", "mmcblk0p2"], help="Location of the RootFS.")
    VexRiscvSMP.args_fill(parser)
    args = parser.parse_args()
    board_name = "sipeed_tang_nano_20k"
    board = board_classes[board_name]()
    soc = setup_soc(board, args)
    add_optional_interfaces(soc, board, args)
    build_and_generate(soc, board_name, args)

if __name__ == "__main__":
    main()
