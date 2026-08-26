# ⚡ Quick Start - TalkAndTrack

Empieza en 5 minutos (instalación básica + primera prueba).

---

## 🚀 TL;DR - Instalación rápida

### 1️⃣ Requisitos previos
```bash
# Raspberry Pi 3 con:
# - Raspberry Pi OS Bookworm
# - Conexión a internet
# - Usuario con sudo
# - Dongle Bluetooth USB (para Fase 1)
# - Micrófono USB (para Fase 4)
```

### 2️⃣ Clonar y entrar
```bash
cd ~
git clone https://github.com/zpma82/TalkAndTrack.git moto-voice
cd moto-voice
```

### 3️⃣ Instalar dependencias (2 minutos)
```bash
sudo apt update
sudo apt install -y python3-venv python3-pip vlc mpv firefox \
    espeak-ng bluez bluealsa alsa-utils portaudio19-dev socat

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar Python packages
pip install -U pip setuptools wheel
pip install vosk sounddevice pyaudio
```

### 4️⃣ Descargar modelo de voz (2 minutos)
```bash
mkdir -p model-es
cd model-es
wget https://github.com/alphacep/vosk-model-small-es/releases/download/v0.42/model-es-0.42.zip
unzip model-es-0.42.zip
rm model-es-0.42.zip
cd ..
```

### 5️⃣ Configurar servicios (1 minuto)
```bash
# Copiar archivos systemd
sudo cp systemd/moto-voice.service /etc/systemd/system/
sudo cp systemd/bluealsa.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable moto-voice bluealsa
```

### 6️⃣ Primera prueba ✅
```bash
# Iniciar
sudo systemctl start moto-voice

# Ver logs
journalctl -u moto-voice -f

# Debe mostrar: "Sistema de voz listo"
# Presionar Ctrl+C para salir
```

---

## 🎤 Primera prueba de voz

### Prueba 1: Micrófono

```bash
# Ver dispositivos de audio
arecord -l

# Busca tu micrófono USB (ej: "card 2")
# Anota el número en config.json → "audio_device": 1
```

### Prueba 2: Vosk reconoce

```bash
# Activar venv
cd ~/moto-voice
source venv/bin/activate

# Ejecutar manual (para debug)
python3 moto-voice.py

# Habla:
# "Hola" (palabra de activación)
# Sistema responde: "Dime"
# "Reproducir" (comando)
# Sistema responde: "play"

# Presionar Ctrl+C para salir
```

### Prueba 3: VLC reproduce

```bash
# Copiar música
mkdir -p ~/Musica
cp ~/Downloads/*.mp3 ~/Musica/ 2>/dev/null || echo "Agrega MP3 a ~/Musica/"

# Iniciar servicio VLC
sudo systemctl start vlc-music
sleep 2

# Probar API
curl -u :motovlc2026 'http://localhost:8080/requests/status.json?command=pl_play'
```

### Prueba 4: Bluetooth

```bash
# Conectar dispositivo Bluetooth
bluetoothctl

# En bluetoothctl:
scan on
# Esperar a ver tu dispositivo
pair DEVICE_MAC
connect DEVICE_MAC
exit

# Verificar
alsamixer -c 0
```

### Prueba 5: GPS abre

```bash
# Lanzar GPS
./ui/launch-gps.sh

# Debería abrir Firefox con dos botones (Maps/Waze)
# Presionar Alt+F4 para cerrar
```

---

## 📝 Configuración básica

### Cambiar palabra de activación

```bash
./scripts/set-wakeword.sh "jesus"
# Ahora di "jesus" en lugar de "hola"
```

### Añadir emisora de radio

```bash
nano radios_espana.m3u

# Añadir al final:
# #EXTINF:-1,Mi Emisora
# https://mi-url-streaming.com/stream.mp3
```

### Crear nuevo comando

```bash
# Asistente interactivo
./scripts/add-app-commands.sh

# O editar JSON directamente
nano commands/cmd_musica.json
```

---

## 🐛 Troubleshooting rápido

### No reconoce voz
```bash
# 1. Aumentar volumen micrófono
alsamixer -c 2
# (Presionar F4, subir "Mic" a 60-70)

# 2. Reducir umbral de confianza
nano config.json
# Cambiar "confidence_threshold": 0.7 → 0.5

# 3. Reiniciar
sudo systemctl restart moto-voice
```

### VLC no funciona
```bash
# Verificar puerto
curl http://localhost:8080/requests/status.json

# Si error, reiniciar
sudo systemctl restart vlc-music
```

### Sin audio Bluetooth
```bash
# Verificar BlueALSA
systemctl status bluealsa

# Recargar todo
sudo systemctl restart bluetooth bluealsa
```

### Firefox no abre GPS
```bash
# Probar manualmente
firefox --kiosk file:///home/jesus/moto-ui/gps.html

# Si falla, intentar con software rendering
LIBGL_ALWAYS_SOFTWARE=1 firefox --kiosk file:///home/jesus/moto-ui/gps.html
```

