import random
import unittest
from campusaccess.avl import AgendaAVL
from campusaccess.carga import cargar_datos, preparar_sistema
from campusaccess.hash_metricas import TablaHashEducativa, evaluar, hash_estable
from campusaccess.models import Solicitud, hora
from campusaccess.registro import RegistroSolicitudes
from main import sistema_completo, resultados_metricas


def s(i: int, minuto: int) -> Solicitud:
    return Solicitud(f"T-{i:03d}", "u@ejemplo.edu.co", "Laboratorio", minuto)


class RegistroTests(unittest.TestCase):
    def test_datos_json_39(self):
        self.assertEqual(len(cargar_datos()), 39)

    def test_alta_y_consulta(self):
        r = RegistroSolicitudes(); r.insertar(s(1, 540))
        self.assertEqual(r.consultar("T-001").minuto, 540)
        self.assertEqual(len(r), 1)

    def test_set_existencia_y_fallo(self):
        r = RegistroSolicitudes(); r.insertar(s(1, 540))
        self.assertTrue(r.existe("T-001"))
        self.assertFalse(r.existe("T-999"))
        self.assertIsNone(r.consultar("T-999"))

    def test_rechaza_duplicados(self):
        r = RegistroSolicitudes(); r.insertar(s(1, 540))
        with self.assertRaises(ValueError): r.insertar(s(1, 600))

    def test_actualizacion(self):
        r = RegistroSolicitudes(); r.insertar(s(1, 540))
        self.assertEqual(r.actualizar_estado("T-001", "autorizada").estado, "autorizada")
        self.assertEqual(r.consultar("T-001").estado, "autorizada")

    def test_actualizacion_inexistente(self):
        with self.assertRaises(KeyError): RegistroSolicitudes().actualizar_estado("T-999", "cerrada")

    def test_estado_invalido_no_cambia_sistema(self):
        r=RegistroSolicitudes(); r.insertar(s(1,540))
        with self.assertRaises(ValueError): r.actualizar_estado("T-001", "desconocida")
        self.assertEqual(r.consultar("T-001").estado, "pendiente")


class AVLTests(unittest.TestCase):
    def test_minimo_maximo_vacio(self):
        a=AgendaAVL(); self.assertIsNone(a.minimo()); self.assertIsNone(a.maximo())

    def test_actualizar_datos_mantiene_indice_consistente(self):
        a = AgendaAVL(); original = s(1, 540); a.insertar(original)
        nuevo = original.con_estado("autorizada")
        a.actualizar_solicitud(nuevo)
        self.assertEqual(a.rango(540, 541)[0].estado, "autorizada")
        self.assertTrue(a.validar())

    def test_actualizacion_inexistente_indice(self):
        a = AgendaAVL()
        with self.assertRaises(KeyError):
            a.actualizar_solicitud(s(1, 540))

    def test_rango_semiabierto_incluye_inicio_excluye_fin(self):
        a=AgendaAVL()
        for i,t in [(1,539),(2,540),(3,599),(4,600)]:a.insertar(s(i,t))
        self.assertEqual([x.minuto for x in a.rango(540,600)],[540,599])

    def test_dos_registros_mismo_minuto(self):
        a=AgendaAVL(); a.insertar(s(2,540)); a.insertar(s(1,540))
        self.assertEqual([x.identificador for x in a.rango(540,541)],['T-001','T-002'])

    def test_rango_vacio(self):
        a=AgendaAVL(); a.insertar(s(1,540))
        self.assertEqual(a.rango(800,900),[])

    def test_rango_invalido(self):
        a=AgendaAVL()
        for lo,hi in [(5,5),(10,3),(-1,10),(1439,1441)]:
            with self.assertRaises(ValueError): a.rango(lo,hi)

    def test_orden_adversarial_y_balance(self):
        a=AgendaAVL()
        for i in range(1,201): a.insertar(s(i,480+i))
        self.assertTrue(a.validar())
        self.assertLessEqual(a.altura, 12)
        self.assertEqual(a.minimo().minuto,481)
        self.assertEqual(a.maximo().minuto,680)

    def test_rechazo_id_repetido(self):
        a=AgendaAVL(); a.insertar(s(1,540))
        with self.assertRaises(ValueError): a.insertar(s(1,700))

    def test_aleatorio_coincide_con_filtro_ordenado(self):
        rnd = random.Random(2026)
        valores=list(range(450,650))
        rnd.shuffle(valores)
        a=AgendaAVL()
        for i,t in enumerate(valores): a.insertar(s(i,t))
        self.assertTrue(a.validar())
        esperado=sorted((x for x in valores if 500 <= x < 580))
        self.assertEqual([x.minuto for x in a.rango(500,580)], esperado)


class HashTests(unittest.TestCase):
    def test_hash_estable(self):
        self.assertEqual(hash_estable(''), 0x811C9DC5)
        self.assertEqual(hash_estable('hello'), 0x4F9F2CAB)

    def test_carga_y_aciertos_fallos(self):
        r,_=sistema_completo()
        m=resultados_metricas(r)
        self.assertEqual(m['n'], 40)
        self.assertEqual(m['capacidad'], 53)
        self.assertEqual(m['aciertos'], 5)
        self.assertEqual(m['fallos'], 5)
        self.assertAlmostEqual(m['alfa'],40/53,places=4)

    def test_colisiones_preservan_claves(self):
        h=TablaHashEducativa(capacidad=1)
        h.insertar('A');h.insertar('B');h.insertar('C')
        self.assertEqual(h.n,3)
        self.assertEqual(h.colisiones_insercion,2)
        self.assertEqual(h.buscar('C').pasos,4)

    def test_repeticion_no_aumenta_carga(self):
        h=TablaHashEducativa(capacidad=17)
        h.insertar('A');h.insertar('A')
        self.assertEqual(h.n,1)

    def test_actualizacion_integridad_registro(self):
        r,a=sistema_completo()
        self.assertEqual(len(r),40)
        self.assertEqual(len(a),40)
        self.assertTrue(r.validar() and a.validar())
        self.assertEqual({x.identificador for x in r.solicitudes()},
                         {f'AC-{i:03d}' for i in range(1, 41)})
        self.assertEqual([len(a.rango(lo, hi)) for lo, hi in
                          [(540, 600), (600, 660), (1260, 1320)]], [7, 6, 0])
        self.assertEqual(len(a.rango(540,600)) + len(a.rango(600,660)),
                         sum(540 <= x.minuto < 660 for x in r.solicitudes()))


if __name__ == '__main__': unittest.main()
