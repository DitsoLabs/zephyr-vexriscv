"""
Linux-on-LiteX-VexRiscv SoC Linux integration and helpers.
"""

import os
import json
import shutil
import subprocess
from migen import Cat
from litex.soc.interconnect.csr import CSR
from litex.soc.cores.gpio import GPIOIn
from litex.soc.cores.spi import SPIMaster
from litex.soc.cores.bitbang import I2CMaster
from litex.soc.cores.pwm import PWM
from litex.tools.litex_json2dts_linux import generate_dts

# SoCLinux -----------------------------------------------------------------------------------------

def SoCLinux(soc_cls, **kwargs):
    """Create a Linux-capable SoC class with board-specific helpers."""
    class _SoCLinux(soc_cls):
        def __init__(self, **kwargs):
            """Initialize the SoC with Linux CPU variant."""
            soc_cls.__init__(self, cpu_type="vexriscv_smp", cpu_variant="linux", **kwargs)
            self.switches = None
            self.spi = None
            self.i2c0 = None

        def add_rgb_led(self):
            """Add RGB LED PWM modules to the SoC."""
            rgb_led_pads = self.platform.request("rgb_led", 0)
            for color in "rgb":
                self.add_module(name=f"rgb_led_{color}0", module=PWM(getattr(rgb_led_pads, color)))

        def add_switches(self):
            """Add user switches with IRQ to the SoC."""
            self.switches = GPIOIn(Cat(self.platform.request_all("user_sw")), with_irq=True)
            self.irq.add("switches")

        def add_spi(self, data_width, clk_freq):
            """Add SPI master to the SoC."""
            spi_pads = self.platform.request("spi")
            self.spi = SPIMaster(spi_pads, data_width, self.clk_freq, clk_freq)

        def add_i2c(self):
            """Add I2C master to the SoC."""
            self.i2c0 = I2CMaster(self.platform.request("i2c", 0))

        def configure_ethernet(self, remote_ip):
            """Configure Ethernet remote IP constants."""
            remote_ip_parts = remote_ip.split(".")
            try:
                self.constants.pop("REMOTEIP1")
                self.constants.pop("REMOTEIP2")
                self.constants.pop("REMOTEIP3")
                self.constants.pop("REMOTEIP4")
            except KeyError:
                pass
            self.add_constant("REMOTEIP1", int(remote_ip_parts[0]))
            self.add_constant("REMOTEIP2", int(remote_ip_parts[1]))
            self.add_constant("REMOTEIP3", int(remote_ip_parts[2]))
            self.add_constant("REMOTEIP4", int(remote_ip_parts[3]))

        def generate_dts(self, board_name, rootfs="ram0"):
            """Generate device tree source from SoC JSON."""
            json_src = os.path.join("build", board_name, "csr.json")
            dts = os.path.join("build", board_name, f"{board_name}.dts")
            initrd = "enabled" if rootfs == "ram0" else "disabled"
            with open(json_src, encoding="utf-8") as json_file, open(dts, "w", encoding="utf-8") as dts_file:
                dts_content = generate_dts(
                    json.load(json_file),
                    initrd=initrd,
                    polling=False,
                    root_device=rootfs
                )
                # Add voltage regulator for MMC if needed
                if "vmmc-supply = <&vreg_mmc>;" in dts_content and "vreg_mmc:" not in dts_content:
                    chosen_end = dts_content.find("};", dts_content.find("chosen {")) + 2
                    regulator_def = (
                        "\n        vreg_mmc: vreg_mmc {\n"
                        "            compatible = \"regulator-fixed\";\n"
                        "            regulator-name = \"vreg_mmc\";\n"
                        "            regulator-min-microvolt = <3300000>;\n"
                        "            regulator-max-microvolt = <3300000>;\n"
                        "            regulator-always-on;\n        };\n"
                    )
                    dts_content = dts_content[:chosen_end] + regulator_def + dts_content[chosen_end:]
                dts_file.write(dts_content)

        def compile_dts(self, board_name, symbols=False):
            """Compile device tree source to binary."""
            dts = os.path.join("build", board_name, f"{board_name}.dts")
            dtb = os.path.join("build", board_name, f"{board_name}.dtb")
            symbol_flag = "-@" if symbols else ""
            subprocess.check_call(
                f"dtc {symbol_flag} -O dtb -o {dtb} {dts}", shell=True)

        def combine_dtb(self, board_name, overlays=""):
            """Combine DTB with overlays if provided."""
            dtb_in = os.path.join("build", board_name, f"{board_name}.dtb")
            dtb_out = os.path.join("software", "rv32.dtb")
            if overlays == "":
                shutil.copyfile(dtb_in, dtb_out)
            else:
                subprocess.check_call(
                    f"fdtoverlay -i {dtb_in} -o {dtb_out} {overlays}", shell=True)

        def generate_doc(self, board_name):
            """Generate SoC documentation using Sphinx."""
            from litex.soc.doc import generate_docs
            doc_dir = os.path.join("build", board_name, "doc")
            generate_docs(self, doc_dir)
            os.system(f"sphinx-build -M html {doc_dir}/ {doc_dir}/_build")

    return _SoCLinux(**kwargs)
