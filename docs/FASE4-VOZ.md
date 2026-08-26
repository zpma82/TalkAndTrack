# 🎤 Fase 4: Control por voz offline - TalkAndTrack

Control completo del sistema mediante reconocimiento de voz offline con Vosk.

---

## 📌 Visión general

**Objetivo:** Sistema de voz offline que:
- Funciona sin internet (100% local)
- Reconoce comandos en español
- Responde mediante síntesis de voz (espeak-ng)
- Ejecuta scripts bash de forma segura
- Modular: fácil añadir nuevos comandos

**Ventajas sobre speech-to-text online:**
- ✅ Privacidad total (sin enviar audio)
- ✅ Funcionamiento sin internet
- ✅ Latencia baja
- ✅ Más barato (no hay cuotas API)

**Requisitos:**
- Micrófono USB
- Modelo de lenguaje (~50MB)
- Python 3.10+
- Vosk library

```
┌──────────────────────────────────────────────┐
│         Sistema de Control por Voz            │
├──────────────────────────────────────────────┤
│                                              │
│  [Micrófono USB] → arecord (16000 Hz)       │
│                    ↓                         │
│  Vosk (Modelo Español) → Reconocimiento      │
│                    ↓                         │
│  Búsqueda de comandos en JSON                │
│                    ↓                         │
│  Ejecución de script bash (si encontrado)    │
│                    ↓                         │
│  Respuesta por voz: espeak-ng                │
│                    ↓                         │
│  [Altavoz/Bluetooth] ← Reproducción          │
│                                              │
└──────────────────────────────────────────────┘
```

---

## 🎙️ Flujo de funcionamiento

```
Usuario: "Hola"
         ↓
    [Escucha audio]
         ↓
    Vosk: "hola" detectado
         ↓
    ¿Es palabra de activación? → SÍ
         ↓
    Sistema: "Dime" (respuesta por voz)
         ↓
    [Escucha siguiente comando]
         ↓
    Vosk: "reproducir"
         ↓
    Busca en cmd_musica.json → "play"
         ↓
    Ejecuta: curl -u :motovlc2026 'http://localhost:8080/requests/status.json?command=pl_play'
         ↓
    Sistema: "play" (respuesta)
         ↓
    [Música comienza]
```

---

## 🛠️ Instalación

### Paso 1: Instalar dependencias

```bash
sudo apt install -y \
    python3-dev \
    python3-pip \
    python3-venv \
    portaudio19-dev \
    espeak-ng \
    sox

# Compilar herramientas si es necesario
sudo apt install -y build-essential
```

### Paso 2: Crear entorno virtual

```bash
cd ~/moto-voice
python3 -m venv venv
source venv/bin/activate

pip install -U pip setuptools wheel
```

### Paso 3: Instalar Vosk

```bash
pip install vosk sounddevice pyaudio
```

**Nota:** Si falla al instalar pyaudio, probar:
```bash
pip install --upgrade --no-cache-dir pyaudio
# O si aún falla:
sudo apt install -y python3-pyaudio
```

### Paso 4: Descargar modelo de voz español

```bash
# Crear directorio
mkdir -p ~/moto-voice/model-es

cd ~/moto-voice/model-es

# Descargar modelo small (~50MB)
wget https://github.com/alphacep/vosk-model-small-es/releases/download/v0.42/model-es-0.42.zip

# Extraer
unzip model-es-0.42.zip
rm model-es-0.42.zip

# Verificar
ls -la
# Debe haber: mfcc.fea, model, etc.
```

**Modelos disponibles:**
- **small** (~50MB) - Rápido, menor precisión
- **big** (~200MB) - Más preciso, más lento

Para moto, recomendamos **small** por velocidad.

### Paso 5: Resolver problema libvosk en ARM

El problema conocido: `libvosk.so: cannot enable executable stack`

Solución:
```bash
# Instalar patchelf
sudo apt install -y patchelf

# Localizar libvosk
cd ~/moto-voice/venv/lib/python3.*/site-packages/vosk/

# Hacer backup
cp libvosk.so libvosk_backup.so

# Limpiar execstack
sudo patchelf --clear-execstack libvosk.so

# Verificar
ls -la libvosk.so
```

---

## ⚙️ Configuración

### Archivo: config.json

```json
{
  "wakeword": "hola",
  "model_path": "/home/jesus/moto-voice/model-es",
  "commands_dir": "/home/jesus/moto-voice/commands",
  "audio_device": 1,
  "confidence_threshold": 0.7,
  "response_voice": true,
  "response_voice_cmd": "espeak-ng -v es",
  "log_file": "/home/jesus/moto-voice/voice.log"
}
```

**Parámetros:**
- `wakeword` - Palabra que activa escucha (ej: "hola", "jesus", "ok pi")
- `model_path` - Ruta del modelo de Vosk
- `commands_dir` - Directorio con JSON de comandos
- `audio_device` - Índice del micrófono (0-based)
- `confidence_threshold` - Confianza mínima (0.0-1.0)
- `response_voice` - Habilitar respuesta por voz
- `response_voice_cmd` - Comando para síntesis de voz
- `log_file` - Archivo de logs

