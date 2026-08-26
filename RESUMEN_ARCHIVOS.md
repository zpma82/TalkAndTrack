# 📋 Resumen de archivos - TalkAndTrack

Guía rápida de qué es cada archivo y carpeta.

---

## 📂 Estructura principal

### Scripts principales
- **`moto-voice.py`** - Script principal de reconocimiento de voz
  - Lee audio del micrófono
  - Reconoce comandos con Vosk
  - Ejecuta scripts bash correspondientes
  - Responde por voz
  - **Usar:** `python3 moto-voice.py` o vía `systemctl`

### Configuración
- **`config.json`** - Configuración del sistema de voz
  - Palabra de activación
  - Ruta del modelo de Vosk
  - Dispositivo de audio
  - Umbrales de confianza
  - Comando de síntesis de voz
  - **Editar:** `nano config.json`

- **`requirements.txt`** - Dependencias Python
  - Vosk, pyaudio, requests, etc.
  - **Instalar:** `pip install -r requirements.txt`

- **`.gitignore`** - Archivos ignorados por Git
  - No commit: música personal, logs, credenciales
  - **Auto-generado:** No editar

### Datos multimedia
- **`radios_espana.m3u`** - Playlist de emisoras de radio
  - URLs de streaming de radios españolas
  - Formato M3U (estándar)
  - **Editar:** Añadir/quitar emisoras según necesites

---

## 📁 Carpetas

### `/commands/` - Definiciones de comandos
Archivos JSON que definen qué hace cada comando de voz.

```
commands/
├── cmd_musica.json      # Comandos VLC (play, pause, siguiente)
├── cmd_radio.json       # Comandos mpv (radio, emisoras)
├── cmd_gps.json         # Comandos Firefox (mapas, waze)
└── cmd_sistema.json     # Comandos del sistema (apagar, reiniciar)
```

**Estructura:**
```json
{
  "app": "nombre_app",
  "descripcion": "Qué hace",
  "comandos": [
    {
      "frases": ["palabra1", "palabra2"],
      "accion": "nombre_accion",
      "script": "bash -c 'comando_a_ejecutar'"
    }
  ]
}
```

**Cómo modificar:**
```bash
# Ver comandos actuales
cat commands/cmd_musica.json | jq .

# Añadir nuevo comando (interactivo)
./scripts/add-app-commands.sh

# Editar directamente
nano commands/cmd_musica.json
```

**Después de cambios:**
```bash
sudo systemctl restart moto-voice
```

---

### `/ui/` - Interfaces web

Archivos HTML/CSS/JS para interfaces de usuario.

```
ui/
├── gps.html             # Selector de mapas/waze
└── launch-gps.sh        # Script para lanzar en kiosco
```

**`gps.html`** - Interfaz de GPS
- Dos botones: Google Maps y Waze
- Tema oscuro optimizado para moto
- Botón "Volver" para salir
- Click en Maps/Waze abre en Firefox

**`launch-gps.sh`** - Lanzador GPS
- Cierra Firefox previo
- Oculta cursor automáticamente
- Abre GPS en modo pantalla completa
- Ejecutable: `~/moto-ui/launch-gps.sh`

**Cómo usar:**
```bash
# Lanzar por voz (en cmd_gps.json)
# Lanzar manual
./ui/launch-gps.sh

# Lanzar Firefox directamente
firefox --kiosk file:///home/jesus/moto-ui/gps.html
```

---

### `/scripts/` - Herramientas de configuración

Utilidades bash para administrar el sistema.

```
scripts/
├── set-wakeword.sh      # Cambiar palabra de activación
└── add-app-commands.sh  # Asistente para nuevos comandos
```

**`set-wakeword.sh`** - Cambiar palabra de activación
```bash
# Ver actual
./scripts/set-wakeword.sh

# Cambiar a "jesus"
./scripts/set-wakeword.sh "jesus"

# Cambiar a "picaros"
./scripts/set-wakeword.sh "picaros"
```

**`add-app-commands.sh`** - Asistente interactivo
```bash
./scripts/add-app-commands.sh

# Preguntas:
# 1. Nombre de la app (ej: "llamadas")
# 2. Descripción (ej: "Realizar llamadas")
# 3. Crea archivo cmd_llamadas.json
# 4. Opción de editar con nano

# Tras terminar, reinicia el servicio automáticamente
```

---

### `/systemd/` - Servicios Linux

Archivos de configuración de systemd para autoarranque.

```
systemd/
├── moto-voice.service      # Servicio principal de voz
├── vlc-music.service       # Servicio VLC para música
├── bluealsa.service        # Proxy de audio Bluetooth
└── bluealsa-aplay.service  # Reproducción Bluetooth
```

**`moto-voice.service`** - Sistema de voz
```ini
[Unit]
Description=Moto Voice - Sistema de control por voz
After=sound.target bluetooth.service bluealsa.service

[Service]
Type=simple
User=jesus
WorkingDirectory=/home/jesus/moto-voice
ExecStart=/home/jesus/moto-voice/venv/bin/python3 /home/jesus/moto-voice/moto-voice.py
Restart=on-failure
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

**Cómo usar:**
```bash
# Copiar a systemd
sudo cp systemd/moto-voice.service /etc/systemd/system/

# Habilitar (autoarranque)
sudo systemctl enable moto-voice

