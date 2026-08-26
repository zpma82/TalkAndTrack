# 📦 Guía de Instalación - TalkAndTrack

Guía completa y paso a paso para instalar y configurar TalkAndTrack en tu Raspberry Pi 3.

---

## 📋 Requisitos previos

### Sistema operativo
- **Raspberry Pi OS Bookworm** (recomendado imagen lite + desktop)
- SSH habilitado
- Conexión a internet (cable o WiFi)

### Hardware
- Raspberry Pi 3 (o superior)
- Tarjeta microSD de 32GB mínimo
- Alimentación 5V/2.5A estable
- Dongle Bluetooth CSR8510 (para Fase 1)
- Micrófono USB C-Media (para Fase 4)

---

## 🔧 Instalación

### Paso 1: Actualizar sistema
```bash
sudo apt update
sudo apt upgrade -y
sudo reboot
```

### Paso 2: Instalar dependencias base
```bash
sudo apt install -y \
  python3-pip \
  python3-venv \
  python3-dev \
  git \
  wget \
  curl \
  socat \
  pulseaudio \
  alsa-utils \
  pavucontrol
```

### Paso 3: Instalar aplicaciones multimedia
```bash
sudo apt install -y vlc mpv firefox espeak-ng sox
```

### Paso 4: Instalar soporte Bluetooth
```bash
sudo apt install -y \
  bluez \
  bluealsa \
  libbluealsa-charger0 \
  libbluealsa0 \
  python3-bluez
```

### Paso 5: Desabilitar PipeWire conflictivo
```bash
# PipeWire por defecto compite con BlueALSA
mkdir -p ~/.config/wireplumber/wireplumber.conf.d

cat > ~/.config/wireplumber/wireplumber.conf.d/51-disable-bluetooth.conf << 'EOF'
wireplumber.profiles = {
  main = {
    monitor.bluez = disabled
  }
}
EOF

# Reiniciar servicios de audio
systemctl --user restart wireplumber pipewire pipewire-pulse
```

### Paso 6: Clonar repositorio
```bash
cd ~
git clone https://github.com/zpma82/TalkAndTrack.git moto-voice
cd moto-voice
```

### Paso 7: Crear entorno virtual Python
```bash
python3 -m venv venv
source venv/bin/activate
pip install -U pip setuptools wheel
```

### Paso 8: Instalar dependencias Python
```bash
# Paquetes principales
pip install vosk sounddevice pyaudio

# Herramientas opcionales
pip install numpy scipy  # Para remuestreo de audio futuro
```

---

## 📥 Descargar modelo de voz

```bash
# Crear directorio de modelos
mkdir -p ~/moto-voice/model-es

# Descargar modelo small español (~50MB)
cd ~/moto-voice/model-es
wget https://github.com/alphacep/vosk-model-small-es/releases/download/v0.42/model-es-0.42.zip

# Extraer
unzip model-es-0.42.zip
rm model-es-0.42.zip

# Verificar
ls -la
# Debe haber un archivo "mfcc.fea" y otros archivos de modelo
```

---

## 🐻 Configurar servicios Bluetooth

### Editar configuración BlueALSA
```bash
sudo nano /etc/systemd/system/bluealsa.service
```

Asegúrate de que contenga:
```ini
[Unit]
Description=BlueALSA proxy
Requires=bluetooth.service
After=bluetooth.service

[Service]
Type=simple
User=root
ExecStart=/usr/bin/bluealsad --profile=a2dp-sink --profile=a2dp-source --profile=hfp-ag

[Install]
WantedBy=multi-user.target
```

### Editar configuración Bluetooth main.conf
```bash
sudo nano /etc/bluetooth/main.conf
```

En la sección `[General]` asegurar que existe:
```ini
[General]
Enable=Source,Sink,Media,Socket,Headset,HandsFree
```

### Recargar servicios
```bash
sudo systemctl daemon-reload
sudo systemctl enable bluealsa
sudo systemctl start bluealsa
```

---

## 🎙️ Configurar micrófono USB

### Paso 1: Identificar dispositivo de audio
```bash
# Listar todos los dispositivos
arecord -l

# Buscar "C-Media USB Headphone Set" o similar
# Nota el número (ej: card 2)
```

### Paso 2: Ajustar volumen de captura
```bash
# Reemplazar "2" con tu número de tarjeta
alsamixer -c 2

# Presionar F4 para ver controles de captura
# Navegar a "Mic" o "Capture"
# Ajustar a nivel 44
# Presionar ESC para salir
```

### Paso 3: Actualizar config.json
```bash
nano ~/moto-voice/config.json
```

Verificar que contiene:
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

**Nota:** `audio_device: 1` es típico para micrófono USB, pero ajusta según tu setup.

---

## 🎵 Configurar VLC

### Copiar música
```bash
# Crear directorio de música
mkdir -p ~/Musica

# Copiar tus archivos MP3/FLAC/OGG
cp /ruta/a/musica/* ~/Musica/
```

### Crear servicio systemd
```bash
sudo cp systemd/vlc-music.service /etc/systemd/system/vlc-music.service
sudo systemctl daemon-reload
```

