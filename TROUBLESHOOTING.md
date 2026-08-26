# 🔧 Troubleshooting - TalkAndTrack

Guía de diagnóstico y resolución de problemas comunes.

---

## 🎤 Problemas de audio y micrófono

### Problema: "No se detecta el micrófono USB"

**Síntomas:**
- `arecord -l` no muestra el dispositivo
- Vosk reporta "No input device"

**Solución:**

```bash
# 1. Verificar que el USB está conectado
lsusb | grep -i media
# Debe mostrar algo como "C-Media Electronics, Inc."

# 2. Verificar que está en la lista de ALSA
arecord -l

# 3. Si aparece, usar número de tarjeta en alsamixer
alsamixer -c 2  # (sustituir 2 por tu número)

# 4. Aumentar volumen de captura a 44
# Presionar F4 para ver captura, navegar con flechas, ajustar con +/-

# 5. Reiniciar servicios de audio
systemctl --user restart pipewire pulseaudio
```

### Problema: "El micrófono suena muy bajo o distorsionado"

**Solución:**

```bash
# 1. Ajustar en alsamixer
alsamixer -c 2
# Aumentar "Mic" o "Capture" gradualmente

# 2. Verificar niveles de entrada en PyAudio
python3 -c "
import pyaudio
pa = pyaudio.PyAudio()
for i in range(pa.get_device_count()):
    print(f'{i}: {pa.get_device_info_by_index(i)}')
"

# 3. Probar grabación
arecord -D plughw:2,0 -f S16_LE -r 16000 -t wav test.wav
# Hablar durante 5 segundos
# Ctrl+C
# Reproducir y escuchar
aplay test.wav
```

### Problema: "No hay sonido en el altavoz/Bluetooth"

**Síntomas:**
- Vosk reconoce pero no reproduce respuesta
- Bluetooth no emite audio

**Solución:**

```bash
# 1. Verificar que BlueALSA está funcionando
systemctl status bluealsa
systemctl status bluealsa-aplay

# 2. Ver dispositivos Bluetooth conectados
alsamixer -c 0

# 3. Verificar PipeWire no interfiere
ps aux | grep -i pipewire

# 4. Si PipeWire interfiere:
mkdir -p ~/.config/wireplumber/wireplumber.conf.d
cat > ~/.config/wireplumber/wireplumber.conf.d/51-disable-bluetooth.conf << EOF
wireplumber.profiles = {
  main = {
    monitor.bluez = disabled
  }
}
EOF

systemctl --user restart wireplumber pipewire pipewire-pulse
systemctl restart bluealsa

# 5. Probar salida con speaker-test
speaker-test -D plughw:Headphones -c 2 -l 5
```

### Problema: "Vosk dice 'confidence too low' constante"

**Síntomas:**
- Reconoce palabras pero siempre reporta confianza baja
- "No entendi el comando" frecuentemente

**Solución:**

```bash
# 1. Reducir umbral de confianza en config.json
nano config.json
# Cambiar "confidence_threshold" de 0.7 a 0.5

# 2. Verificar que el modelo está completo
ls -la ~/moto-voice/model-es/
# Debe contener mfcc.fea, model, etc.

# 3. Aumentar volumen del micrófono
alsamixer -c 2
# Subir "Mic" a 60-70

# 4. Reiniciar el servicio
sudo systemctl restart moto-voice
```

---

## 🔊 Problemas de Bluetooth

### Problema: "El intercomunicador no empareja o desconecta"

**Síntomas:**
- No aparece en `scan on`
- Empareja pero se desconecta inmediatamente
- No funciona HFP (llamadas/micrófono)

**Solución:**

```bash
# 1. Reiniciar Bluetooth
sudo systemctl restart bluetooth

# 2. Verificar configuración main.conf
sudo nano /etc/bluetooth/main.conf
# En [General] debe haber:
# Enable=Source,Sink,Media,Socket,Headset,HandsFree

# 3. Limpiar dispositivos previos
bluetoothctl
paired-devices
remove 00:12:6F:64:39:12  # (sustituir MAC)
exit

# 4. Escanear y emparejar de nuevo
bluetoothctl
scan on
# Esperar a ver el dispositivo
pair 00:12:6F:64:39:12
connect 00:12:6F:64:39:12
trust 00:12:6F:64:39:12
exit

# 5. Verificar conexión SCO (para HFP)
journalctl -u bluetooth -f
```