### Identificar audio_device

```bash
# Ver dispositivos disponibles
source ~/moto-voice/venv/bin/activate
python3 << 'EOF'
import pyaudio
pa = pyaudio.PyAudio()
for i in range(pa.get_device_count()):
    info = pa.get_device_info_by_index(i)
    print(f"{i}: {info['name']} (in: {info['max_input_channels']}, out: {info['max_output_channels']})")
EOF

# Buscar "C-Media USB" o similar
# Anotar el número (ej: 1)
# Actualizar en config.json
```

### Cambiar palabra de activación

```bash
./scripts/set-wakeword.sh "nueva-palabra"

# Ejemplos válidos:
# - "hola"       (1 sílaba clara)
# - "jesus"      (2 sílabas)
# - "picaros"    (3 sílabas, muy claro)
# - "ok pi"      (2 palabras)
```

---

## 📝 Estructura de comandos JSON

### Template

```json
{
  "app": "nombre_app",
  "descripcion": "Descripción corta",
  "comandos": [
    {
      "frases": ["frase 1", "frase 2", "frase 3"],
      "accion": "nombre_accion",
      "script": "bash -c 'comando_a_ejecutar'"
    }
  ]
}
```

### Ejemplo: Control de música

```json
{
  "app": "musica",
  "descripcion": "Reproductor de musica VLC",
  "comandos": [
    {
      "frases": ["musica", "reproducir", "play"],
      "accion": "play",
      "script": "curl -s -u :motovlc2026 'http://localhost:8080/requests/status.json?command=pl_play'"
    },
    {
      "frases": ["pausa", "pausar", "para"],
      "accion": "pause",
      "script": "curl -s -u :motovlc2026 'http://localhost:8080/requests/status.json?command=pl_pause'"
    },
    {
      "frases": ["siguiente", "saltar"],
      "accion": "next",
      "script": "curl -s -u :motovlc2026 'http://localhost:8080/requests/status.json?command=pl_next'"
    }
  ]
}
```

### Agregar nuevos comandos

Usar script automático:
```bash
./scripts/add-app-commands.sh
```

O editando JSON manualmente:
```bash
nano commands/cmd_nuevaapp.json

# Luego reiniciar
sudo systemctl restart moto-voice
```

---

## 🎙️ Comandos disponibles

### Música (VLC)
- "reproducir", "play", "música"
- "pausa", "pausar", "para"
- "siguiente", "saltar"
- "anterior", "volver"
- "sube volumen", "más volumen"
- "baja volumen", "menos volumen"

### Radio (mpv)
- "pon la radio", "radio"
- "pon la cope", "cope"
- "pon onda cero"
- "parar radio", "silencio radio"

### GPS
- "mapas", "google maps"
- "waze"
- "cierra gps", "cierra mapas"

### Sistema
- "apagar", "apaga"
- "reiniciar"
- "hora", "qué hora es"
- "volumen arriba", "volumen abajo"

---

## 🚀 Iniciar sistema de voz

### Opción 1: Servicio systemd (recomendado)

```bash
# Copiar servicio
sudo cp systemd/moto-voice.service /etc/systemd/system/

# Habilitar e iniciar
sudo systemctl daemon-reload
sudo systemctl enable moto-voice
sudo systemctl start moto-voice

# Ver estado
journalctl -u moto-voice -f

# Debe mostrar: "Sistema de voz listo"
```

### Opción 2: Manual (debug)

```bash
cd ~/moto-voice
source venv/bin/activate
python3 moto-voice.py

# Ver logs en tiempo real
# Presionar Ctrl+C para detener
```

---

## 📊 Monitoreo y logs

### Ver logs en tiempo real

```bash
# Archivo de log
tail -f ~/moto-voice/voice.log

# Servicio systemd
journalctl -u moto-voice -f

# Con filtro (solo errores)
journalctl -u moto-voice -p err -f
```

### Interpretar logs

```
[INFO] Sistema iniciado. Wakeword: 'hola'
       → Sistema arrancó correctamente

[INFO] Reconocido: 'reproducir musica'
       → Usuario habló, Vosk lo capturó

[INFO] Wakeword detectada
       → Se reconoció la palabra de activación

[INFO] Comando: play
       → Se encontró acción en JSON

[INFO] Ejecutando [musica] play: curl -s ...
       → Se va a ejecutar el script

[ERROR] Error en play (rc=1): Connection refused
       → El comando falló (ej: VLC no está activo)
```

### Debug avanzado

Ver información detallada de Vosk:
```python
# En moto-voice.py, cambiar:
# vosk.SetLogLevel(-1)  # -1 = sin logs
# A:
# vosk.SetLogLevel(0)   # 0 = info
# vosk.SetLogLevel(1)   # 1 = debug
```

