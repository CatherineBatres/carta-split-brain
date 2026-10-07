"""D-29: el benchmark debe poder interrumpirse (apagón, cierre) y retomarse sin perder nada."""
import json
import shutil

from bench import correr_bench as cb
from splitbrain.local_llm import Generacion, OllamaNoDisponible


class ClienteQueSeCae:
    limite = 10**9      # cuántas respuestas da antes de "apagarse"
    llamadas = 0
    semillas = set()

    def __init__(self, modelo):
        self.modelo = modelo

    def disponible(self):
        return True

    def descargar(self):
        pass

    def generar(self, prompt, sistema="", formato_json=False, semilla=None):
        type(self).semillas.add(semilla)
        if prompt in ("Hola", "Responde solo: listo"):
            return Generacion("listo", self.modelo, {"latencia_total_s": 0.1})
        type(self).llamadas += 1
        if type(self).llamadas > type(self).limite:
            raise OllamaNoDisponible("se apagó")
        texto = '{"puesto":"x","requisitos":[],"modalidad":"remoto"}' if formato_json else \
            (f"[{self.modelo}] Tu expectativa es razonable; menciónala cuando RR. HH. pregunte. "
             f"Ref {sum(map(ord, prompt)) % 9973}. " * 4)
        return Generacion(texto, self.modelo, {"latencia_total_s": 1.0})


def _preparar(tmp_path, monkeypatch):
    (tmp_path / "bench").mkdir()
    shutil.copy(cb.CASOS, tmp_path / "bench" / "casos.json")
    monkeypatch.setattr(cb, "RAIZ", tmp_path)
    monkeypatch.setattr(cb, "ClienteOllama", ClienteQueSeCae)
    ClienteQueSeCae.llamadas = 0


def test_se_retoma_donde_se_quedo_sin_repetir(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch)
    args = dict(modelos=["a", "b"], reps=2, tareas=["nota", "extraccion"], simulado=False,
                pausa=0, cada=0)
    progreso = tmp_path / "resultados" / "crudo" / "progreso.jsonl"

    ClienteQueSeCae.limite = 7                      # primera corrida: se "apaga" a la 8.ª
    cb.correr(**args)
    assert len(progreso.read_text(encoding="utf-8").splitlines()) == 7

    with open(progreso, "a", encoding="utf-8") as fh:   # línea a medias por el apagón
        fh.write('{"modelo": "a", "caso": "c0')

    ClienteQueSeCae.limite = 10**9                  # segunda corrida: termina
    ClienteQueSeCae.llamadas = 0
    cb.correr(**args)
    filas = cb._leer_progreso(progreso)
    claves = [(f["modelo"], f["caso"], f["tarea"], f["rep"]) for f in filas]
    plan = cb._plan(json.loads(cb.CASOS.read_text(encoding="utf-8")), ["a", "b"],
                    ["nota", "extraccion"], 2)
    assert sorted(claves) == sorted(plan) and len(set(claves)) == len(claves)
    assert ClienteQueSeCae.llamadas == len(plan) - 7    # no repitió lo ya hecho
    assert {42, 43} <= ClienteQueSeCae.semillas         # cada repetición usa su propia semilla


def test_la_hoja_ciega_conserva_notas_y_no_confunde_corridas(tmp_path, monkeypatch):
    import csv
    from bench.hoja import leer_hoja
    _preparar(tmp_path, monkeypatch)
    ClienteQueSeCae.limite = 10**9
    base = dict(reps=1, tareas=["nota"], simulado=False, pausa=0, cada=0)
    hoja = tmp_path / "resultados" / "evaluacion_ciega.csv"

    # Una hoja VIEJA, de otra corrida, con la misma cantidad de notas (10) y otros textos.
    hoja.parent.mkdir(parents=True)
    (hoja.parent / "crudo").mkdir()
    with open(hoja, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "caso", "tarea", "texto", *cb.COLS_HOJA])
        w.writerows([[f"T{i:03d}", "c01", "nota", f"nota vieja {i}", "", "", "", ""]
                     for i in range(10)])
    (hoja.parent / "crudo" / "clave_ciega.json").write_text(
        json.dumps({f"T{i:03d}": "viejo" for i in range(10)}))

    cb.correr(modelos=["a"], **base)                 # 10 notas nuevas del modelo "a"
    filas = leer_hoja(hoja)
    assert len(filas) == 10 and not any("vieja" in f["texto"] for f in filas)

    filas[0]["claridad_1a5"], filas[0]["inventa_datos_si_no"] = "4", "no"   # califico una
    texto_calificado = filas[0]["texto"]
    with open(hoja, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0].keys()), delimiter=";")  # como Excel
        w.writeheader()
        w.writerows(filas)

    cb.correr(modelos=["a", "b"], **base)            # llega el segundo modelo: 20 notas
    filas = leer_hoja(hoja)
    assert len(filas) == 20
    mias = [f for f in filas if f["texto"] == texto_calificado and f["claridad_1a5"] == "4"]
    assert mias and mias[0]["inventa_datos_si_no"] == "no"   # la calificación no se perdió

    antes = hoja.read_bytes()
    cb.correr(modelos=["a", "b"], **base)            # nada nuevo: la hoja queda intacta
    assert hoja.read_bytes() == antes
