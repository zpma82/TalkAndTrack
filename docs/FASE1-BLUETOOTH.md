# 🔊 Fase 1: Bluetooth HFP/AVRCP - TalkAndTrack

Documentación completa de la configuración Bluetooth para intercomunicadores y dispositivos manos libres.

---

## 📌 Visión general

**Objetivo:** Conectar intercomunicadores y auriculares Bluetooth al Raspberry Pi 3 con soporte para:
- **HFP** (Hands-Free Profile) - Llamadas y micrófono
- **AVRCP** (Audio/Video Remote Control) - Control remoto (play/pause)
- **A2DP** (Advanced Audio Distribution Profile) - Audio estéreo

**Problema resuelto:** El chip Bluetooth integrado en Pi 3 (BCM43438) no soporta SCO (Synchronous Connection Oriented), necesario para HFP. Solución: usar dongle USB CSR8510.

---

## ⚙️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    Raspberry Pi 3                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ BlueALSA Daemon (hfp-ag, a2dp-sink, a2dp-source)    │   │
│  │ ├─ Audio Gateway (Pi actúa como teléfono)          │   │
│  │ ├─ Audio In/Out (micrófono y altavoz)              │   │
│  │ └─ Control AVRCP                                    │   │
│  └──────────────────────────────────────────────────────┘   │
│                        ↓                                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ ALSA (Advanced Linux Sound Architecture)             │   │
│  │ ├─ PCM (audio digital)                              │   │
│  │ └─ Mezcla de audio Bluetooth + altavoz local        │   │
│  └──────────────────────────────────────────────────────┘   │
│                        ↓                                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ PulseAudio / PipeWire (gestión audio)               │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
         ↑                                          
    USB Dongle CSR8510 (Bluetooth 4.0)
         ↓
┌─────────────────────────────────────────────────────────────┐
│         Intercomunicador Bluetooth (HFP/AVRCP)              │
│         ó Auriculares Manos libres                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔌 Hardware requerido

### Dongle Bluetooth USB
```
┌─────────────────────────────────────────┐
│ CSR8510 USB Bluetooth Adapter v4.0       │
├─────────────────────────────────────────┤
│ Características:                          │
│ • Chip: Broadcom CSR8510 A10             │
│ • Versión: Bluetooth 4.0 (LE + Classic) │
│ • Puerto: USB 2.0                        │
│ • Antena: Integrada                      │
│ • Rango: ~10 metros                      │
├─────────────────────────────────────────┤
│ ¿Por qué no el chip integrado?           │
│ • BCM43438 (en Pi 3) no soporta SCO      │
│ • SCO = voz en llamadas (necesario HFP)  │
│ • Comparte antena con WiFi               │
│ • No enruta audio correctamente          │
└─────────────────────────────────────────┘
```

---

## 🛠️ Instalación de software

### Paso 1: Instalar BlueALSA desde fuentes

```bash
# Dependencias
sudo apt install -y \
    bluez \
    bluealsa \
    libbluealsa-charger0 \
    libbluealsa0 \
    python3-bluez \
    alsa-utils

# Verificar versión
/usr/bin/bluealsad --version
```

### Paso 2: Desabilitar PipeWire (conflicto con BlueALSA)

```bash
# PipeWire por defecto compite por el perfil Bluetooth
# Solución: deshabilitar el módulo bluez

mkdir -p ~/.config/wireplumber/wireplumber.conf.d

cat > ~/.config/wireplumber/wireplumber.conf.d/51-disable-bluetooth.conf << 'EOF'
wireplumber.profiles = {
  main = {
    monitor.bluez = disabled
  }
}
EOF

# Reiniciar servicios
systemctl --user restart wireplumber pipewire pipewire-pulse
```

### Paso 3: Configurar BlueALSA como servicio systemd

```bash
sudo tee /etc/systemd/system/bluealsa.service > /dev/null << 'EOF'
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
EOF

sudo systemctl daemon-reload
sudo systemctl enable bluealsa
sudo systemctl start bluealsa
```

### Paso 4: Configurar bluealsa-aplay (reproducción)

```bash
sudo tee /etc/systemd/system/bluealsa-aplay.service > /dev/null << 'EOF'
[Unit]
Description=BlueALSA aplay
After=bluealsa.service
Requires=bluealsa.service

[Service]
Type=simple
User=jesus
ExecStartPre=/bin/sleep 5
ExecStart=/usr/bin/bluealsa-aplay 00:00:00:00:00:00
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable bluealsa-aplay
```

### Paso 5: Configurar Bluetooth main.conf

```bash
sudo nano /etc/bluetooth/main.conf
```

