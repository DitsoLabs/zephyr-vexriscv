# Zephyr-VexRiscv

[![Pylint](https://github.com/DitsoLabs/zephyr-vexriscv/actions/workflows/pylint.yml/badge.svg)](https://github.com/DitsoLabs/zephyr-vexriscv/actions/workflows/pylint.yml)
[![License: BSD-2-Clause](https://img.shields.io/badge/License-BSD--2--Clause-blue.svg)](https://opensource.org/licenses/BSD-2-Clause)
[![Platform](https://img.shields.io/badge/Platform-Tang%20Nano%2020K-green)](https://wiki.sipeed.com/hardware/en/tang/tang-nano-20k/nano-20k.html)

**Zephyr RTOS on VexRiscv SMP for Sipeed Tang Nano 20K FPGA**

<p align="center">
  <img src="https://zephyrproject.org/wp-content/uploads/sites/38/2023/10/zephyr-logo-2023.png" alt="Zephyr RTOS" width="200">
  <img src="https://github.com/SpinalHDL/VexRiscv/raw/master/assets/vexriscv_logo.png" alt="VexRiscv" width="200">
</p>

---

## 🎯 Overview

This project provides a complete implementation of [Zephyr RTOS](https://zephyrproject.org/) running on the [VexRiscv SMP](https://github.com/SpinalHDL/VexRiscv) RISC-V core, specifically targeting the **Sipeed Tang Nano 20K** FPGA development board. Using [LiteX](https://github.com/enjoy-digital/litex) as the SoC builder framework, we create a full system with Zephyr-compatible peripherals and drivers.

### Key Features
- 🔧 **Complete SoC**: VexRiscv SMP CPU with UART, GPIO, SPI, I2C, and SDRAM
- ⚡ **Real-time OS**: Full Zephyr RTOS support with threading and interrupts
- 🛠️ **Open Source**: 100% open-source toolchain (Gowin + LiteX + Zephyr)
- 📱 **Low Cost**: Runs on affordable Tang Nano 20K (~$15 USD)
- 🔄 **Extensible**: Easy to add custom peripherals and drivers

---

##  Quick Start

### Prerequisites
- **Python 3.8+** with pip
- **RISC-V Toolchain** (or Zephyr SDK)
- **Gowin EDA** (for FPGA synthesis)
- **Git** and **west** (Zephyr build system)

### Hardware Requirements
- [Sipeed Tang Nano 20K](https://wiki.sipeed.com/hardware/en/tang/tang-nano-20k/nano-20k.html) FPGA board
- USB-C cable for programming and power
- MicroSD card (optional, for storage)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/DitsoLabs/zephyr-vexriscv.git
   cd zephyr-vexriscv
   ```

2. **Install dependencies**
   ```bash
   # Install LiteX and dependencies
   pip install -r requirements.txt
   
   # Install Zephyr SDK (if not already installed)
   wget https://github.com/zephyrproject-rtos/sdk-ng/releases/download/v0.16.5/zephyr-sdk-0.16.5_linux-x86_64.tar.xz
   tar xf zephyr-sdk-0.16.5_linux-x86_64.tar.xz
   cd zephyr-sdk-0.16.5
   ./setup.sh
   ```

3. **Generate and build the SoC**
   ```bash
   # Generate FPGA bitstream
   python3 bitstream_generator.py --build --load
   ```

4. **Set up Zephyr environment**
   ```bash
   # Initialize west workspace
   west init -l boards/
   west update
   
   # Set Zephyr environment
   export ZEPHYR_TOOLCHAIN_VARIANT=zephyr
   export ZEPHYR_SDK_INSTALL_DIR=~/zephyr-sdk-0.16.5
   ```

5. **Build and run Zephyr application**
   ```bash
   # Build hello world sample
   west build -b tang_nano_20k samples/hello_world --pristine
   
   # Program the board (if using UART bootloader)
   west flash
   ```

---

##  Project Structure

```
zephyr-vexriscv/
├── bitstream_generator.py      # Main SoC build script
├── install_board.py           # Board installation utility
├── boards/                    # Zephyr board definitions
│   └── ditsolabs/
│       └── tang_nano_20k/     # Tang Nano 20K board files
├── dts/                       # Device tree includes
│   └── riscv/litex/
├── misc/                      # SoC and board definitions
│   ├── boards.py             # Board class definitions
│   ├── soc_linux.py          # SoC integration helpers
│   └── targets/              # Target-specific implementations
├── software/                  # Boot configuration and images
└── build/                     # Generated files (gitignored)
```

---

## 🛠️ Hardware Specifications

### SoC Configuration
| Component | Specification |
|-----------|---------------|
| **CPU** | VexRiscv SMP (RV32IMA) |
| **Clock** | 48 MHz (configurable) |
| **RAM** | 64MB SDRAM + 32KB SRAM |
| **Flash** | 16MB SPI Flash (optional) |
| **Peripherals** | UART, GPIO, SPI, I2C, PWM |

### Tang Nano 20K Features
| Feature | Details |
|---------|---------|
| **FPGA** | Gowin GW2AR-LV18QN88C8/I7 |
| **Logic Elements** | 20,736 LUT4 |
| **Memory** | 15,552 Kbit Block RAM |
| **I/O** | 63 user IOs |
| **External RAM** | 64Mbit (8MB) SDRAM |
| **Connectivity** | USB-C, HDMI, 40-pin header |

---

## 🎮 Examples and Applications

### Available Samples
- **Hello World** - Basic console output
- **Blinky** - LED blinking with GPIO
- **Shell** - Interactive command shell
- **Threads** - Multi-threading demonstration
- **SPI/I2C** - Peripheral communication

### Running Examples
```bash
# LED blinky
west build -b tang_nano_20k samples/basic/blinky

# Interactive shell
west build -b tang_nano_20k samples/subsys/shell/shell_module

# Multi-threading demo
west build -b tang_nano_20k samples/kernel/threads
```

---

##  Development

### Adding Custom Peripherals
1. Modify `misc/soc_linux.py` to add new peripheral
2. Update device tree in `dts/riscv/litex/tang_nano_20k.dtsi`
3. Add Zephyr driver in `drivers/` (if needed)
4. Rebuild SoC and Zephyr application

### Debugging
- **Console**: UART output at 115200 baud on USB-C
- **GDB**: Use OpenOCD with RISC-V GDB
- **Logic Analyzer**: GPIO pins available for debugging

### Performance Tuning
- Adjust CPU frequency in `bitstream_generator.py`
- Configure cache sizes for optimal performance
- Enable/disable peripherals to save resources

---

## 🤝 Contributing

We welcome contributions to the zephyr-vexriscv project! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### Quick Contribution Guide
1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Follow** our code style guidelines (run `pylint` before submitting)
4. **Commit** your changes (`git commit -m 'Add amazing feature'`)
5. **Push** to the branch (`git push origin feature/amazing-feature`)
6. **Open** a Pull Request

### Areas for Contribution
- 🔧 **Hardware Support**: Add new FPGA boards and peripherals
- 🐛 **Bug Fixes**: Improve stability and performance
- 📚 **Documentation**: Enhance guides and examples
- 🧪 **Testing**: Add test cases and validation
- 💡 **Features**: Implement new SoC capabilities

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### Third-Party Licenses
- **Zephyr RTOS**: Apache License 2.0
- **LiteX**: BSD 2-Clause License
- **VexRiscv**: MIT License

---

## 🙏 Acknowledgments

- **[Enjoy Digital](https://github.com/enjoy-digital)** for the amazing LiteX framework
- **[SpinalHDL](https://github.com/SpinalHDL)** team for VexRiscv RISC-V core
- **[Zephyr Project](https://www.zephyrproject.org/)** for the robust RTOS
- **[Sipeed](https://www.sipeed.com/)** for affordable FPGA development boards
- **RISC-V Foundation** for the open instruction set architecture

---

## 📞 Support & Contact

### Getting Help
- 🐛 **Issues**: [GitHub Issues](https://github.com/DitsoLabs/zephyr-vexriscv/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/DitsoLabs/zephyr-vexriscv/discussions)
- 📧 **Email**: support@ditsolabs.com

### Community
- 🌐 **Website**: [ditsolabs.com](https://ditsolabs.com)
- 🐦 **Twitter**: [@DitsoLabs](https://twitter.com/DitsoLabs)
- 💼 **LinkedIn**: [DitsoLabs](https://linkedin.com/company/ditsolabs)

### Useful Links
- 📖 **Zephyr Documentation**: [docs.zephyrproject.org](https://docs.zephyrproject.org)
- 🔗 **LiteX Documentation**: [github.com/enjoy-digital/litex](https://github.com/enjoy-digital/litex)
- 🏗️ **VexRiscv Repository**: [github.com/SpinalHDL/VexRiscv](https://github.com/SpinalHDL/VexRiscv)
- 📋 **Tang Nano 20K Wiki**: [wiki.sipeed.com](https://wiki.sipeed.com/hardware/en/tang/tang-nano-20k/nano-20k.html)

---

<div align="center">

**Made with ❤️ by [DitsoLabs](https://ditsolabs.com)**

⭐ **Star this repository if you find it useful!** ⭐

</div>