### Problema: "HFP no funciona (sin audio de llamadas)"

**Síntomas:**
- El dispositivo conecta pero sin HFP
- Dice "HSP" en lugar de "HFP"

**Solución:**

```bash
# 1. Verificar que BlueALSA usa perfil correcto
systemctl status bluealsa | grep profile
# Debe incluir "hfp-ag" (Audio Gateway)

# 2. Editar servicio BlueALSA
sudo nano /etc/systemd/system/bluealsa.service
# ExecStart debe tener: --profile=hfp-ag

# 3. Recargar y reiniciar
sudo systemctl daemon-reload
sudo systemctl restart bluealsa

# 4. Buscar dispositivo que soporte HFP completo
# Dispositivos probados que funcionan: Q7 intercomunicador
```

### Problema: "Conflicto PipeWire vs BlueALSA"

**Síntomas:**
- BlueALSA reporta error
- Audio distorsionado o sin salida
- Múltiples servicios de audio compitiendo

**Solución:**

```bash
# 1. Ver qué está usando Bluetooth
ps aux | grep -E "pipewire|bluetooth|alsa"

# 2. Deshabilitar módulo Bluetooth de WirePlumber
mkdir -p ~/.config/wireplumber/wireplumber.conf.d

cat > ~/.config/wireplumber/wireplumber.conf.d/51-disable-bluetooth.conf << 'EOF'
wireplumber.profiles = {
  main = {
    monitor.bluez = disabled
  }
}
EOF

# 3. Reiniciar servicios de usuario
systemctl --user stop wireplumber pipewire pipewire-pulse
systemctl --user start pipewire

# 4. Reiniciar BlueALSA
sudo systemctl restart bluealsa bluealsa-aplay

# 5. Verificar que funciona
bluetoothctl connect 00:12:6F:64:39:12
```

---

## 🎵 Problemas de VLC

### Problema: "VLC no inicia o falla"

**Síntomas:**
- `systemctl status vlc-music` reporta error
- Puerto 8080 no responde

**Solución:**

```bash
# 1. Probar manualmente
source ~/moto-voice/venv/bin/activate
/usr/bin/cvlc --intf http --http-password motovlc2026 --http-port 8080 --no-video ~/Musica

# 2. Ver errores
journalctl -u vlc-music -n 50

# 3. Verificar puerto disponible
sudo lsof -i :8080

# 4. Si puerto en uso, cambiar en servicio systemd
sudo nano /etc/systemd/system/vlc-music.service
# Cambiar puerto en ExecStart (ej: --http-port 8081)

# 5. Recargar y reiniciar
sudo systemctl daemon-reload
sudo systemctl restart vlc-music
```

### Problema: "Comandos de VLC no funcionan"

**Síntomas:**
- curl devuelve error
- Música no inicia/pausa

**Solución:**

```bash
# 1. Verificar que VLC está corriendo
curl -u :motovlc2026 'http://localhost:8080/requests/status.json'

# 2. Si falla, iniciar manualmente
sudo systemctl start vlc-music
sleep 2

# 3. Probar comando simple
curl -u :motovlc2026 'http://localhost:8080/requests/status.json?command=pl_play'

# 4. Verificar archivos de música
ls -la ~/Musica/
# Debe haber archivos .mp3, .flac, .ogg

# 5. Ver logs detallados
journalctl -u vlc-music -f
```

### Problema: "VLC reconoce música pero no reproduce"

**Síntomas:**
- Lista de reproducción visible
- Sin sonido

**Solución:**

```bash
# 1. Verificar tarjeta de sonido
aplay -l

# 2. Editar servicio para especificar dispositivo
sudo nano /etc/systemd/system/vlc-music.service

# Agregar al ExecStart:
# --aout=alsa --alsa-audio-device=plughw:Headphones

# 3. Probar con salida verbose
/usr/bin/cvlc --intf http --http-password motovlc2026 --http-port 8080 --verbose 2 ~/Musica

# 4. Reiniciar
sudo systemctl daemon-reload
sudo systemctl restart vlc-music
```

