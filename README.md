# SIGTVA — Implementación de patrones de diseño

Aplicación Flask en **tres capas** (MVC) que implementa un proceso por patrón:

| Patrón | Proceso | Dónde está |
|---|---|---|
| **Factory Method** | Venta de tiquete: creación de la tarifa | `factories/fabrica_tarifa.py` |
| **Abstract Factory** | Registro de envío (Paqueteo / Corporativa / Remesa) | `factories/fabrica_envio.py` — cliente: `services/servicio_registro_envio.py` |
| **Builder** | Venta de tiquete | `builders/constructor_tiquete.py` |
| **Prototype** | Registro de envío: remesa múltiple por clonación | `prototypes/prototipos_envio.py` — cliente: `services/servicio_prototipos.py` |
| **Singleton** | Venta de tiquete: bloqueo, consecutivo y caché única | `singletons/` (gestor, secuenciadores, validador) |

En la venta de tiquete los patrones **componen**: la `Tarifa` la crea el Factory Method y el Builder la recibe ya creada; en el registro de envío, cada guía clonada por Prototype se numera con el SecuenciadorGuia (Singleton).

## Capas

| Capa | Carpetas / archivos |
|---|---|
| Presentación (vista + controlador) | `app.py`, `templates/` |
| Lógica de negocio | `services/`, `factories/`, `builders/`, `prototypes/`, `singletons/`, `domain/` |
| Datos | `dao/`, `models/` |

Regla de dependencias: datos solo usa datos; lógica usa lógica y datos; presentación usa lógica (los procesos) y, en tres rutas de consulta, datos directamente.

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
python demos/demo_prototype.py
python demos/demo_singleton.py
```

## Calidad

```bash
python -m ruff check .   # limpio: imports ordenados, sin excepciones ciegas,
                         # datetimes con zona, anotaciones modernas
```

Convenciones: español en código y diagramas, tipos con `X | None` (Python 3.11+),
nombres UML en camelCase igual que en los diagramas de clase.
