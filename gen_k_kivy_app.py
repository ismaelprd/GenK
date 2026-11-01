# -*- coding: utf-8 -*-
"""
Gen K - Aprende Cultura General (Clon en Kivy + IA Gemini)
==========================================================
Aplicación móvil multiplataforma escrita en Python puro usando Kivy.
Replica la interfaz visual de Gen K e integra gemini-3.5-flash-lite
para generar lecciones y preguntas infinitas de cultura general.

Requisitos:
    pip install kivy

Ejecución:
    python gen_k_app.py
"""

import json
import math
import os
import random
import threading
import urllib.error
import urllib.request

from kivy.config import Config
Config.set('graphics', 'width', '410')
Config.set('graphics', 'height', '860')
Config.set('graphics', 'resizable', '1')

from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import (
    Color, Ellipse, Line, Rectangle, RoundedRectangle, Triangle
)
from kivy.metrics import dp, sp
from kivy.properties import (
    BooleanProperty, NumericProperty, StringProperty
)
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

# =====================================================================
# CONFIGURACIÓN DE GEMINI API (gemini-3.5-flash-lite)
# =====================================================================
GEMINI_API_KEY = os.environ.get(
    "GEMINI_API_KEY",
    "AQ.Ab8RN6InRAl4jEaB4rfT6mQ3FocLpqM47mYuqXchjTFMRoQO4A"
)
GEMINI_MODEL = "gemini-3.5-flash-lite"


def generate_lesson_with_gemini(category, title, callback):
    """
    Consulta el modelo gemini-3.5-flash-lite en un hilo secundario
    para generar una nueva píldora cultural y 3 preguntas de tipo test.
    """
    def _worker():
        prompt = (
            f"Eres el creador de contenido de la app 'Gen K aprende cultura general'. "
            f"Genera una lección breve e interesante sobre la categoría '{category}' "
            f"(tema sugerido: '{title}') y 3 preguntas de opción múltiple (4 opciones cada una). "
            f"Responde ÚNICAMENTE con un objeto JSON válido con esta estructura exacta: "
            f'{{"title": "Título atractivo", "summary": "Explicación amena de 60 a 90 palabras...", '
            f'"quiz": [{{"q": "¿Pregunta?", "options": ["Opción A", "Opción B", "Opción C", "Opción D"], "answer": 0}}]}}'
        )
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
        )
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "responseMimeType": "application/json"
            }
        }
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=12) as resp:
                raw = json.loads(resp.read().decode("utf-8"))
                text = raw["candidates"][0]["content"]["parts"][0]["text"]
                data = json.loads(text)
                Clock.schedule_once(lambda dt: callback(data, None), 0)
        except Exception as exc:
            Clock.schedule_once(lambda dt, e=str(exc): callback(None, e), 0)

    threading.Thread(target=_worker, daemon=True).start()


# =====================================================================
# PALETA DE COLORES (Extraída del diseño original)
# =====================================================================
COLOR_BG_PURPLE = (0.478, 0.318, 0.827, 1)       # #7A51D3 Fondo principal
COLOR_GRID_LINE = (0.396, 0.243, 0.722, 1)       # #653EB8 Líneas de cuadrícula
COLOR_PATH_YELLOW = (0.949, 0.788, 0.298, 1)     # #F2C94C Camino sinuoso amarillo
COLOR_PREMIUM_GOLD = (0.949, 0.792, 0.275, 1)    # #F2CA46 Botón Premium
COLOR_HUD_BG = (0.557, 0.408, 0.871, 0.88)       # Cápsulas superiores e inferiores
COLOR_HUD_BORDER = (0.725, 0.608, 0.945, 1)      # Borde claro de cápsulas
COLOR_TAB_ACTIVE = (0.710, 0.569, 0.949, 1)      # Píldora activa en barra inferior

NODE_ORANGE = (0.922, 0.596, 0.204, 1)           # Nivel 2 (Microscopio / Ciencia)
NODE_BLUE = (0.361, 0.576, 0.910, 1)             # Nivel 3 y 5 (Mapa / Engranaje)
NODE_PINK = (0.918, 0.451, 0.580, 1)             # Nivel 4 (Evolución / Biología)
NODE_GREEN = (0.345, 0.780, 0.490, 1)            # Nivel 1
NODE_PURPLE = (0.659, 0.420, 0.929, 1)           # Nivel 6


