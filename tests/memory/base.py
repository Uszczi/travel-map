from datetime import datetime
from typing import Any

import folium as fl
import gpxpy
import networkx as nx
import osmnx as ox
import pytest
from playwright.sync_api import sync_playwright

from tests.conftest import (
    get_image_path,
)
from travel_map.utils import (
    ROOT_PATH,
    get_graph_distance,
    route_to_zip_x_y,
)

INIT_DATA_PATH = ROOT_PATH / "init_data"

SAVE_TO_PNG = False
SAVE_TO_HTML = True or SAVE_TO_PNG
OPEN_IN_BROWSER = False


P = (1177493762, 1177493777)  # "Środek Piotrkowskiej"
L = (1177493766, 1177493886)  # "Odnoga na początku Lubelskiej"
W = (2131056242, 2131056249)  # "Wysoka"
WCZ = (1177493568, 1177493621)  # Wczasowa
J = (1177493669, 1177493724)  # Jagiełły
J2 = (1177493724, 1177493775)  # Jagiełły 2

KOSCIOL = 1177493848
PIASKOWA = 1177493695

start_time = None

import threading
import time
from contextlib import AbstractContextManager
from typing import Optional, List

import psutil
import matplotlib.pyplot as plt


class CPUUsagePlotter(AbstractContextManager):
    """
    Kontekst-menedżer próbkujący użycie CPU i rysujący wykres po wyjściu z kontekstu.

    Parametry:
        interval:      odstęp między próbkami w sekundach (np. 0.1 = 10 Hz)
        include_system: czy próbkować zużycie CPU całego systemu
        include_process: czy próbkować zużycie CPU bieżącego procesu
        normalize_process_to_100: jeśli True, dzieli wynik procesu przez liczbę logicznych CPU,
                                  aby uzyskać skalę 0–100% (zamiast 0–100*n_cpu)
        title:         tytuł wykresu (opcjonalnie)
        save_path:     ścieżka do zapisu PNG; jeśli None, zrobi plt.show()

    Uwaga:
        - Pierwsza próbka psutil.cpu_percent() służy jako „rozgrzewka” i może być 0.
        - __exit__ zadziała także przy wyjątku: wykres i tak zostanie wygenerowany.
    """

    def __init__(
        self,
        interval: float = 0.0000001,
        include_system: bool = True,
        include_process: bool = True,
        normalize_process_to_100: bool = True,
        title: Optional[str] = None,
        save_path: Optional[str] = None,
        fig=None,
        ax=None,
        legend=None,
    ):
        if not include_system and not include_process:
            raise ValueError(
                "Musisz włączyć include_system lub include_process (albo oba)."
            )

        self.interval = float(interval)
        self.include_system = include_system
        self.include_process = include_process
        self.normalize_process_to_100 = normalize_process_to_100
        self.title = title
        self.save_path = save_path

        self.legend = legend

        # Dane z próbkowania
        self._t0: Optional[float] = None
        self.times: List[float] = []
        self.system_cpu: List[float] = []
        self.process_cpu: List[float] = []

        # Wątek próbkowania
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None

        # Proces bieżący
        self._proc = psutil.Process()
        self._cpu_count = psutil.cpu_count(logical=True) or 1
        if not fig:
            self.fig, self.ax = plt.subplots()
        else:
            self.fig = fig
            self.ax = ax

    def __enter__(self):
        self._t0 = time.perf_counter()
        self.times.clear()
        self.system_cpu.clear()
        self.process_cpu.clear()

        # "Rozgrzewka" liczników psutil
        if self.include_system:
            psutil.cpu_percent(interval=None)
        if self.include_process:
            # Dla procesu – także rozgrzewka
            self._proc.cpu_percent(interval=None)

        self._stop.clear()
        self._thread = threading.Thread(
            target=self._sampler, name="CPUUsageSampler", daemon=True
        )
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        # Zatrzymaj próbkowanie
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=max(1.0, 3 * self.interval))

        # Narysuj wykres
        self._plot()
        # Nie tłumimy wyjątków — pozwalamy im się przebić dalej
        return False

    def _sampler(self):
        next_tick = time.perf_counter()
        while not self._stop.is_set():
            now = time.perf_counter()
            if now >= next_tick:
                t = now - (self._t0 or now)
                self.times.append(t)

                if self.include_system:
                    self.system_cpu.append(psutil.cpu_percent(interval=None))
                if self.include_process:
                    p = psutil.cpu_percent(interval=None)
                    # if self.normalize_process_to_100:
                    #     p = p / self._cpu_count
                    self.process_cpu.append(p)

                # wyznacz kolejny termin próbki
                next_tick += self.interval
            # śpij najkrócej jak trzeba, żeby ograniczyć jitter
            time.sleep(max(0.0, next_tick - time.perf_counter()) * 0.9)

    def _plot(self):
        # Dopasuj długości (gdy włączono/wyłączono któreś z pomiarów)
        # if self.include_system:
        #     plt.plot(
        #         self.times[: len(self.system_cpu)],
        #         self.system_cpu,
        #         label="CPU systemu [%]",
        #     )
        if self.include_process:
            self.ax.plot(
                self.times[: len(self.process_cpu)],
                self.process_cpu,
                label=self.legend,
            )

        self.fig.supxlabel("Czas [s]")
        self.fig.supylabel("Zużycie CPU [%]")
        self.fig.legend()
        # self.fig.tight_layout()

        if self.save_path:
            plt.savefig(self.save_path, dpi=150)
        else:
            plt.show()


