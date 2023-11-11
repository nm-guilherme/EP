import gurobipy as gp
from gurobipy import GRB
from get_cargo_sets import *
from stowing_classes import Cargo, Ship
# gp.setParam("LogToConsole", 0)

class MathematicalModel():
    def __init__(self, cargos_id_list: list[str]) -> None:
        self.m = gp.Model("Modelo")
        self.C_AUX = get_C_AUX(cargos_id_list)
        self.add_variables()
        self.add_area_constrains()
        self.add_cargos_constrains()
        self.m.setObjective(gp.quicksum(self.z_cargos[i] for i in cargos_id_list), GRB.MAXIMIZE)
        
    def solve_model(self):
        self.m.optimize()

    def add_variables(self, ship: Ship, cargos: list[Cargo], cargos_id_list: list[str]) -> None:
        m = self.m
        self.z_cargos = m.addVars(cargos_id_list, vtype=GRB.BINARY) #cargas alocadas
        self.r_cargos = m.addVars(cargos_id_list, vtype=GRB.BINARY) #rotacionada
        self.x_cargos = m.addVars(cargos_id_list, vtype=GRB.CONTINUOUS, lb=0.0) #posicao x
        self.y_cargos = m.addVars(cargos_id_list, vtype=GRB.CONTINUOUS, lb=0.0) #posicao y
        self.z_areas = m.addVars(ship.areas_id, vtype=GRB.BINARY) #areas alocadas
        self.w_areas = m.addVars(ship.areas_id, vtype=GRB.CONTINUOUS, lb=0.0) #largura
        self.h_areas = m.addVars(ship.areas_id, vtype=GRB.CONTINUOUS, lb=0.0) #altura
        self.x_areas = m.addVars(ship.areas_id, vtype=GRB.CONTINUOUS, lb=0.0) #posicao x
        self.y_areas = m.addVars(ship.areas_id, vtype=GRB.CONTINUOUS, lb=0.0) #posicao y
        
        self.a, self.b, self.c, self.d = {}, {}, {}, {}
        for cargo_i in cargos:
            for cargo_j in cargos:
                if cargo_j.cargo_id > cargo_i.cargo_id:
                    self.a[cargo_i.cargo_id, cargo_j.cargo_id] = m.addVar(vtype=GRB.BINARY)
                    self.b[cargo_i.cargo_id, cargo_j.cargo_id] = m.addVar(vtype=GRB.BINARY)
                    self.c[cargo_i.cargo_id, cargo_j.cargo_id] = m.addVar(vtype=GRB.BINARY)
                    self.d[cargo_i.cargo_id, cargo_j.cargo_id] = m.addVar(vtype=GRB.BINARY)	

        self.a_areas, self.b_areas, self.c_areas, self.d_areas = {}, {}, {}, {}
        for area_i in ship.areas_id:
            for area_j in ship.areas_id:
                if area_j > area_i:
                    self.a_areas[area_i, area_j] = m.addVar(vtype=GRB.BINARY)
                    self.b_areas[area_i, area_j] = m.addVar(vtype=GRB.BINARY)
                    self.c_areas[area_i, area_j] = m.addVar(vtype=GRB.BINARY)
                    self.d_areas[area_i, area_j] = m.addVar(vtype=GRB.BINARY)

    def add_area_constrains(self, ship: Ship):
        m = self.m
        #area width and height
        m.addConstrs((self.x_areas[idx]+ self.w_areas[idx] <= self.z_areas[idx]*ship.W for idx in ship.areas_id), name="area_width")
        m.addConstrs((self.y_areas[idx]+ self.h_areas[idx] <= self.z_areas[idx]*ship.H for idx in ship.areas_id), name="area_height")

        for k in ship.areas_id:
            if k==0:
                m.addConstr(self.x_areas[k] >= 0.35*ship.W, name="x_area_min")
                m.addConstr(self.x_areas[k] <= 0.36*ship.W, name="x_area_max")
                m.addConstr(self.y_areas[k] == 0, name="y_area0")

                m.addConstr(self.w_areas[k] == ship.W_CORREDOR, name="w_area0")
                m.addConstr(self.h_areas[k] == ship.H, name="h_area0")
                m.addConstr(self.z_areas[k] == 1, name="z_area0")
            if ship.areas[k] == ship.dangerous_area:
                m.addConstr(self.h_areas[k] <= ship.H_DG, name="h_area_dg")
                m.addConstr(self.y_areas[k] == 0 , name="y_area_dg")

            for l in ship.areas_id:
                if k<l:
                    m.addConstr(self.a_areas[k, l] <= (1/2)*(self.z_areas[k] + self.z_areas[l]), name="a_area")
                    m.addConstr(self.b_areas[k, l] <= (1/2)*(self.z_areas[k] + self.z_areas[l]), name="b_area")
                    m.addConstr(self.c_areas[k, l] <= (1/2)*(self.z_areas[k] + self.z_areas[l]), name="c_area")
                    m.addConstr(self.d_areas[k, l] <= (1/2)*(self.z_areas[k] + self.z_areas[l]), name="d_area")
                    m.addConstr(self.a_areas[k, l] + self.b_areas[k, l] + self.c_areas[k, l] + self.d_areas[k, l] <= 1, name="area_exclusivity")
                    m.addConstr(self.a_areas[k, l] + self.b_areas[k, l] + self.c_areas[k, l] + self.d_areas[k, l] >= self.z_areas[k]+self.z_areas[l]+1, name="area_exclusivity")
                    m.addConstr(self.x_areas[k] + self.w_areas[k] <= self.x_areas[l] + (1-self.a_areas[k, l])*ship.W, name="width_a")
                    m.addConstr(self.x_areas[l] + self.w_areas[l] <= self.x_areas[k] + (1-self.b_areas[k, l])*ship.W, name="width_b")
                    m.addConstr(self.y_areas[k] + self.h_areas[k] <= self.y_areas[l] + (1-self.c_areas[k, l])*ship.H, name="height_c")
                    m.addConstr(self.y_areas[l] + self.h_areas[l] <= self.y_areas[k] + (1-self.d_areas[k, l])*ship.H, name="height_d")     
        
    def add_cargos_constrains(self, cargos: list[Cargo], ship: Ship):
        m = self.m

        for i, j in self.C_AUX:
            if i<j:
                m.addConstr(self.a[i, j] <= (1/2)*(self.z_cargos[i] + self.z_cargos[j]), name="a")
                m.addConstr(self.b[i, j] <= (1/2)*(self.z_cargos[i] + self.z_cargos[j]), name="b")
                m.addConstr(self.c[i, j] <= (1/2)*(self.z_cargos[i] + self.z_cargos[j]), name="c")
                m.addConstr(self.d[i, j] <= (1/2)*(self.z_cargos[i] + self.z_cargos[j]), name="d")
                m.addConstr(self.a[i, j] + self.b[i, j] + self.c[i, j] + self.d[i, j] <= 1, name="exclusivity")
                m.addConstr(self.a[i, j] + self.b[i, j] + self.c[i, j] + self.d[i, j] >= self.z_cargos[i]+self.z_cargos[j]+1, name="exclusivity2")

                m.addConstr(self.x_cargos[i] + cargos[i].w*(1-self.r_cargos[i]) +\
                            self.h_cargos[i]*self.r_cargos[i] <= self.x_cargos[j] + ship.W*(1-self.a[i, j]), name="width_a")
                m.addConstr(self.x_cargos[j] + cargos[j].w*(1-self.r_cargos[j]) +\
                            self.h_cargos[j]*self.r_cargos[j] <= self.x_cargos[i] + ship.W*(1-self.b[i, j]), name="width_b")
                m.addConstr(self.y_cargos[i] + cargos[i].h*(1-self.r_cargos[i]) +\
                            self.w_cargos[i]*self.r_cargos[i] <= self.y_cargos[j] + ship.H*(1-self.c[i, j]), name="height_c")
                m.addConstr(self.y_cargos[j] + cargos[j].h*(1-self.r_cargos[j]) +\
                            self.w_cargos[j]*self.r_cargos[j] <= self.y_cargos[i] + ship.H*(1-self.d[i, j]), name="height_d")
                
        for c in cargos:
            if not c.dangerous:
                m.addConstr(self.x_cargos[c.cargo_id] >= self.x_areas[c.area] - ship.W*(1-self.z_cargos[c.cargo_id]), name="x_cargo_area")
                m.addConstr(self.x_cargos[c.cargo_id] + c.w*(1-self.r_cargos[c.cargo_id]) +\
                            c.h*self.r_cargos[c.cargo_id] <= self.x_areas[c.area] + self.w_areas[c.area] - ship.W*(1-self.z_cargos[c.cargo_id]), name="x_cargo_area2")
                m.addConstr(self.y_cargos[c.cargo_id] >= self.y_areas[c.area] - ship.H*(1-self.z_cargos[c.cargo_id]), name="y_cargo_area")
                m.addConstr(self.y_cargos[c.cargo_id] + c.h*(1-self.r_cargos[c.cargo_id]) +\
                            c.w*self.r_cargos[c.cargo_id] <= self.y_areas[c.area] + self.h_areas[c.area] - ship.H*(1-self.z_cargos[c.cargo_id]), name="y_cargo_area2")
                
            if c.urgent:
                m.addConstr(self.z_cargos[c.cargo_id] == 1, name="urgent")

            if c.restricted_area:
                m.addConstr(self.z_cargos[c.area] == 1, name="restricted_area")
                m.addConstr(self.x_cargos[c.cargo_id] == c.x_restricted, name="x_restricted")
                m.addConstr(self.y_cargos[c.cargo_id] == c.y_restricted, name="y_restricted")

        
        C_REF = [c.cargo_id for c in cargos if c.refrigerated]

        m.addConstr(gp.quicksum(self.z_cargos[i] for i in C_REF) <= ship.T, name='128')