# =====================================================================
# BASE DE DATOS INICIAL DE LECCIONES
# =====================================================================
LEVELS_DATA = [
    {
        "level": 1,
        "title": "Orígenes de la Civilización",
        "category": "Historia",
        "icon_type": "scroll",
        "color": NODE_GREEN,
        "x_rel": 0.52,
        "sub_nodes": [{"num": 1, "color": (0.85, 0.93, 0.98, 1), "side": "right"}],
        "summary": (
            "Hace unos 5.500 años, en la región de Mesopotamia ('tierra entre ríos', "
            "entre el Tigris y el Éufrates), surgieron las primeras ciudades-estado como Uruk y Ur. "
            "Allí se inventó la escritura cuneiforme sobre tablillas de arcilla, inicialmente "
            "para llevar la contabilidad de las cosechas y los impuestos, además del primer "
            "código de leyes escrito conocido: el Código de Hammurabi."
        ),
        "quiz": [
            {
                "q": "¿Qué significa literalmente la palabra 'Mesopotamia'?",
                "options": ["Tierra entre ríos", "Valle de los reyes", "Cuna del sol", "Montaña sagrada"],
                "answer": 0
            },
            {
                "q": "¿Cuál fue el primer sistema de escritura desarrollado en Sumeria?",
                "options": ["Jeroglífico", "Cuneiforme", "Alfabético fenicio", "Lineal B"],
                "answer": 1
            },
            {
                "q": "¿Con qué propósito principal nació la escritura en Mesopotamia?",
                "options": ["Escribir poemas épicos", "Contabilidad de cosechas y comercio", "Cartas diplomáticas", "Textos astronómicos"],
                "answer": 1
            }
        ]
    },
    {
        "level": 2,
        "title": "El Mundo Microscópico",
        "category": "Ciencia",
        "icon_type": "microscope",
        "color": NODE_ORANGE,
        "x_rel": 0.74,
        "sub_nodes": [{"num": 1, "color": (0.98, 0.91, 0.76, 1), "side": "left"}],
        "summary": (
            "En 1665, Robert Hooke observó con un microscopio rudimentario una lámina de corcho "
            "y vio pequeñas cavidades a las que llamó 'células' (celdillas). Pocos años después, "
            "Anton van Leeuwenhoek perfeccionó las lentes y fue el primer ser humano en observar "
            "bacterias, protozoos y glóbulos rojos en una gota de agua, inaugurando la microbiología."
        ),
        "quiz": [
            {
                "q": "¿Quién acuñó el término 'célula' al observar una lámina de corcho en 1665?",
                "options": ["Louis Pasteur", "Robert Hooke", "Alexander Fleming", "Gregor Mendel"],
                "answer": 1
            },
            {
                "q": "¿Qué científico observó por primera vez bacterias y microbios vivos?",
                "options": ["Anton van Leeuwenhoek", "Galileo Galilei", "Isaac Newton", "Charles Darwin"],
                "answer": 0
            },
            {
                "q": "¿Qué orgánulo celular es conocido como la 'central energética' de la célula?",
                "options": ["Ribosoma", "Lisosoma", "Mitocondria", "Aparato de Golgi"],
                "answer": 2
            }
        ]
    },
    {
        "level": 3,
        "title": "Cartografía y Continentes",
        "category": "Geografía",
        "icon_type": "map",
        "color": NODE_BLUE,
        "x_rel": 0.49,
        "sub_nodes": [{"num": 1, "color": (0.85, 0.92, 0.98, 1), "side": "right"}],
        "summary": (
            "Representar una esfera tridimensional (la Tierra) en un plano bidimensional "
            "siempre genera distorsiones. En 1569, Gerardus Mercator creó su famosa proyección "
            "cilíndrica, ideal para la navegación marítima porque respeta los ángulos, pero que "
            "agranda enormemente las tierras cercanas a los polos: Groenlandia parece del tamaño "
            "de África, cuando en realidad África es 14 veces mayor."
        ),
        "quiz": [
            {
                "q": "¿Cuántas veces es África más grande que Groenlandia en la realidad?",
                "options": ["Son casi iguales", "Unas 3 veces", "Unas 14 veces", "Unas 30 veces"],
                "answer": 2
            },
            {
                "q": "¿Por qué se popularizó tanto la proyección de Mercator en el siglo XVI?",
                "options": ["Era perfecta para la navegación marítima", "No distorsionaba el tamaño de los países", "Fue la primera en incluir la Antártida", "Era más fácil de colorear"],
                "answer": 0
            },
            {
                "q": "¿Cómo se llamó el supercontinente que agrupaba casi toda la tierra firme hace 300 millones de años?",
                "options": ["Gondwana", "Pangea", "Laurasia", "Rodinia"],
                "answer": 1
            }
        ]
    },
    {
        "level": 4,
        "title": "La Evolución Humana",
        "category": "Biología",
        "icon_type": "monkey",
        "color": NODE_PINK,
        "x_rel": 0.25,
        "sub_nodes": [{"num": 1, "color": (0.98, 0.85, 0.89, 1), "side": "right"}],
        "summary": (
            "Al contrario del mito popular, el ser humano no desciende de los monos actuales, "
            "sino que compartimos un ancestro común con los chimpancés y bonobos que vivió en "
            "África hace entre 6 y 7 millones de años. El paso decisivo de los primeros homínidos "
            "(como Australopithecus afarensis, la famosa 'Lucy') fue el bipedismo: caminar erguidos "
            "liberó las manos para fabricar herramientas antes incluso de que creciera el cerebro."
        ),
        "quiz": [
            {
                "q": "¿Cuál fue el primer gran cambio anatómico que distinguió a los primeros homínidos?",
                "options": ["El lenguaje articulado", "El bipedismo (caminar en dos pies)", "El uso del fuego", "El gran tamaño cerebral"],
                "answer": 1
            },
            {
                "q": "¿A qué especie pertenecía el famoso fósil 'Lucy' descubierto en Etiopía?",
                "options": ["Homo habilis", "Homo neanderthalensis", "Australopithecus afarensis", "Homo erectus"],
                "answer": 2
            },
            {
                "q": "¿Qué porcentaje aproximado de ADN compartimos los humanos con los chimpancés?",
                "options": ["75%", "85%", "98.8%", "60%"],
                "answer": 2
            }
        ]
    },
    {
        "level": 5,
        "title": "Revoluciones Industriales",
        "category": "Tecnología",
        "icon_type": "gear",
        "color": NODE_BLUE,
        "x_rel": 0.49,
        "sub_nodes": [
            {"num": 5, "color": (0.98, 0.78, 0.84, 1), "side": "right"},
            {"num": 1, "color": (0.85, 0.92, 0.98, 1), "side": "right_far"}
        ],
        "summary": (
            "En la segunda mitad del siglo XVIII, Gran Bretaña lideró la Primera Revolución "
            "Industrial gracias al perfeccionamiento de la máquina de vapor por James Watt. "
            "Por primera vez en la historia, la humanidad dejó de depender exclusivamente "
            "de la fuerza muscular (humana o animal), del viento o del agua para producir "
            "bienes y mover trenes y barcos."
        ),
        "quiz": [
            {
                "q": "¿Quién perfeccionó la máquina de vapor impulsando la Primera Revolución Industrial?",
                "options": ["Thomas Edison", "James Watt", "Nikola Tesla", "Henry Ford"],
                "answer": 1
            },
            {
                "q": "¿En qué país comenzó la Primera Revolución Industrial en el siglo XVIII?",
                "options": ["Alemania", "Estados Unidos", "Gran Bretaña", "Francia"],
                "answer": 2
            },
            {
                "q": "¿Qué fuente de energía alimentaba principalmente a las primeras máquinas de vapor?",
                "options": ["Petróleo", "Carbón mineral", "Gas natural", "Electricidad"],
                "answer": 1
            }
        ]
    },
    {
        "level": 6,
        "title": "El Renacimiento y el Arte",
        "category": "Arte",
        "icon_type": "palette",
        "color": NODE_PURPLE,
        "x_rel": 0.72,
        "sub_nodes": [{"num": 1, "color": (0.91, 0.85, 0.98, 1), "side": "left"}],
        "summary": (
            "Durante los siglos XV y XVI, ciudades italianas como Florencia, Roma y Venecia "
            "vivieron el Renacimiento. Artistas como Filippo Brunelleschi y Masaccio introdujeron "
            "la perspectiva lineal matemática en la pintura, logrando que un lienzo plano "
            "pareciera tener profundidad tridimensional real, técnica que llevaron a la cumbre "
            "Leonardo da Vinci, Miguel Ángel y Rafael."
        ),
        "quiz": [
            {
                "q": "¿Qué ciudad italiana es considerada la cuna del Renacimiento en el siglo XV?",
                "options": ["Milán", "Florencia", "Nápoles", "Bolonia"],
                "answer": 1
            },
            {
                "q": "¿Qué innovación técnica permitió dar sensación de profundidad 3D en los cuadros renacentistas?",
                "options": ["El puntillismo", "La perspectiva lineal", "El collage", "El arte abstracto"],
                "answer": 1
            },
            {
                "q": "¿Quién pintó la bóveda de la Capilla Sixtina en el Vaticano?",
                "options": ["Leonardo da Vinci", "Miguel Ángel Buonarroti", "Sandro Botticelli", "Tiziano"],
                "answer": 1
            }
        ]
    },
    {
        "level": 7,
        "title": "Filosofía Clásica Griega",
        "category": "Filosofía",
        "icon_type": "scroll",
        "color": NODE_ORANGE,
        "x_rel": 0.32,
        "sub_nodes": [{"num": 1, "color": (0.98, 0.91, 0.76, 1), "side": "right"}],
        "summary": (
            "En la Atenas del siglo V a.C., Sócrates revolucionó el pensamiento con la 'mayéutica': "
            "en lugar de dar respuestas cerradas, hacía preguntas para que su interlocutor "
            "descubriera la verdad por sí mismo. No dejó nada escrito; conocemos sus ideas gracias "
            "a su discípulo Platón, quien a su vez fue maestro de Aristóteles."
        ),
        "quiz": [
            {
                "q": "¿Cómo se llamaba el método socrático basado en hacer preguntas para alumbrar el conocimiento?",
                "options": ["Escolástica", "Mayéutica", "Sofística", "Empirismo"],
                "answer": 1
            },
            {
                "q": "¿Cuál es el orden cronológico correcto de maestro a discípulo en la Grecia clásica?",
                "options": ["Platón -> Sócrates -> Aristóteles", "Sócrates -> Platón -> Aristóteles", "Aristóteles -> Sócrates -> Platón", "Sócrates -> Aristóteles -> Platón"],
                "answer": 1
            },
            {
                "q": "¿Cómo se llamó la escuela filosófica fundada por Platón en Atenas?",
                "options": ["El Liceo", "La Academia", "El Jardín", "La Stoa"],
                "answer": 1
            }
        ]
    }
]


