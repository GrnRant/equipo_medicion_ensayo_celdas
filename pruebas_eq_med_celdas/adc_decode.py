import serial
import numpy as np
import matplotlib.pyplot as plt

PORT = "COM6"
BAUD = 115200

FS = 100000
CHANNELS = 3
SECONDS = 0.1

N = int(FS * SECONDS * CHANNELS)
BYTES_TO_READ = N * 2

VREF = 3.300


def read_exactly(ser, n):
    data = bytearray()

    while len(data) < n:
        chunk = ser.read(n - len(data))

        if not chunk:
            raise TimeoutError(
                f"Timeout: recibidos {len(data)} de {n} bytes"
            )

        data.extend(chunk)

    return bytes(data)


# ---------------------------------------------------------
# Pasabajos IIR de primer orden
# ---------------------------------------------------------

def lowpass_filter(signal, cutoff, fs):
    rc = 1.0 / (2.0 * np.pi * cutoff)
    dt = 1.0 / fs
    alpha = dt / (rc + dt)

    filtered = np.empty_like(signal, dtype=np.float64)
    filtered[0] = signal[0]

    for i in range(1, len(signal)):
        filtered[i] = (
            filtered[i - 1]
            + alpha * (signal[i] - filtered[i - 1])
        )

    return filtered


# ---------------------------------------------------------
# Adquisición
# ---------------------------------------------------------

ser = serial.Serial(
    PORT,
    BAUD,
    timeout=7
)

print("Iniciando adquisición...")
ser.write(b"s\n")

response = ser.readline()

if response != b"DONE\n":
    raise RuntimeError(
        f"Respuesta inesperada del STM32: {response!r}"
    )

print("Adquisición terminada.")

print(f"Solicitando {BYTES_TO_READ} bytes...")
ser.write(b"r\n")

raw = read_exactly(ser, BYTES_TO_READ)

print(f"Recibidos {len(raw)} bytes.")

ser.close()


# ---------------------------------------------------------
# Convertir a uint16
# ---------------------------------------------------------

data = np.frombuffer(raw, dtype="<u2")

print("RAW min: ", data.min())
print("RAW max: ", data.max())
print("RAW mean:", data.mean())


# ---------------------------------------------------------
# Separar canales
# ---------------------------------------------------------

ch1 = data[0::3].astype(np.float64)
ch2 = data[1::3].astype(np.float64)
ch3 = data[2::3].astype(np.float64)


# ---------------------------------------------------------
# Convertir a mV
# ---------------------------------------------------------

ch1_mv = ch1 * VREF * 1000.0 / 4095.0
ch2_mv = ch2 * VREF * 1000.0 / 4095.0
ch3_mv = ch3 * VREF * 1000.0 / 4095.0


# ---------------------------------------------------------
# Filtrar CH1
# ---------------------------------------------------------

CUTOFF = 5000.0  # Hz

ch1_filtered = lowpass_filter(
    ch1_mv,
    CUTOFF,
    FS
)


# ---------------------------------------------------------
# Tiempo en ms
# ---------------------------------------------------------

t_ms = np.arange(len(ch1)) / FS * 1000.0


# =========================================================
# PLOT 1 - Tres canales sin filtrar
# =========================================================

plt.figure(figsize=(12, 6))

plt.plot(t_ms, ch1_mv, label="CH1")
plt.plot(t_ms, ch2_mv, label="CH2")
plt.plot(t_ms, ch3_mv, label="CH3")

plt.xlabel("Tiempo [ms]")
plt.ylabel("Tensión [mV]")
plt.title("ADC - 100 kS/s - Señales sin filtrar")
plt.grid(True)
plt.legend()

plt.tight_layout()


# =========================================================
# PLOT 2 - CH1 filtrado
# =========================================================

plt.figure(figsize=(12, 6))

plt.plot(t_ms, ch1_filtered, label="CH1 filtrado")

plt.xlabel("Tiempo [ms]")
plt.ylabel("Tensión [mV]")
plt.title(f"CH1 - Pasabajos {CUTOFF / 1000:.1f} kHz")
plt.grid(True)
plt.legend()

plt.tight_layout()

plt.show()