def print_coverage(graph, v_edges):
    graph_distance = get_graph_distance(graph)
    visited_routes_distance = v_edges.get_visited_distance(graph)

    print(f"{visited_routes_distance / graph_distance * 100:.2f}")


import time
import threading
import tracemalloc
from dataclasses import dataclass, field
from typing import Optional, List

try:
    import psutil

    _PROC = psutil.Process()
except Exception:
    _PROC = None


@dataclass
class MemSample:
    t: float
    py_cur_mb: float
    py_peak_mb: float
    rss_mb: Optional[float]


@dataclass
class MemProfileResult:
    samples: List[MemSample] = field(default_factory=list)
    duration_s: float = 0.0
    py_peak_mb: float = 0.0
    rss_start_mb: Optional[float] = None
    rss_end_mb: Optional[float] = None

    @property
    def rss_increase_mb(self) -> Optional[float]:
        if self.rss_start_mb is None or self.rss_end_mb is None:
            return None
        return self.rss_end_mb - self.rss_start_mb


def _get_rss_mb() -> Optional[float]:
    if _PROC is None:
        return None
    try:
        return _PROC.memory_info().rss / (1024 * 1024)
    except Exception:
        return None


def _print_table(result: MemProfileResult, max_rows: int = 20) -> None:
    rows = result.samples
    data = rows if len(rows) <= max_rows else (rows[:10] + rows[-10:])
    headers = ["t(s)", "py_cur(MB)", "py_peak(MB)", "rss(MB)"]

    def w(col):
        vals = [headers[col]] + [
            (
                f"{r.t:.3f}"
                if col == 0
                else (
                    f"{r.py_cur_mb:.3f}"
                    if col == 1
                    else (
                        f"{r.py_peak_mb:.3f}"
                        if col == 2
                        else ("NA" if r.rss_mb is None else f"{r.rss_mb:.3f}")
                    )
                )
            )
            for r in data
        ]
        return max(len(v) for v in vals)

    ws = [w(i) for i in range(4)]
    header = f"{headers[0]:>{ws[0]}} | {headers[1]:>{ws[1]}} | {headers[2]:>{ws[2]}} | {headers[3]:>{ws[3]}}"
    sep = "-+-".join("-" * w for w in ws)
    print("=== MEMORY PROFILE TABLE ===")
    print(header)
    print(sep)
    for r in data:
        rss = "NA" if r.rss_mb is None else f"{r.rss_mb:.3f}"
        print(
            f"{r.t:>{ws[0]}.3f} | {r.py_cur_mb:>{ws[1]}.3f} | {r.py_peak_mb:>{ws[2]}.3f} | {rss:>{ws[3]}}"
        )
    if len(rows) > max_rows:
        print(f"... ({len(rows) - len(data)} rows omitted) ...")
    print(
        f"\nPeak: {result.py_peak_mb:.3f} MB  |  "
        f"RSS Δ: {('NA' if result.rss_increase_mb is None else f'{result.rss_increase_mb:.3f} MB')}  |  "
        f"Duration: {result.duration_s:.3f} s"
    )


# rss_plotter.py
import os
import time
import threading
from typing import List, Tuple, Optional

import psutil
import matplotlib.pyplot as plt