# =====================================================================
# COMPONENTES DE DIBUJO VECTORIAL (Fondo, Camino, Stickers, Iconos)
# =====================================================================
class GridBackgroundWidget(FloatLayout):
    """Dibuja el fondo morado con cuadrícula estilo Gen K."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._update_canvas, size=self._update_canvas)

    def _update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*COLOR_BG_PURPLE)
            Rectangle(pos=self.pos, size=self.size)

            Color(*COLOR_GRID_LINE)
            step = dp(44)
            x0, y0 = self.pos
            w, h = self.size

            x = x0 + (step / 2.0)
            while x < x0 + w:
                Line(points=[x, y0, x, y0 + h], width=dp(1.1))
                x += step

            y = y0 + (step / 2.0)
            while y < y0 + h:
                Line(points=[x0, y, x0 + w, y], width=dp(1.1))
                y += step


class PumpkinSticker(Widget):
    """Dibuja la calabaza decorativa de la esquina inferior izquierda."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(115), dp(105))
        self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *args):
        self.canvas.clear()
        x, y = self.pos
        w, h = self.size
        with self.canvas:
            Color(0.08, 0.04, 0.05, 1)
            Ellipse(pos=(x + dp(4), y - dp(4)), size=(w * 0.45, h * 0.78))
            Ellipse(pos=(x + w * 0.55 + dp(4), y - dp(4)), size=(w * 0.45, h * 0.78))
            Ellipse(pos=(x + w * 0.18 + dp(4), y - dp(5)), size=(w * 0.64, h * 0.82))

            Color(0.08, 0.04, 0.05, 1)
            RoundedRectangle(pos=(x + w * 0.42, y + h * 0.72), size=(w * 0.16, h * 0.25), radius=[dp(5)])
            Color(0.55, 0.32, 0.18, 1)
            RoundedRectangle(pos=(x + w * 0.44, y + h * 0.74), size=(w * 0.12, h * 0.21), radius=[dp(4)])

            Color(0.89, 0.49, 0.20, 1)
            Ellipse(pos=(x, y), size=(w * 0.46, h * 0.78))
            Ellipse(pos=(x + w * 0.54, y), size=(w * 0.46, h * 0.78))

            Color(0.95, 0.56, 0.24, 1)
            Ellipse(pos=(x + w * 0.18, y - dp(1)), size=(w * 0.64, h * 0.82))

            Color(0.99, 0.85, 0.52, 1)
            Triangle(points=[
                x + w * 0.26, y + h * 0.42,
                x + w * 0.42, y + h * 0.42,
                x + w * 0.34, y + h * 0.58
            ])
            Triangle(points=[
                x + w * 0.58, y + h * 0.42,
                x + w * 0.74, y + h * 0.42,
                x + w * 0.66, y + h * 0.58
            ])
            Triangle(points=[
                x + w * 0.46, y + h * 0.33,
                x + w * 0.54, y + h * 0.33,
                x + w * 0.50, y + h * 0.41
            ])
            Line(
                points=[
                    x + w * 0.26, y + h * 0.26,
                    x + w * 0.38, y + h * 0.17,
                    x + w * 0.50, y + h * 0.20,
                    x + w * 0.62, y + h * 0.17,
                    x + w * 0.74, y + h * 0.26
                ],
                width=dp(4.5),
                cap='round',
                joint='round'
            )


