import gurobipy as gp
from gurobipy import GRB
from get_cargo_sets import *
from stowing_classes import Cargo, Ship
gp.setParam("LogToConsole", 0)

class MathematicalModel():
    def __init__(self, time_max) -> None:
        self.m = gp.Model("Modelo")
        if time_max:
            self.m.setParam(GRB.Param.TimeLimit, time_max)

    def add_variables(self, ship: Ship, cargos: list[Cargo], cargos_id_list: list[str]) -> None:
        m = self.m
        self.C_AUX = get_C_AUX(cargos)
        self.z_cargos = m.addVars(cargos_id_list, vtype=GRB.BINARY, name="z_cargo") #cargas alocadas
        self.r_cargos = m.addVars(cargos_id_list, vtype=GRB.BINARY, name='r_cargo') #rotacionada
        self.x_cargos = m.addVars(cargos_id_list, vtype=GRB.CONTINUOUS, lb=0.0, name='x_cargo') #posicao x
        self.y_cargos = m.addVars(cargos_id_list, vtype=GRB.CONTINUOUS, lb=0.0, name='y_cargo') #posicao y
        self.z_areas = m.addVars(ship.areas_id, vtype=GRB.BINARY, name='z_area') #areas alocadas
        self.w_areas = m.addVars(ship.areas_id, vtype=GRB.CONTINUOUS, lb=0.0, name='w_area') #largura
        self.h_areas = m.addVars(ship.areas_id, vtype=GRB.CONTINUOUS, lb=0.0, name='h_area') #altura
        self.x_areas = m.addVars(ship.areas_id, vtype=GRB.CONTINUOUS, lb=0.0, name='x_area') #posicao x
        self.y_areas = m.addVars(ship.areas_id, vtype=GRB.CONTINUOUS, lb=0.0, name='y_area') #posicao y
        
        self.a, self.b, self.c, self.d = {}, {}, {}, {}
        for cargo_i in cargos:
            for cargo_j in cargos:
                if cargo_i.cargo_id < cargo_j.cargo_id:
                    self.a[cargo_i.cargo_id, cargo_j.cargo_id] = m.addVar(vtype=GRB.BINARY, name=f'a_{cargo_i.cargo_id}_{cargo_j.cargo_id}')
                    self.b[cargo_i.cargo_id, cargo_j.cargo_id] = m.addVar(vtype=GRB.BINARY, name=f'b_{cargo_i.cargo_id}_{cargo_j.cargo_id}')
                    self.c[cargo_i.cargo_id, cargo_j.cargo_id] = m.addVar(vtype=GRB.BINARY, name=f'c_{cargo_i.cargo_id}_{cargo_j.cargo_id}')
                    self.d[cargo_i.cargo_id, cargo_j.cargo_id] = m.addVar(vtype=GRB.BINARY, name=f'd_{cargo_i.cargo_id}_{cargo_j.cargo_id}')	

        self.a_areas, self.b_areas, self.c_areas, self.d_areas = {}, {}, {}, {}
        for area_i in ship.areas_id:
            for area_j in ship.areas_id:
                if area_i < area_j:
                    self.a_areas[area_i, area_j] = m.addVar(vtype=GRB.BINARY, name=f'a_area_{area_i}_{area_j}')
                    self.b_areas[area_i, area_j] = m.addVar(vtype=GRB.BINARY, name=f'b_area_{area_i}_{area_j}')
                    self.c_areas[area_i, area_j] = m.addVar(vtype=GRB.BINARY, name=f'c_area_{area_i}_{area_j}')
                    self.d_areas[area_i, area_j] = m.addVar(vtype=GRB.BINARY, name=f'd_area_{area_i}_{area_j}')
        self.m.update()

    def add_area_constrains(self, ship: Ship):
        m = self.m
        m.addConstrs((self.x_areas[idx]+ self.w_areas[idx] <= self.z_areas[idx]*ship.W for idx in ship.areas_id), name="area_width")
        m.addConstrs((self.y_areas[idx]+ self.h_areas[idx] <= self.z_areas[idx]*ship.H for idx in ship.areas_id), name="area_height")

        for a in ship.areas:
            k = a.area_id
            if k==0:
                m.addConstr(self.x_areas[k] >= 0.35*ship.W, name="x_area_min_corredor")
                m.addConstr(self.x_areas[k] <= 0.65*ship.W, name="x_area_max_corredor")
                m.addConstr(self.w_areas[k] == ship.W_CORREDOR, name="w_area_corredor")
                m.addConstr(self.h_areas[k] == ship.H, name="h_area_corredor")
                m.addConstr(self.z_areas[k] == 1, name="z_area_corredor")


            if a.area_id == ship.dangerous_area:
                m.addConstr(self.h_areas[k] <= ship.H_DG, name="h_area_dg")
                m.addConstr(self.y_areas[k] == 0 , name="y_area_dg")

            for a2 in ship.areas:
                l = a2.area_id
                if k<l:
                    m.addConstr(self.a_areas[k, l] <= (1/2)*(self.z_areas[k] + self.z_areas[l]), name=f"a_area_{k},{l}")
                    m.addConstr(self.b_areas[k, l] <= (1/2)*(self.z_areas[k] + self.z_areas[l]), name=f"b_area_{k},{l}")
                    m.addConstr(self.c_areas[k, l] <= (1/2)*(self.z_areas[k] + self.z_areas[l]), name=f"c_area_{k},{l}")
                    m.addConstr(self.d_areas[k, l] <= (1/2)*(self.z_areas[k] + self.z_areas[l]), name=f"d_area_{k},{l}")
                    m.addConstr(self.a_areas[k, l] + self.b_areas[k, l] + self.c_areas[k, l] + self.d_areas[k, l] <= 1, name=f"max_relative_position_area_{k},{l}")
                    m.addConstr(self.a_areas[k, l] + self.b_areas[k, l] + self.c_areas[k, l] + self.d_areas[k, l] >= self.z_areas[k]+self.z_areas[l]-1, name=f"min_relative_position_area_{k},{l}")
                    m.addConstr(self.x_areas[k] + self.w_areas[k] <= self.x_areas[l] + (1-self.a_areas[k, l])*ship.W, name=f"width_area_a_{k},{l}")
                    m.addConstr(self.x_areas[l] + self.w_areas[l] <= self.x_areas[k] + (1-self.b_areas[k, l])*ship.W, name=f"width_area_b_{k},{l}")
                    m.addConstr(self.y_areas[k] + self.h_areas[k] <= self.y_areas[l] + (1-self.c_areas[k, l])*ship.H, name=f"height_area_c_{k},{l}")
                    m.addConstr(self.y_areas[l] + self.h_areas[l] <= self.y_areas[k] + (1-self.d_areas[k, l])*ship.H, name=f"height_area_d_{k},{l}")     
        self.m.update()
        
    def add_cargos_constrains(self, cargos: list[Cargo], ship: Ship):
        m = self.m

        for c_i, c_j in self.C_AUX:
            i = c_i.cargo_id
            j = c_j.cargo_id
            if i<j:
                m.addConstr(self.a[i, j] <= (1/2)*(self.z_cargos[i] + self.z_cargos[j]), name=f"a_{i},{j}")
                m.addConstr(self.b[i, j] <= (1/2)*(self.z_cargos[i] + self.z_cargos[j]), name=f"b_{i},{j}")
                m.addConstr(self.c[i, j] <= (1/2)*(self.z_cargos[i] + self.z_cargos[j]), name=f"c_{i},{j}")
                m.addConstr(self.d[i, j] <= (1/2)*(self.z_cargos[i] + self.z_cargos[j]), name=f"d_{i},{j}")
                m.addConstr(self.a[i, j] + self.b[i, j] + self.c[i, j] + self.d[i, j] <= 1, name=f"max_relative_position_cargo_{i},{j}")
                m.addConstr(self.a[i, j] + self.b[i, j] + self.c[i, j] + self.d[i, j] >= self.z_cargos[i]+self.z_cargos[j]-1, name=f"min_relative_position_cargo_{i},{j}")

                m.addConstr(self.x_cargos[i] + c_i.w*(1-self.r_cargos[i]) +\
                            c_i.h*self.r_cargos[i] <= self.x_cargos[j] + ship.W*(1-self.a[i, j]), name=f"width_a_{i},{j}")
                m.addConstr(self.x_cargos[j] + c_j.w*(1-self.r_cargos[j]) +\
                            c_j.h*self.r_cargos[j] <= self.x_cargos[i] + ship.W*(1-self.b[i, j]), name=f"width_b_{i},{j}")
                m.addConstr(self.y_cargos[i] + c_i.h*(1-self.r_cargos[i]) +\
                            c_i.w*self.r_cargos[i] <= self.y_cargos[j] + ship.H*(1-self.c[i, j]), name=f"height_c_{i},{j}")
                m.addConstr(self.y_cargos[j] + c_j.h*(1-self.r_cargos[j]) +\
                            c_j.w*self.r_cargos[j] <= self.y_cargos[i] + ship.H*(1-self.d[i, j]), name=f"height_d_{i},{j}")
                
        for c in cargos:

            if not c.restricted_area:
                m.addConstr(self.z_cargos[c.cargo_id] <= self.z_areas[c.area], name=f"z_cargo_area_{c.cargo_id}")
                m.addConstr(self.x_cargos[c.cargo_id] >= self.x_areas[c.area] - ship.W*(1-self.z_cargos[c.cargo_id]), name=f"x_cargo_area_{c.cargo_id}")
                m.addConstr(self.x_cargos[c.cargo_id] + c.w*(1-self.r_cargos[c.cargo_id]) + c.h*self.r_cargos[c.cargo_id] \
                            <= self.x_areas[c.area] + self.w_areas[c.area] + ship.W*(1-self.z_cargos[c.cargo_id]), name=f"x_cargo_area2_{c.cargo_id}")
                
                m.addConstr(self.y_cargos[c.cargo_id] >= self.y_areas[c.area] - ship.H*(1-self.z_cargos[c.cargo_id]), name=f"y_cargo_area_{c.cargo_id}")
                m.addConstr(self.y_cargos[c.cargo_id] + c.h*(1-self.r_cargos[c.cargo_id]) + c.w*self.r_cargos[c.cargo_id] \
                            <= self.y_areas[c.area] + self.h_areas[c.area] + ship.H*(1-self.z_cargos[c.cargo_id]), name=f"y_cargo_area2_{c.cargo_id}")
                
            if c.urgent:
                m.addConstr(self.z_cargos[c.cargo_id] == 1, name=f"urgent_{c.cargo_id}")

            if c.restricted_area:
                m.addConstr(self.z_cargos[c.cargo_id] == 1, name=f"restricted_cargo_{c.cargo_id}")
                m.addConstr(self.x_cargos[c.cargo_id] == c.x, name=f"x_restricted_{c.cargo_id}")
                m.addConstr(self.y_cargos[c.cargo_id] == c.y, name=f"y_restricted_{c.cargo_id}")
                
        C_REF = [c.cargo_id for c in cargos if c.refrigerated]
        m.addConstr(gp.quicksum(self.z_cargos[i] for i in C_REF) <= ship.T, name='refrigerated')
        self.m.update()

    def solve_model(self, cargos_id_list: list[str]):
        self.m.setObjective(gp.quicksum(self.z_cargos[i] for i in cargos_id_list), GRB.MAXIMIZE)
        self.m.optimize()
        print(f"Status: {self.m.status}")
        self.m.write("model.lp")

    def get_results(self, cargos: list[Cargo], ship: Ship):
        for cargo in cargos:
            if self.z_cargos[cargo.cargo_id].X == 1:
                cargo.allocated = True
                cargo.x = self.x_cargos[cargo.cargo_id].X
                cargo.y = self.y_cargos[cargo.cargo_id].X
                cargo.rotated = self.r_cargos[cargo.cargo_id].X
        for area in ship.areas:
            area.x = self.x_areas[area.area_id].X
            area.y = self.y_areas[area.area_id].X
            area.w = self.w_areas[area.area_id].X
            area.h = self.h_areas[area.area_id].X
            area.cargos = [c for c in cargos if self.z_cargos[c.cargo_id].X == 1 and c.area == area.area_id]
        return cargos, ship