---

## 📊 Ver estado del sistema

```bash
# ¿Qué está corriendo?
systemctl status moto-voice vlc-music bluealsa

# ¿Qué errores hay?
journalctl -u moto-voice -p err

# ¿Último comando ejecutado?
tail -n 10 ~/moto-voice/voice.log

# ¿Micrófono funciona?
arecord -D plughw:2,0 -f S16_LE -r 16000 -q -t wav /tmp/test.wav
# (Habla 5 segundos, Ctrl+C)
aplay /tmp/test.wav

# ¿Dispositivos de audio?
aplay -l
arecord -l
```

---

## 🎯 Comandos disponibles (sin configurar)

### Música
```
"reproducir", "play", "música"
"pausa", "pausar"
"siguiente", "anterior"
"volumen arriba", "volumen abajo"
```

### Radio
```
"pon la radio"
"pon la cope", "pon onda cero"
"parar radio"
```

### GPS
```
"mapas", "waze"
"cierra gps"
```

### Sistema
```
"apagar", "reiniciar"
"hora"
```

---

## 📚 Documentación completa

| Tema | Archivo |
|------|---------|
| Overview | [README.md](README.md) |
| Instalación paso a paso | [INSTALACION.md](INSTALACION.md) |
| Troubleshooting | [TROUBLESHOOTING.md](TROUBLESHOOTING.md) |
| Bluetooth HFP | [FASE1-BLUETOOTH.md](FASE1-BLUETOOTH.md) |
| VLC + Radio | [FASE2-MULTIMEDIA.md](FASE2-MULTIMEDIA.md) |
| GPS Kiosco | [FASE3-GPS.md](FASE3-GPS.md) |
| Vosk Voz | [FASE4-VOZ.md](FASE4-VOZ.md) |
| Contribuir | [CONTRIBUTING.md](CONTRIBUTING.md) |
| Cambios | [CHANGELOG.md](CHANGELOG.md) |

---

## ⏱️ Timeline esperado

```
Tiempo      Tarea
────────────────────────────────────────
0:00-0:30   Instalación dependencias
0:30-1:00   Descargar modelo Vosk
1:00-1:05   Configurar systemd
1:05-1:15   Primera prueba de voz
1:15-1:30   Probar VLC/Radio
1:30-1:45   Conectar Bluetooth
1:45-2:00   Probar GPS
────────────────────────────────────────
TOTAL:      ~2 horas (primera vez)
```

---

## ✅ Checklist de verificación

- [ ] Micrófono detectado (`arecord -l`)
- [ ] Vosk reconoce voz (`python3 moto-voice.py`)
- [ ] VLC responde (`curl http://localhost:8080/...`)
- [ ] Bluetooth conectado (`bluetoothctl paired-devices`)
- [ ] GPS abre (`./ui/launch-gps.sh`)
- [ ] Servicio activo (`systemctl status moto-voice`)
- [ ] Logs limpios (`journalctl -u moto-voice | tail`)

---

## 🆘 SOS rápido

```bash
# Nuclear option: Reiniciar TODO
sudo systemctl stop moto-voice vlc-music bluealsa
sleep 2
sudo systemctl start bluealsa moto-voice
journalctl -u moto-voice -f

# Ver qué proceso está fallando
ps aux | grep -E "vosk|vlc|mpv|firefox"

# Limpiar logs viejos
> ~/moto-voice/voice.log

# Ver error systemd
sudo systemctl status moto-voice -l
```

---

## 🎓 Siguientes pasos

1. **Lee** [README.md](README.md) completo
2. **Explora** [INSTALACION.md](INSTALACION.md) para config avanzada
3. **Personaliza** comandos con `add-app-commands.sh`
4. **Lee** documentación de cada fase si necesitas más profundidad
5. **Contribuye** con mejoras (ver [CONTRIBUTING.md](CONTRIBUTING.md))

---

## 💬 Preguntas frecuentes

**P: ¿Necesito internet para usar TalkAndTrack?**  
R: No para voz/música local. Sí para radio/GPS (pero sin datos personales).

**P: ¿Funciona sin el dongle Bluetooth?**  
R: Sí. Fase 4 (voz) funciona sin él. Fases 1-3 sí lo necesitan.

**P: ¿Puedo usar con Pi 4/5?**  
R: Sí, es compatible. Solo revisa rutas de archivos.

**P: ¿Es seguro/privado?**  
R: Sí. Todo local. No se envía audio a servidores.

**P: ¿Cómo agrego mis propios comandos?**  
R: Usar `./scripts/add-app-commands.sh` o editar JSON.

---

¿Listo? 🚀

```bash
cd ~/moto-voice
source venv/bin/activate
python3 moto-voice.py

# ¡Prueba diciendo "hola"!
```

---

**Tiempo estimado hasta primera voz:** 15 minutos  
**Tiempo estimado hasta sistema completo:** 2 horas

¡Buena suerte! 🎉

