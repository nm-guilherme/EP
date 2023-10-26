import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

class Cargo():
    def __init__(self, cargo_id, n_destinations, input_row) -> None:
        self.cargo_id = cargo_id
        self.allocated = False
        self.x: float = None
        self.y: float = None
        self.w: float = input_row['w']
        self.h: float = input_row['l']
        self.dangerous: bool = True if input_row['carga perigosa']==1 else False
        self.urgent: bool = True if input_row['urgente']==1 else False
        self.refrigerated: bool = True if input_row['refrigerado']==1 else False
        self.restricted_area: bool = True if input_row['área mangote']==1 else False
        self.priority: int = input_row['prioridade']
        self.destination = int(input_row['destino'])
        self.set_area(n_destinations)
    def set_area(self, n_destinations):
        if self.dangerous:
            self.area = "area_" + str(int(n_destinations))
        elif self.restricted_area:
            self.area = "area_0"
        else:
            self.area = "area_" + str(self.destination)

class Area():
    def __init__(self, area_id) -> None:
        self.area_id = area_id
        self.x: float = 0
        self.y: float = 0
        self._w: float = 0
        self._h: float = 0
        self.area_m2: float = 0
        self.cargos: list[Cargo] = list()
        self.color: str = None
        self.label: str = None

    @property
    def w(self):
        return self._w
    @w.setter
    def w(self, value):
        self._w = value
        self._update_area_m2()
    @property
    def h(self):
        return self._h
    @h.setter
    def h(self, value):
        self._h = value
        self._update_area_m2()
    def _update_area_m2(self):
        self.area_m2 = self._w * self._h

class Ship():
    def __init__(self, H, H_DG, W, T, W_CORREDOR):
        self.H = H
        self.H_DG = H_DG
        self.W = W
        self.T = T
        self.W_CORREDOR = W_CORREDOR
    def set_areas(self, areas_id_list, dangerous_area):
        self.dangerous_area = dangerous_area
        self.areas = {area_id: Area(area_id) for area_id in areas_id_list} 
        self.areas_id = areas_id_list
        cmap = plt.get_cmap('tab20c')
        norm = Normalize(vmin=0, vmax=len(areas_id_list))
        for i, area in enumerate(self.areas.values()):
            if area.area_id == self.dangerous_area:
                area.color = 'red'
                area.label = 'DG'
            elif area.area_id == 'area_0':
                area.color = 'grey'
                area.label = '-'
            else:
                area.color = cmap(norm(i))
                area.label = area.area_id.split('_')[-1]
    