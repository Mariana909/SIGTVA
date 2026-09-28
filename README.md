# SIGTVA — Implementación de patrones de diseño

Aplicación Flask en **tres capas** (MVC) que implementa un proceso por patrón:

| Patrón | Proceso | Dónde está |
|---|---|---|
| **Factory Method** | Venta de tiquete: creación de la tarifa | `factories/fabrica_tarifa.py` |
| **Abstract Factory** | Registro de envío (Paqueteo / Corporativa / Remesa) | `factories/fabrica_envio.py` · cliente: `services/servicio_registro_envio.py` |
| **Builder** | Venta de tiquete | `builders/constructor_tiquete.py` |

En la venta de tiquete los patrones **componen**: la `Tarifa` la crea el Factory Method y el Builder la recibe ya creada.

## Capas

| Capa | Carpetas / archivos |
|---|---|
| Presentación (vista + controlador) | `app.py`, `templates/` |
| Lógica de negocio | `services/`, `factories/`, `builders/`, `domain/` |
| Datos | `dao/`, `models/` |

## Ejecución

```bash
pip install -r requirements.txt
python app.py            # http://127.0.0.1:5000  (crea la BD y datos de prueba solos)
```

Tras cada compra o envío, la factura muestra el panel **«Patrones en acción»** con los pasos reales de cada patrón.

## Demos por consola (una por patrón)

```bash
python demos/demo_factory_method.py
python demos/demo_abstract_factory.py
python demos/demo_builder.py
```
