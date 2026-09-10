"""Pruebas de la API y del ciclo completo del gemelo simulado."""

import json
import threading
import time

import anyio
import httpx
import pytest
import uvicorn
from fastapi.testclient import TestClient

from campus_twin_demo import configuracion as cfg
from campus_twin_demo.api import app, flujo_de_estado, gemelo
from campus_twin_demo.gemelo import GemeloEnVivo


PUERTO_DE_PRUEBA = 8419


@pytest.fixture
def cliente():
    with TestClient(app) as cliente:
        yield cliente


@pytest.fixture(scope="module")
def servidor():
    """Levanta uvicorn en un hilo para probar el servidor de verdad."""
    configuracion = uvicorn.Config(
        app, host="127.0.0.1", port=PUERTO_DE_PRUEBA, log_level="warning", lifespan="on"
    )
    servidor = uvicorn.Server(configuracion)
    hilo = threading.Thread(target=servidor.run, daemon=True)
    hilo.start()

    url = f"http://127.0.0.1:{PUERTO_DE_PRUEBA}"
    limite = time.monotonic() + 15
    while time.monotonic() < limite:
        if servidor.started:
            break
        time.sleep(0.05)
    else:
        raise AssertionError("uvicorn no arranco a tiempo")

    try:
        yield url
    finally:
        servidor.should_exit = True
        hilo.join(timeout=10)


def correr_un_dia(velocidad: float = 3600.0) -> GemeloEnVivo:
    """Un dia simulado completo, en pasos de un minuto simulado."""
    propio = GemeloEnVivo(velocidad=velocidad, semilla=419)
    segundos_reales_por_minuto = 60.0 / velocidad
    for _ in range(24 * 60):
        propio.paso(segundos_reales_por_minuto)
    return propio


def test_el_estado_trae_todas_las_secciones(cliente):
    respuesta = cliente.get("/api/estado")
    assert respuesta.status_code == 200
    datos = respuesta.json()
    for clave in ("reloj", "resumen", "nodos", "alertas", "salud", "fantasma", "mensajes", "umbrales"):
        assert clave in datos, f"falta la seccion {clave}"
    assert datos["reloj"]["velocidad"] > 0


def test_el_historico_valida_el_nodo(cliente):
    assert cliente.get("/api/historico", params={"nodo": "no-existe", "magnitud": "co2"}).status_code == 404
    respuesta = cliente.get("/api/historico", params={"nodo": cfg.NODO_AMBIENTAL, "magnitud": "co2"})
    assert respuesta.status_code == 200
    assert respuesta.json()["unidad"] == "ppm"


def test_los_escenarios_se_aplican_y_se_validan(cliente):
    assert cliente.post("/api/demo/escenario/no-existe").status_code == 404
    respuesta = cliente.post("/api/demo/escenario/vacio-con-luces")
    assert respuesta.json()["escenario"] == "vacio-con-luces"
    cliente.post("/api/demo/escenario/restablecer")


def test_la_velocidad_queda_acotada(cliente):
    assert cliente.post(f"/api/demo/velocidad/{cfg.VELOCIDAD_MAXIMA * 10}").json()["velocidad"] == cfg.VELOCIDAD_MAXIMA
    assert cliente.post("/api/demo/velocidad/0").json()["velocidad"] == cfg.VELOCIDAD_MINIMA
    cliente.post(f"/api/demo/velocidad/{cfg.VELOCIDAD_POR_DEFECTO}")


def test_la_pausa_se_alterna(cliente):
    primero = cliente.post("/api/demo/pausa").json()["pausado"]
    segundo = cliente.post("/api/demo/pausa").json()["pausado"]
    assert primero != segundo
    assert gemelo.reloj.pausado is False


def test_la_configuracion_expone_umbrales_y_escenarios(cliente):
    datos = cliente.get("/api/configuracion").json()
    assert datos["umbralDeCo2"] == cfg.UMBRAL_DE_CO2_PPM
    assert "vacio-con-luces" in datos["escenarios"]
    assert datos["nodos"][cfg.NODO_ENERGIA]["requisito"] == "RF-01"


