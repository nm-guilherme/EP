import gurobipy as gp
from gurobipy import GRB
from stevedore import Cargos, Ship

def first_stage(cargo: Cargos, ship: Ship):
    m1 = gp.Model("Estágio1")
    z = m1.addVars(cargo.cargas_id, vtype=GRB.BINARY)
    m1.addConstr(gp.quicksum((cargo.w[i]*cargo.h[i])*z[i] for i in cargo.cargas_id) <= ship.H*ship.W)
    m1.addConstrs(z[i]==1 for i in cargo.urgentes)
    m1.addConstrs(z[i]==1 for i in cargo.espacos_restritos)
    m1.addConstr(gp.quicksum(z[i] for i in cargo.tomadas)<=T)
    m1.setObjective(gp.quicksum(z[i]*cargo.prioridades[i] for i in cargo.cargas_id), GRB.MAXIMIZE)
    m1.optimize()

    C_OTIMO = [i for i in cargo.cargas_id if z[i].X == 1]
    areas = {}
    for i in cargo.cargas_id:
        area_destino = cargo.relacao_carga_area[i]
        if area_destino in areas.keys():
            areas[area_destino] += w[i]*h[i]
        else:
            areas[area_destino] = w[i]*h[i]