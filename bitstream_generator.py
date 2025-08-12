#!/usr/bin/env python3
#
#
# Copyright (c) 2025, Fabian Alvarez [SantaCRC] (contact@fabianalvarez.dev)
#
import logging
import os
import re
import sys
import argparse
import shutil

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


from litex.soc.integration.builder import Builder
from litex.soc.cores.cpu.vexriscv_smp import VexRiscvSMP

from misc.boards import *
from misc.soc_linux import SoCLinux

# ---------------------------------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------------------------------

def camel_to_snake(name):
    name = re.sub(r'(?<=[a-z])(?=[A-Z])', '_', name)
    return name.lower()

def get_board():
    board_classes = {}
    for name, obj in globals().items():
        name = camel_to_snake(name)
        if isinstance(obj, type) and issubclass(obj, Board) and obj is not Board:
            board_classes[name] = obj
    return board_classes

board_classes = get_board()

# ---------------------------------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------------------------------

def main():
    description = "Zephyr on Tang Nano 20k by SantaCRC\n\n"
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--device",         default=None,                help="FPGA device.")
    parser.add_argument("--variant",        default=None,                help="FPGA board variant.")
    parser.add_argument("--toolchain",      default=None,                help="Toolchain use to build.")
    parser.add_argument("--uart-baudrate",  default=115.2e3, type=float, help="UART baudrate.")
    parser.add_argument("--build",          action="store_true",         help="Build bitstream.")
    parser.add_argument("--load",           action="store_true",         help="Load bitstream (to SRAM).")
    parser.add_argument("--flash",          action="store_true",         help="Flash bitstream/images (to Flash).")
    parser.add_argument("--doc",            action="store_true",         help="Build documentation.")
    parser.add_argument("--local-ip",       default="192.168.1.50",      help="Local IP address.")
    parser.add_argument("--remote-ip",      default="192.168.1.100",     help="Remote IP address of TFTP server.")
    parser.add_argument("--spi-data-width", default=8,   type=int,       help="SPI data width (max bits per xfer).")
    parser.add_argument("--spi-clk-freq",   default=1e6, type=int,       help="SPI clock frequency.")
    parser.add_argument("--fdtoverlays",    default="",                  help="Device Tree Overlays to apply.")
    parser.add_argument(
        "--rootfs",
        default="mmcblk0p2",
        choices=["ram0", "mmcblk0p2"],
        help="Location of the RootFS."
    )
    VexRiscvSMP.args_fill(parser)
    args = parser.parse_args()

    # For now we just take the Tang Nano 20K board -----------------------------------------------
    board_name = "sipeed_tang_nano_20k"
    board = board_classes[board_name]()
    soc_kwargs = Board.soc_kwargs.copy()
    




    # CPU parameters ------------------------------------------------------------------------------
    if args.with_wishbone_memory:
        soc_kwargs["l2_size"] = max(soc_kwargs.get("l2_size", 0), 2048)
    else:
        args.with_wishbone_memory = soc_kwargs.get("l2_size", 0) != 0

    if "usb_host" in board.soc_capabilities:
        args.with_coherent_dma = True

    VexRiscvSMP.args_read(args)

    # SoC parameters ------------------------------------------------------------------------------
    if args.device is not None:
        soc_kwargs["device"] = args.device
    if args.variant is not None:
        soc_kwargs["variant"] = args.variant
    if args.toolchain is not None:
        soc_kwargs["toolchain"] = args.toolchain

    # UART
    soc_kwargs["uart_baudrate"] = int(args.uart_baudrate)
    if "crossover" in board.soc_capabilities:
        soc_kwargs["uart_name"] = "crossover"
    if "usb_fifo" in board.soc_capabilities:
        soc_kwargs["uart_name"] = "usb_fifo"
    if "usb_acm" in board.soc_capabilities:
        soc_kwargs["uart_name"] = "usb_acm"

    # Peripherals
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

    # Instantiate SoC -------------------------------------------------------------------------------
    soc = SoCLinux(board.soc_cls, **soc_kwargs)
    board.platform = soc.platform

    # Add SoC constants ----------------------------------------------------------------------------
    for k, v in board.soc_constants.items():
        soc.add_constant(k, v)

    # Identifier dict ---------------------------------------------------------------------------------
    identifier = {
        "sipeed_tang_nano_20k": "Sipeed Tang Nano 20K Linux SoC by Fabian Alvarez (SantaCRC)"
    }

    # Add identifier ---------------------------------------------------------------------------------
    soc.constants['CONFIG_IDENTIFIER'] = identifier[board_name]

    # Optional interfaces ----------------------------------------------------------------------------
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

    # Build ----------------------------------------------------------------------------------------
    build_dir = os.path.join("build", board_name)

    # Create log directory
    os.makedirs(os.path.join(build_dir, "logs"), exist_ok=True)

    # Log soc constant
    for k, v in soc.constants.items():
        with open(os.path.join(build_dir, "logs", "soc_constants.log"), "a") as f:
            f.write(f"{k}: {v}\n")
    

    builder = Builder(
        soc,
        output_dir   = build_dir,
        bios_console = "lite",
        csr_json     = os.path.join(build_dir, "csr.json"),
        csr_csv      = os.path.join(build_dir, "csr.csv")
    )
    builder.build(run=args.build, build_name=board_name)

    # Device Tree ----------------------------------------------------------------------------------
    soc.generate_dts(board_name, args.rootfs)
    soc.compile_dts(board_name, args.fdtoverlays)
    soc.combine_dtb(board_name, args.fdtoverlays)

    # Boot JSON ------------------------------------------------------------------------------------
    shutil.copyfile(f"software/boot_{args.rootfs}.json", "software/boot.json")

    # PCIe driver ----------------------------------------------------------------------------------
    if "pcie" in board.soc_capabilities:
        from litepcie.software import generate_litepcie_software
        generate_litepcie_software(soc, os.path.join(builder.output_dir, "driver"))

    # Load or flash ---------------------------------------------------------------------------------
    if args.load:
        board.load(filename=builder.get_bitstream_filename(mode="sram"))
    if args.flash:
        board.flash(filename=builder.get_bitstream_filename(mode="flash"))

    # Documentation --------------------------------------------------------------------------------
    if args.doc:
        soc.generate_doc(board_name)


if __name__ == "__main__":
    main()