# Iniciar
sudo systemctl start moto-voice

# Ver estado
sudo systemctl status moto-voice

# Ver logs
journalctl -u moto-voice -f

# Detener
sudo systemctl stop moto-voice

# Editar configuración
sudo nano /etc/systemd/system/moto-voice.service
sudo systemctl daemon-reload
sudo systemctl restart moto-voice
```

---

### `/docs/` - Documentación

Guías detalladas por fase del proyecto.

```
docs/
├── INSTALACION.md       # Guía paso a paso de instalación
├── TROUBLESHOOTING.md   # Resolución de problemas
├── FASE1-BLUETOOTH.md   # Bluetooth HFP/AVRCP
├── FASE2-MULTIMEDIA.md  # VLC + Radio
├── FASE3-GPS.md         # GPS en kiosco
└── FASE4-VOZ.md         # Control por voz
```

**Cómo leer:**
- Start: [README.md](README.md)
- Installation: [INSTALACION.md](INSTALACION.md)
- Problems: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Deep dive: [FASE1-4](README.md#-documentación-completa)

---

### `/.github/` - Configuración de GitHub

Plantillas y configuración para GitHub.

```
.github/
├── workflows/           # CI/CD (futuro)
├── ISSUE_TEMPLATE/      # Plantillas de issues (futuro)
└── PULL_REQUEST_TEMPLATE/ # Plantillas de PRs (futuro)
```

---

## 📄 Archivos raíz

- **`README.md`** - Visión general y guía rápida
- **`CHANGELOG.md`** - Historia de cambios (versiones)
- **`CONTRIBUTING.md`** - Cómo contribuir
- **`LICENSE`** - Licencia MIT
- **`.gitignore`** - Archivos ignorados por Git

---

## 🗂️ Estructura completa

```
TalkAndTrack/
├── moto-voice.py              # ⭐ Script principal
├── config.json                # Configuración de voz
├── requirements.txt           # Dependencias Python
├── radios_espana.m3u          # Emisoras de radio
│
├── commands/                  # Definiciones de comandos
│   ├── cmd_musica.json        # VLC
│   ├── cmd_radio.json         # mpv
│   ├── cmd_gps.json           # Firefox
│   └── cmd_sistema.json       # Sistema
│
├── ui/                        # Interfaces web
│   ├── gps.html               # Selector GPS
│   └── launch-gps.sh          # Lanzador GPS
│
├── scripts/                   # Herramientas
│   ├── set-wakeword.sh        # Cambiar palabra activación
│   └── add-app-commands.sh    # Asistente comandos
│
├── systemd/                   # Servicios Linux
│   ├── moto-voice.service
│   ├── vlc-music.service
│   ├── bluealsa.service
│   └── bluealsa-aplay.service
│
├── docs/                      # Documentación
│   ├── INSTALACION.md
│   ├── TROUBLESHOOTING.md
│   ├── FASE1-BLUETOOTH.md
│   ├── FASE2-MULTIMEDIA.md
│   ├── FASE3-GPS.md
│   └── FASE4-VOZ.md
│
├── .github/                   # GitHub config
├── .gitignore                 # Git ignore
├── README.md                  # ⭐ Documentación principal
├── CHANGELOG.md               # Historial de versiones
├── CONTRIBUTING.md            # Guía de contribución
└── LICENSE                    # MIT License

# Generados en runtime (NO commitear):
├── venv/                      # Virtual env Python
├── model-es/                  # Modelo Vosk (~50MB)
├── *.log                      # Archivos de logs
└── .env                       # Credenciales locales
```

---

## 🚀 Flujo típico de uso

### Instalación inicial
1. Clonar repo: `git clone ...`
2. Seguir [INSTALACION.md](docs/INSTALACION.md)
3. Copiar servicios systemd
4. Iniciar: `sudo systemctl start moto-voice`

### Uso diario
1. Sistema arranca automáticamente
2. Decir palabra de activación: "Hola"
3. Sistema responde: "Dime"
4. Decir comando: "Reproducir"
5. VLC comienza música

### Personalización
1. Cambiar palabra activación: `./scripts/set-wakeword.sh "mi-palabra"`
2. Añadir emisoras: `nano radios_espana.m3u`
3. Crear nuevos comandos: `./scripts/add-app-commands.sh`
4. Ajustar config: `nano config.json` + reiniciar

### Troubleshooting
1. Ver logs: `journalctl -u moto-voice -f`
2. Consultar [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
3. Ejecutar diagnóstico (futuro): `./scripts/diagnose.sh`

---

## 💡 Tips útiles

### Ver qué hace cada comando
```bash
cat commands/cmd_musica.json | jq '.comandos[] | {frases, accion}'
```

### Buscar comando por palabra
```bash
grep -r "siguiente" commands/
```

### Ver logs últimas 50 líneas
```bash
tail -n 50 ~/moto-voice/voice.log
```

### Reiniciar todo
```bash
sudo systemctl restart moto-voice vlc-music bluealsa
```

### Test de micrófono
```bash
arecord -D plughw:2,0 -f S16_LE -r 16000 -t wav /tmp/test.wav
# Hablar 5 segundos, Ctrl+C
aplay /tmp/test.wav
```

---

¿Necesitas más detalles? Consulta las guías específicas en `/docs/`.

