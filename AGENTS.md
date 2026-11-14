# Codex: guía técnica del repositorio ProtoDS CampusAccess

- Aplicar cambios mínimos y verificables; se implementan exactamente los módulos A y B.
- No agregar un menú interactivo, API, frontend, grafo BFS ni dependencias si no lo exige un defecto o cambio aprobado.
- Evitar datos reales del campus. Todos los ejemplos deben seguir siendo ficticios.
- No modificar `evidencias/metricas_hash.json` sin regenerarla mediante `python main.py metricas --guardar`.
- Conservar la definición de α: la capacidad es la de `TablaHashEducativa`, no la interna de Python `dict`.
- Validar `python main.py demo`, `python main.py metricas` y `python -m unittest discover -s tests -v` antes de commit.
- No crear commits retroactivos, ni hacer `push --force`, ni borrar el historial remoto.
- Si el repositorio remoto existe, primero consultar su contenido y las ramas antes de publicar.
