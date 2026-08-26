# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### Planned
- Remuestreo de audio USB (44100 → 16000 Hz) con scipy/numpy
- UI web centralizada con Flask/FastAPI
- Soporte pantalla táctil 7"
- Integración WhatsApp Web
- Llamadas HFP completas
- Multiidioma (en, pt, fr, de)
- Tests unitarios y CI/CD
- Documentación en vídeo

---

## [1.0.0] - 2024-08-25

### Added

#### Fase 1 - Bluetooth HFP/AVRCP ✅
- [x] Soporte para perfiles HFP (Audio Gateway), A2DP, AVRCP
- [x] BlueALSA como proxy de audio Bluetooth
- [x] Compatibilidad con dongle USB CSR8510
- [x] Configuración automática de servicios systemd
- [x] Reconexión automática a dispositivos emparejados
- [x] Documentación completa de pairing y troubleshooting
- Dispositivos probados:
  - ✅ Q7 Intercomunicador (HFP completo, SCO activo)
  - ❌ Redmi Buds 3 Lite (solo HSP básico)
  - ❌ QTA35 (sin HFP completo)

#### Fase 2 - Multimedia ✅
- [x] VLC en modo headless con API HTTP (puerto 8080)
- [x] Control de reproducción por curl/Python
  - Play/Pause
  - Siguiente/Anterior
  - Control de volumen
- [x] mpv con socket IPC para radio por internet
- [x] Comandos JSON modulares por aplicación
- [x] 20+ emisoras españolas preconfiguradas
  - RNE Radio Nacional
  - Cadena SER
  - COPE
  - Los 40
  - Cadena Dial
  - Onda Cero
  - Europa FM
- [x] Mezcla de audio ALSA
- [x] Servicios systemd para VLC y mpv
- [x] Documentación de API HTTP y socket IPC

#### Fase 3 - GPS ✅
- [x] Interfaz HTML personalizada para GPS
  - Selector visual entre Google Maps y Waze
  - Diseño optimizado para pantalla táctil
  - Tema oscuro para uso diurno
- [x] Firefox en modo kiosco (`--kiosk`)
- [x] Script de lanzamiento automático
- [x] Soporte USB tethering (recomendado para moto)
- [x] Soporte WiFi hotspot móvil
- [x] Cursor automáticamente oculto (unclutter)
- [x] Integración con comandos de voz
- [x] Documentación de conectividad GPS

#### Fase 4 - Control por voz ✅
- [x] Reconocimiento de voz offline con Vosk
- [x] Modelo de lenguaje español (~50MB)
- [x] Sistema de palabra de activación configurable
- [x] Síntesis de voz con espeak-ng
- [x] Arquitectura modular de comandos JSON
- [x] Scripts auxiliares:
  - `set-wakeword.sh` - Cambiar palabra de activación
  - `add-app-commands.sh` - Asistente para nuevos comandos
- [x] Sistema de logging detallado
- [x] Manejo de errores robusto
- [x] Timeout de comandos (10 segundos)
- [x] Servicio systemd con reinicio automático
- Comandos incluidos:
  - Música: play, pause, siguiente, anterior, volumen
  - Radio: abrir, cambiar emisoras, parar
  - GPS: mapas, waze, cerrar
  - Sistema: apagar, reiniciar, hora, volumen
- [x] Documentación completa con troubleshooting

### Infrastructure

#### Configuración systemd
- `moto-voice.service` - Sistema principal de voz
- `vlc-music.service` - Demonio de reproducción VLC
- `bluealsa.service` - Proxy de audio Bluetooth
- `bluealsa-aplay.service` - Reproducción Bluetooth

#### Scripts y utilidades
- `launch-gps.sh` - Lanzador de GPS en kiosco
- `set-wakeword.sh` - Configurador de palabra de activación
- `add-app-commands.sh` - Asistente interactivo para comandos
- `diagnose.sh` - Script de diagnóstico del sistema

#### Estructura de carpetas
```
TalkAndTrack/
├── moto-voice.py          # Script principal
├── config.json            # Configuración
├── radios_espana.m3u      # Lista de emisoras
├── commands/              # JSON de comandos
├── ui/                    # Interfaz HTML/JS
├── scripts/               # Herramientas
├── systemd/               # Servicios Linux
├── docs/                  # Documentación
└── .github/               # GitHub config
```

### Documentation

- [README.md](README.md) - Visión general y guía rápida
- [INSTALACION.md](INSTALACION.md) - Guía paso a paso
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Resolución de problemas
- [FASE1-BLUETOOTH.md](FASE1-BLUETOOTH.md) - Documentación Bluetooth HFP
- [FASE2-MULTIMEDIA.md](FASE2-MULTIMEDIA.md) - VLC y Radio
- [FASE3-GPS.md](FASE3-GPS.md) - GPS en kiosco
- [FASE4-VOZ.md](FASE4-VOZ.md) - Control por voz Vosk
- [CONTRIBUTING.md](CONTRIBUTING.md) - Guía de contribución
- [LICENSE](LICENSE) - MIT License
- [.gitignore](.gitignore) - Git configuration

### Configuration Files

- `config.json` - Configuración principal de Vosk
- `commands/cmd_musica.json` - Comandos VLC
- `commands/cmd_radio.json` - Comandos mpv
- `commands/cmd_gps.json` - Comandos Firefox GPS
- `commands/cmd_sistema.json` - Comandos del sistema
- `radios_espana.m3u` - Playlist de emisoras

### Fixed

- ✅ Conflicto PipeWire vs BlueALSA (deshabilitar módulo bluez)
- ✅ libvosk.so execstack en ARM (patchelf)
- ✅ Firefox en Wayland/labwc (usar `--kiosk`)
- ✅ Remuestreo de audio USB pendiente (configuración base lista)

### Known Issues

- ⚠️ Micrófono USB 44100 Hz requiere remuestreo a 16000 Hz para Vosk
  - Afecta precisión de reconocimiento
  - Solución en progreso (scipy/numpy)
- ⚠️ Algunos dongles Bluetooth CSR8510 tienen firmware antiguo
  - Afecta estabilidad de conexión HFP
  - Solución: actualizar firmware o cambiar dongle

---

## [0.5.0] - 2024-06-15

### Added (Prototipo inicial)
- Estructura base del proyecto
- Configuración de BlueALSA básica
- VLC en headless funcional
- Prototipo de Vosk (sin optimizaciones)

### Notes
- Versión experimental no documentada

---

## Contribuyentes

- **Jesús** - Diseño e implementación principal

---

## Cómo contribuir

Ver [CONTRIBUTING.md](CONTRIBUTING.md) para:
- Reportar bugs
- Proponer features
- Enviar PRs
- Mejorar documentación

---

## Licencia

Este proyecto está bajo [MIT License](LICENSE).

---

## Roadmap futuro

### Corto plazo (Q4 2024)
- Remuestreo de audio USB completamente funcional
- Tests unitarios básicos
- Mejora de precisión de voz

### Medio plazo (Q1-Q2 2025)
- UI web centralizada
- Soporte para múltiples idiomas
- Integración WhatsApp Web

### Largo plazo (Q3+ 2025)
- Llamadas HFP completas
- IA local para respuestas naturales
- Compatibilidad con Pi 4 y Pi 5
- Apps comunitarias (registro de viajes, etc.)

---

**Última actualización:** Agosto 2024

