# 🎵 Fase 2: Multimedia - VLC + Radio - TalkAndTrack

Control de reproducción de música local (VLC) y radio por internet (mpv).

---

## 📌 Visión general

**Objetivo:** Proporcionar dos sistemas complementarios:
1. **VLC en headless** - Reproductor de música local con API HTTP
2. **mpv en socket IPC** - Reproductor de radio por internet

```
┌──────────────────────────────┐
│   Sistema Multimedia          │
├──────────────────────────────┤
│                               │
│  MÚSICA LOCAL                 │
│  ├─ VLC (puerto 8080)        │
│  ├─ API REST HTTP             │
│  ├─ Control por curl/Python   │
│  └─ Playlist local            │
│                               │
│  +                            │
│                               │
│  RADIO POR INTERNET           │
│  ├─ mpv (socket IPC)          │
│  ├─ Comandos JSON             │
│  ├─ Streaming directo         │
│  └─ +20 emisoras españolas    │
│                               │
│  =                            │
│  Audio MPEGTS/ALSA ─→ Altavoz │
│                               │
└──────────────────────────────┘
```

---

## 🎵 VLC - Reproductor de música local

### Instalación

```bash
sudo apt install -y vlc vlc-plugin-base
```

### Lanzar manualmente (pruebas)

```bash
# Con interfaz HTTP en puerto 8080
cvlc --intf http --http-password motovlc2026 --http-port 8080 /home/jesus/Musica

# Flags importantes:
# --intf http        : Interfaz HTTP
# --http-password X  : Contraseña (motovlc2026)
# --http-port 8080   : Puerto HTTP
# --no-video         : Sin salida de video (headless)
# /ruta/musica       : Directorio con archivos
```

### Preparar carpeta de música

```bash
# Crear estructura
mkdir -p ~/Musica
mkdir -p ~/Musica/{Pop,Rock,Clasica,Podcast}

# Copiar tus archivos
cp /ruta/descarga/*.mp3 ~/Musica/
cp /ruta/descarga/*.flac ~/Musica/

# Verificar
ls -la ~/Musica/ | head -10
```

### Configurar servicio systemd

```bash
sudo tee /etc/systemd/system/vlc-music.service > /dev/null << 'EOF'
[Unit]
Description=VLC headless music engine
After=sound.target bluetooth.service

[Service]
Type=simple
User=jesus
ExecStart=/usr/bin/cvlc --intf http --http-password motovlc2026 --http-port 8080 --no-video /home/jesus/Musica
Restart=on-failure
RestartSec=5
Environment=DISPLAY=:0

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable vlc-music
# NO iniciar aún (se inicia a demanda)
```

### API HTTP de VLC

#### Estructura de URLs
```
http://usuario:password@localhost:puerto/requests/request.json?comando=accion&parametros
```

#### Comandos principales

**Reproducir/Pausar**
```bash
# Play
curl -u :motovlc2026 'http://localhost:8080/requests/status.json?command=pl_play'

# Pause
curl -u :motovlc2026 'http://localhost:8080/requests/status.json?command=pl_pause'

# Toggle play/pause
curl -u :motovlc2026 'http://localhost:8080/requests/status.json?command=pl_togglepause'
```

**Navegación de lista**
```bash
# Siguiente track
curl -u :motovlc2026 'http://localhost:8080/requests/status.json?command=pl_next'

# Anterior track
curl -u :motovlc2026 'http://localhost:8080/requests/status.json?command=pl_previous'

# Ir a posición específica (índice 0-based)
curl -u :motovlc2026 'http://localhost:8080/requests/status.json?command=pl_play&id=3'
```

**Volumen**
```bash
# Obtener volumen actual
curl -s -u :motovlc2026 'http://localhost:8080/requests/status.json' | grep -o '"volume":[0-9]*'

# Set volumen (0-256)
curl -u :motovlc2026 'http://localhost:8080/requests/status.json?command=volume&val=128'

# Aumentar volumen +20
curl -u :motovlc2026 'http://localhost:8080/requests/status.json?command=volume&val=+20'

# Bajar volumen -20
curl -u :motovlc2026 'http://localhost:8080/requests/status.json?command=volume&val=-20'
```

**Información**
```bash
# Estado actual (JSON)
curl -s -u :motovlc2026 'http://localhost:8080/requests/status.json' | jq .

# Playlist actual
curl -s -u :motovlc2026 'http://localhost:8080/requests/playlist.json' | jq '.children[0].children'

# Información del track actual
curl -s -u :motovlc2026 'http://localhost:8080/requests/status.json' | jq '.information.category'
```

