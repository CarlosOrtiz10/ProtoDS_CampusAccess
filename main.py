"""ProtoDS CampusAccess · Evaluación Momento 2 · módulos A + B solamente."""
import argparse
import json
from pathlib import Path
from campusaccess.avl import AgendaAVL
from campusaccess.carga import preparar_sistema
from campusaccess.hash_metricas import TablaHashEducativa, evaluar
from campusaccess.models import Solicitud, hora

ROOT = Path(__file__).resolve().parent
EVIDENCIAS = ROOT / "evidencias"


def sistema_completo():
    registro, agenda = preparar_sistema()
    # Alta real: parte de 39 registros persistidos en JSON y llega a 40.
    nuevo = Solicitud("AC-040", "alumno40@ejemplo.edu.co", "Licencia GIS", 599)
    registro.insertar(nuevo)
    agenda.insertar(nuevo)
    return registro, agenda


def resultados_metricas(registro) -> dict:
    tabla = TablaHashEducativa(capacidad=53)
    for clave in sorted(s.identificador for s in registro.solicitudes()):
        tabla.insertar(clave)
    presentes = ["AC-003", "AC-011", "AC-020", "AC-034", "AC-040"]
    ausentes = ["AC-091", "AC-092", "AC-093", "AC-094", "AC-095"]
    return evaluar(tabla, presentes, ausentes)


def demo() -> None:
    registro, agenda = sistema_completo()
    print("=== PROTODS · CAMPUSACCESS / UCC · ESCENARIO FICTICIO ===")
    print("[DATOS] JSON: 39 solicitudes iniciales; alta demostrada: AC-040; total: 40")
    print("\n[A] MAPA/CONJUNTO · 3 operaciones exitosas + 1 inexistente")
    print("  1. INSERTAR  AC-040 ->", registro.consultar("AC-040").recurso)
    actualizado = registro.actualizar_estado("AC-005", "autorizada")
    agenda.actualizar_solicitud(actualizado)  # mantener registro e índice sincronizados
    print("  2. ACTUALIZAR AC-005 ->", actualizado.estado)
    print("  3. CONSULTAR  AC-005 ->", registro.consultar("AC-005").recurso)
    print("  EXISTE AC-040 ->", registro.existe("AC-040"), "| AC-999 ->", registro.existe("AC-999"))
    print("  4. CONSULTA INEXISTENTE AC-999 ->", registro.consultar("AC-999"))
    print("  IDS sin duplicados ->", registro.validar())
    try:
        registro.insertar(Solicitud("AC-040", "otro@ejemplo.edu.co", "Impresora 3D", 630))
    except ValueError as e:
        print("  DUPLICADO RECHAZADO ->", e)
    print("\n[B] ÁRBOL AVL · 40 registros indexados por (minuto, ID)")
    print("  min:", hora(agenda.minimo().minuto), agenda.minimo().identificador)
    print("  max:", hora(agenda.maximo().minuto), agenda.maximo().identificador)
    for lo, hi in [(540, 600), (600, 660), (1260, 1320)]:
        encontrados = agenda.rango(lo, hi)
        print(f"  RANGO [{hora(lo)}, {hora(hi)}) · {len(encontrados)} resultados:")
        print("   ", ", ".join(f"{hora(s.minuto)} {s.identificador}" for s in encontrados) or "(vacío)")
    print(f"  ALTURA AVL={agenda.altura} | BALANCE={agenda.validar()} | N={len(agenda)}")
    print("\n[CIERRE] A y B funcionales. Hash educativo: python main.py metricas")


def metricas(guardar: bool = False) -> None:
    registro, _ = sistema_completo()
    r = resultados_metricas(registro)
    print("=== MÓDULO A: MINI-MÉTRICA HASH EDUCATIVA (ENCADENAMIENTO) ===")
    print(f"Registros={r['n']} | capacidad={r['capacidad']} cubetas | α={r['alfa']:.4f}")
    print(f"Colisiones en inserción={r['colisiones']}")
    print(f"Búsquedas: {r['aciertos']} aciertos / {r['fallos']} fallos (5 existentes + 5 inexistentes)")
    print("Pasos = 1 acceso a cubeta + 1 por comparación de clave")
    print(f"Promedio exitosas={r['promedio_pasos_existentes']:.2f} | fallidas={r['promedio_pasos_ausentes']:.2f} | total={r['promedio_pasos_total']:.2f}")
    print("Nota: α pertenece a la TABLA EDUCATIVA de 53 cubetas, no al dict interno de Python.")
    if guardar:
        EVIDENCIAS.mkdir(exist_ok=True)
        archivo = EVIDENCIAS / "metricas_hash.json"
        archivo.write_text(json.dumps(r, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("Datos guardados en", archivo.relative_to(ROOT))


def main() -> None:
    p = argparse.ArgumentParser(description="Microprototipos A y B - CampusAccess")
    p.add_argument("comando", choices=["demo", "metricas"])
    p.add_argument("--guardar", action="store_true", help="Persistir mediciones en evidencias/")
    args = p.parse_args()
    if args.comando == "demo":
        demo()
    else:
        metricas(guardar=args.guardar)


if __name__ == "__main__":
    main()
