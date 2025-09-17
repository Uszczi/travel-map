from datetime import datetime
from typing import Any

import matplotlib.pyplot as plt
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


from dataclasses import dataclass, field
from typing import Optional

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
from typing import List, Tuple, Optional, Literal

import psutil


def _read_smaps_rollup(pid: int) -> dict[str, int]:
    """Czyta /proc/<pid>/smaps_rollup i zwraca wybrane pola (w bajtach)."""
    out: dict[str, int] = {}
    path = f"/proc/{pid}/smaps_rollup"
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if ":" not in line:
                    continue
                k, v = line.split(":", 1)
                k = k.strip()
                v = v.strip().split()[0]  # wartość w kB
                if k in {"Pss", "Rss", "Private_Clean", "Private_Dirty"}:
                    out[k] = int(v) * 1024  # kB -> B
    except FileNotFoundError:
        pass
    except Exception:
        pass
    return out


class RssPlotter:
    """
    Dokładniejszy profiler pamięci procesu:
      - precyzyjne próbkowanie (perf_counter + planowanie kolejnych ticków),
      - metryki: RSS (domyślna), PSS, USS (z psutil lub /proc/*/smaps_rollup),
      - opcjonalne doliczanie potomków.

    Parametry zgodne z poprzednią wersją + nowy 'metric':
      metric: 'rss' | 'pss' | 'uss'
    """

    _SCALE = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3}

    def __init__(
        self,
        fig=None,
        ax=None,
        *,
        interval: float = 0.01,
        unit: str = "KB",
        include_children: bool = False,
        title: Optional[str] = None,
        show: bool = True,
        save: Optional[str] = None,
        figsize: Tuple[float, float] = (8, 4),
        metric: Literal["rss", "pss", "uss"] = "rss",
        min_interval: float = 0.005,  # twarde minimum, psutil i tak ma pewien narzut
    ):
        unit = unit.upper()
        if unit not in self._SCALE:
            raise ValueError(f"Nieobsługiwana jednostka: {unit}")
        if metric not in {"rss", "pss", "uss"}:
            raise ValueError("metric musi być jednym z: 'rss', 'pss', 'uss'")

        # Utrzymaj API: jeśli fig/ax nie podane, stworzymy je przy __exit__
        self.fig = fig
        self.ax = ax

        self.interval = max(float(interval), float(min_interval))
        self.unit = unit
        self.include_children = include_children
        self.title = title or "Zużycie pamięci procesu"
        self.show = show
        self.save = save
        self.figsize = figsize
        self.metric = metric

        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._t: List[float] = []
        self._bytes: List[int] = []
        self._t0: Optional[float] = None
        self._proc = psutil.Process(os.getpid())

    # --- API pomocnicze ---
    def data(self) -> Tuple[List[float], List[float]]:
        scale = self._SCALE[self.unit]
        return self._t[:], [b / scale for b in self._bytes]

    def peak(self) -> float:
        _, y = self.data()
        return max(y) if y else 0.0

    # --- pobieranie metryk pamięci ---
    def _proc_mem_bytes(self, proc: psutil.Process) -> int:
        """Zwraca bajty dla wybranej metryki (rss/pss/uss) jednego procesu."""
        try:
            if self.metric == "rss":
                return proc.memory_info().rss
            # pss / uss: najpierw spróbuj przez psutil (szybciej), potem smaps_rollup
            if self.metric in {"pss", "uss"}:
                mfull = None
                try:
                    mfull = proc.memory_full_info()
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    mfull = None

                if mfull is not None:
                    if self.metric == "pss" and hasattr(mfull, "pss"):
                        return int(mfull.pss)
                    if self.metric == "uss" and hasattr(mfull, "uss"):
                        return int(mfull.uss)

                sm = _read_smaps_rollup(proc.pid)
                if self.metric == "pss":
                    return sm.get("Pss", 0)
                # USS ~= Private_Clean + Private_Dirty
                if self.metric == "uss":
                    return sm.get("Private_Clean", 0) + sm.get("Private_Dirty", 0)
        except (psutil.NoSuchProcess, psutil.ZombieProcess, psutil.AccessDenied):
            return 0
        except Exception:
            return 0
        return 0

    def _mem_now_bytes(self) -> int:
        total = self._proc_mem_bytes(self._proc)
        if self.include_children:
            try:
                for ch in self._proc.children(recursive=True):
                    total += self._proc_mem_bytes(ch)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return total

    # --- pętla próbkowania z planowaniem next_tick ---
    def _sample_loop(self):
        next_tick = time.perf_counter()
        while not self._stop.is_set():
            now = time.perf_counter()
            if now >= next_tick:
                self._record_sample(now)
                # jeżeli byliśmy spóźnieni, nadgonimy bez „spirali”
                skipped = int((now - next_tick) // self.interval)
                next_tick += (skipped + 1) * self.interval
            # czekaj dokładnie do następnego ticka (lub krócej, jeśli przerwano)
            sleep_for = max(0.0, next_tick - time.perf_counter())
            self._stop.wait(sleep_for)

    def _record_sample(self, now: Optional[float] = None):
        if now is None:
            now = time.perf_counter()
        t = now - (self._t0 or now)
        self._t.append(t)
        self._bytes.append(self._mem_now_bytes())

    def __enter__(self):
        # ustal t0 i zrób zerową próbkę
        self._t0 = time.perf_counter()
        self._record_sample(self._t0)
        self._thread = threading.Thread(
            target=self._sample_loop, daemon=True, name="RssPlotterSampler"
        )
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        self._stop.set()
        if self._thread is not None:
            self._thread.join()
        self._record_sample()  # ostatnia próbka

        x, y = self.data()
        if self.fig is None or self.ax is None:
            self.fig, self.ax = plt.subplots(figsize=self.figsize)

        # Rysunek
        self.ax.plot(x, y)
        self.ax.set_xlabel("czas [s]")
        self.ax.set_ylabel(f"{self.metric.upper()} [{self.unit}]")
        self.ax.set_title(self.title)
        self.ax.grid(True, alpha=0.3)

        # --- WYŁĄCZENIE NOTACJI NAUKOWEJ NA OSIACH ---
        from matplotlib.ticker import ScalarFormatter

        sf_x = ScalarFormatter(useMathText=False)
        sf_x.set_scientific(False)
        sf_x.set_useOffset(False)
        self.ax.xaxis.set_major_formatter(sf_x)

        sf_y = ScalarFormatter(useMathText=False)
        sf_y.set_scientific(False)
        sf_y.set_useOffset(False)
        self.ax.yaxis.set_major_formatter(sf_y)

        # Dodatkowe zabezpieczenie (obejmuje obie osie)
        self.ax.ticklabel_format(style="plain", useOffset=False, axis="both")
        # ---------------------------------------------

        if y:
            peak_val = max(y)
            peak_idx = y.index(peak_val)
            self.ax.annotate(
                f"peak: {peak_val:.2f} {self.unit}",
                xy=(x[peak_idx], peak_val),
                xytext=(10, 10),
                textcoords="offset points",
                arrowprops=dict(arrowstyle="->", lw=1),
            )
            start_val, end_val = y[0], y[-1]
            delta = end_val - start_val
        else:
            start_val = end_val = delta = 0.0

        if self.save:
            self.fig.savefig(self.save, bbox_inches="tight")

        if self.show:
            plt.show()
        else:
            plt.close(self.fig)

        print(
            f"{self.metric.upper()} start: {start_val:.2f} {self.unit}, "
            f"end: {end_val:.2f} {self.unit}, "
            f"peak: {peak_val:.2f} {self.unit}, "
            f"Δ: {delta:+.2f} {self.unit}"
        )


# --- end of replacement ---


class Routes:
    generator_class_1: Any
    generator_class_2: Any
    generator_class_3: Any

    use_end_node: bool = True

    NUMBER_OF_ROUTES: int = 20
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
    def generator1(self, graph, v_edges):
        return self.generator_class_1(graph, v_edges)

    @pytest.fixture()
    def generator2(self, graph, v_edges):
        return self.generator_class_2(graph, v_edges)

    @pytest.fixture()
    def generator3(self, graph, v_edges):
        return self.generator_class_3(graph, v_edges)

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
        generator1,
        generator2,
        generator3,
        request,
    ):
        # --- 1) jedna figura + 3 osie (po jednej dla każdego generatora) ---
        fig, axs = plt.subplots(nrows=3, ncols=1, figsize=(10, 9), sharex=True)
        ax1, ax2, ax3 = axs

        routes: list[list[int]] = []

        # --- 2) generator1 na pierwszej osi ---
        with RssPlotter(
            fig=fig,
            ax=ax1,
            title=f"{generator1.__class__.__name__}",
            metric="uss",
            show=False,  # nie otwieraj okna
            save=None,  # nie zapisuj pojedynczych wykresów
        ):
            for _ in range(self.NUMBER_OF_ROUTES):
                route = generator1.generate(
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

        # --- 3) generator2 na drugiej osi ---
        with RssPlotter(
            fig=fig,
            ax=ax2,
            title=f"{generator2.__class__.__name__}",
            metric="uss",
            show=False,
            save=None,
        ):
            for _ in range(self.NUMBER_OF_ROUTES):
                route = generator2.generate(
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

        v_edges.clear()

        # --- 4) generator3 na trzeciej osi ---
        with RssPlotter(
            fig=fig,
            ax=ax3,
            title=f"{generator3.__class__.__name__}",
            metric="uss",
            show=False,
            save=None,
        ):
            for _ in range(self.NUMBER_OF_ROUTES * 5):
                route = generator3.generate(
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

        # --- 5) kosmetyka + wspólny zapis ---
        fig.suptitle("Porównanie zużycia pamięci", y=0.98)
        fig.supxlabel("czas [s]")
        fig.supylabel("USS [B]")
        fig.tight_layout(rect=[0, 0.03, 1, 0.95])

        out_path = f"memory_combined_{request.node.originalname}.png"
        fig.savefig(out_path, dpi=150)
        plt.close(fig)

        # Jeśli chcesz też obejrzeć trasy na mapie, odkomentuj niżej:
        # self.show(
        #     fm,
        #     graph,
        #     routes,
        #     request,
        #     start_node,
        #     end_node,
        #     paths=[],
        #     ignored_edges=self.IGNORED_EDGES,
        #     ignored_nodes=self.IGNORED_NODES,
        # )
