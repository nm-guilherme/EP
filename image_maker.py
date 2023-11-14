import matplotlib.pyplot as plt
from stowing_classes import Ship, Cargo, Area
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

def get_cargo_plot_points(cargo: Cargo):
    if cargo.rotated:
        height = cargo.w
        width = cargo.h
    else:
        height = cargo.h
        width = cargo.w
    mid_x = cargo.x + width / 2
    mid_y = cargo.y + height / 2
    return mid_x, mid_y, height, width

def get_area_plot_points(area: Area):
    mid_x = area.x + area.w / 2
    mid_y = area.y + area.h / 2
    return mid_x, mid_y

def plot_cargos(ship: Ship, cargos: list[Cargo]):
    fig, ax = plt.subplots(figsize=(ship.W/4, ship.H/4), dpi=120)
    ax.plot()
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    ax.set_xlim(0, ship.W)
    ax.set_ylim(0, ship.H)

    for area in ship.areas:
        for cargo in area.cargos:
            if cargo.allocated:
                label_cargo = cargo.cargo_id
                mid_x, mid_y, height, width = get_cargo_plot_points(cargo)
                area_rectangle = plt.Rectangle((cargo.x,cargo.y), width, height, facecolor = area.color, edgecolor='gray', linewidth=1)
                ax.add_patch(area_rectangle)
                ax.annotate(f"{label_cargo}", (mid_x, mid_y), color='white', ha='center', va='center', fontsize= 8)
        
        mid_x_area, mid_y_area = get_area_plot_points(area)
        background_circle = plt.Circle((mid_x_area, mid_y_area), radius=1.2, fill=True, color='white', alpha=0.8)
        ax.add_patch(background_circle)
        ax.annotate(f"{area.label}", (mid_x_area, mid_y_area), color='black', ha='center', va='center', fontsize= 8)

        if area.area_id==0:
            area_rectangle = plt.Rectangle((area.x,area.y), area.w, area.h, facecolor = area.color, edgecolor='gray', linewidth=1)
            ax.add_patch(area_rectangle)
            ax.add_patch(background_circle)
            ax.annotate(f"{area.label}", (mid_x_area, mid_y_area), color='black', ha='center', va='center', fontsize= 8)

    for cargo in cargos:
        if cargo.restricted_area:
            label_cargo = cargo.cargo_id
            mid_x, mid_y, height, width = get_cargo_plot_points(cargo)
            area_rectangle = plt.Rectangle((cargo.x,cargo.y), width, height, facecolor = 'gray', edgecolor='gray', linewidth=1)
            ax.add_patch(area_rectangle)
            ax.annotate(f"{label_cargo}", (mid_x, mid_y), color='white', ha='center', va='center', fontsize= 8)

    fig.savefig("cargas.png", bbox_inches='tight', pad_inches=0.1)

def plot_cargos_inverted(ship: Ship, cargos: list[Cargo]):
    fig, ax = plt.subplots(figsize=(ship.H/4, ship.W/4), dpi=120)
    ax.plot()
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    ax.set_xlim(0, ship.H)
    ax.set_ylim(0, ship.W)

    for area in ship.areas:
        for cargo in area.cargos:
            if cargo.allocated:
                label_cargo = cargo.cargo_id
                mid_y, mid_x, width, height = get_cargo_plot_points(cargo)
                area_rectangle = plt.Rectangle((cargo.y,cargo.x), width, height, facecolor = area.color, edgecolor='gray', linewidth=1)
                ax.add_patch(area_rectangle)
                ax.annotate(f"{label_cargo}", (mid_x, mid_y), color='white', ha='center', va='center', fontsize= 8)
        
        mid_y_area, mid_x_area = get_area_plot_points(area)
        background_circle = plt.Circle((mid_x_area, mid_y_area), radius=1.2, fill=True, color='white', alpha=0.8)
        ax.add_patch(background_circle)
        ax.annotate(f"{area.label}", (mid_x_area, mid_y_area), color='black', ha='center', va='center', fontsize= 8)

        if area.area_id==0:
            area_rectangle = plt.Rectangle((area.y,area.x), area.h, area.w, facecolor = area.color, edgecolor='gray', linewidth=1)
            ax.add_patch(area_rectangle)
            ax.add_patch(background_circle)
            ax.annotate(f"{area.label}", (mid_x_area, mid_y_area), color='black', ha='center', va='center', fontsize= 8)

    for cargo in cargos:
        if cargo.restricted_area:
            # label_cargo = "R"+str(cargo.cargo_id)
            label_cargo = cargo.cargo_id
            mid_y, mid_x, width, height = get_cargo_plot_points(cargo)
            area_rectangle = plt.Rectangle((cargo.y,cargo.x), width, height, facecolor = 'gray', edgecolor='gray', linewidth=1)
            ax.add_patch(area_rectangle)
            ax.annotate(f"{label_cargo}", (mid_x, mid_y), color='white', ha='center', va='center', fontsize= 8)

    fig.savefig("cargas_inverted.png", bbox_inches='tight', pad_inches=0.1)
