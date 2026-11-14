# ProtoDS CampusAccess — Evaluación #2 (Momento 2)

**Caso simulado:** centro de acceso a recursos de un campus digital universitario. Este proyecto desarrolla **exactamente dos microprototipos**: **A (mapa/conjunto hash)** y **B (árbol AVL para rangos)**. No implementa un grafo BFS, porque la guía pide seleccionar dos de tres módulos.

## Ejecución

Requiere **Python 3.10 o superior**. Usa exclusivamente la biblioteca estándar.

```bash
python main.py demo
python main.py metricas
python main.py metricas --guardar
python -m unittest discover -s tests -v
```

## Escenario

El laboratorio digital registra solicitudes de acceso a recursos tecnológicos mediante su ID. Cada solicitud tiene un horario de atención (minutos desde la medianoche) y un estado. Los datos ficticios se almacenan en `data/solicitudes.json` (39 solicitudes). La demostración agrega la solicitud `AC-040` y opera sobre un total de **40 registros**.

### Módulo A · acceso exacto por ID

- `RegistroSolicitudes` almacena `id -> Solicitud` en `dict` y el conjunto de IDs en `set`.
- Operaciones: `insertar`, `consultar`, `actualizar_estado`, `existe`, rechazo de duplicados y casos inexistentes.
- Complejidad **promedio** de inserción/búsqueda/actualización `O(1)`; peor caso puede ser `O(n)` bajo colisiones adversas.

### Módulo B · consultas temporales ordenadas

- `AgendaAVL` indexa la clave **(minuto, ID)** para conservar solicitudes con el mismo horario.
- La consulta `rango(desde, hasta)` representa **[desde, hasta)**, con inicio inclusivo y fin exclusivo.
- El recorrido produce resultados ordenados; se muestran dos rangos y uno vacío, más el mínimo y el máximo.
- Inserción `O(log n)` y rango `O(log n + k)` para `k` resultados, asumiendo el AVL equilibrado.

### Hash mini-métrica (opcional, vinculada a A)

`TablaHashEducativa` usa encadenamiento con **53 cubetas de capacidad fija**, índice con FNV-1a determinista y conteo definido de pasos: **1 acceso a cubeta + 1 por comparación de clave**. Inserta 40 IDs y mide 5 búsquedas exitosas y 5 inexistentes. Calcula `α = n / capacidad` y las colisiones de inserción.

**No afirmamos conocer el factor de carga interno de `dict`:** esta métrica corresponde únicamente a la tabla **educativa** que implementamos.

## Estructura

```text
main.py                  CLI demo y metricas
campusaccess/models.py   modelo inmutable y validación
campusaccess/registro.py módulo A: dict/set
campusaccess/avl.py      módulo B: AVL y rango [a,b)
campusaccess/hash_metricas.py tabla hash educativa
campusaccess/carga.py    carga desde JSON
data/solicitudes.json     39 solicitudes ficticias
tests/test_modulos.py    22 pruebas unitarias
evidencias/               transcripciones y mini-métrica JSON
```

## Alcance y límites

Prototipo académico en memoria, determinista, sin datos personales reales, autenticación, API, concurrencia ni persistencia de actualizaciones. El escenario UCC es **ilustrativo**, no una integración institucional. El índice AVL no ofrece cambio de horario en caliente: una edición de `minuto` exigiría sincronizar o reconstruir el índice. El sistema demuestra acceso por clave y consulta por rango; no pretende ser un software de producción.

## Reproducibilidad

Ejecuta `python main.py demo`, `python main.py metricas` y los tests en la raíz del proyecto. Las evidencias almacenadas son resultados de estas ejecuciones, no capturas de una interfaz institucional. El resultado puede variar en duración, pero **no** en contenidos ni conteos.

## Referencias

- OpenDSA. *Chapter Introduction: Search* (búsqueda exacta y por rango): https://opendsa-server.cs.vt.edu/ODSA/Books/cnu/cpsc270/spring-2025/CNUCPSC270SP2025/html/SearchIntro.html
- OpenDSA. *Tree-based Indexing*: https://opendsa-server.cs.vt.edu/ODSA/StandaloneModules/20231208151338/html/TreeIndexing.html
- OpenDSA. *Hashing - Chapter Introduction*: https://opendsa-server.cs.vt.edu/ODSA/Books/pubbook/odsa-all-0013bb43-a12f-4ab3-9b86-73b317f1e37e/fall-2017/Public_Access_0926b/html/HashIntro.html
- Python Software Foundation. *Built-in Types*: https://docs.python.org/3/library/stdtypes.html