def test_el_flujo_de_estado_emite_eventos_sse():
    """Cada evento del flujo es una linea `data:` con el estado completo."""

    async def dos_eventos():
        with anyio.fail_after(10):
            flujo = flujo_de_estado()
            try:
                primero = await flujo.__anext__()
                segundo = await flujo.__anext__()
            finally:
                await flujo.aclose()
        return primero, segundo

    primero, segundo = anyio.run(dos_eventos)
    for evento in (primero, segundo):
        assert evento.startswith("data: ") and evento.endswith("\n\n")
        assert "resumen" in json.loads(evento[len("data: ") :])


def test_el_servidor_real_entrega_el_stream(servidor):
    """Prueba de punta a punta contra uvicorn, que es como lo consume el navegador."""

    with httpx.stream("GET", f"{servidor}/api/stream", timeout=10.0) as respuesta:
        assert respuesta.status_code == 200
        assert respuesta.headers["content-type"].startswith("text/event-stream")
        for linea in respuesta.iter_lines():
            if linea.startswith("data: "):
                datos = json.loads(linea[len("data: ") :])
                assert datos["resumen"]["potencia"] > 0
                return
    raise AssertionError("el servidor no envio ningun evento")


def test_el_servidor_real_sirve_la_api(servidor):
    respuesta = httpx.get(f"{servidor}/api/estado", timeout=10.0)
    assert respuesta.status_code == 200
    assert respuesta.json()["reloj"]["velocidad"] > 0


def test_un_dia_completo_deja_consumo_fantasma_medible():
    propio = correr_un_dia()
    reporte = propio.auditor.como_diccionario()
    assert reporte["kwhTotales"] > 0
    assert reporte["kwhFantasma"] > 0
    # la meta del proyecto es identificar al menos un 5 % evitable
    assert reporte["porcentajeEvitable"] >= 5.0
    assert reporte["kwhFueraDeHorario"] > reporte["kwhEnHorario"]
    assert reporte["soles"] > 0 and reporte["kgCO2"] > 0


def test_un_dia_completo_dispara_las_reglas_esperadas():
    propio = correr_un_dia()
    disparadas = {alerta["codigo"] for alerta in propio.reglas.historial_como_lista(limite=40)}
    assert "co2-alto" in disparadas
    assert "consumo-con-aula-vacia" in disparadas


def test_un_dia_completo_no_pierde_muestras():
    propio = correr_un_dia()
    for fila in propio.almacen.salud_como_lista(propio.reloj.momento):
        if fila["recibidas"] == 0:
            continue
        assert fila["muestrasPerdidas"] == 0.0, fila
        assert fila["duplicadas"] == 0
        assert fila["recibidas"] == fila["esperadas"]


def test_la_instantanea_es_serializable_a_json():
    propio = correr_un_dia(velocidad=3600.0)
    texto = json.dumps(propio.instantanea(), ensure_ascii=False)
    assert len(texto) > 500


def test_la_senal_debil_se_ve_como_muestras_perdidas():
    """RF-13: los huecos de secuencia delatan al nodo con mala senal."""
    propio = GemeloEnVivo(velocidad=3600.0, semilla=419)
    propio.aplicar_escenario("senal-debil")
    for _ in range(240):
        propio.paso(60.0 / 3600.0)

    por_nodo = {fila["nodo"]: fila for fila in propio.almacen.salud_como_lista(propio.reloj.momento)}
    debil = por_nodo[cfg.NODO_OCUPACION_FONDO]
    sano = por_nodo[cfg.NODO_ENERGIA]
    assert debil["muestrasPerdidas"] > cfg.MAXIMO_DE_MUESTRAS_PERDIDAS
    assert debil["senal"] < cfg.SENAL_TIPICA_DBM
    assert sano["muestrasPerdidas"] == 0.0
