# M.A.C.A.C.O

[English](README.en.md)

Herramienta de prueba para enviar múltiples solicitudes `POST` con datos sintéticos a un endpoint de registro en un servidor local. Sustituye la labor manual de preparar y enviar muchas cargas JSON en pruebas autorizadas de volumen o de comportamiento ante solicitudes repetidas, por ejemplo para comprobar la validación de datos, las respuestas y los controles de limitación de solicitudes.

## Funcionamiento

El script `main.py` lee `template.json` y genera una carga nueva para cada solicitud. Los valores con la forma `|? -> proveedor|` se sustituyen por datos de [Faker](https://faker.readthedocs.io/); los demás valores se envían tal como aparecen en la plantilla. El reemplazo también funciona dentro de objetos y listas anidados. Por ejemplo:

```json
{
  "username": "|? -> user_name|",
  "email": "|? -> email|",
  "password": "123456"
}
```

En este ejemplo, `username` y `email` cambian en cada envío, mientras que `password` permanece fijo. El nombre del marcador debe corresponder a un proveedor de Faker; `|? -> number|` utiliza el proveedor `random_number`. La plantilla debe ser un objeto JSON válido.

Las solicitudes se envían como JSON con un tiempo de espera de cinco segundos y sin seguir redirecciones. La barra de progreso muestra el último código de estado o el tipo de error de conexión. El resumen final cuenta como exitosas únicamente las respuestas HTTP `200` y `201`.

## Instalación y uso

Requiere Python 3 y un servidor de pruebas local con el endpoint correspondiente disponible.

```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
python3 main.py --host http://127.0.0.1:8000 --endpoint /api/auth/register --count 10 --workers 2
```

Antes de ejecutar, adapta `template.json` a los campos que acepta tu API. Las opciones disponibles son:

| Opción | Descripción | Valor predeterminado |
| --- | --- | --- |
| `--host` | Origen HTTP o HTTPS del servidor local, sin ruta. Solo admite `localhost`, `127.0.0.1` o `::1`. | `http://127.0.0.1:8000` |
| `--endpoint` | Ruta del endpoint; debe comenzar con `/`. | `/api/auth/register` |
| `--count` | Número máximo de solicitudes; debe ser positivo. | `10` |
| `--workers` | Solicitudes simultáneas, entre `1` y `5`. | `2` |

Faker usa `es_ES` por defecto. Para cambiar el idioma, copia `.env.example` a `.env` y ajusta `FAKER_LOCALE`, o define esa variable en el entorno. La variable de entorno tiene prioridad sobre `.env`.

## Uso responsable

Esta herramienta se proporciona para pruebas éticas de ciberseguridad en sistemas propios o con autorización expresa. Los envíos repetidos pueden crear registros y consumir recursos: utiliza un entorno de pruebas, datos sintéticos y un volumen acordado con el responsable del sistema. El usuario es responsable de cumplir el alcance de su autorización y la normativa aplicable.

## Licencia

Distribuido bajo la [licencia MIT](LICENSE). Consulta el archivo de licencia para conocer sus términos y el aviso de ausencia de garantías.
