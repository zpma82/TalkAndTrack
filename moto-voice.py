#!/usr/bin/env python3
import json
import os
import subprocess
import logging

from pathlib import Path
import vosk


CONFIG_PATH = Path(__file__).parent / "config.json"
with open(CONFIG_PATH) as f:
    CONFIG = json.load(f)

logging.basicConfig(
    filename=CONFIG["log_file"],
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
log = logging.getLogger("moto-voice")

vosk.SetLogLevel(-1)
model = vosk.Model(CONFIG["model_path"])

VOCABULARIO = json.dumps([
    "hola", "jesus", "musica", "reproducir", "play", "pausa", "pausar",
    "para", "siguiente", "saltar", "anterior", "volver", "sube", "baja",
    "volumen", "mas", "menos", "radio", "la ser", "los cuarenta", "cuarenta",
    "mapas", "waze", "cierra", "apagar", "apaga", "reiniciar", "hora",
    "dime", "sistema", "[unk]"
], ensure_ascii=False)
rec = vosk.KaldiRecognizer(model, 16000, VOCABULARIO)

def cargar_comandos():
    comandos = []
    commands_dir = Path(CONFIG["commands_dir"])
    for archivo in sorted(commands_dir.glob("cmd_*.json")):
        with open(archivo) as f:
            datos = json.load(f)
        for cmd in datos["comandos"]:
            for frase in cmd["frases"]:
                comandos.append({
                    "frase": frase.lower(),
                    "accion": cmd["accion"],
                    "script": cmd["script"],
                    "app": datos["app"]
                })
    log.info(f"Cargados {len(comandos)} comandos")
    return comandos

COMANDOS = cargar_comandos()
WAKEWORD = CONFIG["wakeword"].lower()

def hablar(texto):
    if CONFIG.get("response_voice"):
        cmd = CONFIG["response_voice_cmd"]
        subprocess.Popen(f'{cmd} "{texto}"', shell=True)

def buscar_comando(texto):
    texto = texto.lower().strip()
    mejor = None
    mejor_len = 0
    for cmd in COMANDOS:
        if cmd["frase"] in texto:
            if len(cmd["frase"]) > mejor_len:
                mejor = cmd
                mejor_len = len(cmd["frase"])
    return mejor

def ejecutar(cmd):
    log.info(f"Ejecutando [{cmd['app']}] {cmd['accion']}: {cmd['script']}")
    try:
        resultado = subprocess.run(cmd["script"], shell=True, capture_output=True, text=True, timeout=10)
        if resultado.returncode != 0:
            log.error(f"Error en {cmd['accion']} (rc={resultado.returncode}): {resultado.stderr.strip()}")
        else:
            log.info(f"OK {cmd['accion']}: {resultado.stdout.strip()[:100]}")
        return resultado.returncode == 0
    except subprocess.TimeoutExpired:
        log.error(f"Timeout en {cmd['accion']}")
        return False
    except Exception as e:
        log.error(f"Excepcion en {cmd['accion']}: {e}")
        return False
        
        
def main():
    print(f"[moto-voice] Escuchando... Wakeword: '{WAKEWORD}'")
    log.info(f"Sistema iniciado. Wakeword: '{WAKEWORD}'")
    hablar("Sistema de voz listo")

    esperando_comando = False

    proceso = subprocess.Popen(
        ["arecord", "-D", "plughw:2,0", "-f", "S16_LE", "-r", "16000", "-c", "1", "-q"],
        stdout=subprocess.PIPE
    )

    while True:
        data = proceso.stdout.read(8000)
        if not data:
            break

        if rec.AcceptWaveform(data):
            resultado = json.loads(rec.Result())
            texto = resultado.get("text", "").lower().strip()
            print(f"Reconocido: '{texto}'")

            if not texto:
                continue

            log.info(f"Reconocido: '{texto}'")

            if not esperando_comando:
                if WAKEWORD in texto:
                    esperando_comando = True
                    hablar("Dime")
                    log.info("Wakeword detectada")
            else:
                esperando_comando = False
                cmd = buscar_comando(texto)
                if cmd:
                    log.info(f"Comando: {cmd['accion']}")
                    hablar(cmd["accion"])
                    ejecutar(cmd)
                else:
                    hablar("No entendi el comando")
                    log.warning(f"No reconocido: '{texto}'")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[moto-voice] Detenido.")
