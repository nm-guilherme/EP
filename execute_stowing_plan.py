import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '../..')))
import time
import logging
import pandas as pd
from typing import Tuple
import image_maker as im
from stages import stage_1, stage_2, stage_3
from complete_model import MathematicalModel
from stowing_classes import Cargo, Ship, Area

FORMAT = '%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s] %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)

def read_inputs(path, restricted_positions) -> Tuple[list[Cargo], str]:
    plan_dataframe = pd.read_excel(path, skiprows=3, usecols="A:I").set_index("carga")
    n_destinations = len(plan_dataframe['destino'].unique())
    cargos_dict = plan_dataframe.T.to_dict()
    cargos = list()
    dangerous_area = None
    for i in cargos_dict:
        if cargos_dict[i]['carga perigosa'] == 1:
            dangerous_area = n_destinations+1
        cargos.append(Cargo(i, n_destinations, cargos_dict[i], restricted_positions))
    return cargos, dangerous_area

def main(H, H_DG, W, T, W_CORREDOR, restricted_positions, time_max=30, path="Plano de Estivagem.xlsx"):
    logging.info("Reading inputs...")
    cargos, dangerous_area = read_inputs(path, restricted_positions)
    
    logging.info("Creating Cargos...")
    cargos_id_list = [c.cargo_id for c in cargos]

    logging.info("Creating Ship...")
    ship = Ship(H, H_DG, W, T, W_CORREDOR)
    areas = [Area(0)]+[Area(area_id) for area_id in list(set([c.area for c in cargos if not c.restricted_area]))]
    ship.set_areas(areas, dangerous_area)
    
    logging.info("Creating Model...")
    model = MathematicalModel(time_max=time_max)
    model.add_variables(ship, cargos, cargos_id_list)
    model.add_area_constrains(ship)
    model.add_cargos_constrains(cargos, ship)
    logging.info("Executing Model...")
    s = time.time()
    model.solve_model(cargos_id_list)
    e = time.time()
    logging.info(f"Model executed in {e-s} seconds")
    model.get_results(cargos, ship)
    print(f"Total # of cargos: {len(cargos)}")
    print(f"Total # of allocated cargos: {sum([1 if c.allocated else 0 for c in cargos])}")
    area_cargos = sum([c.area for c in cargos if c.allocated])
    ship_area = ship.W*ship.H-ship.W_CORREDOR*ship.H
    print(f"Occupied area:"+f"{area_cargos/ship_area*100:.2f}%")
    print(f"Objective function value: {model.m.objVal}")

    logging.info(f"Plotting results...")
    im.plot_cargos(ship, cargos)
    im.plot_cargos_inverted(ship, cargos)
    logging.info(f"Script executed successfully!")

restricted_positions = {1: {'x': 0, 'y':14}, 2: {'x': 14, 'y':30}}

main(H=60, H_DG=8, W=15, T=12, W_CORREDOR=1, restricted_positions = restricted_positions, time_max=120)
    