class RssPlotter:
    """
    Kontekst menedżer śledzący RSS procesu i (opcjonalnie) jego dzieci
    w regularnych odstępach czasu, a następnie rysujący wykres.

    Parametry:
      interval:        odstęp próbkowania w sekundach (float)
      unit:            'B' | 'KB' | 'MB' | 'GB'
      include_children:jeśli True, dolicza RSS procesów potomnych
      title:           tytuł wykresu (domyślny: 'Zużycie pamięci RSS procesu')
      show:            czy wyświetlić wykres (plt.show())
      save:            ścieżka do zapisu wykresu (np. 'rss.png'); None żeby nie zapisywać

    Użycie:
      with RssPlotter(interval=0.1, unit='MB') as mon:
          # ... kod do profilowania ...
      # po wyjściu z bloku wykres jest narysowany/zapisany, a mon.data() zwróci próbki
    """

    _SCALE = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3}

    def __init__(
        self,
        fig,
        ax,
        interval: float = 0.00001,
        unit: str = "MB",
        include_children: bool = False,
        title: Optional[str] = None,
        show: bool = True,
        save: Optional[str] = None,
        figsize: Tuple[float, float] = (8, 4),
    ):
        unit = unit.upper()
        if unit not in self._SCALE:
            raise ValueError(f"Nieobsługiwana jednostka: {unit}")
        self.interval = interval
        self.unit = unit
        self.include_children = include_children
        self.title = title or "Zużycie pamięci RSS procesu"
        self.show = show
        self.save = save
        self.figsize = figsize

        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._t: List[float] = []
        self._rss_bytes: List[int] = []
        self._start: Optional[float] = None
        self._proc = psutil.Process(os.getpid())
        self.fig = fig
        self.ax = ax

    # --- API pomocnicze ---
    def data(self) -> Tuple[List[float], List[float]]:
        scale = self._SCALE[self.unit]
        return self._t[:], [b / scale for b in self._rss_bytes]

    def peak(self) -> float:
        _, y = self.data()
        return max(y) if y else 0.0

    def _rss_now(self) -> int:
        rss = 0
        try:
            rss += self._proc.memory_info().rss
        except psutil.Error:
            pass
        if self.include_children:
            for ch in self._proc.children(recursive=True):
                try:
                    rss += ch.memory_info().rss
                except psutil.Error:
                    continue
        return rss

    def _sample_loop(self):
        while not self._stop.is_set():
            self._record_sample()
            self._stop.wait(self.interval)

    def _record_sample(self):
        t = time.monotonic() - (self._start or 0.0)
        self._t.append(t)
        self._rss_bytes.append(self._rss_now())

    def __enter__(self):
        self._start = time.monotonic()
        self._record_sample()
        self._thread = threading.Thread(target=self._sample_loop, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        self._stop.set()
        if self._thread is not None:
            self._thread.join()
        self._record_sample()

        x, y = self.data()
        if not self.fig:
            self.fig, self.ax = plt.subplots(figsize=self.figsize)
        self.ax.plot(x, y)
        self.ax.set_xlabel("czas [s]")
        self.ax.set_ylabel(f"RSS [{self.unit}]")
        self.ax.set_title(self.title)
        self.ax.grid(True, alpha=0.3)

        peak_val = max(y) if y else 0.0
        start_val = y[0] if y else 0.0
        end_val = y[-1] if y else 0.0
        delta = end_val - start_val
        if y:
            peak_idx = y.index(peak_val)
            ax.annotate(
                f"peak: {peak_val:.2f} {self.unit}",
                xy=(x[peak_idx], peak_val),
                xytext=(10, 10),
                textcoords="offset points",
                arrowprops=dict(arrowstyle="->", lw=1),
            )

        if self.save:
            self.fig.savefig(self.save, bbox_inches="tight")

        if self.show:
            plt.show()
        else:
            plt.close(self.fig)

        print(
            f"RSS start: {start_val:.2f} {self.unit}, "
            f"end: {end_val:.2f} {self.unit}, "
            f"peak: {peak_val:.2f} {self.unit}, "
            f"Δ: {delta:+.2f} {self.unit}"
        )


class Routes:
    generator_class: Any
    use_end_node: bool = True

    NUMBER_OF_ROUTES: int = 10
    DISTANCE: int = 6_000
    IGNORED_EDGES = (P, L, W, WCZ, J, J2)
    # IGNORED_NODES = (KOSCIOL, PIASKOWA)
    IGNORED_NODES = ()

    @pytest.fixture(autouse=True)
    def init(self) -> None:
        global start_time
        if start_time is None:
            start_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

    @pytest.fixture()
    def generator(self, graph, v_edges):
        return self.generator_class(graph, v_edges)

    def show(
        self,
        m: fl.Map,
        graph: nx.MultiDiGraph,
        routes: list[list[int]],
        request,
        start_node: int | None = None,
        end_node: int | None = None,
        paths: list[list[int]] | None = None,
        ignored_edges: list[tuple[int, int]] | None = None,
        ignored_nodes: list[int] | None = None,
    ):
        # if not isinstance(routes[0], int):
        #     routes = [routes]

        for edge in ignored_edges or []:
            x_y = route_to_zip_x_y(graph, [edge[0], edge[1]], reversed=True)
            fl.PolyLine(x_y, color="red").add_to(m)

        for node in ignored_nodes or []:
            fl.Marker(
                (graph.nodes[node]["y"], graph.nodes[node]["x"]),
                icon=fl.Icon(color="red"),
            ).add_to(m)

        for path in paths or []:
            x_y = route_to_zip_x_y(graph, path, reversed=True)
            fl.PolyLine(x_y, color="red").add_to(m)

        for route in routes:
            x_y = route_to_zip_x_y(graph, route, reversed=True)
            fl.PolyLine(x_y).add_to(m)

        if start_node:
            fl.Marker(
                (graph.nodes[start_node]["y"], graph.nodes[start_node]["x"]),
                icon=fl.Icon(color="green"),
            ).add_to(m)
        if end_node:
            fl.Marker(
                (graph.nodes[end_node]["y"], graph.nodes[end_node]["x"]),
                icon=fl.Icon(color="blue"),
            ).add_to(m)

        if SAVE_TO_HTML:
            name = request.node.originalname
            path = get_image_path(self, start_time) / name
            path = str(path)
            html_path = f"{path}.html"
            m.save(html_path)

            if SAVE_TO_PNG:
                png_path = f"{path}.png"
                with sync_playwright() as p:
                    browser = p.chromium.launch()
                    page = browser.new_page()
                    page.goto(f"file://{html_path}")
                    # TODO
                    page.wait_for_timeout(1000)
                    page.screenshot(path=png_path, full_page=True)
                    browser.close()

        if OPEN_IN_BROWSER:
            m.show_in_browser()

    def load_init_data(self, graph, v_edges) -> list[list[int]]:
        paths = []
        for path in sorted(INIT_DATA_PATH.glob("*.gpx")):
            with path.open("r", encoding="utf-8") as f:
                gpx = gpxpy.parse(f)

            points: list[tuple[float, float]] = []
            if gpx.tracks:
                for trk in gpx.tracks:
                    for seg in trk.segments:
                        for p in seg.points:
                            points.append((float(p.longitude), float(p.latitude)))
            elif gpx.routes:
                for rte in gpx.routes:
                    for p in rte.points:
                        points.append((float(p.longitude), float(p.latitude)))

            x: list[float] = []
            y: list[float] = []
            prev = None
            for lon, lat in points:
                pair = (lon, lat)
                if pair != prev:
                    x.append(lon)
                    y.append(lat)
                    prev = pair

            nodes = ox.nearest_nodes(graph, x, y)
            nodes = list(dict.fromkeys(nodes))

            filtered_nodes = []
            _nodes = nodes[:]
            current_node = _nodes.pop(0)
            next_node = _nodes.pop(0)
            while _nodes:
                if graph.get_edge_data(current_node, next_node):
                    filtered_nodes.append(current_node)
                    filtered_nodes.append(next_node)
                    current_node = next_node
                    if _nodes:
                        next_node = _nodes.pop(0)
                else:
                    # TODO
                    # Move tail few time (50?) until it finds edge otherwise move head
                    current_node = next_node
                    if _nodes:
                        next_node = _nodes.pop(0)

            filtered_nodes = list(dict.fromkeys(filtered_nodes))
            paths.append(filtered_nodes)

        for path in paths:
            v_edges.mark_edges_visited(path)

        return paths

    def test_memory(
        self,
        graph,
        fm,
        start_node,
        end_node,
        v_edges,
        generator,
        request,
    ):
        routes = []
        with CPUUsagePlotter(
            save_path=f"{generator.__class__.__name__}_{request.node.originalname}",
            legend="Random",
        ) as f:
            for _ in range(self.NUMBER_OF_ROUTES):
                route = generator.generate(
                    start_node=start_node,
                    end_node=end_node if self.use_end_node else None,
                    distance=self.DISTANCE,
                    ignored_edges=[],
                    ignored_nodes=[],
                )
                if route:
                    v_edges.mark_edges_visited(route)
                    routes.append(route)
                else:
                    print("Generating route failed.")

        print_coverage(graph, v_edges)
        v_edges.clear()

        with CPUUsagePlotter(
            save_path=f"{generator.__class__.__name__}_{request.node.originalname}",
            ax=f.ax,
            fig=f.fig,
            legend="DFS",
        ) as f:
            for _ in range(self.NUMBER_OF_ROUTES):
                route = generator.generate(
                    start_node=start_node,
                    end_node=end_node if self.use_end_node else None,
                    distance=self.DISTANCE,
                    ignored_edges=[],
                    ignored_nodes=[],
                )
                if route:
                    v_edges.mark_edges_visited(route)
                    routes.append(route)
                else:
                    print("Generating route failed.")

        print_coverage(graph, v_edges)
        # self.show(
        #     fm,
        #     graph,
        #     routes,
        #     request,
        #     start_node,
        #     end_node,
        #     [],
        #     self.IGNORED_EDGES,
        #     self.IGNORED_NODES,
        # )