En la sección `[General]`, añadir:
```ini
[General]
Enable=Source,Sink,Media,Socket,Headset,HandsFree
```

---

## 📝 Perfiles Bluetooth explicados

### HFP (Hands-Free Profile)
```
├─ Variantes:
│  ├─ HFP AG (Audio Gateway) ← PI ACTUA COMO ESTO
│  └─ HFP HF (Hands-Free) 
│
├─ Características:
│  ├─ Llamadas (enviar/recibir)
│  ├─ Control de llamada (responder/colgar)
│  ├─ Micrófono (entrada)
│  ├─ Altavoz (salida)
│  └─ SCO (voz, requiere USB dongle)
│
└─ Casos de uso:
   ├─ Intercomunicadores
   ├─ Auriculares manos libres
   └─ Sistemas de llamada en coche
```

### A2DP (Advanced Audio Distribution Profile)
```
├─ Variantes:
│  ├─ Source (Pi envía audio) ← OPCIONAL
│  └─ Sink (Pi recibe audio) ← INCLUIDO
│
├─ Características:
│  ├─ Audio estéreo de alta calidad
│  ├─ Codec: SBC, AAC, LDAC, aptX
│  ├─ Sin voz (solo música)
│  └─ No requiere SCO
│
└─ Casos de uso:
   ├─ Altavoces Bluetooth
   ├─ Auriculares estéreo
   └─ Coches con Bluetooth
```

### AVRCP (Audio/Video Remote Control)
```
├─ Características:
│  ├─ Play/Pause
│  ├─ Siguiente/Anterior
│  ├─ Volumen +/-
│  └─ Metadatos (título, artista)
│
└─ Requisito:
   └─ Funciona junto con A2DP o HFP
```

---

## 🔍 Comandos Bluetooth útiles

### bluetoothctl - Gestión interactiva

```bash
# Entrar en modo interactivo
bluetoothctl

# Ver dispositivos disponibles
scan on
# Esperar ~10 segundos
scan off

# Emparejar
pair 00:12:6F:64:39:12

# Conectar (después de emparejar)
connect 00:12:6F:64:39:12

# Desconectar (mantiene emparejamiento)
disconnect 00:12:6F:64:39:12

# Marcar como confiable
trust 00:12:6F:64:39:12

# Ver dispositivos emparejados
paired-devices

# Ver dispositivos conectados
connected-devices

# Eliminar dispositivo
remove 00:12:6F:64:39:12

# Ver información del dispositivo
info 00:12:6F:64:39:12

# Salir
exit
```

### bluealsactl - Ver PCMs de audio

```bash
# Listar dispositivos BlueALSA
bluealsactl list-pcms

# Ejemplo de salida:
# hci0 00:12:6F:64:39:12 HFP  [x] [x]
#      MAC del dispositivo ↑   ↑   ↑
#      Perfil (HFP/A2DP) ─────┘   │
#      Playback (salida) ────────────┘
#      Capture (entrada) ─────────────┘
```

### alsamixer - Ajustar volúmenes

```bash
# Ver tarjeta default (0)
alsamixer

# Ver tarjeta específica (ej: Bluetooth)
alsamixer -c 0

# Navegar con flechas
# F3 = Playback (salida)
# F4 = Capture (entrada)
# +/- = Ajustar volumen
# M = Mute/Unmute
# ESC = Salir
```

---

## ✅ Dispositivos probados

| Dispositivo | MAC | Perfil HFP | Audio | Notas |
|-------------|-----|-----------|-------|-------|
| **Q7** (intercomunicador) | 00:12:6F:64:39:12 | ✅ Completo | ✅ SCO activo | **RECOMENDADO** - Funciona perfectamente |
| Redmi Buds 3 Lite | 7C:C9:5E:3E:84:B9 | ❌ Básico | ❌ HSP solo | Sin HFP completo |
| QTA35 | 11:75:58:53:03:30 | ❌ Básico | ❌ HSP solo | Sin SCO |

**Conclusión:** El Q7 es el dispositivo recomendado para motocicleta. Tiene:
- HSP + HFP completo
- SCO activo para voz clara
- Batería larga duración
- Cómodo para casco

---

## 📡 Conectar el intercomunicador Q7

### Primer emparejamiento

```bash
# 1. Poner Q7 en modo emparejamiento
# Presionar botón 3 segundos hasta que parpadee LED

# 2. Desde Pi
bluetoothctl
scan on
# Esperar a ver "Q7" en la lista
scan off

# 3. Emparejar
pair 00:12:6F:64:39:12

# 4. Conectar
connect 00:12:6F:64:39:12

# 5. Confiar (conexión automática en futuro)
trust 00:12:6F:64:39:12

# 6. Salir
exit
```

### Verificar conexión

