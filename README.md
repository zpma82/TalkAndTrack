# TalkAndTrack 🏍️

**Sistema de entretenimiento y control por voz para motocicleta basado en Raspberry Pi 3**

Un sistema modular y expandible que integra reproducción de música, radio por internet, GPS, control por voz offline y telefonía Bluetooth, diseñado específicamente para uso en moto.

![Estado](https://img.shields.io/badge/Estado-En%20progreso-yellow)
![Raspberry Pi](https://img.shields.io/badge/Hardware-Raspberry%20Pi%203-red)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Licencia](https://img.shields.io/badge/Licencia-MIT-green)

---

## 📋 Tabla de contenidos

- [Características](#características)
- [Fases del proyecto](#fases-del-proyecto)
- [Requisitos hardware](#requisitos-hardware)
- [Instalación rápida](#instalación-rápida)
- [Configuración](#configuración)
- [Estructura del proyecto](#estructura-del-proyecto)
- [API de comandos](#api-de-comandos)
- [Control por voz](#control-por-voz)
- [Troubleshooting](#troubleshooting)
- [Contribuciones](#contribuciones)

---

## ✨ Características

### Implementadas ✅
- **Bluetooth HFP/AVRCP** - Conectar intercomunicadores y dispositivos manos libres
- **Reproductor VLC** - Música local con control por voz y API HTTP
- **Radio por internet** - Streaming de emisoras españolas (RNE, SER, COPE, Los40, etc.)
- **GPS en kiosco** - Google Maps y Waze en pantalla completa optimizada para moto
- **Control por voz offline** - Reconocimiento de voz con Vosk (sin internet requerido)
- **Sistema modular** - Comandos organizados por aplicación en JSON

### En progreso 🔄
- **Optimización de audio** - Remuestreo de micrófono USB (44100 → 16000 Hz)

### Pendientes 📝
- **Llamadas y WhatsApp** - Integración HFP y WebWhatsApp
- **UI unificada** - Launcher central con pantalla táctil

---

## 🎯 Fases del proyecto

| Fase | Descripción | Estado |
|------|-------------|--------|
| **Fase 1** | Bluetooth HFP/AVRCP con BlueALSA | ✅ Completada |
| **Fase 2** | Reproductor VLC + Radio (mpv) | ✅ Completada |
| **Fase 3** | GPS en kiosco (Firefox + Maps/Waze) | ✅ Completada |
| **Fase 4** | Control por voz offline con Vosk | 🔄 En progreso |
| **Fase 5** | Llamadas y WhatsApp | 📝 Pendiente |
| **Fase 6** | UI unificada y pantalla táctil | 📝 Pendiente |

---

## 💻 Requisitos hardware

### Sistema base
- **Raspberry Pi 3** (o superior)
- **Raspberry Pi OS Bookworm** (con Wayland)
- **Alimentación** 5V/2.5A con protección para vibraciones

### Periféricos (según fase)
| Componente | Modelo | Fase | Notas |
|-----------|--------|------|-------|
| Dongle Bluetooth | CSR8510 | 1 | El chip Pi 3 no soporta HFP/SCO |
| Micrófono USB | C-Media USB Headphone Set | 4 | Card 2, device index 1 |
| Altavoz/Intercomunicador | Q7 HSP+HFP | 1 | Probado y verificado |
| Pantalla | Cualquier HDMI | 3/6 | Recomendado: 5-7" para moto |
| GPS Móvil | Cualquier teléfono | 3 | Hotspot USB tethering |

---

## 🚀 Instalación rápida

### 1. Preparar el sistema
```bash
sudo apt update
sudo apt install -y python3-pip python3-venv vlc mpv firefox espeak-ng alsamixer socat
sudo apt install -y bluez bluealsa libbluealsa
```

### 2. Clonar el repositorio
```bash
git clone https://github.com/zpma82/TalkAndTrack.git ~/moto-voice
cd ~/moto-voice
```

### 3. Crear entorno virtual de Python
```bash
python3 -m venv venv
source venv/bin/activate
pip install -U pip setuptools wheel
pip install vosk sounddevice pyaudio
```

### 4. Configurar servicios systemd
```bash
sudo cp systemd/moto-voice.service /etc/systemd/system/
sudo cp systemd/vlc-music.service /etc/systemd/system/
sudo cp systemd/bluealsa.service /etc/systemd/system/
sudo cp systemd/bluealsa-aplay.service /etc/systemd/system/
sudo systemctl daemon-reload
```

### 5. Descargar modelo de voz
```bash
mkdir -p model-es
cd model-es
wget https://github.com/alphacep/vosk-model-small-es/releases/download/v0.42/model-es-0.42.zip
unzip model-es-0.42.zip
cd ..
```

### 6. Iniciar servicios
```bash
sudo systemctl enable moto-voice vlc-music bluealsa bluealsa-aplay
sudo systemctl start moto-voice
```

---

## ⚙️ Configuración

### config.json
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

### Cambiar palabra de activación
```bash
./scripts/set-wakeword.sh "nueva-palabra"
```

### Configurar Bluetooth
```bash
# Ver dispositivos disponibles
bluetoothctl scan on

# Conectar intercomunicador
bluetoothctl connect 00:12:6F:64:39:12

# Ver estado de PCMs activos
alsamixer -c 2
```

### Ajustar micrófono USB
```bash
alsamixer -c 2
# Usar F4 para ver controles de captura
# Ajustar nivel a 44
```

---

## 📁 Estructura del proyecto

```
TalkAndTrack/
├── moto-voice.py                 # Script principal de control por voz
├── config.json                   # Configuración global
├── radios_espana.m3u             # Lista de emisoras (streaming)
│
├── commands/                     # Comandos por aplicación
│   ├── cmd_musica.json          # Control VLC
│   ├── cmd_radio.json           # Control mpv (radio)
│   ├── cmd_gps.json             # Firefox + Maps/Waze
│   └── cmd_sistema.json         # Apagar, reiniciar, etc.
│
├── ui/                          # Interfaces web
│   ├── launch-gps.sh            # Script para lanzar GPS
│   └── gps.html                 # Selector Google Maps / Waze
│
├── scripts/                     # Herramientas de configuración
│   ├── set-wakeword.sh          # Cambiar palabra de activación
│   └── add-app-commands.sh      # Wizard para añadir apps
│
├── systemd/                     # Servicios systemd
│   ├── moto-voice.service       # Servicio principal de voz
│   ├── vlc-music.service        # Demonio VLC
│   ├── bluealsa.service         # Proxy de audio Bluetooth
│   └── bluealsa-aplay.service   # Reproducción Bluetooth
│
├── docs/                        # Documentación
│   ├── INSTALACION.md           # Guía de instalación detallada
│   ├── TROUBLESHOOTING.md       # Resolución de problemas
│   ├── FASE1-BLUETOOTH.md       # Documentación Bluetooth HFP
│   ├── FASE2-MULTIMEDIA.md      # VLC y radio
│   ├── FASE3-GPS.md             # GPS en kiosco
│   └── FASE4-VOZ.md             # Control por voz Vosk
│
├── .github/
│   └── workflows/               # CI/CD (futuro)
│
├── LICENSE                      # MIT License
└── README.md                    # Este archivo
```

---

## 🎤 API de comandos

### Estructura JSON
Cada archivo de comandos define un app y sus acciones:

```json
{
  "app": "nombre_app",
  "descripcion": "Descripcion breve",
  "comandos": [
    {
      "frases": ["frase 1", "frase 2"],
      "accion": "nombre_accion",
      "script": "comando shell a ejecutar"
    }
  ]
}
```

### Ejemplos

#### Música (VLC HTTP)
```bash
# Play
curl -u :motovlc2026 'http://localhost:8080/requests/status.json?command=pl_play'

# Pausar
curl -u :motovlc2026 'http://localhost:8080/requests/status.json?command=pl_pause'

# Siguiente
curl -u :motovlc2026 'http://localhost:8080/requests/status.json?command=pl_next'

# Volumen +20
curl -u :motovlc2026 'http://localhost:8080/requests/status.json?command=volume&val=+20'
```

#### Radio (mpv socket)
```bash
# Cargar emisora
echo '{"command": ["loadfile", "https://radiourl.mp3"]}' | socat - /tmp/mpvsocket

# Pausar/reanudar
echo '{"command": ["cycle", "pause"]}' | socat - /tmp/mpvsocket

# Parar
echo '{"command": ["stop"]}' | socat - /tmp/mpvsocket
```

#### Añadir comando personalizado
```bash
./scripts/add-app-commands.sh
```

---

## 🎙️ Control por voz

### Palabra de activación
Por defecto: **"hola"**

Después de decir la palabra de activación, el sistema responde "Dime" y espera el comando.

### Comandos disponibles

#### Música
- "reproducir", "play" → iniciar VLC
- "pausa", "pausar", "para" → pausar
- "siguiente", "saltar" → siguiente tema
- "anterior", "volver" → tema anterior
- "sube volumen", "más volumen" → aumentar volumen
- "baja volumen", "menos volumen" → reducir volumen

#### Radio
- "pon la radio", "radio" → RNE
- "pon la cope", "cope" → Cadena COPE
- "pon onda cero", "onda cero" → Onda Cero
- "parar radio", "silencio radio" → detener

#### GPS
- "mapas", "google maps" → Google Maps
- "waze" → Waze
- "cierra gps", "cierra mapas" → cerrar GPS

#### Sistema
- "apagar", "apaga" → apagar Pi
- "reiniciar", "reinicia" → reiniciar
- "hora", "qué hora es" → leer hora
- "volumen arriba" → aumentar volumen sistema
- "volumen abajo" → reducir volumen sistema

### Logs
```bash
# Ver logs en tiempo real
tail -f ~/moto-voice/voice.log

# Ver logs del servicio
journalctl -u moto-voice -f
```

---

## 🔧 Troubleshooting

### Micrófono no se detecta
```bash
# Listar dispositivos de audio
arecord -l

# Ver tarjeta específica
alsamixer -c 2

# Probar captura
arecord -D plughw:2,0 -f S16_LE -r 16000 -q test.wav
```

### VLC no inicia
```bash
# Probar manualmente
cvlc --intf http --http-password motovlc2026 --http-port 8080 /home/jesus/Musica

# Ver servicio
systemctl status vlc-music
journalctl -u vlc-music -f
```

### Bluetooth sin audio
```bash
# Verificar BlueALSA
systemctl status bluealsa
systemctl status bluealsa-aplay

# Deshabilitar PipeWire Bluetooth
mkdir -p ~/.config/wireplumber/wireplumber.conf.d
cat > ~/.config/wireplumber/wireplumber.conf.d/51-disable-bluetooth.conf << EOF
wireplumber.profiles = { main = { monitor.bluez = disabled } }
EOF

systemctl --user restart wireplumber pipewire
```

### Firefox no abre GPS
```bash
# Verificar que labwc está en uso
echo $XDG_SESSION_TYPE  # Debe mostrar "wayland"

# Lanzar manualmente
firefox --kiosk file:///home/jesus/moto-ui/gps.html
```

### Vosk no reconoce comandos
1. Verificar que el modelo está descargado: `ls ~/moto-voice/model-es/`
2. Comprobar umbral de confianza en `config.json` (por defecto 0.7)
3. Revisar logs: `tail -f ~/moto-voice/voice.log`
4. Probar con micrófono más cercano a la boca

---

## 📝 Documentación completa

Consulta las guías detalladas en `/docs/`:
- [Instalación paso a paso](docs/INSTALACION.md)
- [Resolución de problemas](docs/TROUBLESHOOTING.md)
- [Fase 1: Bluetooth HFP](docs/FASE1-BLUETOOTH.md)
- [Fase 2: Multimedia](docs/FASE2-MULTIMEDIA.md)
- [Fase 3: GPS](docs/FASE3-GPS.md)
- [Fase 4: Control por voz](docs/FASE4-VOZ.md)

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Para cambios importantes:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/mejora`)
3. Commit tus cambios (`git commit -m 'Agrega mejora'`)
4. Push a la rama (`git push origin feature/mejora`)
5. Abre un Pull Request

### Áreas donde se buscan contribuciones:
- Remuestreo de audio USB (44100 → 16000 Hz) con numpy/scipy
- Interfaz web para launcher unificado (Flask/FastAPI)
- UI táctil optimizada para pantallas pequeñas
- Integración de WhatsApp Web
- Soporte para otros idiomas

---

## 📄 Licencia

Este proyecto está bajo licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

---

## 👤 Autor

**Jesús** - Desarrollo y documentación

---

## 🔗 Enlaces útiles

- **Vosk** - Reconocimiento de voz offline: https://alphacephei.com/vosk/
- **BlueALSA** - Proxy de audio Bluetooth: https://github.com/arkq/bluez-alsa
- **VLC** - Reproductor multimedia: https://www.videolan.org/
- **mpv** - Reproductor de vídeo: https://mpv.io/
- **Raspberry Pi OS** - Sistema operativo: https://www.raspberrypi.org/software/

---

**Última actualización:** Agosto 2024  
**Estado del proyecto:** En desarrollo activo

