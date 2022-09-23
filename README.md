# Wil6210 Firmware Controller

This is a proprietary software. Do not redistribute it without written 
permission from WCSN group, UCSD.

# Build Requirements

This program currently builds for two platforms: x86 and armv7l
To build the program, host must install gcc for x86 and ARM.

To prepare the ARM toolchain, download Buildroot https://buildroot.org/downloads/buildroot-2018.02.tar.gz
Uncompress into $HOME/tool/, configure and install it as follows:
- Target Architecture: ARM (little endian)
- Target Binary Format: ELF
- Target Architecture Variant: cortex-A15
- Target ABI: EABIhf
- Floating point strategy: VFPv4-D16
- ARM instruction set: ARM
- Toolchain C library: nClibc-ng

# ToDo

- Add wmi command and parameter descriptions. Follow example in src/wil6210fwctrl/wmi_echo.py
  The string in variables ``description`` and ``cmd_args`` will be printed out with --help flag.
