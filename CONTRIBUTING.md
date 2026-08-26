# 🤝 Contribuyendo a TalkAndTrack

¡Gracias por querer contribuir! Aquí están las directrices para hacerlo de forma efectiva.

---

## 📋 Cómo empezar

### 1. Fork el repositorio
- Haz clic en "Fork" en GitHub
- Clona tu fork: `git clone https://github.com/TU_USUARIO/TalkAndTrack.git`
- Añade el repositorio original como "upstream": `git remote add upstream https://github.com/zpma82/TalkAndTrack.git`

### 2. Crea una rama para tu trabajo
```bash
git checkout -b feature/mi-caracteristica
# o
git checkout -b fix/mi-bug
# o
git checkout -b docs/mejora-documentacion
```

### 3. Haz tus cambios
- Mantén commits pequeños y descriptivos
- Sigue el estilo de código existente
- Prueba tus cambios localmente

### 4. Envía un Pull Request
- Push a tu fork: `git push origin feature/mi-caracteristica`
- Abre un PR contra `main` en el repositorio original
- Describe los cambios claramente

---

## 📝 Tipos de contribuciones bienvenidas

### 🐛 Reportar bugs
1. Usa "Issues" en GitHub
2. Describe:
   - Qué ocurrió
   - Qué esperabas que ocurriera
   - Pasos para reproducir
   - Output de `diagnose.sh`
   - Configuración (Pi model, SO, etc.)

### 📚 Mejorar documentación
- Corregir errores ortográficos
- Añadir ejemplos más claros
- Traducir a otros idiomas
- Mejorar claridad de explicaciones

### ✨ Nuevas características
- Remuestreo de audio USB (44100 → 16000 Hz)
- UI web con Flask/FastAPI
- Interfaz táctil optimizada
- Integración WhatsApp
- Soporte para más idiomas

### 🔧 Mejoras de código
- Refactorizar código duplicado
- Optimizar rendimiento
- Mejorar manejo de errores
- Añadir logging

### 🧪 Tests
- Crear tests unitarios
- Tests de integración
- Scripts de verificación

---

## 💻 Estilo de código

### Python
```python
# Seguir PEP 8
# - Máximo 80 caracteres de línea
# - Nombres descriptivos
# - Docstrings en funciones importantes

def procesar_comando(comando: str) -> bool:
    """
    Procesa un comando de voz.
    
    Args:
        comando: Texto del comando
        
    Returns:
        True si se ejecutó correctamente
    """
    pass
```

### JSON
```json
{
  "app": "nombre_app",
  "descripcion": "Descripcion clara",
  "comandos": [
    {
      "frases": ["frase 1", "frase 2"],
      "accion": "nombre_accion",
      "script": "comando"
    }
  ]
}
```

### Bash
```bash
#!/bin/bash
# Comentarios explicativos
# Manejar errores correctamente

set -e  # Exit on error
set -u  # Exit on undefined variable
```

### Commit messages
```
[TIPO] Descripción breve (max 50 caracteres)

Descripción más detallada si es necesario (max 72 caracteres por línea).
Explicar por qué este cambio es necesario.

Fixes #123
```

Tipos de commit:
- `[FEATURE]` - Nueva característica
- `[FIX]` - Corrección de bug
- `[DOCS]` - Documentación
- `[REFACTOR]` - Refactorización
- `[PERF]` - Mejora de rendimiento
- `[TEST]` - Tests

---

## 🧪 Probar cambios

### Antes de hacer PR

```bash
# 1. Crear venv limpio
python3 -m venv test_venv
source test_venv/bin/activate
pip install -r requirements.txt

# 2. Probar el script principal
python3 moto-voice.py

# 3. Verificar comandos
python3 -c "import json; json.load(open('commands/cmd_musica.json'))"

# 4. Ejecutar linter (si lo hay)
# pylint moto-voice.py

# 5. Ver logs
tail -f voice.log
```

### Tests unitarios (futuro)
```bash
python3 -m pytest tests/
```

---

## 📊 Áreas prioritarias

### 1. Remuestreo de audio (URGENTE)
- Problema: micrófono USB en 44100 Hz, Vosk necesita 16000 Hz
- Solución: usar `librosa`, `scipy.signal` o `audioop-lts`
- Files: `moto-voice.py` línea ~150

### 2. UI unificada (IMPORTANTE)
- Framework sugerido: Flask o FastAPI + HTML/CSS
- Debe incluir: botones para cada app, estado de servicios
- Considerar pantalla táctil de 5-7"

### 3. Integración WhatsApp (IMPORTANTE)
- Usar WhatsApp Web en Firefox kiosco
- Comandos: "envía a X", "lee mensajes"
- Requiere escrapeo o API (complejo)

### 4. Soporte de idiomas (AGRADABLE)
- Traducir guías a otros idiomas
- Añadir modelos de voz para otros idiomas
- Mantener config.json agnóstico a idioma

### 5. Tests y CI/CD (FUTURO)
- GitHub Actions para validar PRs
- Tests de integración
- Validación de JSON

---

## 🔐 Seguridad

### Contraseñas y credenciales
- **NUNCA** commitear contraseñas reales
- Usar variables de entorno (.env)
- Actualizar motovlc2026 si es público

### Ejemplo seguro:
```python
import os
from dotenv import load_dotenv

load_dotenv()
VLC_PASSWORD = os.getenv('VLC_PASSWORD', 'default')
```

---

## 📞 Comunicación

### Preguntas o dudas
- Abre un "Discussion" en GitHub
- Tag al maintainer si es urgente
- Sé respetuoso y claro

### Before/After de cambios
Si mejoras algo, incluye:
```
## Antes
[Mostrar cómo funcionaba]

## Después
[Mostrar cómo funciona ahora]
```

---

## ✅ Checklist para PR

Antes de enviar, verifica:

- [ ] Mi código sigue el estilo del proyecto
- [ ] He documentado cambios importantes
- [ ] Probé localmente y funciona
- [ ] No hay credenciales en el código
- [ ] Mensajes de commit son descriptivos
- [ ] He actualizado README.md si es relevante
- [ ] Mi rama está actualizada con `main`

---

## 🎓 Aprender sobre el proyecto

- Lee [README.md](README.md) completo
- Revisa [INSTALACION.md](INSTALACION.md)
- Estudia el PDF de documentación técnica
- Explora los archivos de comandos JSON
- Ejecuta `diagnose.sh` para entender el setup

---

## 🎯 Roadmap del proyecto

### Fase 4 (En progreso)
- [x] Reconocimiento básico con Vosk
- [ ] Remuestreo de audio USB
- [ ] Mejora de precisión con vocabulario personalizado

### Fase 5 (Pendiente)
- [ ] Llamadas via HFP
- [ ] WhatsApp Web
- [ ] Reconocer llamadas entrantes

### Fase 6 (Pendiente)
- [ ] Launcher UI centralizado
- [ ] Soporte pantalla táctil
- [ ] Indicadores visuales de estado

---

## 🙏 Gracias

Tu contribución, sin importar el tamaño, ayuda a que TalkAndTrack sea mejor.

¡Bienvenido al proyecto! 🎉

