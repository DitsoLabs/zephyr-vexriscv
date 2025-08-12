# zephyr-vexriscv
[![Pylint](https://github.com/DitsoLabs/zephyr-vexriscv/actions/workflows/pylint.yml/badge.svg)](https://github.com/DitsoLabs/zephyr-vexriscv/actions/workflows/pylint.yml)

**Zephyr RTOS on VexRiscv for Tang Nano 20K (and possibly 9K in the future)**

<p align="center">
  <img src="https://raw.githubusercontent.com/litex-hub/linux-on-litex-vexriscv/master/doc/logo.png" alt="Zephyr on VexRiscv" width="300">
</p>

---

## ✨ Project Overview

`zephyr-vexriscv` is a working implementation of the [Zephyr RTOS](https://zephyrproject.org/) running on the [VexRiscv](https://github.com/SpinalHDL/VexRiscv) softcore CPU, targeting the **Sipeed Tang Nano 20K** FPGA development board. The project leverages the [LiteX SoC builder](https://github.com/enjoy-digital/litex) to generate a RISC-V based SoC with Zephyr-compatible peripherals.

> 🚀 This project aims to provide a minimal yet extensible RISC-V platform for real-time applications running on low-cost FPGAs.

---

## 🛠 Features

* ✅ **Zephyr RTOS** booting on VexRiscv SMP
* ✅ **LiteX SoC** with UART, Timer, SPI-SDCard, GPIO
* ✅ Support for **interrupts (PLIC)** and memory-mapped peripherals
* ✅ Cross-compilation using **Zephyr SDK**
* ✅ Flexible SoC design using Python/LiteX
* ✅ 100% open source toolchain (Gowin, LiteX, Zephyr)

> ⚙️ FPGA: Sipeed Tang Nano 20K (GW2AR-LV18QN88C8/I7)
> 💻 CPU: VexRiscv SMP (rv32ima)

---

## 🧩 Platform Roadmap

| Board         | Status      | Notes                           |
| ------------- | ----------- | ------------------------------- |
| Tang Nano 20K | ✅ Supported | Primary development target      |
| Tang Nano 9K  | 🕻 Planned  | Future support under evaluation |

---

## 📦 Directory Structure

```plaintext
zephyr-vexriscv/
├── boards/             # Zephyr board definitions (DTS, Kconfig)
├── soc/                # Custom SoC files based on LiteX
├── litex_project/      # Python scripts to generate FPGA bitstream
├── zephyr/             # Sample apps (e.g. hello_world)
└── README.md           # You're here!
```

---

## ⚙️ Getting Started

### ✅ Requirements

* Python 3.8+
* [Zephyr SDK](https://docs.zephyrproject.org/latest/develop/toolchains/zephyr_sdk.html)
* [west](https://docs.zephyrproject.org/latest/develop/west/index.html) (Zephyr build tool)
* Gowin IDE / GOWIN toolchain
* [LiteX](https://github.com/enjoy-digital/litex) + dependencies

### 🔧 Build SoC + Bitstream

```bash
# Clone LiteX & related cores (optional if already done)
git clone https://github.com/enjoy-digital/litex
cd litex

# Build SoC (example)
python3 litex_project/soc.py --build --load
```

### 🚀 Build and Flash Zephyr App

```bash
# Set environment
source zephyr/zephyr-env.sh

# Build hello_world
west build -b tang_nano_20k zephyr/hello_world --pristine

# Flash via serial or programmer (depending on setup)
```

---

## 📸 Demo

<p align="center">
  <img src="https://user-images.githubusercontent.com/your_screenshot.png" width="500" alt="Zephyr running on Tang Nano 20K" />
</p>

---

## 🤝 Contributing

Pull requests, feedback, and ideas are welcome! Feel free to:

* Improve device tree bindings
* Add support for Tang Nano 9K
* Integrate more Zephyr drivers

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## ✉️ Contact

Made with ❤️ by [Ditso Labs](https://github.com/your-org).
For questions, ideas or collaboration: `contact@ditsolabs.com`