### Editar configuración (opcional)
```bash
sudo nano /etc/systemd/system/vlc-music.service
```

Cambiar rutas si es necesario:
```ini
ExecStart=/usr/bin/cvlc --intf http --http-password motovlc2026 --http-port 8080 --no-video /home/jesus/Musica
```

### Iniciar servicio
```bash
sudo systemctl enable vlc-music
# No iniciamos todavía (se inicia a demanda)
```

---

## 📻 Configurar radio (mpv)

### Crear socket IPC
```bash
# El script moto-voice.py lo crea automáticamente
# Solo verificar que /tmp/mpvsocket se crea al iniciarse
```

### Emisoras personalizadas
Editar `radios_espana.m3u`:
```
#EXTINF:-1,RNE
http://dispatcher.rndfnk.com/rtve/rne/radio1/mp3/high
#EXTINF:-1,Cadena SER
https://playerservices.streamtheworld.com/api/livestream-redirect/SER.mp3
#EXTINF:-1,COPE
https://flucast2-cope.flumotion.com/cope/cope.mp3
```

---

## 🗺️ Configurar GPS

### Crear directorios
```bash
mkdir -p ~/moto-ui
cp ui/gps.html ~/moto-ui/
cp ui/launch-gps.sh ~/moto-ui/
chmod +x ~/moto-ui/launch-gps.sh
```

### Instalar utilidades
```bash
sudo apt install -y unclutter  # Para ocultar cursor en kiosco
```

### Probar manualmente
```bash
~/moto-ui/launch-gps.sh
# Debe abrir Firefox en pantalla completa
```

---

## 🎤 Configurar control por voz

### Crear servicios systemd
```bash
# Copiar servicios
sudo cp systemd/moto-voice.service /etc/systemd/system/
sudo cp systemd/bluealsa.service /etc/systemd/system/
sudo cp systemd/bluealsa-aplay.service /etc/systemd/system/

sudo systemctl daemon-reload
```

### Habilitar servicios
```bash
sudo systemctl enable moto-voice
sudo systemctl enable bluealsa
sudo systemctl enable bluealsa-aplay
```

### Cambiar palabra de activación
```bash
./scripts/set-wakeword.sh "mi-palabra"
```

### Iniciar sistema de voz
```bash
sudo systemctl start moto-voice

# Verificar que inicia correctamente
journalctl -u moto-voice -f
```

---

## 🔗 Conectar Bluetooth

### Emparejar dispositivo
```bash
# Iniciar bluetoothctl
bluetoothctl

# Ver dispositivos disponibles
scan on

# Esperar a que aparezca tu dispositivo
# Conectar (sustituir MAC)
connect 00:12:6F:64:39:12

# Ver dispositivos emparejados
paired-devices

# Salir
exit
```

### Verificar conexión de audio
```bash
# Listar PCMs activos
alsamixer -c 0

# Debe aparecer tu dispositivo Bluetooth
```

---

## ✅ Verificación post-instalación

### 1. Probar micrófono
```bash
source ~/moto-voice/venv/bin/activate
python3 -c "import sounddevice; print(sounddevice.query_devices())"
```

### 2. Probar reconocimiento de voz
```bash
arecord -D plughw:2,0 -f S16_LE -r 16000 -q test.wav
# Decir algo y ctrl+C después de 3 segundos
```

### 3. Probar VLC
```bash
curl -u :motovlc2026 'http://localhost:8080/requests/status.json?command=pl_play'
```

### 4. Probar radio
```bash
echo '{"command": ["loadfile", "https://radiourl.mp3"]}' | socat - /tmp/mpvsocket
```

### 5. Probar GPS
```bash
firefox --kiosk file:///home/jesus/moto-ui/gps.html
```

---

## 🐛 Problemas comunes

### ImportError: No module named vosk
```bash
# Asegurar que estás en el venv
source ~/moto-voice/venv/bin/activate
pip install vosk
```

### libvosk.so: cannot enable executable stack
```bash
# Problema conocido en kernels recientes
cd ~/moto-voice/venv/lib/python*/site-packages/vosk/
sudo apt install patchelf
patchelf --clear-execstack libvosk.so
```

### El micrófono no se escucha
```bash
# Verificar que está conectado
lsusb | grep -i media

# Comprobar volumen en alsamixer
alsamixer -c 2
```

### VLC no inicia
```bash
# Probar manualmente
/usr/bin/cvlc --intf http --http-password motovlc2026 --http-port 8080 --no-video ~/Musica

# Ver errores en systemd
journalctl -u vlc-music -n 50
```

---

## 🚀 Siguientes pasos

1. **Configura autoarranque** en systemd (ya incluido)
2. **Personaliza comandos** con `./scripts/add-app-commands.sh`
3. **Añade tus emisoras** a `radios_espana.m3u`
4. **Cambia palabra de activación** con `./scripts/set-wakeword.sh`
5. **Mira los logs**: `journalctl -u moto-voice -f`

---

¿Necesitas ayuda? Abre un issue en GitHub: https://github.com/zpma82/TalkAndTrack/issues