---

## 📻 Problemas de radio (mpv)

### Problema: "Socket /tmp/mpvsocket no se crea"

**Síntomas:**
- "No such file or directory" al enviar comandos
- Radio no arranca

**Solución:**

```bash
# 1. Verificar que mpv está instalado
which mpv

# 2. El socket se crea automáticamente al iniciar moto-voice.py
# Verificar que el servicio inicia correctamente
sudo systemctl status moto-voice

# 3. Ver logs
journalctl -u moto-voice -f

# 4. Si falta, crear manualmente
mpv --idle --input-ipc-server=/tmp/mpvsocket &

# 5. Probar comando
echo '{"command": ["loadfile", "https://radiourl.mp3"]}' | socat - /tmp/mpvsocket
```

### Problema: "Emisoras de radio no cargan (error 404)"

**Síntomas:**
- mpv reporta error de URL
- "Connection refused"

**Solución:**

```bash
# 1. Verificar URL es válida
curl -I https://radiourl.mp3
# Debe devolver 200 OK o 206 Partial Content

# 2. Probar con mpv directamente
mpv "https://radiourl.mp3"

# 3. Actualizar radios_espana.m3u con URLs activas
nano radios_espana.m3u

# 4. Verificar conectividad
ping 8.8.8.8

# 5. Ver logs de mpv
journalctl -u moto-voice | grep mpv
```

---

## 🗺️ Problemas de GPS

### Problema: "Firefox no abre o se cierra inmediatamente"

**Síntomas:**
- `launch-gps.sh` no muestra Firefox
- Error de sesión Wayland

**Solución:**

```bash
# 1. Verificar sesión de escritorio
echo $XDG_SESSION_TYPE
# Debe mostrar "wayland"

# 2. Probar Firefox manualmente
firefox --kiosk file:///home/jesus/moto-ui/gps.html

# 3. Ver errores de Firefox
firefox --kiosk file:///home/jesus/moto-ui/gps.html 2>&1

# 4. Si falla OpenGL, usar software rendering
LIBGL_ALWAYS_SOFTWARE=1 firefox --kiosk file:///home/jesus/moto-ui/gps.html

# 5. Editar launch-gps.sh si es necesario
nano ui/launch-gps.sh
# Agregar: export LIBGL_ALWAYS_SOFTWARE=1
```

### Problema: "Maps/Waze no cargan (sin internet)"

**Síntomas:**
- Página blanca
- Error de conexión

**Solución:**

```bash
# 1. Verificar conectividad
ping 8.8.8.8

# 2. Si usa hotspot móvil
nmcli device wifi connect 'SSID' password 'contraseña'

# 3. Si usa USB tethering
sudo dhclient usb0

# 4. Verificar DNS
cat /etc/resolv.conf

# 5. Usar direcciones IP públicas de Google
sudo nano /etc/systemd/resolved.conf
# Agregar:
# DNS=8.8.8.8 8.8.4.4
# FallbackDNS=1.1.1.1

sudo systemctl restart systemd-resolved
```

---

## 🎙️ Problemas de voz

### Problema: "Vosk no se inicia o da error de librería"

**Síntomas:**
- "libvosk.so: cannot execute binary file"
- ImportError: No module named vosk

**Solución:**

```bash
# 1. Verificar versión de Vosk
python3 -c "import vosk; print(vosk.__version__)"

# 2. Problema conocido: execstack en ARM
cd ~/moto-voice/venv/lib/python*/site-packages/vosk/
ls -la libvosk.so

# 3. Instalar patchelf
sudo apt install patchelf

# 4. Limpiar execstack
sudo patchelf --clear-execstack libvosk.so

# 5. Revertir si hay problemas
sudo cp libvosk_backup.so libvosk.so
```

### Problema: "No reconoce la palabra de activación"

**Síntomas:**
- Dice "Dime" después de cualquier audio
- No detecta wakeword

**Solución:**

