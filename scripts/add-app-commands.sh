#!/bin/bash
# Asistente para añadir comandos de una nueva aplicación

echo "=== Añadir comandos para nueva aplicación ==="
read -p "Nombre de la app (ej: llamadas): " APP
read -p "Descripción: " DESC

ARCHIVO="/home/jesus/moto-voice/commands/cmd_${APP}.json"

if [ -f "$ARCHIVO" ]; then
    echo "Ya existe un archivo de comandos para '$APP'."
    read -p "¿Editar el existente? (s/n): " RESP
    [ "$RESP" != "s" ] && exit 0
    nano "$ARCHIVO"
else
    cat > "$ARCHIVO" << EOF
{
  "app": "${APP}",
  "descripcion": "${DESC}",
  "comandos": [
    {
      "frases": ["ejemplo de frase", "otra frase"],
      "accion": "nombre_accion",
      "script": "comando_a_ejecutar"
    }
  ]
}
EOF
    echo "Archivo creado: $ARCHIVO"
    read -p "¿Editar ahora? (s/n): " RESP
    [ "$RESP" = "s" ] && nano "$ARCHIVO"
fi

echo "Recargando comandos..."
sudo systemctl restart moto-voice
echo "Listo."