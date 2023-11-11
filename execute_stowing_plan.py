import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '../..')))

import logging
import pandas as pd
from typing import Tuple
import image_maker as im
from stages import stage_1, stage_2, stage_3
from stowing_classes import Cargo, Ship, Area

FORMAT = '%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s] %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)

def read_inputs(path) -> Tuple[list[Cargo], str]:
    plan_dataframe = pd.read_excel(path, skiprows=3, usecols="A:I").set_index("carga")
    # plan_dataframe = plan_dataframe.set_axis(["carga_"+str(i) for i in plan_dataframe.index], copy=False)
    n_destinations = len(plan_dataframe['destino'].unique())
    cargos_dict = plan_dataframe.T.to_dict()
    cargos = list()
    for i in cargos_dict:
        try:
            cargos.append(Cargo(i, n_destinations, cargos_dict[i]))
        except:
            print(i)
    dangerous_area = "area_" + str(n_destinations)
    return cargos, dangerous_area

def main(H, H_DG, W, T, W_CORREDOR, x_HS, y_HS, time_max, path="Plano de Estivagem - Copy - Copy.xlsx"):
    logging.info("Reading inputs...")
    cargos, dangerous_area = read_inputs(path)
    cargos_id_list = [c.cargo_id for c in cargos]
    logging.info("Creating Ship...")
    ship = Ship(H, H_DG, W, T, W_CORREDOR)
    areas = [Area(area_id) for area_id in list(set([c.area for c in cargos]))]
    areas_id_list = [a.area_id for a in areas]
    ship.set_areas(areas_id_list, dangerous_area)
    logging.info("Executing Stage 1...")
    optimal_cargos_stage1 = stage_1(cargos, ship, cargos_id_list)
    for cargo in optimal_cargos_stage1:
        print(f"{cargo.cargo_id}: W = {cargo.w}; H = {cargo.h}, Area = {cargo.area}")
    logging.info("Executing Stage 2...")
    a_areas, b_areas, c_areas, d_areas = stage_2(ship, optimal_cargos_stage1, time_max)
    im.plot_areas(ship=ship)
    logging.info("Ship areas plotted!")
    logging.info("Executing Stage 3")
    stage_3(ship, optimal_cargos_stage1, cargos, x_HS, y_HS, a_areas, b_areas, c_areas, d_areas) 
    im.plot_cargos(ship=ship)
    logging.info("Stowing plan executed!")
    for c in cargos:
        print(c.cargo_id, c.x, c.y)

x_HS = {"carga_1":0, "carga_2":14}
y_HS = {"carga_1":30, "carga_2":30}

x_HS = {"carga_1":30, "carga_2":30}
y_HS = {"carga_1":0, "carga_2":14}

main(H=60, H_DG=5, W=15, T=12, W_CORREDOR=1, x_HS=x_HS, y_HS=y_HS, time_max=20)
    

