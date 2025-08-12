#!/usr/bin/env python3

#
# This file is part of Linux-on-LiteX-VexRiscv
#
# Copyright (c) 2019-2024, Linux-on-LiteX-VexRiscv Developers
# SPDX-License-Identifier: BSD-2-Clause

# Board Definition ---------------------------------------------------------------------------------

class Board:
    soc_kwargs = {
        "integrated_rom_size"  : 0x10000,
        "integrated_sram_size" : 0x1800,
        "l2_size"              : 0
    }
    def __init__(self, soc_cls=None, soc_capabilities={}, soc_constants={}):
        self.soc_cls          = soc_cls
        self.soc_capabilities = soc_capabilities
        self.soc_constants    = soc_constants

    def load(self, filename):
        prog = self.platform.create_programmer()
        prog.load_bitstream(filename)

    def flash(self, filename):
        prog = self.platform.create_programmer()
        prog.flash(0, filename)
#---------------------------------------------------------------------------------------------------
# Gowin Boards
#---------------------------------------------------------------------------------------------------

# Sipeed Tang Nano 20K support ---------------------------------------------------------------------

class Sipeed_tang_nano_20k(Board):
    soc_kwargs = {"l2_size" : 2048} # Use Wishbone and L2 for memory accesses.
    def __init__(self):
        from misc.targets import sipeed_tang_nano_20k
        Board.__init__(self, sipeed_tang_nano_20k.BaseSoC, soc_capabilities={
            # Communication
            "serial",
            "sdcard",
        })
# Sipeed Tang Primer 20K support -------------------------------------------------------------------

class Sipeed_tang_primer_20k(Board):
    soc_kwargs = {"l2_size" : 512} # Use Wishbone and L2 for memory accesses.
    def __init__(self):
        from litex_boards.targets import sipeed_tang_primer_20k
        Board.__init__(self, sipeed_tang_primer_20k.BaseSoC, soc_capabilities={
            # Communication
            "serial",
            "spisdcard",
        })