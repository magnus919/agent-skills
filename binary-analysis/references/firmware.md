# Firmware Analysis

Firmware-specific analysis patterns for embedded system images. Load this when
the binary is a firmware image (flat binary, bootloader, RTOS-based), when
`binary metadata` reports `format: "RAW"` and the context suggests firmware, or
when the user mentions IoT, embedded, bootloader, or memory dump analysis.

## What Makes Firmware Different

Firmware images differ from standard executables in key ways:

| Characteristic | Standard Executable | Firmware |
|---------------|-------------------|----------|
| Format | PE, ELF, Mach-O | Often flat binary (RAW) with custom layout |
| Load address | OS loader determines | Fixed flash address (e.g., 0x08000000) |
| Entry point | Defined in header | Vector table at offset 0 (ARM Cortex-M) or fixed address |
| Sections | Named, with permissions | Memory-mapped regions without metadata |
| Dependencies | Dynamic libraries | Self-contained or hardware-specific |
| Strings | OS API references | Hardware register names, RTOS symbols, custom protocols |
| Relocation | OS handles ASLR | None — fixed addresses |

## Detecting Firmware

### Primary Indicators

1. **RAW format** with no PE/ELF/Mach-O magic:
   ```bash
   binary metadata --project <proj> --json
   # data.format: "RAW"
   ```

2. **Recognizable strings** for embedded platforms:
   ```bash
   binary strings --project <proj> --min-length 8 --json
   ```
   Look for:
   - RTOS names: "FreeRTOS", "ThreadX", "Zephyr", "uC/OS", "RT-Thread", "embOS", "VxWorks"
   - MCU families: "STM32", "ESP32", "nRF52", "MSP430", "PIC32", "LPC", "Kinetis"
   - Bootloader strings: "U-Boot", "Das U-Boot", "barebox", "MCUboot", "Little Kernel"
   - Hardware registers: "GPIO", "UART", "SPI", "I2C", "NVIC", "SCB"
   - Build toolchains: "arm-none-eabi-gcc", "IAR", "Keil", "STM32CubeIDE"
   - File systems: "LittleFS", "FATFS", "SPIFFS", "JFFS2", "UBIFS"
   - Network stacks: "lwIP", "uIP", "MQTT", "CoAP"

3. **Size characteristics**: Firmware is typically:
   - Power-of-2 aligned (e.g., exactly 256KB, 512KB, 1MB).
   - Smaller than desktop executables (mostly under 10MB).
   - Filled with `0xFF` padding (flash erase state).

### ARM Cortex-M Vector Table Detection

ARM Cortex-M firmware starts with a vector table at offset 0:

| Offset | Content | Expected Pattern |
|--------|---------|-----------------|
| 0x00 | Initial stack pointer | Should point to RAM range (e.g., 0x20000000+ for SRAM) |
| 0x04 | Reset vector (entry point) | Should point to flash range (e.g., 0x08000000+) with bit 0 set (Thumb mode) |
| 0x08 | NMI handler | Thumb-mode address |
| 0x0C | HardFault handler | Thumb-mode address |
| 0x10+ | Other exception handlers | Thumb-mode addresses |

**Detection check:**
```bash
binary bytes --project <proj> 0x0 128 --json
```
Look at the first 4 words:
- Word[0] should be a RAM address (typical: 0x20000000-0x20020000 range).
- Word[1] should be a flash address with bit 0 set (LSB = 1 = Thumb).
- Words[2-15] should also be flash-range addresses with bit 0 set.

### ARM Exception Vector Table IDs

| Vector Number | IRQ | Handler |
|---------------|-----|---------|
| 0 | — | Initial SP |
| 1 | — | Reset |
| 2 | -14 | NMI |
| 3 | -13 | HardFault |
| 4 | -12 | MemManage |
| 5 | -11 | BusFault |
| 6 | -10 | UsageFault |
| 11 | -5 | SVCall |
| 14 | -2 | PendSV |
| 15 | -1 | SysTick |
| 16+ | 0+ | Device-specific IRQs |

## Firmware Analysis Workflow

### Step 1: Determine Architecture and Base Address

Without format headers, you need to determine:

1. **Architecture**: Usually evident from build toolchain strings. You can also
   try to guess from the binary structure:
   - ARM Thumb: Instructions are 2 or 4 bytes, bit 0 of addresses = 1.
   - ARM (A32): Instructions are 4 bytes, addresses are 4-byte aligned.
   - AArch64: Instructions are 4 bytes, addresses are 4-byte aligned.
   - RISC-V: Instructions are 2 or 4 bytes (compressed extension).
   - MIPS: Instructions are 4 bytes.

2. **Base address**: Where in memory the firmware is loaded. This is critical
   for correct disassembly. Signs:
   - Vector table addresses (ARM Cortex-M: initial SP and reset vector).
   - Absolute addresses in strings or data structures.
   - Bootloader configuration headers.

### Step 2: Use String Analysis as Primary Tool

For formatless firmware, strings are your most valuable source:

```bash
binary strings --project <proj> --min-length 6 --json
```

Categorize strings:

| Category | Example Strings | What They Reveal |
|----------|----------------|-------------------|
| RTOS identification | "FreeRTOS", "vTaskDelay", "xQueueSend" | Operating system and version |
| Hardware identification | "STM32F407", "nRF52840", "bcm2835" | Target chip — determines architecture and peripherals |
| Pin/peripheral names | "UART1_TX", "SPI2_MOSI", "PA5" | Hardware interfaces in use |
| Error messages | "WiFi connection failed", "Sensor timeout" | Functionality and failure modes |
| AT commands | "AT+CIPSTART", "AT+HTTPGET" | Modem/communication interface |
| Protocol strings | "MQTT", "HTTP/1.1", "/api/v1/" | Communication protocols and endpoints |
| File paths | "/cfg/wifi.cfg", "/data/log.txt" | File system layout |
| TLS certificates | "-----BEGIN CERTIFICATE-----" | Embedded certificates — note these |
| Credentials | "admin:password", hardcoded keys | **Flag as security concern** |
| Build identifiers | "v2.4.1-0-g3a7b", build dates | Firmware version and build info |

