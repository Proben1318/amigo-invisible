"""Amigo Invisible - App Kivy (compilable a APK con Buildozer)."""
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.metrics import dp

from sorteo import sortear, SorteoError

ROJO = (0.80, 0.15, 0.20, 1)
VERDE = (0.10, 0.55, 0.30, 1)
GRIS = (0.45, 0.45, 0.45, 1)


def aviso(titulo, texto):
    contenido = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))
    lbl = Label(text=texto, halign="center", valign="middle", font_size="18sp")
    lbl.bind(size=lambda w, s: setattr(w, "text_size", s))
    contenido.add_widget(lbl)
    btn = Button(text="OK", size_hint_y=None, height=dp(50))
    contenido.add_widget(btn)
    p = Popup(title=titulo, content=contenido, size_hint=(0.85, 0.5))
    btn.bind(on_release=p.dismiss)
    p.open()


def lista_scroll():
    grid = GridLayout(cols=1, spacing=dp(6), size_hint_y=None)
    grid.bind(minimum_height=grid.setter("height"))
    sv = ScrollView()
    sv.add_widget(grid)
    return sv, grid


def fila(texto, al_borrar):
    f = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(6))
    f.add_widget(Label(text=texto, font_size="18sp"))
    b = Button(text="X", size_hint_x=None, width=dp(48), background_color=ROJO)
    b.bind(on_release=lambda *_: al_borrar())
    f.add_widget(b)
    return f


# ---------------------------------------------------------------- Pantalla 1
class PantallaNombres(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        raiz = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))
        raiz.add_widget(Label(text="🎁 Amigo Invisible", font_size="28sp",
                              size_hint_y=None, height=dp(60)))

        entrada = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(6))
        self.txt = TextInput(hint_text="Nombre", multiline=False, font_size="18sp")
        self.txt.bind(on_text_validate=self.agregar)
        entrada.add_widget(self.txt)
        b = Button(text="Agregar", size_hint_x=None, width=dp(110), background_color=VERDE)
        b.bind(on_release=self.agregar)
        entrada.add_widget(b)
        raiz.add_widget(entrada)

        sv, self.grid = lista_scroll()
        raiz.add_widget(sv)

        sig = Button(text="Siguiente: excepciones →", size_hint_y=None, height=dp(56),
                     font_size="18sp")
        sig.bind(on_release=self.siguiente)
        raiz.add_widget(sig)
        self.add_widget(raiz)

    @property
    def app(self):
        return App.get_running_app()

    def agregar(self, *_):
        nombre = self.txt.text.strip()
        self.txt.text = ""
        if not nombre:
            return
        if nombre in self.app.nombres:
            aviso("Ojo", f"'{nombre}' ya está en la lista.")
            return
        self.app.nombres.append(nombre)
        self.refrescar()

    def borrar(self, nombre):
        self.app.nombres.remove(nombre)
        # Quitar excepciones que usen ese nombre
        self.app.fijas = [p for p in self.app.fijas if nombre not in p]
        self.app.prohibidas = [p for p in self.app.prohibidas if nombre not in p]
        self.refrescar()

    def refrescar(self):
        self.grid.clear_widgets()
        for n in self.app.nombres:
            self.grid.add_widget(fila(n, lambda n=n: self.borrar(n)))

    def siguiente(self, *_):
        if len(self.app.nombres) < 2:
            aviso("Faltan personas", "Agregá al menos 2 nombres.")
            return
        self.manager.current = "excepciones"