```bash
# Ver que está conectado
bluetoothctl connected-devices

# Ver PCMs de audio
bluealsactl list-pcms
# Debe mostrar HFP con [x] [x]

# Probar audio
alsamixer -c 0
# Debe mostrar entrada/salida del Q7
```

### Reconexión automática

BlueALSA intenta reconectar automáticamente después de:
- Desconexión temporal
- Reinicio del Pi
- Reinicio del dispositivo

Para asegurar reconexión rápida:
```bash
# En el Q7, activar "autoconexión"
# (depende del modelo específico)
```

---

## 🔧 Configuración avanzada

### Cambiar codec de audio

```bash
# Ver codecs disponibles
sudo cat /etc/alsa/conf.d/bluealsa.conf | grep codec

# Forzar SBC (compatible, pero menor calidad)
# Editar /etc/systemd/system/bluealsa.service
# ExecStart con: --a2dp-codec=sbc

sudo systemctl restart bluealsa
```

### Aumentar potencia Bluetooth

```bash
# Ver potencia actual
sudo hcitool cmd 0x04 0x0009

# Aumentar potencia (valor máximo depende del dongle)
sudo hciconfig hci0 up
sudo hcitool cmd 0x04 0x0009 0x00 0x07 0x00  # Potencia máxima
```

### Deshabilitar LE (si solo necesitas Classic)

```bash
# Editar configuración BlueALSA
# Algunos dongles tienen mejor rendimiento sin LE

# Nota: LE (Low Energy) es útil para sensores, relojes, etc.
```

---

## 🐛 Problemas comunes y soluciones

### Dongle no se detecta

```bash
# Verificar que está conectado
lsusb | grep -i bluetooth

# Si no aparece, probar otro puerto USB
# o cable diferente
```

### BlueALSA no se inicia

```bash
# Ver error
journalctl -u bluealsa -n 50

# Verificar permisos
ls -la /usr/bin/bluealsad

# Reiniciar bluetooth
sudo systemctl restart bluetooth
sudo systemctl restart bluealsa
```

### Sin audio en Bluetooth

```bash
# 1. Verificar conexión
bluetoothctl info 00:12:6F:64:39:12

# 2. Ver PCMs
bluealsactl list-pcms

# 3. Ajustar volumen
alsamixer -c 0

# 4. Verificar que bluealsa-aplay está corriendo
systemctl status bluealsa-aplay

# 5. Último recurso: reiniciar todo
sudo systemctl restart bluetooth bluealsa bluealsa-aplay
```

### Conexión se cae constantemente

```bash
# 1. Distancia: acercar dispositivo a Pi
# 2. Interferencia: alejar de WiFi/microondas
# 3. Firmware: actualizar dongle si hay firmware disponible
# 4. Otro dongle: probar CSR8510 diferente
```

---

## 📚 Referencia de comandos HFP

(Para fase siguiente - llamadas)

```bash
# Responder llamada (futuro)
dbus-send --system /org/bluez/hci0/dev_XX_XX_XX_XX_XX_XX \
  org.bluez.HandsFreeAudioGateway.AnswerCall

# Rechazar llamada (futuro)
dbus-send --system /org/bluez/hci0/dev_XX_XX_XX_XX_XX_XX \
  org.bluez.HandsFreeAudioGateway.ReleaseCall
```

---

## 🔍 Verificación de instalación

Script para verificar que todo está configurado:

```bash
#!/bin/bash
echo "=== Verificación Bluetooth Fase 1 ==="

echo "1. Dongle detectado:"
lsusb | grep -i bluetooth || echo "❌ No detectado"

echo ""
echo "2. BlueALSA corriendo:"
systemctl is-active bluealsa

echo ""
echo "3. Servicio de reproducción:"
systemctl is-active bluealsa-aplay

echo ""
echo "4. Dispositivos emparejados:"
bluetoothctl paired-devices

echo ""
echo "5. PCMs activos:"
bluealsactl list-pcms

echo ""
echo "6. Tarjetas ALSA:"
arecord -l | grep -E "^card|Device:"

echo ""
echo "✅ Si todo muestra valores, la Fase 1 está lista"
```

---

## 📖 Enlaces útiles

- **BlueALSA**: https://github.com/arkq/bluez-alsa
- **BlueZ**: http://www.bluez.org/
- **Bluetooth SIG**: https://www.bluetooth.com/specifications/assigned-numbers/
- **HFP Profile**: https://www.bluetooth.com/specifications/specs/hands-free-profile/

---

**Estado:** ✅ Fase 1 completada  
**Siguiente:** [Fase 2 - Multimedia (VLC + Radio)](FASE2-MULTIMEDIA.md)