### Step 3: Identify Memory Regions

Firmware images often contain multiple concatenated regions:

- **Bootloader** (typically first 16-64KB): Minimal code to load the
  application.
- **Application** (majority of the image): The main firmware.
- **Filesystem** (trailing region): LittleFS, FATFS, or custom format.
- **Configuration** (fixed offset): Calibration data, MAC addresses, serial
  numbers.
- **OTA partitions**: Duplicate application and filesystem regions for
  over-the-air updates.

Look for region boundaries:
- String content changes (code-like strings → file-system-like strings).
- Data pattern changes (compressed code → repeated structures → 0xFF padding).
- Magic bytes for filesystems at aligned offsets.

### Step 4: Extract Filesystem (If Present)

If you identify a filesystem region, note its offset and size. Common embedded
filesystems and their magic bytes:

| Filesystem | Magic / Signature |
|-----------|-------------------|
| LittleFS | `littlefs` at superblock offset |
| FATFS | `MSDOS5.0` or `FAT12/16/32` in boot sector |
| SPIFFS | `SPIFFS` in magic bytes |
| JFFS2 | `0x1984` or `0x1985` at node headers |
| UBIFS | `UBI#` at UBI eraseblock headers |

Extract the filesystem for offline analysis using external tools — this is
beyond the scope of the CLI, but identifying the presence and type of
filesystem is within scope.

### Step 5: Look for Bootloader Patterns

If the image contains a bootloader:

```bash
# U-Boot specific
binary strings --project <proj> --contains "U-Boot" --json

# Bootloader version strings
binary strings --project <proj> --contains "bootloader" --json
```

Common bootloader characteristics:
- U-Boot: Has environment variables, device tree, boot commands.
- MCUboot: SWAP/SCRATCH regions, image headers with TLV (type-length-value)
  structures.
- Little Kernel (LK): "lk" or "Little Kernel" strings, app entry marker.

### Step 6: Look for Security Concerns

Firmware-specific security concerns:

1. **Hardcoded credentials**: Passwords, API keys, tokens in strings.
   ```bash
   binary strings --project <proj> --contains "password" --json
   binary strings --project <proj> --contains "secret" --json
   binary strings --project <proj> --contains "key" --json
   ```

2. **Debug interfaces left enabled**: JTAG/SWD/UART strings.
   ```bash
   binary strings --project <proj> --contains "debug" --json
   binary strings --project <proj> --contains "JTAG" --json
   ```

3. **Insecure update mechanisms**: No signature verification, HTTP (not HTTPS)
   updates.
   ```bash
   binary strings --project <proj> --contains "http://" --json
   ```

4. **Exposed UART/serial consoles**: Shell access strings.
   ```bash
   binary strings --project <proj> --contains "login" --json
   binary strings --project <proj> --contains "shell" --json
   ```

## Architecture-Specific Patterns

### ARM Cortex-M

- Vector table at 0x00000000 (or remapped).
- Thumb/Thumb-2 instruction set.
- Memory-mapped I/O: Peripheral registers at fixed addresses.
- No MMU — flat memory model.
- NVIC at 0xE000E100 for interrupt control.

### ARM Cortex-A

- Typically runs Linux or an RTOS.
- May have U-Boot headers.
- Device tree blob (DTB) present: magic `0xD00DFEED`.
- ELF or RAW kernel image.

### ESP32 / Xtensa

- ESP32 uses Xtensa LX6 or LX7 cores.
- ESP-IDF framework: "esp_image_header" magic.
- Partition table at offset 0x8000.
- NVS (Non-Volatile Storage) with "NVS" magic.

### RISC-V

- Vector table optional (depends on implementation).
- May have Device Tree Blob.
- Compressed (RVC) and standard instructions coexist.

### MIPS

- Firmware often starts at 0x9FC00000 (kseg0 boot) or 0xBFC00000.
- Interrupt vector at 0x80000180.

## Reporting Firmware Findings

Structure your firmware analysis report:

```
## Firmware Analysis

### Identity
- Format: RAW
- Size: 524,288 bytes (512 KB — matches typical STM32F4 flash size)
- Architecture: ARM Cortex-M (Thumb), likely STM32F4
- Build ID: "v2.4.1-0-g3a7b" (from strings)

### Components Identified
- RTOS: FreeRTOS v10.4.3 (from task names and API strings)
- Network stack: lwIP 2.1.2 (from init strings)
- TLS: mbedTLS 2.28 (from certificate parsing strings)
- File system: LittleFS (from LFS magic)

### Memory Layout (Determined from Strings and Structure)
- 0x08000000-0x0800FFFF: Bootloader (64KB)
- 0x08010000-0x0805FFFF: Application (320KB)
- 0x08060000-0x0807FFFF: LittleFS filesystem (128KB)

### Security Observations
- TLS certificates found — expected for IoT device
- HTTP endpoint: http://api.device.example.com/firmware — update over HTTP, not HTTPS
- Hardcoded string: "debugpass123" — possible debug backdoor
- No secure boot indicators (no MCUboot or signature verification strings)

### Unknowns
- SPI Flash configuration parameters not identified
- Custom AT command parser at 0x08032000 — proprietary protocol
```
