# Cómo crear y usar una API de Groq en Google Colab

## 1. Crear una cuenta

1. Ingresar a [Groq Console](https://console.groq.com/).
2. Crear una cuenta o iniciar sesión.
3. Confirmar el correo si la plataforma lo solicita.

## 2. Crear la API key

1. Abrir la sección [API Keys](https://console.groq.com/keys).
2. Seleccionar **Create API Key**.
3. Asignar un nombre identificable, por ejemplo: `clase-03-colab`.
4. Copiar la clave inmediatamente. Normalmente solo se muestra una vez.

La clave funciona como una contraseña. No compartirla por WhatsApp, correo, capturas de pantalla, notebooks públicos ni GitHub.

## 3. Guardar la clave como secreto en Colab

En el notebook:

1. Abrir el panel izquierdo de Colab.
2. Seleccionar el ícono de **llaves / Secrets**.
3. Crear un secreto llamado exactamente:

```text
GROQ_API_KEY
```

4. Pegar la clave en el valor.
5. Activar la opción para que el notebook pueda acceder al secreto.

No escribir la clave directamente en una celda compartida.

## 4. Instalar el SDK

Ejecutar en una celda de Colab:

```python
%pip install -q groq
```

## 5. Leer el secreto sin mostrarlo

```python
import os
from google.colab import userdata

os.environ["GROQ_API_KEY"] = userdata.get("GROQ_API_KEY")
```

La celda no debe contener `print(os.environ["GROQ_API_KEY"])`.

## 6. Probar la conexión

```python
from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

respuesta = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {"role": "user", "content": "Responde únicamente: conexión exitosa"}
    ],
    max_tokens=20,
)

print(respuesta.choices[0].message.content)
```

Si todo funciona, debe aparecer una respuesta breve del modelo.

## 7. Usar la clave en el demo de Clase 03

En el notebook de la clase:

```python
MODO_DEMO = "groq"
MODEL = "openai/gpt-oss-20b"
```

Primero ejecutar el notebook en modo `mock`. Después configurar el secreto, cambiar a `groq` y volver a ejecutar las celdas dependientes.

## 8. Si aparece un error

- **Falta `GROQ_API_KEY`:** revisar que el secreto se llame exactamente así.
- **401 Unauthorized:** la clave está incorrecta, fue revocada o tiene espacios adicionales.
- **404 o modelo no encontrado:** verificar el identificador `openai/gpt-oss-20b` y los modelos disponibles en la cuenta.
- **429 Too Many Requests:** se alcanzó un límite; esperar y reducir el número de solicitudes.
- **Error de esquema:** revisar que todos los campos estén en `required` y que los objetos tengan `additionalProperties: false` cuando se use `strict: true`.

## 9. Seguridad y cierre

- Usar claves individuales; no compartir una clave entre equipos.
- No subir la clave a GitHub ni guardarla en la bitácora.
- Revocar la clave desde Groq Console si se expone accidentalmente.
- Usar datos ficticios o anonimizados en las pruebas.
- Consultar la [documentación oficial de Groq](https://console.groq.com/docs/quickstart) y sus [límites de uso](https://console.groq.com/docs/rate-limits).

