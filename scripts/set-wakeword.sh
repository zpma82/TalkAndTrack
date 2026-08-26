#!/bin/bash
# Script para cambiar la palabra de activación del sistema de voz
# USO: ./set-wakeword.sh nuevapalabra

CONFIG="/home/jesus/moto-voice/config.json"

if [ -z "$1" ]; then
    ACTUAL=$(python3 -c "import json; d=json.load(open('$CONFIG')); print(d['wakeword'])")
    echo "Palabra de activación actual: $ACTUAL"
    echo "Uso: $0 <nueva_palabra>"
    exit 0
fi

NUEVA="$1"
python3 -c "
import json
with open('$CONFIG', 'r') as f:
    config = json.load(f)
config['wakeword'] = '$NUEVA'
with open('$CONFIG', 'w') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)
print('Palabra de activación cambiada a: $NUEVA')
"