---

## 🔧 Optimizaciones

### Remuestreo de audio (pendiente)

**Problema:** Micrófono USB en 44100 Hz, Vosk necesita 16000 Hz

**Solución futura:** Usar scipy para remuestreo
```python
from scipy import signal
import numpy as np

# Remuestrear 44100 → 16000
def resample_audio(audio_44k, sr_old=44100, sr_new=16000):
    num_samples = int(len(audio_44k) * sr_new / sr_old)
    return signal.resample(audio_44k, num_samples)
```

### Mejorar precisión

1. **Aumentar confianza si hay falsos positivos:**
   ```json
   "confidence_threshold": 0.8
   ```

2. **Reducir si no reconoce:**
   ```json
   "confidence_threshold": 0.5
   ```

3. **Usar vocabulario personalizado:**
   ```python
   VOCABULARIO = json.dumps([
       "hola", "jesus", "reproducir", "mapas", "waze",
       "musica", "radio", "apagar", "siguiente", "[unk]"
   ])
   ```

### Mejorar velocidad

- Usar modelo "small" (ya incluido)
- Reducir tamaño de vocabulario
- Ejecutar en CPU (no hay GPU disponible en Pi 3)

---

## 🐛 Troubleshooting

### Micrófono no funciona

```bash
# 1. Verificar que está conectado
lsusb | grep -i media

# 2. Ver dispositivos PyAudio
python3 << 'EOF'
import pyaudio
pa = pyaudio.PyAudio()
print(f"Total devices: {pa.get_device_count()}")
for i in range(pa.get_device_count()):
    print(f"{i}: {pa.get_device_info_by_index(i)['name']}")
EOF

# 3. Probar grabación
arecord -D plughw:2,0 -f S16_LE -r 16000 -t wav test.wav
# Hablar 5 segundos
# Ctrl+C
# Reproducir
aplay test.wav
```

### Vosk no reconoce

```bash
# 1. Verificar modelo
ls -la ~/moto-voice/model-es/
# Debe contener archivos de modelo

# 2. Aumentar volumen del micrófono
alsamixer -c 2
# F4 para captura, aumentar a 60-70

# 3. Reducir umbral de confianza
nano config.json
# confidence_threshold: 0.5

# 4. Hablar más claro y lentamente

# 5. Reiniciar servicio
sudo systemctl restart moto-voice
```

### Sin audio de respuesta

```bash
# 1. Verificar espeak-ng
espeak-ng -v es "Prueba"

# 2. Verificar que response_voice está habilitado
cat config.json | grep response_voice

# 3. Aumentar volumen general
amixer set Master 100%

# 4. Ver logs de error
journalctl -u moto-voice | grep ERROR
```

---

## 🔐 Seguridad

### Evitar ejecución de comandos peligrosos

**Actual:** Scripts se ejecutan como usuario `jesus`
```bash
[Service]
User=jesus
```

**Ventaja:** No puede ejecutar `sudo`

**Mejora:** Whitelist de comandos
```python
# En moto-voice.py, agregar validación
COMANDO_PERMITIDOS = [
    "curl", "echo", "espeak-ng", "pkill", "amixer"
]

# Validar script antes de ejecutar
if not any(cmd in script for cmd in COMANDO_PERMITIDOS):
    log.error(f"Comando no permitido: {script}")
    return False
```

### Logs y auditoría

Todos los comandos quedan registrados en `voice.log`:
```
[INFO] Ejecutando [radio] radio_play: echo '{"command": [...]}'
```

---

## 📈 Estadísticas y análisis

### Ver resumen de comandos ejecutados

```bash
# Últimos 50 comandos
grep "Ejecutando" ~/moto-voice/voice.log | tail -50

# Comandos más usados
grep "Ejecutando" ~/moto-voice/voice.log | cut -d'] ' -f2 | sort | uniq -c | sort -rn

# Errores del último día
grep "ERROR" ~/moto-voice/voice.log | grep "$(date +%Y-%m-%d)"
```

---

## ✅ Checklist Fase 4

- [x] Python 3 y venv configurados
- [x] Vosk instalado correctamente
- [x] Modelo de voz descargado
- [x] libvosk.so patcheado (si es necesario)
- [x] Micrófono USB detectado y funcionando
- [x] config.json configurado correctamente
- [x] Comandos JSON cargados
- [x] Respuesta por voz funcionando
- [x] Servicio systemd activo
- [x] Logs accesibles y claros

---

## 🔮 Mejoras futuras

- [ ] Remuestreo de audio USB automático
- [ ] Reconocimiento de emociones/tono
- [ ] Respuestas dinámicas (no solo nombre de acción)
- [ ] Aprendizaje de palabras personalizadas
- [ ] Integración con NLU (Intent recognition)
- [ ] Soporte multiidioma

---

**Estado:** 🔄 Fase 4 en progreso  
**Siguiente:** [Fase 5 - Llamadas y WhatsApp](../README.md#fases-pendientes)

