# 🗺️ Fase 3: GPS en modo kiosco - TalkAndTrack

Sistema de navegación GPS con interfaz en pantalla completa optimizada para motocicleta.

---

## 📌 Visión general

**Objetivo:** Proporcionar acceso rápido a Google Maps y Waze en pantalla completa (kiosco).

**Desafíos resueltos:**
- Chromium falla en Wayland (labwc) en Raspberry Pi
- Solución: usar Firefox con flag `--kiosk`
- Interfaz HTML personalizada para seleccionar GPS

```
┌──────────────────────────────────────┐
│      GPS Moto - Interfaz               │
├──────────────────────────────────────┤
│                                      │
│           🗺️ GPS 🗺️                   │
│                                      │
│  ┌────────────────────────────────┐  │
│  │  🗺 Google Maps  │  🧭 Waze    │  │
│  │                  │              │  │
│  │    Clic aquí     │  Clic aquí   │  │
│  └────────────────────────────────┘  │
│                                      │
│            [← Volver]                │
│                                      │
└──────────────────────────────────────┘
```

---

## 🖥️ Hardware requerido

### Pantalla
- Cualquier monitor/pantalla HDMI
- Recomendado: 5-7" para montaje en moto
- Resolución: 1024x600 mínimo
- Orientación: Horizontal (landscape)

### Ejemplo: Pantalla 7" Raspberry Pi
```
┌─────────────────────────────────────┐
│  Raspberry Pi 7" Touch Display       │
├─────────────────────────────────────┤
│ • Resolución: 800x480               │
│ • Conexión: Ribbon cable a CSI      │
│ • Touch: Opcional (se puede usar)   │
│ • Precio: ~60€                      │
└─────────────────────────────────────┘
```

### Conectividad GPS
Opciones:
1. **Hotspot WiFi móvil** - Rápido, pero consume batería
2. **USB Tethering** - ⭐ RECOMENDADO - Estable, más confiable en moto

```
┌──────────────────┐
│  Teléfono Móvil  │
│  • GPS activo    │
│  • USB Tethering │
└────────┬─────────┘
         │ Cable USB
         │
┌────────▼─────────┐
│  Raspberry Pi 3  │
│  • eth0 = usb0   │
└──────────────────┘
```

---

## 🔧 Instalación

### Paso 1: Instalar Firefox

```bash
sudo apt install -y firefox-esr
```

### Paso 2: Ocultar cursor (unclutter)

```bash
sudo apt install -y unclutter

# unclutter: Oculta el cursor después de 1 segundo de inactividad
# Perfecto para pantallas táctiles sin ratón
```

### Paso 3: Crear directorio de UI

```bash
mkdir -p ~/moto-ui
cd ~/moto-ui
```

### Paso 4: Crear interfaz HTML