# ---------------------------------------------------------------- Pantalla 2
class PantallaExcepciones(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        raiz = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))
        raiz.add_widget(Label(text="Excepciones (opcional)", font_size="24sp",
                              size_hint_y=None, height=dp(50)))

        sel = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(6))
        self.sp_a = Spinner(text="Quién regala")
        self.sp_b = Spinner(text="A quién")
        sel.add_widget(self.sp_a)
        sel.add_widget(Label(text="→", size_hint_x=None, width=dp(30), font_size="22sp"))
        sel.add_widget(self.sp_b)
        raiz.add_widget(sel)

        botones = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(6))
        bf = Button(text="✔ Fija (le toca sí o sí)", background_color=VERDE)
        bf.bind(on_release=lambda *_: self.agregar("fija"))
        bp = Button(text="✖ Prohibida", background_color=ROJO)
        bp.bind(on_release=lambda *_: self.agregar("prohibida"))
        botones.add_widget(bf)
        botones.add_widget(bp)
        raiz.add_widget(botones)

        sv, self.grid = lista_scroll()
        raiz.add_widget(sv)

        nav = BoxLayout(size_hint_y=None, height=dp(56), spacing=dp(6))
        atras = Button(text="← Nombres", background_color=GRIS)
        atras.bind(on_release=lambda *_: setattr(self.manager, "current", "nombres"))
        sortear_btn = Button(text="🎲 ¡SORTEAR!", font_size="20sp", background_color=VERDE)
        sortear_btn.bind(on_release=self.sortear)
        nav.add_widget(atras)
        nav.add_widget(sortear_btn)
        raiz.add_widget(nav)
        self.add_widget(raiz)

    @property
    def app(self):
        return App.get_running_app()

    def on_pre_enter(self, *_):
        self.sp_a.values = self.app.nombres
        self.sp_b.values = self.app.nombres
        self.refrescar()

    def agregar(self, tipo):
        a, b = self.sp_a.text, self.sp_b.text
        if a not in self.app.nombres or b not in self.app.nombres:
            aviso("Ojo", "Elegí las dos personas.")
            return
        if a == b:
            aviso("Ojo", "Una persona no puede regalarse a sí misma.")
            return
        if tipo == "fija":
            if any(x == a for x, _ in self.app.fijas):
                aviso("Ojo", f"{a} ya tiene una pareja fija.")
                return
            if any(y == b for _, y in self.app.fijas):
                aviso("Ojo", f"A {b} ya le regala alguien fijo.")
                return
            self.app.fijas.append((a, b))
        else:
            if (a, b) not in self.app.prohibidas:
                self.app.prohibidas.append((a, b))
        self.refrescar()

    def refrescar(self):
        self.grid.clear_widgets()
        for p in self.app.fijas:
            self.grid.add_widget(fila(f"✔ {p[0]} → {p[1]}",
                                      lambda p=p: self.quitar(self.app.fijas, p)))
        for p in self.app.prohibidas:
            self.grid.add_widget(fila(f"✖ {p[0]} ↛ {p[1]}",
                                      lambda p=p: self.quitar(self.app.prohibidas, p)))

    def quitar(self, lista, p):
        lista.remove(p)
        self.refrescar()

    def sortear(self, *_):
        try:
            self.app.resultado = sortear(self.app.nombres, self.app.fijas, self.app.prohibidas)
        except SorteoError as e:
            aviso("No se pudo sortear", str(e))
            return
        self.manager.current = "resultado"


# ---------------------------------------------------------------- Pantalla 3
class PantallaResultado(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        raiz = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))
        raiz.add_widget(Label(
            text="Pasá el celular: cada uno toca SU nombre\npara ver a quién le regala",
            font_size="18sp", halign="center", size_hint_y=None, height=dp(70)))
        sv, self.grid = lista_scroll()
        raiz.add_widget(sv)

        nav = BoxLayout(size_hint_y=None, height=dp(56), spacing=dp(6))
        nuevo = Button(text="Nuevo sorteo", background_color=GRIS)
        nuevo.bind(on_release=self.confirmar_nuevo)
        nav.add_widget(nuevo)
        raiz.add_widget(nav)
        self.add_widget(raiz)

    @property
    def app(self):
        return App.get_running_app()

    def on_pre_enter(self, *_):
        self.grid.clear_widgets()
        for n in self.app.nombres:
            b = Button(text=n, size_hint_y=None, height=dp(56), font_size="20sp")
            b.bind(on_release=lambda btn, n=n: self.revelar(btn, n))
            self.grid.add_widget(b)

    def revelar(self, btn, nombre):
        contenido = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))
        lbl = Label(text=f"¿Sos {nombre}?\n\nTocá para ver (que nadie mire 👀)",
                    halign="center", font_size="20sp")
        contenido.add_widget(lbl)
        ver = Button(text="Ver", size_hint_y=None, height=dp(56), background_color=VERDE)
        contenido.add_widget(ver)
        p = Popup(title=nombre, content=contenido, size_hint=(0.9, 0.6), auto_dismiss=False)

        def mostrar(*_):
            lbl.text = f"Le regalás a:\n\n[b]{self.app.resultado[nombre]}[/b] 🎁"
            lbl.markup = True
            lbl.font_size = "26sp"
            ver.text = "Listo, ocultar"
            ver.unbind(on_release=mostrar)
            ver.bind(on_release=cerrar)

        def cerrar(*_):
            p.dismiss()
            btn.text = f"{nombre} ✔ (ya vio)"
            btn.disabled = True

        ver.bind(on_release=mostrar)
        p.open()

    def confirmar_nuevo(self, *_):
        contenido = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))
        contenido.add_widget(Label(text="¿Volver a empezar?\nSe pierde el sorteo actual.",
                                   halign="center"))
        fila_b = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(6))
        no = Button(text="Cancelar")
        si = Button(text="Sí", background_color=ROJO)
        fila_b.add_widget(no)
        fila_b.add_widget(si)
        contenido.add_widget(fila_b)
        p = Popup(title="Nuevo sorteo", content=contenido, size_hint=(0.85, 0.4))
        no.bind(on_release=p.dismiss)

        def reiniciar(*_):
            p.dismiss()
            self.app.resultado = {}
            self.manager.current = "excepciones"

        si.bind(on_release=reiniciar)
        p.open()


class AmigoInvisibleApp(App):
    title = "Amigo Invisible"

    def build(self):
        self.nombres, self.fijas, self.prohibidas, self.resultado = [], [], [], {}
        sm = ScreenManager()
        sm.add_widget(PantallaNombres(name="nombres"))
        sm.add_widget(PantallaExcepciones(name="excepciones"))
        sm.add_widget(PantallaResultado(name="resultado"))
        return sm


if __name__ == "__main__":
    AmigoInvisibleApp().run()
