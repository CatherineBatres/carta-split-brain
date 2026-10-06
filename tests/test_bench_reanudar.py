"""D-29: el benchmark debe poder interrumpirse (apagón, cierre) y retomarse sin perder nada."""
import json
import shutil

from bench import correr_bench as cb
from splitbrain.local_llm import Generacion, OllamaNoDisponible


class ClienteQueSeCae:
    limite = 10**9      # cuántas respuestas da antes de "apagarse"
    llamadas = 0

    def __init__(self, modelo):
        self.modelo = modelo

    def disponible(self):
        return True

    def descargar(self):
        pass

    def generar(self, prompt, sistema="", formato_json=False):
        if prompt in ("Hola", "Responde solo: listo"):
            return Generacion("listo", self.modelo, {"latencia_total_s": 0.1})
        type(self).llamadas += 1
        if type(self).llamadas > type(self).limite:
            raise OllamaNoDisponible("se apagó")
        texto = '{"puesto":"x","requisitos":[],"modalidad":"remoto"}' if formato_json else \
            "Tu expectativa es razonable; menciónala cuando RR. HH. pregunte. " * 4
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


def test_no_borra_la_hoja_ciega_ya_calificada(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch)
    ClienteQueSeCae.limite = 10**9
    args = dict(modelos=["a", "b"], reps=1, tareas=["nota"], simulado=False, pausa=0, cada=0)
    cb.correr(**args)
    hoja = tmp_path / "resultados" / "evaluacion_ciega.csv"
    hoja.write_text(hoja.read_text(encoding="utf-8-sig") + "MIS NOTAS", encoding="utf-8-sig")
    cb.correr(**args)                                # nada pendiente: solo rearma archivos
    assert "MIS NOTAS" in hoja.read_text(encoding="utf-8-sig")