Archivo: `~/moto-ui/gps.html`

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GPS Moto</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }

    body {
      background: #1a1a2e;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100vh;
      font-family: sans-serif;
      gap: 30px;
    }

    h1 {
      color: #ffffff;
      font-size: 2em;
      letter-spacing: 2px;
      margin-bottom: 10px;
    }

    .btn-container {
      display: flex;
      gap: 40px;
    }

    .btn {
      width: 200px;
      height: 200px;
      border: none;
      border-radius: 20px;
      font-size: 1.5em;
      font-weight: bold;
      color: white;
      cursor: pointer;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 15px;
      transition: transform 0.1s, opacity 0.1s;
      text-decoration: none;
    }

    .btn:active { 
      transform: scale(0.95); 
      opacity: 0.85; 
    }

    .btn-maps { background: #4285F4; }
    .btn-waze { background: #05C8F7; color: #1a1a2e; }

    .btn svg { width: 64px; height: 64px; fill: currentColor; }

    .back-btn {
      position: fixed;
      bottom: 20px;
      right: 20px;
      background: #333;
      color: white;
      border: none;
      border-radius: 50px;
      padding: 15px 30px;
      font-size: 1.1em;
      cursor: pointer;
    }
  </style>
</head>
<body>
  <h1>GPS</h1>
  <div class="btn-container">
    <a class="btn btn-maps"
       href="https://maps.google.com/?force=pwa"
       target="_self">
      <svg viewBox="0 0 24 24">
        <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
      </svg>
      Google Maps
    </a>
    <a class="btn btn-waze"
       href="https://www.waze.com"
       target="_self">
      <svg viewBox="0 0 24 24">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
      </svg>
      Waze
    </a>
  </div>
  <button class="back-btn" onclick="history.back()">Volver</button>
</body>
</html>
```

### Paso 5: Crear script de lanzamiento

Archivo: `~/moto-ui/launch-gps.sh`

```bash
#!/bin/bash

# Script para lanzar GPS en modo kiosco

# Cerrar Firefox previo
pkill firefox 2>/dev/null
sleep 2

# Ocultar cursor (inactivo tras 1 segundo)
unclutter -idle 1 &
sleep 1

# Lanzar Firefox en modo kiosco con archivo local
firefox --kiosk file:///home/jesus/moto-ui/gps.html
```

Hacer ejecutable:
```bash
chmod +x ~/moto-ui/launch-gps.sh
```

### Paso 6: Probar manualmente

```bash
~/moto-ui/launch-gps.sh

# Debe abrir Firefox en pantalla completa con dos botones
# Salir: Presionar F11 o Alt+F4
```

---

## 🌐 Configurar conectividad GPS

### Opción 1: Hotspot WiFi móvil (simple)

```bash
# Conectar a hotspot del teléfono
nmcli device wifi connect 'NombreHotspot' password 'contrasena'

# Verificar conexión
ping 8.8.8.8

# Desconectar
nmcli device wifi disconnect
```

### Opción 2: USB Tethering (recomendado para moto) ⭐

**Ventajas:**
- Más estable (sin interferencia de vibraciones)
- No interfiere con Bluetooth
- Menor consumo de batería del móvil
- Conexión directa más rápida

**Configuración:**

1. **En el teléfono:**
   - Ir a Ajustes → Conexión → USB tethering
   - Conectar cable USB a Pi

2. **En Raspberry Pi:**
   ```bash
   # Listar interfaces
   ip link show
   # Debe aparecer "usb0"

   # Obtener dirección IP automáticamente (DHCP)
   sudo dhclient usb0

   # Verificar conexión
   ip addr show usb0
   ping 8.8.8.8
   ```

3. **Hacer permanente:**
   ```bash
   sudo nano /etc/dhcp/dhclient.conf
   # Añadir:
   # interface "usb0" {
   #     send host-name = "raspi-talkandtrack";
   # }
   ```

4. **Reconexión automática:**
   ```bash
   sudo nano /etc/systemd/system/usb-tethering.service
   ```
   
   Contenido:
   ```ini
   [Unit]
   Description=USB Tethering
   After=network-online.target
   Wants=network-online.target

   [Service]
   Type=oneshot
   ExecStart=/sbin/dhclient usb0
   RemainAfterExit=yes

   [Install]
   WantedBy=multi-user.target
   ```

   Activar:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable usb-tethering
   ```

### Opción 3: Hotspot USB con IP estática

```bash
# Ver IP del teléfono
ip addr show usb0

# Configurar IP estática
sudo nano /etc/network/interfaces
```

Añadir:
```
auto usb0
iface usb0 inet static
    address 192.168.42.2
    netmask 255.255.255.0
    gateway 192.168.42.1
```

Aplicar:
```bash
sudo systemctl restart networking
```

---

## 📱 Abrir GPS por voz (integración)

El archivo `cmd_gps.json` contiene comandos para abrir GPS:

```json
{
  "app": "gps",
  "descripcion": "Navegacion GPS",
  "comandos": [
    {
      "frases": ["mapas", "google maps"],
      "accion": "open_maps",
      "script": "pkill firefox 2>/dev/null; sleep 1; firefox --kiosk 'https://maps.google.com/?force=pwa' &"
    },
    {
      "frases": ["waze"],
      "accion": "open_waze",
      "script": "pkill firefox 2>/dev/null; sleep 1; firefox --kiosk 'https://www.waze.com/ul' &"
    },
    {
      "frases": ["cierra mapas", "cierra gps"],
      "accion": "close_gps",
      "script": "pkill firefox 2>/dev/null"
    }
  ]
}
```

### Uso por voz

```
Usuario: "Hola"
Sistema: "Dime"

Usuario: "Mapas"
Sistema: "open_maps"
# Firefox abre Google Maps en pantalla completa

Usuario: "Hola"
Sistema: "Dime"

Usuario: "Cierra GPS"
Sistema: "close_gps"
# Firefox cierra
```

---

## 🔧 Optimizaciones para moto

### Diseño de botones grandes

- Botones de 200x200px
- Espaciado: 40px entre botones
- Fuente grande y legible
- Colores de alto contraste

### Tema oscuro

- Fondo: #1a1a2e (gris muy oscuro)
- Texto: blanco (#ffffff)
- Reduce fatiga visual en exterior luminoso

### Eliminación de cursor

```bash
# unclutter oculta automáticamente el cursor
# No necesita ratón, solo pantalla táctil o comandos de voz
```

### Botón "Volver"

- Fijo en esquina inferior derecha
- Fácil de alcanzar sin mirar pantalla

---

## 🌐 URLs de Maps y Waze

### Google Maps PWA
```
https://maps.google.com/?force=pwa
```

**Ventajas:**
- Progressive Web App (funciona offline parcialmente)
- Más ligero que versión completa
- Carga rápida en conexiones lentas

### Waze mobile
```
https://www.waze.com
```

**Ventajas:**
- Optimizado para móvil
- Tráfico en tiempo real
- Rutas alternativas

---

## 🐛 Troubleshooting GPS

### Firefox no abre

```bash
# Probar manualmente
firefox --kiosk file:///home/jesus/moto-ui/gps.html

# Ver errores
firefox --kiosk file:///home/jesus/moto-ui/gps.html 2>&1
```

### Verificar sesión Wayland

```bash
echo $XDG_SESSION_TYPE
# Debe mostrar "wayland"

# Si muestra "x11", cambiar en ~.bashrc o .bash_profile:
# export XDG_SESSION_TYPE=wayland
```

### Si no funciona OpenGL (labwc)

```bash
# Usar software rendering
LIBGL_ALWAYS_SOFTWARE=1 firefox --kiosk file:///home/jesus/moto-ui/gps.html

# O añadir a launch-gps.sh:
# export LIBGL_ALWAYS_SOFTWARE=1
```

### Sin conexión a internet

```bash
# Verificar si está conectado
ping 8.8.8.8

# Si WiFi:
nmcli device wifi list
nmcli device wifi connect 'SSID' password 'PASS'

# Si USB tethering:
sudo dhclient usb0
ip addr show usb0
```

### Maps carga blanco/en blanco

```bash
# 1. Esperar 5-10 segundos (carga lenta)
# 2. Verificar DNS
cat /etc/resolv.conf

# 3. Cambiar DNS a Google
sudo nano /etc/systemd/resolved.conf
# Descomentar y añadir:
# DNS=8.8.8.8 8.8.4.4

sudo systemctl restart systemd-resolved
```

---

## 🎨 Personalizar interfaz

Editando `gps.html`:

### Cambiar colores
```css
.btn-maps { background: #4285F4; }  /* Azul Google */
.btn-waze { background: #05C8F7; }  /* Cyan Waze */
```

### Cambiar tamaño de botones
```css
.btn {
  width: 200px;   /* Aumentar para pantallas grandes */
  height: 200px;
  /* ... */
}
```

### Añadir más opciones GPS
```html
<!-- Ejemplo: OpenStreetMap -->
<a class="btn btn-osm"
   href="https://www.openstreetmap.org/"
   target="_self">
  <svg viewBox="0 0 24 24"><!-- SVG icon --></svg>
  OpenStreetMap
</a>
```

---

## 📊 Monitoreo de navegación

### Ver histórico de navegación
```bash
# Historial de Firefox
ls -la ~/.mozilla/firefox/*/places.sqlite

# Limpiar después de viajes (privacidad)
rm ~/.mozilla/firefox/*/places.sqlite
```

### Ver consumo de datos
```bash
# Si USB tethering
sudo iftop -i usb0
```

---

## ✅ Checklist Fase 3

- [x] Firefox instalado
- [x] HTML de interfaz GPS creado
- [x] Script launch-gps.sh funcionando
- [x] Conectividad GPS (WiFi o USB tethering)
- [x] Maps/Waze cargando correctamente
- [x] Cursor oculto en kiosco
- [x] Botones táctiles funcionando
- [x] Integración con comandos de voz

---

**Estado:** ✅ Fase 3 completada  
**Siguiente:** [Fase 4 - Control por voz](FASE4-VOZ.md)

