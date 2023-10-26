import matplotlib.pyplot as plt
from stowing_classes import Cargo, Ship
from matplotlib.colors import Normalize
import matplotlib.transforms as transforms

def plot_areas(ship: Ship):
    fig, ax = plt.subplots(figsize=(ship.W/8, ship.H/8))
    ax.plot()
    for area in ship.areas.values():
        mid_x = area.x + area.w / 2
        mid_y = area.y + area.h / 2

        area_rectangle = plt.Rectangle((area.x,area.y), area.w, area.h, facecolor=area.color, edgecolor='gray', linewidth=1)
        background_circle = plt.Circle((mid_x, mid_y), radius=1, fill=True, color='white', alpha=0.8)
        ax.add_patch(area_rectangle)
        ax.add_patch(background_circle)
        ax.annotate(f"{area.label}", (mid_x, mid_y), color='black', ha='center', va='center', fontsize= 8)

    rotate_transform = transforms.Affine2D().rotate_deg(90)
    plt.gcf().set_transform(rotate_transform + plt.gcf().transFigure)
    fig.savefig("areas.png", bbox_inches='tight', pad_inches=0.1)

def plot_cargos(ship: Ship):
    fig, ax = plt.subplots(figsize=(ship.W/8, ship.H/8))
    ax.plot()
    for area in ship.areas.values():
        for cargo in area.cargos:
            if cargo.allocated:
                label_cargo = cargo.cargo_id.split('_')[-1]
                mid_x = cargo.x + cargo.w / 2
                mid_y = cargo.y + cargo.h / 2
                area_rectangle = plt.Rectangle((cargo.x,cargo.y), cargo.w, cargo.h, facecolor = area.color, 
                                               edgecolor='gray', linewidth=1)
                ax.add_patch(area_rectangle)
                ax.annotate(f"{label_cargo}", (mid_x, mid_y), color='white', ha='center', va='center')
        mid_x_area = area.x + area.w / 2
        mid_y_area = area.y + area.h / 2
        background_circle = plt.Circle((mid_x_area, mid_y_area), radius=1.2, fill=True, color='white', alpha=0.8)
        ax.add_patch(background_circle)
        ax.annotate(f"{area.label}", (mid_x_area, mid_y_area), color='black', ha='center', va='center', fontsize= 8)

    fig.savefig("cargas.png", bbox_inches='tight', pad_inches=0.1)