#### Ejemplo de respuesta JSON
```json
{
  "fullscreen": false,
  "stats": { "inputbitrate": 0, "demuxbitrate": 0, ... },
  "currentplid": 1,
  "time": 0,
  "position": 0.0,
  "duration": 285,
  "loop": false,
  "rate": 1.0,
  "state": "playing",
  "volume": 256,
  "length": 45,
  "information": { ... },
  "ERROR": false
}
```

### Script de control en Python

```python
#!/usr/bin/env python3
import requests
from urllib.parse import urlencode

class VLCControl:
    def __init__(self, host='localhost', port=8080, password='motovlc2026'):
        self.base_url = f'http://{host}:{port}/requests'
        self.auth = ('', password)
    
    def play(self):
        return self._command('pl_play')
    
    def pause(self):
        return self._command('pl_pause')
    
    def next(self):
        return self._command('pl_next')
    
    def prev(self):
        return self._command('pl_previous')
    
    def volume_up(self, amount=20):
        return self._command('volume', f'+{amount}')
    
    def volume_down(self, amount=20):
        return self._command('volume', f'-{amount}')
    
    def _command(self, command, val=None):
        params = {'command': command}
        if val:
            params['val'] = val
        url = f'{self.base_url}/status.json?{urlencode(params)}'
        response = requests.get(url, auth=self.auth)
        return response.json()

# Usar
vlc = VLCControl()
vlc.play()
vlc.volume_up()
vlc.next()
```

---

## 📻 mpv - Radio por internet

### Instalación

```bash
sudo apt install -y mpv socat
```

### Iniciar mpv con socket IPC

```bash
# Modo idle con socket IPC
mpv --idle --input-ipc-server=/tmp/mpvsocket

# Nota: moto-voice.py lo lanza automáticamente
```

### Enviar comandos a mpv

Todos los comandos van en formato JSON al socket:

```bash
# Cargar URL de emisora
echo '{"command": ["loadfile", "https://radiourl.mp3"]}' | socat - /tmp/mpvsocket

# Pausar/reanudar
echo '{"command": ["cycle", "pause"]}' | socat - /tmp/mpvsocket

# Parar reproducción
echo '{"command": ["stop"]}' | socat - /tmp/mpvsocket

# Cambiar volumen (0-100)
echo '{"command": ["set", "volume", 50]}' | socat - /tmp/mpvsocket

# Mute/Unmute
echo '{"command": ["cycle", "mute"]}' | socat - /tmp/mpvsocket

# Quit (salir)
echo '{"command": ["quit"]}' | socat - /tmp/mpvsocket
```

### Emisoras españolas

#### Archivo: `radios_espana.m3u`

```m3u
#EXTM3U
#EXTINF:-1,RNE Radio Nacional
http://dispatcher.rndfnk.com/rtve/rne/radio1/mp3/high

#EXTINF:-1,Cadena SER
https://playerservices.streamtheworld.com/api/livestream-redirect/SER.mp3

#EXTINF:-1,COPE
https://flucast2-cope.flumotion.com/cope/cope.mp3

#EXTINF:-1,Los 40
https://22653.live.streamtheworld.com/LOS40.mp3

#EXTINF:-1,Cadena Dial
https://22323.live.streamtheworld.com/CADENADIAL.mp3

#EXTINF:-1,Onda Cero
https://onaire-ondacero.flumotion.com/ondacero/audio.mp3

#EXTINF:-1,Europa FM
https://22893.live.streamtheworld.com/EUROPA_FM.mp3

#EXTINF:-1,Virgin Radio
https://virginradio.streamingparadise.com/virginradio

#EXTINF:-1,Radio Marca
https://playerservices.streamtheworld.com/api/livestream-redirect/RADIOMARCO.mp3

#EXTINF:-1,Radio Olé
https://playerservices.streamtheworld.com/api/livestream-redirect/RADIOLERADIO.mp3
```

#### Prueba de conexión

```bash
# Comprobar que URL responde
curl -I https://playerservices.streamtheworld.com/api/livestream-redirect/SER.mp3
# Debe devolver: HTTP/2 200 o 206

# Probar con mpv directamente
mpv "https://playerservices.streamtheworld.com/api/livestream-redirect/SER.mp3"
# Debe reproducir por 5 segundos y cerrarse
```

### Script de control en Python

