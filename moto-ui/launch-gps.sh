#!/bin/bash

# Cerrar instancias previas
pkill firefox 2>/dev/null
sleep 2

# Ocultar cursor
unclutter -idle 1 &
sleep 1

# Lanzar Firefox en modo kiosco
firefox --kiosk file:///home/jesus/moto-ui/gps.html
