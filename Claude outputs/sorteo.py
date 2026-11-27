"""Lógica del sorteo de amigo invisible (sin dependencias de interfaz)."""
import random


class SorteoError(Exception):
    pass


def sortear(nombres, fijas=None, prohibidas=None, intentos=200):
    """Devuelve un dict {quien_regala: a_quien_le_regala}.

    nombres:    lista de participantes
    fijas:      lista de tuplas (A, B) -> A le regala sí o sí a B
    prohibidas: lista de tuplas (A, B) -> A NO puede regalarle a B
    """
    fijas = fijas or []
    prohibidas = set(prohibidas or [])
    nombres = list(nombres)

    if len(nombres) < 2:
        raise SorteoError("Se necesitan al menos 2 participantes.")
    if len(set(nombres)) != len(nombres):
        raise SorteoError("Hay nombres repetidos.")

    asignacion = {}
    usados = set()
    for a, b in fijas:
        if a not in nombres or b not in nombres:
            raise SorteoError(f"La pareja fija {a} → {b} tiene un nombre que no está en la lista.")
        if a == b:
            raise SorteoError(f"{a} no puede regalarse a sí mismo/a.")
        if a in asignacion:
            raise SorteoError(f"{a} tiene más de una pareja fija.")
        if b in usados:
            raise SorteoError(f"A {b} le regalan dos personas en las parejas fijas.")
        if (a, b) in prohibidas:
            raise SorteoError(f"{a} → {b} está como fija y como prohibida a la vez.")
        asignacion[a] = b
        usados.add(b)

    pendientes = [n for n in nombres if n not in asignacion]
    libres = [n for n in nombres if n not in usados]

    def backtrack(i):
        if i == len(pendientes):
            return True
        quien = pendientes[i]
        opciones = [r for r in libres
                    if r not in usados and r != quien and (quien, r) not in prohibidas]
        random.shuffle(opciones)
        for r in opciones:
            asignacion[quien] = r
            usados.add(r)
            if backtrack(i + 1):
                return True
            del asignacion[quien]
            usados.discard(r)
        return False

    # Ordenar por "más restringido primero" acelera mucho el backtracking
    random.shuffle(pendientes)
    pendientes.sort(key=lambda q: sum(1 for r in libres if r != q and (q, r) not in prohibidas))

    if not backtrack(0):
        raise SorteoError("Con esas excepciones no hay ningún sorteo posible. Revisá las reglas.")
    return dict(asignacion)
