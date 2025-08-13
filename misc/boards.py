#!/usr/bin/env python3
"""
Board definitions for Linux-on-LiteX-VexRiscv.
Provides base Board class and vendor/board implementations.
"""

# This file is part of Linux-on-LiteX-VexRiscv
# Copyright (c) 2019-2024, Linux-on-LiteX-VexRiscv Developers
# SPDX-License-Identifier: BSD-2-Clause

# Board Definition ---------------------------------------------------------------------------------
try:
    from misc.targets import sipeed_tang_nano_20k
except ImportError:
    sipeed_tang_nano_20k = None
try:
    from litex_boards.targets import sipeed_tang_primer_20k
except ImportError:
    sipeed_tang_primer_20k = None

class Board:
    """Base class for FPGA board definitions."""
    soc_kwargs = {
        "integrated_rom_size": 0x10000,
        "integrated_sram_size": 0x1800,
        "l2_size": 0
    }
    def __init__(self, soc_cls=None, soc_capabilities=None, soc_constants=None):
        """Initialize board with SoC class, capabilities, and constants."""
        if soc_capabilities is None:
            soc_capabilities = {}
        if soc_constants is None:
            soc_constants = {}
        self.soc_cls = soc_cls
        self.soc_capabilities = soc_capabilities
        self.soc_constants = soc_constants
        self.platform = None

    def load(self, filename):
        """Load bitstream to board using programmer."""
        prog = self.platform.create_programmer()
        prog.load_bitstream(filename)

    def flash(self, filename):
        """Flash bitstream to board using programmer."""
        prog = self.platform.create_programmer()
        prog.flash(0, filename)

#---------------------------------------------------------------------------------------------------
# Gowin Boards
#---------------------------------------------------------------------------------------------------

# Sipeed Tang Nano 20K support ---------------------------------------------------------------------
class SipeedTangNano20K(Board):
    """Board definition for Sipeed Tang Nano 20K."""
    soc_kwargs = {"l2_size": 2048} # Use Wishbone and L2 for memory accesses.
    def __init__(self):
        """Initialize Sipeed Tang Nano 20K board."""
        if sipeed_tang_nano_20k is None:
            raise ImportError("Could not import sipeed_tang_nano_20k from misc.targets.")
        Board.__init__(self, sipeed_tang_nano_20k.BaseSoC, soc_capabilities={
            # Communication
            "serial",
            "sdcard",
        })

# Sipeed Tang Primer 20K support -------------------------------------------------------------------
class SipeedTangPrimer20K(Board):
    """Board definition for Sipeed Tang Primer 20K."""
    soc_kwargs = {"l2_size": 512} # Use Wishbone and L2 for memory accesses.
    def __init__(self):
        """Initialize Sipeed Tang Primer 20K board."""
        if sipeed_tang_primer_20k is None:
            raise ImportError("Could not import sipeed_tang_primer_20k from litex_boards.targets.")
        Board.__init__(self, sipeed_tang_primer_20k.BaseSoC, soc_capabilities={
            # Communication
            "serial",
            "spisdcard",
        })
