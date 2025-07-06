# Copyright (c) 2024 Ditso Labs
# SPDX-License-Identifier: Apache-2.0

if(CONFIG_SOC_LITEX_VEXRISCV)
  zephyr_compile_definitions(LITEX_VEXRISCV)
endif()