class GhostSticker(Widget):
    """Dibuja el fantasma decorativo en la parte media-derecha."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(105), dp(110))
        self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *args):
        self.canvas.clear()
        x, y = self.pos
        w, h = self.size
        with self.canvas:
            Color(0.05, 0.02, 0.08, 1)
            Ellipse(pos=(x + w * 0.24 + dp(5), y + h * 0.42 - dp(4)), size=(w * 0.52, h * 0.52))
            RoundedRectangle(
                pos=(x + w * 0.22 + dp(5), y + h * 0.12 - dp(4)),
                size=(w * 0.54, h * 0.58),
                radius=[dp(18)]
            )
            Ellipse(pos=(x + w * 0.04 + dp(4), y + h * 0.34 - dp(4)), size=(w * 0.30, h * 0.22))
            Ellipse(pos=(x + w * 0.64 + dp(5), y + h * 0.38 - dp(4)), size=(w * 0.30, h * 0.24))

            Color(0.97, 0.96, 0.92, 1)
            Ellipse(pos=(x + w * 0.24, y + h * 0.42), size=(w * 0.52, h * 0.52))
            RoundedRectangle(
                pos=(x + w * 0.22, y + h * 0.12),
                size=(w * 0.54, h * 0.58),
                radius=[dp(18)]
            )
            Ellipse(pos=(x + w * 0.04, y + h * 0.34), size=(w * 0.30, h * 0.22))
            Ellipse(pos=(x + w * 0.64, y + h * 0.38), size=(w * 0.30, h * 0.24))

            Color(0.1, 0.1, 0.12, 1)
            Ellipse(pos=(x + w * 0.38, y + h * 0.64), size=(dp(7), dp(11)))
            Ellipse(pos=(x + w * 0.55, y + h * 0.66), size=(dp(7), dp(11)))
            Ellipse(pos=(x + w * 0.46, y + h * 0.48), size=(dp(9), dp(13)))


# =====================================================================
# NODOS DE NIVEL INTERACTIVOS
# =====================================================================
class SubNodeBadge(ButtonBehavior, Widget):
    """Pequeños círculos laterales conectados al nodo principal."""
    def __init__(self, num=1, badge_color=(0.95, 0.88, 0.92, 1), callback=None, **kwargs):
        super().__init__(**kwargs)
        self.num = num
        self.badge_color = badge_color
        self.callback = callback
        self.size_hint = (None, None)
        self.size = (dp(42), dp(42))

        self.lbl = Label(
            text=f"[b]{self.num}[/b]",
            markup=True,
            font_size=sp(15),
            color=(0.12, 0.12, 0.15, 1),
            size_hint=(None, None),
            size=self.size
        )
        self.add_widget(self.lbl)
        self.bind(pos=self._draw, size=self._draw)

    def on_release(self):
        if self.callback:
            self.callback()

    def _draw(self, *args):
        self.lbl.pos = (self.x, self.y + dp(2))
        self.lbl.size = self.size
        self.canvas.before.clear()
        x, y = self.pos
        w, h = self.size
        with self.canvas.before:
            Color(0.08, 0.08, 0.1, 1)
            Ellipse(pos=(x - dp(1.5), y - dp(2)), size=(w + dp(3), h + dp(3)))
            Color(0.98, 0.98, 0.99, 1)
            Ellipse(pos=(x, y), size=(w, h))
            Color(*self.badge_color)
            Ellipse(pos=(x + dp(4), y + dp(4)), size=(w - dp(8), h - dp(8)))
            Color(0.15, 0.15, 0.18, 1)
            Line(circle=(x + w / 2.0, y + h / 2.0, (w - dp(8)) / 2.0), width=dp(1.1))
            Color(0.98, 0.98, 0.98, 1)
            RoundedRectangle(pos=(x + w * 0.22, y + dp(3)), size=(w * 0.56, dp(7)), radius=[dp(2)])
            Color(0.12, 0.12, 0.15, 1)
            Line(rounded_rectangle=(x + w * 0.22, y + dp(3), w * 0.56, dp(7), dp(2)), width=dp(1))


class LevelNodeWidget(ButtonBehavior, FloatLayout):
    """Nodo circular de nivel del mapa principal."""
    completed = BooleanProperty(False)

    def __init__(self, level_data, on_select_callback, **kwargs):
        super().__init__(**kwargs)
        self.level_data = level_data
        self.on_select_callback = on_select_callback
        self.size_hint = (None, None)
        self.size = (dp(88), dp(88))

        self.num_shadow = Label(
            text=f"[b]{level_data['level']}[/b]",
            markup=True,
            font_size=sp(21),
            color=(0.05, 0.05, 0.08, 1),
            size_hint=(None, None),
            size=(dp(40), dp(30))
        )
        self.num_label = Label(
            text=f"[b]{level_data['level']}[/b]",
            markup=True,
            font_size=sp(19),
            color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(dp(40), dp(30))
        )
        self.add_widget(self.num_shadow)
        self.add_widget(self.num_label)

        self.bind(pos=self._draw, size=self._draw, completed=self._draw)

    def on_release(self):
        if self.on_select_callback:
            self.on_select_callback(self.level_data)

    def _draw(self, *args):
        x, y = self.pos
        w, h = self.size

        self.num_shadow.center_x = x + w / 2.0 + dp(1)
        self.num_shadow.y = y - dp(3)
        self.num_label.center_x = x + w / 2.0
        self.num_label.y = y - dp(2)

        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.04, 0.02, 0.08, 1)
            Ellipse(pos=(x - dp(1), y - dp(5)), size=(w + dp(2), h + dp(2)))

            Color(*self.level_data["color"])
            Ellipse(pos=(x, y), size=(w, h))

            Color(0.08, 0.05, 0.12, 1)
            Line(circle=(x + w / 2.0, y + h / 2.0, w / 2.0), width=dp(1.6))

            if self.completed:
                Color(0.95, 0.80, 0.25, 1)
                Ellipse(pos=(x + w - dp(22), y + h - dp(22)), size=(dp(20), dp(20)))
                Color(0.1, 0.1, 0.1, 1)
                Line(circle=(x + w - dp(12), y + h - dp(12), dp(10)), width=dp(1.2))

            self._draw_center_icon(x, y, w, h, self.level_data["icon_type"])

    def _draw_center_icon(self, x, y, w, h, icon_type):
        cx = x + w / 2.0
        cy = y + h / 2.0 + dp(5)

        if icon_type == "gear":
            Color(0.75, 0.80, 0.86, 1)
            for angle_deg in range(0, 360, 45):
                rad = math.radians(angle_deg)
                tx = cx + math.cos(rad) * dp(15) - dp(4)
                ty = cy + math.sin(rad) * dp(15) - dp(4)
                Ellipse(pos=(tx, ty), size=(dp(8), dp(8)))
            Color(0.84, 0.88, 0.93, 1)
            Ellipse(pos=(cx - dp(14), cy - dp(14)), size=(dp(28), dp(28)))
            Color(0.45, 0.52, 0.60, 1)
            Ellipse(pos=(cx - dp(7), cy - dp(7)), size=(dp(14), dp(14)))
            Color(0.92, 0.95, 0.98, 1)
            Ellipse(pos=(cx - dp(3.5), cy - dp(3.5)), size=(dp(7), dp(7)))

        elif icon_type == "monkey":
            Color(0.62, 0.42, 0.26, 1)
            Ellipse(pos=(cx - dp(16), cy + dp(1)), size=(dp(9), dp(9)))
            Ellipse(pos=(cx + dp(7), cy + dp(1)), size=(dp(9), dp(9)))
            Color(0.73, 0.51, 0.33, 1)
            Ellipse(pos=(cx - dp(9), cy - dp(14)), size=(dp(18), dp(18)))
            Ellipse(pos=(cx - dp(11), cy - dp(1)), size=(dp(22), dp(20)))
            Color(0.93, 0.80, 0.66, 1)
            Ellipse(pos=(cx - dp(8), cy + dp(1)), size=(dp(16), dp(13)))
            Color(0.12, 0.10, 0.10, 1)
            Ellipse(pos=(cx - dp(5), cy + dp(7)), size=(dp(3), dp(3)))
            Ellipse(pos=(cx + dp(2), cy + dp(7)), size=(dp(3), dp(3)))
            Color(0.62, 0.42, 0.26, 1)
            Line(points=[cx + dp(7), cy - dp(11), cx + dp(16), cy - dp(7), cx + dp(14), cy + dp(2)], width=dp(2))

        elif icon_type == "map":
            Color(0.82, 0.93, 0.99, 1)
            RoundedRectangle(pos=(cx - dp(17), cy - dp(13)), size=(dp(34), dp(26)), radius=[dp(3)])
            Color(0.68, 0.85, 0.96, 1)
            Rectangle(pos=(cx - dp(6), cy - dp(13)), size=(dp(12), dp(26)))
            Color(0.42, 0.72, 0.40, 1)
            Ellipse(pos=(cx - dp(14), cy - dp(4)), size=(dp(11), dp(12)))
            Ellipse(pos=(cx + dp(2), cy - dp(6)), size=(dp(12), dp(14)))
            Color(0.75, 0.62, 0.38, 1)
            Ellipse(pos=(cx - dp(11), cy - dp(1)), size=(dp(6), dp(6)))
            Ellipse(pos=(cx + dp(5), cy - dp(1)), size=(dp(6), dp(7)))

        elif icon_type == "microscope":
            Color(0.28, 0.32, 0.38, 1)
            RoundedRectangle(pos=(cx - dp(12), cy - dp(14)), size=(dp(24), dp(5)), radius=[dp(2)])
            Line(points=[cx + dp(6), cy - dp(11), cx + dp(10), cy, cx + dp(2), cy + dp(10)], width=dp(3.2))
            Color(0.88, 0.91, 0.95, 1)
            Line(points=[cx - dp(4), cy + dp(2), cx + dp(5), cy + dp(15)], width=dp(4.5), cap='square')
            Color(0.20, 0.22, 0.25, 1)
            Line(points=[cx - dp(9), cy - dp(3), cx + dp(5), cy - dp(3)], width=dp(2.2))

        elif icon_type == "palette":
            Color(0.95, 0.83, 0.62, 1)
            Ellipse(pos=(cx - dp(16), cy - dp(12)), size=(dp(32), dp(25)))
            Color(0.90, 0.25, 0.30, 1)
            Ellipse(pos=(cx - dp(11), cy + dp(1)), size=(dp(6), dp(6)))
            Color(0.25, 0.55, 0.95, 1)
            Ellipse(pos=(cx - dp(2), cy + dp(4)), size=(dp(6), dp(6)))
            Color(0.30, 0.80, 0.45, 1)
            Ellipse(pos=(cx + dp(6), cy - dp(1)), size=(dp(6), dp(6)))

        else:
            Color(0.96, 0.90, 0.74, 1)
            RoundedRectangle(pos=(cx - dp(14), cy - dp(12)), size=(dp(28), dp(24)), radius=[dp(4)])
            Color(0.65, 0.48, 0.28, 1)
            Line(points=[cx - dp(9), cy + dp(5), cx + dp(9), cy + dp(5)], width=dp(1.5))
            Line(points=[cx - dp(9), cy, cx + dp(9), cy], width=dp(1.5))
            Line(points=[cx - dp(9), cy - dp(5), cx + dp(5), cy - dp(5)], width=dp(1.5))


# =====================================================================
# LIENZO DEL CAMINO DE NIVELES (Scrollable Map)
# =====================================================================
class MapCanvasWidget(FloatLayout):
    """Contiene el camino amarillo sinuoso, nodos, sub-nodos y stickers."""
    def __init__(self, app_ref, **kwargs):
        super().__init__(**kwargs)
        self.app_ref = app_ref
        self.size_hint = (1, None)
        self.height = dp(1220)
        self.node_widgets = {}
        self.sub_entries = []

        self.pumpkin = PumpkinSticker()
        self.add_widget(self.pumpkin)

        self.ghost = GhostSticker()
        self.add_widget(self.ghost)

        for lvl in LEVELS_DATA:
            node = LevelNodeWidget(
                level_data=lvl,
                on_select_callback=self.app_ref.open_lesson_modal
            )
            self.node_widgets[lvl["level"]] = node
            self.add_widget(node)

            for sub in lvl.get("sub_nodes", []):
                badge = SubNodeBadge(
                    num=sub["num"],
                    badge_color=sub["color"],
                    callback=lambda l=lvl: self.app_ref.open_lesson_modal(l)
                )
                self.add_widget(badge)
                self.sub_entries.append((node, badge, sub["side"]))

        self.bind(pos=self._layout_map, size=self._layout_map)

    def refresh_completion_states(self, completed_levels):
        for lvl_num, widget in self.node_widgets.items():
            widget.completed = (lvl_num in completed_levels)

    def _catmull_rom_spline(self, pts, samples_per_segment=20):
        if len(pts) < 2:
            return []
        extended = [pts[0]] + pts + [pts[-1]]
        curve_points = []
        for i in range(len(extended) - 3):
            p0, p1, p2, p3 = extended[i], extended[i + 1], extended[i + 2], extended[i + 3]
            for step in range(samples_per_segment):
                t = step / float(samples_per_segment)
                t2 = t * t
                t3 = t2 * t
                x = 0.5 * (
                    (2 * p1[0]) +
                    (-p0[0] + p2[0]) * t +
                    (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 +
                    (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3
                )
                y = 0.5 * (
                    (2 * p1[1]) +
                    (-p0[1] + p2[1]) * t +
                    (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 +
                    (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3
                )
                curve_points.extend([x, y])
        curve_points.extend([pts[-1][0], pts[-1][1]])
        return curve_points

    def _layout_map(self, *args):
        w = self.width
        base_y = self.y

        level_y_offsets = {
            1: dp(65),
            2: dp(215),
            3: dp(395),
            4: dp(595),
            5: dp(800),
            6: dp(975),
            7: dp(1120)
        }

        for lvl in LEVELS_DATA:
            num = lvl["level"]
            node = self.node_widgets[num]
            node.center_x = self.x + w * lvl["x_rel"]
            node.center_y = base_y + level_y_offsets[num]

        for node, badge, side in self.sub_entries:
            badge.center_y = node.center_y + dp(2)
            if side == "left":
                badge.center_x = node.center_x - dp(86)
            elif side == "right":
                badge.center_x = node.center_x + dp(84)
            elif side == "right_far":
                badge.center_x = node.center_x + dp(122)

        self.pumpkin.pos = (self.x + w * 0.11, base_y + dp(155))
        self.ghost.pos = (self.x + w * 0.69, base_y + dp(495))

        n1 = self.node_widgets[1].center
        n2 = self.node_widgets[2].center
        n3 = self.node_widgets[3].center
        n4 = self.node_widgets[4].center
        n5 = self.node_widgets[5].center
        n6 = self.node_widgets[6].center
        n7 = self.node_widgets[7].center

        waypoints = [
            (n1[0], base_y + dp(20)),
            n1,
            (self.x + w * 0.25, base_y + dp(195)),
            n2,
            (self.x + w * 0.90, base_y + dp(310)),
            n3,
            (self.x + w * 0.08, base_y + dp(470)),
            n4,
            (self.x + w * 0.37, base_y + dp(660)),
            (self.x + w * 0.60, base_y + dp(525)),
            (self.x + w * 0.77, base_y + dp(680)),
            n5,
            (self.x + w * 0.90, base_y + dp(890)),
            n6,
            (self.x + w * 0.45, base_y + dp(1050)),
            n7
        ]

        smooth_pts = self._catmull_rom_spline(waypoints, samples_per_segment=18)

        self.canvas.before.clear()
        with self.canvas.before:
            if smooth_pts:
                Color(0.35, 0.22, 0.62, 0.85)
                Line(points=smooth_pts, width=dp(6.5), cap='round', joint='round')
                Color(*COLOR_PATH_YELLOW)
                Line(points=smooth_pts, width=dp(4.8), cap='round', joint='round')

            Color(0.06, 0.04, 0.09, 1)
            for node, badge, _ in self.sub_entries:
                Line(
                    points=[node.center_x, badge.center_y, badge.center_x, badge.center_y],
                    width=dp(1.8)
                )


# =====================================================================
# BARRA SUPERIOR (HUD) Y BARRA INFERIOR DE NAVEGACIÓN
# =====================================================================
class TopHudBar(FloatLayout):
    """Barra superior flotante con Racha, Metas (0/3), Estrellas y botón Premium."""
    streak = NumericProperty(0)
    daily_goals = NumericProperty(0)
    stars = NumericProperty(28)

    def __init__(self, on_premium_click=None, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, None)
        self.height = dp(66)
        self.on_premium_click = on_premium_click

        self.lbl_streak = Label(
            text="0",
            font_size=sp(17),
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(dp(34), dp(36))
        )
        self.lbl_goals = Label(
            text="0/3",
            font_size=sp(16),
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(dp(44), dp(36))
        )
        self.lbl_stars = Label(
            text="28",
            font_size=sp(17),
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(dp(40), dp(36))
        )

        self.btn_premium = Label(
            text="[b]Premium[/b]",
            markup=True,
            font_size=sp(16),
            color=(0.12, 0.10, 0.08, 1),
            size_hint=(None, None),
            size=(dp(105), dp(42))
        )

        self.add_widget(self.lbl_streak)
        self.add_widget(self.lbl_goals)
        self.add_widget(self.lbl_stars)
        self.add_widget(self.btn_premium)

        self.bind(
            pos=self._draw,
            size=self._draw,
            streak=self._update_labels,
            daily_goals=self._update_labels,
            stars=self._update_labels
        )

    def _update_labels(self, *args):
        self.lbl_streak.text = str(self.streak)
        self.lbl_goals.text = f"{min(self.daily_goals, 3)}/3"
        self.lbl_stars.text = str(self.stars)

    def on_touch_down(self, touch):
        if self.btn_premium.collide_point(*touch.pos):
            if self.on_premium_click:
                self.on_premium_click()
            return True
        return super().on_touch_down(touch)

    def _draw(self, *args):
        x, y = self.pos
        w, h = self.size
        cy = y + h * 0.45

        cap1_x = x + dp(14)
        cap1_w = dp(152)
        cap_h = dp(42)
        cap_y = cy - cap_h / 2.0

        cap2_x = x + w * 0.49
        cap2_w = dp(72)

        cap3_w = dp(106)
        cap3_x = x + w - cap3_w - dp(14)

        self.lbl_streak.pos = (cap1_x + dp(34), cap_y + dp(3))
        self.lbl_goals.pos = (cap1_x + dp(100), cap_y + dp(3))
        self.lbl_stars.pos = (cap2_x + dp(28), cap_y + dp(3))
        self.btn_premium.pos = (cap3_x, cap_y + dp(3))
        self.btn_premium.size = (cap3_w, cap_h)

        self.canvas.before.clear()
        with self.canvas.before:
            Color(*COLOR_HUD_BG)
            RoundedRectangle(pos=(cap1_x, cap_y), size=(cap1_w, cap_h), radius=[dp(21)])
            Color(*COLOR_HUD_BORDER)
            Line(rounded_rectangle=(cap1_x, cap_y, cap1_w, cap_h, dp(21)), width=dp(1.1))

            fx, fy = cap1_x + dp(16), cap_y + dp(11)
            Color(1, 0.92, 0.85, 1)
            Line(
                points=[
                    fx + dp(6), fy + dp(19),
                    fx + dp(1), fy + dp(10),
                    fx + dp(3), fy + dp(3),
                    fx + dp(8), fy + dp(1),
                    fx + dp(13), fy + dp(5),
                    fx + dp(12), fy + dp(13),
                    fx + dp(6), fy + dp(19)
                ],
                width=dp(1.5),
                joint='round'
            )

            flx, fly = cap1_x + dp(82), cap_y + dp(11)
            Color(1, 1, 1, 1)
            Line(points=[flx, fly, flx, fly + dp(19)], width=dp(1.5))
            Line(
                points=[
                    flx, fly + dp(18),
                    flx + dp(13), fly + dp(18),
                    flx + dp(10), fly + dp(13),
                    flx + dp(13), fly + dp(9),
                    flx, fly + dp(9)
                ],
                width=dp(1.4)
            )

            Color(*COLOR_HUD_BG)
            RoundedRectangle(pos=(cap2_x, cap_y), size=(cap2_w, cap_h), radius=[dp(21)])
            Color(*COLOR_HUD_BORDER)
            Line(rounded_rectangle=(cap2_x, cap_y, cap2_w, cap_h, dp(21)), width=dp(1.1))

            sx, sy = cap2_x + dp(20), cap_y + cap_h / 2.0
            Color(0.98, 0.84, 0.25, 1)
            Ellipse(pos=(sx - dp(9), sy - dp(9)), size=(dp(18), dp(18)))
            Color(1, 1, 1, 1)
            Ellipse(pos=(sx - dp(5), sy - dp(5)), size=(dp(10), dp(10)))

            Color(*COLOR_PREMIUM_GOLD)
            RoundedRectangle(pos=(cap3_x, cap_y), size=(cap3_w, cap_h), radius=[dp(21)])


class BottomNavBar(FloatLayout):
    """Barra de navegación inferior flotante con 4 secciones."""
    active_tab = StringProperty("inicio")

    def __init__(self, on_tab_change, **kwargs):
        super().__init__(**kwargs)
        self.on_tab_change = on_tab_change
        self.size_hint = (1, None)
        self.height = dp(82)

        self.tabs = [
            ("inicio", "Inicio"),
            ("quiz", "Quiz"),
            ("biblioteca", "Biblioteca"),
            ("perfil", "Perfil")
        ]
        self.tab_labels = {}
        for key, title in self.tabs:
            lbl = Label(
                text=f"[b]{title}[/b]" if key == self.active_tab else title,
                markup=True,
                font_size=sp(12),
                color=(1, 1, 1, 1),
                size_hint=(None, None),
                size=(dp(80), dp(22))
            )
            self.tab_labels[key] = lbl
            self.add_widget(lbl)

        self.bind(pos=self._draw, size=self._draw, active_tab=self._draw)

    def on_touch_down(self, touch):
        bar_x = self.x + dp(14)
        bar_y = self.y + dp(12)
        bar_w = self.width - dp(28)
        bar_h = dp(60)

        if bar_x <= touch.x <= bar_x + bar_w and bar_y <= touch.y <= bar_y + bar_h:
            rel_x = touch.x - bar_x
            idx = int(rel_x // (bar_w / 4.0))
            idx = max(0, min(3, idx))
            selected_key = self.tabs[idx][0]
            self.active_tab = selected_key
            if self.on_tab_change:
                self.on_tab_change(selected_key)
            return True
        return super().on_touch_down(touch)

    def _draw(self, *args):
        bar_x = self.x + dp(14)
        bar_y = self.y + dp(12)
        bar_w = self.width - dp(28)
        bar_h = dp(60)
        slot_w = bar_w / 4.0

        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.56, 0.40, 0.88, 0.94)
            RoundedRectangle(pos=(bar_x, bar_y), size=(bar_w, bar_h), radius=[dp(30)])
            Color(*COLOR_HUD_BORDER)
            Line(rounded_rectangle=(bar_x, bar_y, bar_w, bar_h, dp(30)), width=dp(1.2))

            for i, (key, title) in enumerate(self.tabs):
                cx = bar_x + slot_w * (i + 0.5)

                if key == self.active_tab:
                    Color(*COLOR_TAB_ACTIVE)
                    RoundedRectangle(
                        pos=(bar_x + slot_w * i + dp(5), bar_y + dp(4)),
                        size=(slot_w - dp(10), bar_h - dp(8)),
                        radius=[dp(26)]
                    )

                lbl = self.tab_labels[key]
                lbl.text = f"[b]{title}[/b]" if key == self.active_tab else title
                lbl.center_x = cx
                lbl.y = bar_y + dp(5)

                Color(1, 1, 1, 1)
                iy = bar_y + dp(35)
                if key == "inicio":
                    Triangle(points=[cx - dp(11), iy, cx + dp(11), iy, cx, iy + dp(10)])
                    RoundedRectangle(pos=(cx - dp(8), iy - dp(10)), size=(dp(16), dp(11)), radius=[dp(2)])
                    Color(0.56, 0.40, 0.88, 1)
                    Rectangle(pos=(cx - dp(2.5), iy - dp(10)), size=(dp(5), dp(6)))
                elif key == "quiz":
                    Line(rounded_rectangle=(cx - dp(8), iy - dp(10), dp(16), dp(20), dp(3)), width=dp(1.4))
                    Line(points=[cx - dp(3), iy + dp(5), cx + dp(3), iy + dp(5), cx, iy - dp(1)], width=dp(1.3))
                    Ellipse(pos=(cx - dp(1.5), iy - dp(6)), size=(dp(3), dp(3)))
                elif key == "biblioteca":
                    Line(rounded_rectangle=(cx - dp(8), iy - dp(10), dp(16), dp(20), dp(3)), width=dp(1.4))
                    Line(points=[cx - dp(4), iy + dp(2), cx + dp(4), iy + dp(2)], width=dp(1.3))
                    Line(points=[cx - dp(4), iy - dp(3), cx + dp(4), iy - dp(3)], width=dp(1.3))
                elif key == "perfil":
                    Line(circle=(cx, iy + dp(4), dp(5)), width=dp(1.4))
                    Line(ellipse=(cx - dp(9), iy - dp(13), dp(18), dp(12), -70, 70), width=dp(1.5))


# =====================================================================
# MODALES DE MICROAPRENDIZAJE + GENERACIÓN CON IA GEMINI
# =====================================================================
class ButtonBehaviorLabel(ButtonBehavior, Label):
    """Botón estilizado con esquinas redondeadas dibujadas en Kivy Canvas."""
    def __init__(self, bg_color=(0.5, 0.3, 0.8, 1), **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(18)])
            Color(1, 1, 1, 0.25)
            Line(rounded_rectangle=(self.x, self.y, self.width, self.height, dp(18)), width=dp(1))


class LessonModal(ModalView):
    """
    Ventana emergente para cada nivel:
    Muestra la píldora cultural, permite generar una nueva lección en vivo
    con gemini-3.5-flash-lite y lanza el Quiz de 3 preguntas.
    """
    def __init__(self, level_data, on_complete_callback, **kwargs):
        super().__init__(**kwargs)
        self.level_data = dict(level_data)
        self.on_complete_callback = on_complete_callback
        self.size_hint = (0.92, 0.82)
        self.auto_dismiss = False
        self.background_color = (0, 0, 0, 0.65)
        self.current_q_index = 0
        self.correct_count = 0

        self.card = BoxLayout(orientation="vertical", padding=dp(18), spacing=dp(10))
        self.card.bind(pos=self._draw_card, size=self._draw_card)
        self.add_widget(self.card)

        self._build_reading_step()

    def _draw_card(self, *args):
        self.card.canvas.before.clear()
        with self.card.canvas.before:
            Color(0.24, 0.16, 0.45, 1)
            RoundedRectangle(pos=self.card.pos, size=self.card.size, radius=[dp(22)])
            Color(*COLOR_HUD_BORDER)
            Line(rounded_rectangle=(self.card.x, self.card.y, self.card.width, self.card.height, dp(22)), width=dp(1.5))

    def _build_reading_step(self, status_msg=""):
        self.card.clear_widgets()

        header = Label(
            text=f"[b]NIVEL {self.level_data['level']} • {self.level_data['category'].upper()}[/b]",
            markup=True,
            font_size=sp(13),
            color=(0.95, 0.80, 0.28, 1),
            size_hint=(1, None),
            height=dp(24)
        )
        title = Label(
            text=f"[b]{self.level_data['title']}[/b]",
            markup=True,
            font_size=sp(19),
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=dp(36),
            halign="center"
        )
        title.bind(size=lambda inst, val: setattr(inst, 'text_size', val))

        scroll = ScrollView(size_hint=(1, 1))
        body_lbl = Label(
            text=self.level_data["summary"],
            font_size=sp(15.5),
            color=(0.94, 0.92, 0.98, 1),
            size_hint_y=None,
            halign="left",
            valign="top",
            line_height=1.28
        )
        body_lbl.bind(
            width=lambda inst, w: setattr(inst, 'text_size', (w - dp(10), None)),
            texture_size=lambda inst, ts: setattr(inst, 'height', ts[1] + dp(20))
        )
        scroll.add_widget(body_lbl)

        self.ai_status_lbl = Label(
            text=status_msg,
            markup=True,
            font_size=sp(12.5),
            color=(0.75, 0.92, 1, 1),
            size_hint=(1, None),
            height=dp(22)
        )

        btn_ai = self._create_pill_button(
            "✨ Generar nueva lección con Gemini IA",
            (0.32, 0.52, 0.88, 1),
            (1, 1, 1, 1),
            self._request_gemini_lesson,
            height=dp(42)
        )

        btn_row = BoxLayout(orientation="horizontal", size_hint=(1, None), height=dp(46), spacing=dp(10))
        btn_close = self._create_pill_button("Cerrar", (0.45, 0.35, 0.68, 1), (1, 1, 1, 1), lambda *_: self.dismiss())
        btn_quiz = self._create_pill_button("Hacer Quiz (+5 ★)", COLOR_PREMIUM_GOLD, (0.1, 0.1, 0.1, 1), self._start_quiz)

        btn_row.add_widget(btn_close)
        btn_row.add_widget(btn_quiz)

        self.card.add_widget(header)
        self.card.add_widget(title)
        self.card.add_widget(scroll)
        self.card.add_widget(self.ai_status_lbl)
        self.card.add_widget(btn_ai)
        self.card.add_widget(btn_row)

    def _request_gemini_lesson(self, *args):
        self.ai_status_lbl.text = f"[i]Consultando {GEMINI_MODEL}...[/i]"
        generate_lesson_with_gemini(
            self.level_data["category"],
            self.level_data["title"],
            self._on_gemini_response
        )

    def _on_gemini_response(self, data, error):
        if data and "summary" in data and "quiz" in data:
            self.level_data["title"] = data.get("title", self.level_data["title"])
            self.level_data["summary"] = data["summary"]
            self.level_data["quiz"] = data["quiz"]
            self._build_reading_step("[color=#65F085]¡Lección generada con Gemini IA![/color]")
        else:
            self._build_reading_step("[color=#FFD166]Modo offline activo (usando lección local)[/color]")

    def _start_quiz(self, *args):
        self.current_q_index = 0
        self.correct_count = 0
        self._show_question()

    def _show_question(self):
        self.card.clear_widgets()
        questions = self.level_data["quiz"]
        q_data = questions[self.current_q_index]

        progress_lbl = Label(
            text=f"[b]PREGUNTA {self.current_q_index + 1} DE {len(questions)}[/b]",
            markup=True,
            font_size=sp(13),
            color=(0.95, 0.80, 0.28, 1),
            size_hint=(1, None),
            height=dp(26)
        )

        q_lbl = Label(
            text=f"[b]{q_data['q']}[/b]",
            markup=True,
            font_size=sp(18),
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=dp(90),
            halign="center",
            valign="middle"
        )
        q_lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', val))

        self.feedback_lbl = Label(
            text="",
            markup=True,
            font_size=sp(15),
            size_hint=(1, None),
            height=dp(32)
        )

        options_box = BoxLayout(orientation="vertical", spacing=dp(10), size_hint=(1, 1))
        for idx, opt_text in enumerate(q_data["options"]):
            btn = self._create_pill_button(
                opt_text,
                (0.38, 0.26, 0.68, 1),
                (1, 1, 1, 1),
                lambda _, i=idx: self._check_answer(i)
            )
            options_box.add_widget(btn)

        self.card.add_widget(progress_lbl)
        self.card.add_widget(q_lbl)
        self.card.add_widget(options_box)
        self.card.add_widget(self.feedback_lbl)

    def _check_answer(self, selected_idx):
        q_data = self.level_data["quiz"][self.current_q_index]
        if selected_idx == q_data["answer"]:
            self.correct_count += 1
            self.feedback_lbl.text = "[b][color=#58E878]¡Correcto! Excelente memoria.[/color][/b]"
        else:
            correct_txt = q_data["options"][q_data["answer"]]
            self.feedback_lbl.text = f"[b][color=#FF7878]Respuesta correcta: {correct_txt}[/color][/b]"

        Clock.schedule_once(self._next_step, 1.0)

    def _next_step(self, dt):
        self.current_q_index += 1
        if self.current_q_index < len(self.level_data["quiz"]):
            self._show_question()
        else:
            self._show_summary()

    def _show_summary(self):
        self.card.clear_widgets()
        total = len(self.level_data["quiz"])
        earned_stars = 5 if self.correct_count == total else 3

        title = Label(
            text="[b]¡Lección Completada![/b]",
            markup=True,
            font_size=sp(22),
            color=(0.95, 0.80, 0.28, 1),
            size_hint=(1, None),
            height=dp(45)
        )
        score = Label(
            text=(
                f"Has acertado [b]{self.correct_count} de {total}[/b] preguntas.\n\n"
                f"Recompensa: [b]+{earned_stars} Estrellas ★[/b]"
            ),
            markup=True,
            font_size=sp(17),
            halign="center",
            color=(1, 1, 1, 1)
        )
        btn_finish = self._create_pill_button(
            "Continuar en el Mapa",
            COLOR_PREMIUM_GOLD,
            (0.1, 0.1, 0.1, 1),
            lambda *_: self._finish(earned_stars),
            height=dp(50)
        )

        self.card.add_widget(title)
        self.card.add_widget(score)
        self.card.add_widget(btn_finish)

    def _finish(self, earned_stars):
        if self.on_complete_callback:
            self.on_complete_callback(self.level_data["level"], earned_stars)
        self.dismiss()

    def _create_pill_button(self, text, bg_color, text_color, callback, height=dp(46)):
        btn = ButtonBehaviorLabel(
            text=f"[b]{text}[/b]",
            markup=True,
            font_size=sp(15),
            color=text_color,
            bg_color=bg_color,
            size_hint=(1, None),
            height=height
        )
        btn.bind(on_release=callback)
        return btn


# =====================================================================
# VISTAS SECUNDARIAS (Quiz Rápido, Biblioteca, Perfil)
# =====================================================================
class QuickQuizView(BoxLayout):
    """Pestaña 'Quiz': preguntas rápidas y generación bajo demanda con Gemini."""
    def __init__(self, app_ref, **kwargs):
        super().__init__(orientation="vertical", padding=[dp(20), dp(86), dp(20), dp(100)], spacing=dp(10), **kwargs)
        self.app_ref = app_ref
        self.pool = []
        for lvl in LEVELS_DATA:
            for q in lvl["quiz"]:
                self.pool.append({"category": lvl["category"], **q})
        self.next_random_question()

    def next_random_question(self, *args):
        self.clear_widgets()
        item = random.choice(self.pool)
        self._render_question_item(item)

    def _render_question_item(self, item):
        self.clear_widgets()
        badge = Label(
            text=f"[b]RETO DIARIO • {item['category'].upper()}[/b]",
            markup=True,
            font_size=sp(14),
            color=(0.95, 0.80, 0.28, 1),
            size_hint=(1, None),
            height=dp(28)
        )
        q_lbl = Label(
            text=f"[b]{item['q']}[/b]",
            markup=True,
            font_size=sp(18),
            color=(1, 1, 1, 1),
            halign="center",
            valign="middle",
            size_hint=(1, None),
            height=dp(95)
        )
        q_lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', val))

        self.status_lbl = Label(
            text="Selecciona una respuesta para ganar +2 ★",
            markup=True,
            font_size=sp(14.5),
            color=(0.9, 0.88, 0.98, 1),
            size_hint=(1, None),
            height=dp(30)
        )

        self.add_widget(badge)
        self.add_widget(q_lbl)

        for idx, opt in enumerate(item["options"]):
            btn = ButtonBehaviorLabel(
                text=f"[b]{opt}[/b]",
                markup=True,
                font_size=sp(14.5),
                color=(1, 1, 1, 1),
                bg_color=(0.36, 0.23, 0.65, 0.95),
                size_hint=(1, None),
                height=dp(46)
            )
            btn.bind(on_release=lambda _, i=idx, it=item: self._answer(i, it))
            self.add_widget(btn)

        self.add_widget(self.status_lbl)

        ai_btn = ButtonBehaviorLabel(
            text="[b]✨ Pregunta Nueva con Gemini IA[/b]",
            markup=True,
            font_size=sp(14.5),
            color=(1, 1, 1, 1),
            bg_color=(0.32, 0.52, 0.88, 1),
            size_hint=(1, None),
            height=dp(44)
        )
        ai_btn.bind(on_release=self._generate_ai_quiz)
        self.add_widget(ai_btn)

        next_btn = ButtonBehaviorLabel(
            text="[b]Siguiente Pregunta →[/b]",
            markup=True,
            font_size=sp(15),
            color=(0.1, 0.1, 0.1, 1),
            bg_color=COLOR_PREMIUM_GOLD,
            size_hint=(1, None),
            height=dp(44)
        )
        next_btn.bind(on_release=self.next_random_question)
        self.add_widget(next_btn)

    def _generate_ai_quiz(self, *args):
        self.status_lbl.text = f"[i]Generando reto con {GEMINI_MODEL}...[/i]"
        cat = random.choice(["Historia", "Ciencia", "Geografía", "Arte", "Filosofía", "Astronomía", "Literatura"])
        generate_lesson_with_gemini(cat, "Curiosidades fascinantes", self._on_ai_quiz_ready)

    def _on_ai_quiz_ready(self, data, err):
        if data and data.get("quiz"):
            q = data["quiz"][0]
            q["category"] = data.get("title", "Cultura General IA")
            self.pool.append(q)
            self._render_question_item(q)
        else:
            self.next_random_question()

    def _answer(self, idx, item):
        if idx == item["answer"]:
            self.status_lbl.text = "[b][color=#65F085]¡Respuesta correcta! +2 Estrellas ★[/color][/b]"
            self.app_ref.add_stars(2)
        else:
            ans = item["options"][item["answer"]]
            self.status_lbl.text = f"[b][color=#FF8080]Incorrecto. Era: {ans}[/color][/b]"


class LibraryView(BoxLayout):
    """Pestaña 'Biblioteca': tarjetas resumen de todas las píldoras de cultura general."""
    def __init__(self, app_ref, **kwargs):
        super().__init__(orientation="vertical", padding=[dp(18), dp(85), dp(18), dp(100)], spacing=dp(10), **kwargs)
        self.app_ref = app_ref

        title = Label(
            text="[b]Biblioteca de Cultura General[/b]",
            markup=True,
            font_size=sp(20),
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=dp(36)
        )
        self.add_widget(title)

        scroll = ScrollView(size_hint=(1, 1))
        grid = GridLayout(cols=1, spacing=dp(12), size_hint_y=None, padding=[0, dp(6)])
        grid.bind(minimum_height=grid.setter('height'))

        for lvl in LEVELS_DATA:
            btn = ButtonBehaviorLabel(
                text=f"[b]Nivel {lvl['level']} • {lvl['category']}:[/b] {lvl['title']}",
                markup=True,
                font_size=sp(15),
                color=(1, 1, 1, 1),
                bg_color=(0.35, 0.22, 0.64, 0.95),
                size_hint=(1, None),
                height=dp(58)
            )
            btn.bind(on_release=lambda _, l=lvl: self.app_ref.open_lesson_modal(l))
            grid.add_widget(btn)

        scroll.add_widget(grid)
        self.add_widget(scroll)


class ProfileView(BoxLayout):
    """Pestaña 'Perfil': estadísticas de aprendizaje del usuario y estado del motor IA."""
    def __init__(self, app_ref, **kwargs):
        super().__init__(orientation="vertical", padding=[dp(22), dp(95), dp(22), dp(110)], spacing=dp(14), **kwargs)
        self.app_ref = app_ref
        self.stats_lbl = Label(
            text="",
            markup=True,
            font_size=sp(16.5),
            halign="center",
            valign="middle",
            color=(1, 1, 1, 1)
        )
        self.stats_lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
        self.add_widget(self.stats_lbl)

        reset_btn = ButtonBehaviorLabel(
            text="[b]Reiniciar Progreso de Demostración[/b]",
            markup=True,
            font_size=sp(15),
            color=(1, 1, 1, 1),
            bg_color=(0.82, 0.32, 0.42, 1),
            size_hint=(1, None),
            height=dp(48)
        )
        reset_btn.bind(on_release=lambda *_: self.app_ref.reset_progress())
        self.add_widget(reset_btn)
        self.refresh_profile()

    def refresh_profile(self):
        done = len(self.app_ref.completed_levels)
        total = len(LEVELS_DATA)
        self.stats_lbl.text = (
            "[b][size=22sp]Tu Perfil Gen K[/size][/b]\n\n"
            f"🔥 Racha actual: [b]{self.app_ref.hud.streak} días[/b]\n"
            f"🏳️ Metas de hoy: [b]{min(self.app_ref.hud.daily_goals, 3)}/3[/b]\n"
            f"⭐ Estrellas acumuladas: [b]{self.app_ref.hud.stars}[/b]\n"
            f"📚 Niveles superados: [b]{done} de {total}[/b]\n"
            f"🤖 Motor IA activo: [b]{GEMINI_MODEL}[/b]\n\n"
            "Sigue completando píldoras diarias de 5 minutos para dominar "
            "Historia, Ciencia, Geografía, Biología y Arte."
        )


# =====================================================================
# APLICACIÓN PRINCIPAL KIVY
# =====================================================================
class GenKApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Gen K - Aprende Cultura General"
        self.save_file = "genk_progress.json"
        self.completed_levels = set()
        self.stars_count = 28
        self.streak_count = 0
        self.daily_goals_count = 0
        self._load_progress()

    def build(self):
        self.root_layout = GridBackgroundWidget()

        self.content_area = FloatLayout(size_hint=(1, 1))
        self.root_layout.add_widget(self.content_area)

        self.map_scroll = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(0)
        )
        self.map_canvas = MapCanvasWidget(app_ref=self)
        self.map_canvas.refresh_completion_states(self.completed_levels)
        self.map_scroll.add_widget(self.map_canvas)

        self.scroll_top_btn = ButtonBehaviorLabel(
            text="[b]^[/b]",
            markup=True,
            font_size=sp(20),
            color=(1, 1, 1, 1),
            bg_color=(0.64, 0.49, 0.92, 0.92),
            size_hint=(None, None),
            size=(dp(42), dp(42)),
            pos_hint={"right": 0.95, "top": 0.86}
        )
        self.scroll_top_btn.bind(on_release=self._scroll_map_top)

        self.quiz_view = QuickQuizView(app_ref=self)
        self.library_view = LibraryView(app_ref=self)
        self.profile_view = ProfileView(app_ref=self)

        self.content_area.add_widget(self.map_scroll)
        self.content_area.add_widget(self.scroll_top_btn)

        self.hud = TopHudBar(
            on_premium_click=self.open_premium_modal,
            pos_hint={"top": 0.99, "x": 0}
        )
        self.hud.stars = self.stars_count
        self.hud.streak = self.streak_count
        self.hud.daily_goals = self.daily_goals_count
        self.root_layout.add_widget(self.hud)

        self.nav_bar = BottomNavBar(
            on_tab_change=self.switch_tab,
            pos_hint={"y": 0.01, "x": 0}
        )
        self.root_layout.add_widget(self.nav_bar)

        return self.root_layout

    def _scroll_map_top(self, *args):
        if self.map_scroll.scroll_y < 0.5:
            self.map_scroll.scroll_y = 1.0
        else:
            self.map_scroll.scroll_y = 0.0

    def switch_tab(self, tab_key):
        self.content_area.clear_widgets()
        if tab_key == "inicio":
            self.content_area.add_widget(self.map_scroll)
            self.content_area.add_widget(self.scroll_top_btn)
        elif tab_key == "quiz":
            self.content_area.add_widget(self.quiz_view)
        elif tab_key == "biblioteca":
            self.content_area.add_widget(self.library_view)
        elif tab_key == "perfil":
            self.profile_view.refresh_profile()
            self.content_area.add_widget(self.profile_view)

    def open_lesson_modal(self, level_data):
        modal = LessonModal(
            level_data=level_data,
            on_complete_callback=self.on_level_completed
        )
        modal.open()

    def open_premium_modal(self):
        modal = ModalView(size_hint=(0.88, 0.52), background_color=(0, 0, 0, 0.65))
        box = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(12))
        with box.canvas.before:
            Color(0.24, 0.16, 0.45, 1)
            rect = RoundedRectangle(pos=box.pos, size=box.size, radius=[dp(22)])
        box.bind(
            pos=lambda inst, val: setattr(rect, 'pos', val),
            size=lambda inst, val: setattr(rect, 'size', val)
        )
        box.add_widget(Label(
            text="[b][color=#F2CA46]Gen K Premium[/color][/b]",
            markup=True,
            font_size=sp(22),
            size_hint=(1, None),
            height=dp(38)
        ))
        box.add_widget(Label(
            text=(
                "• Acceso ilimitado a todas las categorías\n"
                "• Generación infinita con Gemini 3.5 Flash-Lite\n"
                "• Modo repaso inteligente de tarjetas\n"
                "• Estadísticas avanzadas de memoria"
            ),
            font_size=sp(15.5),
            halign="left",
            color=(1, 1, 1, 1)
        ))
        close_btn = ButtonBehaviorLabel(
            text="[b]¡Entendido![/b]",
            markup=True,
            font_size=sp(16),
            color=(0.1, 0.1, 0.1, 1),
            bg_color=COLOR_PREMIUM_GOLD,
            size_hint=(1, None),
            height=dp(46)
        )
        close_btn.bind(on_release=lambda *_: modal.dismiss())
        box.add_widget(close_btn)
        modal.add_widget(box)
        modal.open()

    def on_level_completed(self, level_num, earned_stars):
        self.completed_levels.add(level_num)
        self.stars_count += earned_stars
        self.daily_goals_count += 1
        if self.streak_count == 0:
            self.streak_count = 1

        self.hud.stars = self.stars_count
        self.hud.daily_goals = self.daily_goals_count
        self.hud.streak = self.streak_count
        self.map_canvas.refresh_completion_states(self.completed_levels)
        self._save_progress()

    def add_stars(self, amount):
        self.stars_count += amount
        self.hud.stars = self.stars_count
        self._save_progress()

    def reset_progress(self):
        self.completed_levels = set()
        self.stars_count = 28
        self.streak_count = 0
        self.daily_goals_count = 0
        self.hud.stars = 28
        self.hud.streak = 0
        self.hud.daily_goals = 0
        self.map_canvas.refresh_completion_states(self.completed_levels)
        self._save_progress()
        self.profile_view.refresh_profile()

    def _load_progress(self):
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.stars_count = data.get("stars", 28)
                    self.streak_count = data.get("streak", 0)
                    self.daily_goals_count = data.get("daily_goals", 0)
                    self.completed_levels = set(data.get("completed_levels", []))
            except Exception:
                pass

    def _save_progress(self):
        try:
            with open(self.save_file, "w", encoding="utf-8") as f:
                json.dump({
                    "stars": self.stars_count,
                    "streak": self.streak_count,
                    "daily_goals": self.daily_goals_count,
                    "completed_levels": list(self.completed_levels)
                }, f, ensure_ascii=False, indent=2)
        except Exception:
            pass


if __name__ == "__main__":
    GenKApp().run()