```python
#!/usr/bin/env python3
import json
import socket
import time

class MpvRadio:
    def __init__(self, socket_path='/tmp/mpvsocket'):
        self.socket_path = socket_path
    
    def send_command(self, cmd):
        """Envía comando JSON a mpv"""
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(self.socket_path)
            sock.sendall(json.dumps(cmd).encode() + b'\n')
            sock.close()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def load(self, url):
        """Cargar emisora"""
        return self.send_command({"command": ["loadfile", url]})
    
    def pause(self):
        """Pausar/reanudar"""
        return self.send_command({"command": ["cycle", "pause"]})
    
    def stop(self):
        """Detener"""
        return self.send_command({"command": ["stop"]})
    
    def set_volume(self, level):
        """Establecer volumen (0-100)"""
        return self.send_command({"command": ["set", "volume", level]})
    
    def mute(self):
        """Silenciar"""
        return self.send_command({"command": ["cycle", "mute"]})

# Usar
radio = MpvRadio()
radio.load("https://playerservices.streamtheworld.com/api/livestream-redirect/SER.mp3")
time.sleep(1)
radio.pause()
```

---

## 🎚️ Integración audio ALSA

### Vista general de dispositivos

```bash
arecord -l   # Entrada
aplay -l     # Salida
```

### Mezcla de audio (ALSA)

VLC + mpv + Vosk pueden reproducir simultáneamente gracias a ALSA:

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│    VLC      │  │    mpv      │  │   Vosk      │
│   Música    │  │    Radio    │  │   Voz       │
└────────┬────┘  └────────┬────┘  └────────┬────┘
         │               │               │
         └───────────────┼───────────────┘
                         │
                    ┌────▼────┐
                    │  ALSA   │
                    │ Mezcla  │
                    └────┬────┘
                         │
                    ┌────▼────────────┐
                    │  Altavoz/Bluetooth │
                    └─────────────────┘
```

### Fader de volumen maestro

```bash
# Ver controles
alsamixer

# Subir Master (afecta a todo)
amixer set Master 10%+

# Bajar Master
amixer set Master 10%-

# Mute Master
amixer set Master toggle

# Ver niveles
amixer sget Master
```

---

## 🔧 Troubleshooting Multimedia

### VLC no inicia

```bash
# 1. Probar manualmente
/usr/bin/cvlc --intf http --http-password motovlc2026 --http-port 8080 --no-video ~/Musica 2>&1

# 2. Ver logs del servicio
journalctl -u vlc-music -n 50

# 3. Verificar puerto disponible
sudo lsof -i :8080

# 4. Si puerto en uso, cambiar:
sudo nano /etc/systemd/system/vlc-music.service
# Cambiar puerto a 8081, 8082, etc.

# 5. Recargar
sudo systemctl daemon-reload
sudo systemctl restart vlc-music
```

### Radio no reproduce

```bash
# 1. Verificar conexión
ping 8.8.8.8

# 2. Verificar URL
curl -I "https://playerservices.streamtheworld.com/api/livestream-redirect/SER.mp3"

# 3. Probar con mpv directamente
mpv "URL" -v

# 4. Ver logs
journalctl -u moto-voice | grep mpv

# 5. Reiniciar socket
pkill mpv
# moto-voice.py lo reinicia automáticamente
```

### Sin sonido desde VLC/mpv

```bash
# 1. Verificar dispositivo de salida
aplay -l

# 2. Ajustar volumen
alsamixer

# 3. Ver si está muteado
amixer sget Master

# 4. Desmutar
amixer set Master unmute

# 5. Subir volumen
amixer set Master 100%
```

---

## 📊 Monitoreo de sistema

### Ver procesos multimedia

```bash
# VLC
ps aux | grep cvlc

# mpv
ps aux | grep mpv

# ALSA
ps aux | grep alsa
```

### Ver uso de recursos

```bash
# Tiempo real
top -p $(pgrep -f "cvlc|mpv" | tr '\n' ',')

# Una snapshot
ps aux | grep -E "cvlc|mpv" | grep -v grep
```

### Ver estadísticas de red

```bash
# Conexiones activas
netstat -i

# Uso de ancho de banda
iftop  # Requiere apt install iftop
```

---

## 📝 Referencia de comandos mpv

Documentación completa: https://mpv.io/manual/stable/

```
# Comandos disponibles
loadfile <file>              Cargar archivo/URL
stop                         Detener reproducción
cycle pause                  Pausar/reanudar
set volume <0-100>          Volumen
cycle mute                   Silenciar/dessilenciar
set playback-speed <speed>   Velocidad (0.25-4.0)
seek <seconds>              Buscar posición
set fullscreen yes/no       Pantalla completa
show-text <text>            Mostrar texto en pantalla
```

---

## ✅ Checklist Fase 2

- [x] VLC instalado y funcionando
- [x] mpv instalado y funcionando
- [x] API HTTP de VLC accesible
- [x] Socket IPC de mpv funcionando
- [x] Archivos de música en ~/Musica
- [x] Emisoras en radios_espana.m3u
- [x] Servicios systemd configurados
- [x] Audio enrutado correctamente

---

**Estado:** ✅ Fase 2 completada  
**Siguiente:** [Fase 3 - GPS](FASE3-GPS.md)