```bash
# 1. Verificar configuración
cat config.json | grep wakeword
# Debe mostrar tu palabra (ej: "hola", "jesus", etc.)

# 2. Ver logs de reconocimiento
tail -f ~/moto-voice/voice.log

# 3. Probar con palabra más clara y larga
./scripts/set-wakeword.sh "picaros"  # Palabra de 2 sílabas clara

# 4. Aumentar umbral de confianza si hay falsos positivos
nano config.json
# Cambiar "confidence_threshold" a 0.8-0.9

# 5. Reiniciar servicio
sudo systemctl restart moto-voice
```

### Problema: "Los comandos no se ejecutan"

**Síntomas:**
- Vosk reconoce ("No entendi el comando")
- Archivos de comandos existentes

**Solución:**

```bash
# 1. Verificar que archivos de comandos existen
ls -la ~/moto-voice/commands/
# Debe haber cmd_*.json

# 2. Verificar que JSON es válido
python3 -m json.tool ~/moto-voice/commands/cmd_musica.json

# 3. Ver logs de comandos
tail -f ~/moto-voice/voice.log | grep -i "ejecut"

# 4. Probar comando manualmente
bash -x "curl -s -u :motovlc2026 'http://localhost:8080/requests/status.json?command=pl_play'"

# 5. Ver permisos de ejecución
chmod +x ~/moto-voice/moto-voice.py

# 6. Reiniciar servicio
sudo systemctl restart moto-voice
```

---

## 🖥️ Problemas de sistema

### Problema: "servicio moto-voice no inicia"

**Síntomas:**
- `systemctl status moto-voice` = failed
- journalctl muestra error

**Solución:**

```bash
# 1. Ver error detallado
journalctl -u moto-voice -n 100

# 2. Probar script manualmente
source ~/moto-voice/venv/bin/activate
python3 ~/moto-voice/moto-voice.py

# 3. Verificar permisos
chmod +x ~/moto-voice/moto-voice.py

# 4. Ver que usuario ejecuta el servicio
cat /etc/systemd/system/moto-voice.service | grep User

# 5. Probar con sudo
sudo systemctl status moto-voice -l

# 6. Editar servicio si es necesario
sudo nano /etc/systemd/system/moto-voice.service
sudo systemctl daemon-reload
sudo systemctl restart moto-voice
```

### Problema: "Raspberry Pi muy lenta o se queda colgada"

**Síntomas:**
- Alto uso de CPU/RAM
- Lag en respuestas

**Solución:**

```bash
# 1. Ver procesos que consumen recursos
top -b -n 1 | head -20

# 2. Ver memoria disponible
free -h

# 3. Ver temperatura
vcgencmd measure_temp

# 4. Si temperatura > 80°C
# - Reducir velocidad de GPU en /boot/config.txt
# - Mejorar refrigeración

# 5. Ver servicios innecesarios
systemctl list-units --type=service --state=running

# 6. Desabilitar servicios que no usas
sudo systemctl disable cups avahi-daemon  # Ejemplos
```

---

## 📊 Script de diagnóstico automático

Crear `diagnose.sh`:

```bash
#!/bin/bash

echo "=== DIAGNOSTICO TALKANDTRACK ==="
echo ""

echo "1. Python y venv"
python3 --version
if [ -d "venv" ]; then
    echo "✓ Venv existe"
else
    echo "✗ Venv NO existe"
fi
echo ""

echo "2. Modelos y configuración"
ls -la model-es/ 2>/dev/null | wc -l
echo "Archivos config.json: $(wc -l < config.json)"
echo ""

echo "3. Servicios systemd"
systemctl is-active moto-voice
systemctl is-active vlc-music
systemctl is-active bluealsa
echo ""

echo "4. Audio"
echo "Dispositivos ALSA:"
arecord -l | head -5
echo ""

echo "5. Bluetooth"
bluetoothctl paired-devices
echo ""

echo "6. Puertos en uso"
sudo lsof -i -P -n 2>/dev/null | grep LISTEN
echo ""

echo "7. Logs recientes"
echo "--- moto-voice ---"
journalctl -u moto-voice -n 3 --no-pager
echo ""
echo "--- vlc-music ---"
journalctl -u vlc-music -n 3 --no-pager
```

Usar:
```bash
chmod +x diagnose.sh
./diagnose.sh
```

---

¿Aún hay problemas? Abre un issue en GitHub con la salida de `diagnose.sh`.

