# ──────────────────────────── benchmarks.py ────────────────────────────
import time
import csv
import pathlib
import random
from statistics import mean

import arcade
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------
# Fenêtre OpenGL masquée : Arcade a besoin d’un contexte OpenGL actif
# ---------------------------------------------------------------------
WINDOW = arcade.Window(800, 600, title="Bench (hidden)", visible=False)

from src.game.gameview import GameView
from src.entities.bat import Bat

# Dossier de sortie
OUTPUT = pathlib.Path("benchmarks")
OUTPUT.mkdir(exist_ok=True)

# Paramètres à explorer
WALL_STEPS  = [1, 10, 50, 100, 500, 1_000, 5_000, 10_000, 100_000]
ENEMY_STEPS = [1, 3, 5, 10, 50, 100, 500, 1_000, 10_000]

FRAME_COUNT = 200      # appels on_update() par cas
DT          = 1 / 60   # delta fixe (60 fps)

# ---------------------------------------------------------------------
# Création d’un niveau synthétique
# ---------------------------------------------------------------------
def build_level(n_walls: int, n_enemies: int) -> GameView:
    """Retourne un GameView contenant `n_walls` briques et `n_enemies` blobs."""
    view = GameView()           # GameView.__init__ lance déjà son setup

    # On part d’un décor vide pour chaque benchmark
    view.wall_list.clear()
    view.monster_list.clear()
    if hasattr(view, "platforms"):
        view.platforms.clear()

    # Murs : briques brunes alignées
    for i in range(n_walls):
        brick = arcade.Sprite(
            ":resources:images/tiles/brickBrown.png",
            scale=0.5,
        )
        brick.center_x = (i % 40) * 32 + 16
        brick.center_y = (i // 40) * 32 + 16
        view.wall_list.append(brick)

    # Ennemis : blobs aléatoires
    for _ in range(n_enemies):
        x = random.randint(32, 800 - 32)
        y = random.randint(96, 600 - 32)
        blob = Bat((x, y), speed=1)
        blob._walls = view.wall_list
        view.monster_list.append(blob)

    return view

# ---------------------------------------------------------------------
# Mesure d’un couple (n_walls, n_enemies)
# ---------------------------------------------------------------------
def measure_case(n_walls: int, n_enemies: int) -> tuple[float, float]:
    """Retourne (load_time, mean_update_time) en secondes."""
    tic = time.perf_counter()
    gv = build_level(n_walls, n_enemies)
    load_time = time.perf_counter() - tic

    frame_times = []
    for _ in range(FRAME_COUNT):
        tic = time.perf_counter()
        gv.on_update(DT)
        frame_times.append(time.perf_counter() - tic)

    return load_time, mean(frame_times)

# ---------------------------------------------------------------------
# Campagne de mesures
# ---------------------------------------------------------------------
def run_bench(param_name: str, values: list[int], fixed: int) -> None:
    """Varie `param_name` (walls ou enemies) en gardant l’autre paramètre fixe."""
    results = []

    for val in values:
        walls   = val if param_name == "walls"   else fixed
        enemies = val if param_name == "enemies" else fixed

        load_t, upd_t = measure_case(walls, enemies)
        results.append({"count": val,
                        "load_time": load_t,
                        "update_time": upd_t})

        print(f"{param_name}={val:>6} | load={load_t*1e3:7.2f} ms"
              f" | update={upd_t*1e6:7.2f} µs")

    # CSV ----------------------------------------------------------------
    csv_path = OUTPUT / f"{param_name}.csv"
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print("CSV →", csv_path)

    # Graphique log-log ---------------------------------------------------
    xs        = [r["count"] for r in results]
    load_ts   = [r["load_time"]   for r in results]
    update_ts = [r["update_time"] for r in results]

    fig, ax = plt.subplots()
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.plot(xs, load_ts,  "o-", label="Load time (s)")
    ax.plot(xs, update_ts, "o-", label="Mean on_update (s)")
    ax.set_xlabel(f"Number of {param_name}")
    ax.legend(); ax.grid(True, which="both", linestyle=":")
    png_path = OUTPUT / f"{param_name}.png"
    fig.savefig(png_path, dpi=150)
    plt.close(fig)
    print("PNG →", png_path, "\n")

# ---------------------------------------------------------------------
# Exécution
# ---------------------------------------------------------------------
if __name__ == "__main__":
    # 1) Variation du nombre de murs (ennemis = 10)
    run_bench("walls", WALL_STEPS, fixed=10)

    # 2) Variation du nombre de blobs (murs = 1 000)
    run_bench("enemies", ENEMY_STEPS, fixed=1_000)

    arcade.close_window()        # proprement
