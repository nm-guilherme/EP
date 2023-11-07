import gurobipy as gp
from gurobipy import GRB
from get_cargo_sets import *
from stowing_classes import Cargo, Ship
# gp.setParam("LogToConsole", 0) 

def stage_1(cargos: list[Cargo], ship: Ship, cargos_id_list) -> list[Cargo]:
    m1 = gp.Model("Estágio1")
    z = m1.addVars(cargos_id_list, vtype=GRB.BINARY)
    m1.addConstr(gp.quicksum((c.w*c.h)*z[c.cargo_id] for c in cargos) <= ship.H*ship.W)
    for cargo in cargos:
        if cargo.dangerous or cargo.restricted_area:
            m1.addConstr(z[cargo.cargo_id]==1)
    
    refrigerated_cargos = [c for c in cargos if c.refrigerated]
    m1.addConstr(gp.quicksum(z[c.cargo_id] for c in refrigerated_cargos)<=ship.T)
    
    m1.setObjective(gp.quicksum(z[c.cargo_id]*c.priority for c in cargos), GRB.MAXIMIZE)
    m1.optimize()
    
    optimal_cargos_stage1 = [c for c in cargos if z[c.cargo_id].X == 1]
    for c in optimal_cargos_stage1:
        ship.areas[c.area].area_m2 += c.w*c.h
    return optimal_cargos_stage1

def stage_2(ship: Ship, optimal_cargos_stage1: list[Cargo], time_max: int=60) -> None:
    m2 = gp.Model("Estágio2")
    m2.setParam(GRB.Param.TimeLimit, time_max)
    m2.setParam(GRB.Param.NonConvex, 2)
    BETA= 1.5*ship.H/ship.W if ship.H/ship.W>ship.W/ship.H else 1.5*ship.W/ship.H

    w_areas = m2.addVars(ship.areas_id, vtype=GRB.CONTINUOUS, lb=0.0, name='w')
    h_areas = m2.addVars(ship.areas_id, vtype=GRB.CONTINUOUS, lb=0.0, name='h')
    x_areas = m2.addVars(ship.areas_id, vtype=GRB.CONTINUOUS, lb=0.0, name='x')
    y_areas = m2.addVars(ship.areas_id, vtype=GRB.CONTINUOUS, lb=0.0, name='y')

    a_kl_areas = m2.addVars(ship.areas_id, ship.areas_id, vtype=GRB.BINARY, name='a')
    b_kl_areas = m2.addVars(ship.areas_id, ship.areas_id, vtype=GRB.BINARY, name='b')
    c_kl_areas = m2.addVars(ship.areas_id, ship.areas_id, vtype=GRB.BINARY, name='c')
    d_kl_areas = m2.addVars(ship.areas_id, ship.areas_id, vtype=GRB.BINARY, name='d')

    min_area_carga = {a: 0 for a in ship.areas_id} 
    for k in ship.areas_id:
        for carga in optimal_cargos_stage1:
            if carga.area==k:
                min_area_carga[k]+=carga.w*carga.h
        m2.addConstr(w_areas[k]*h_areas[k]>=min_area_carga[k], name=f"90_{k[-1]}") #(90)

    for k in ship.areas_id:
        for l in ship.areas_id:
            if int(k.split("_")[-1])<int(l.split("_")[-1]):
                m2.addConstr(x_areas[k]+w_areas[k]<=x_areas[l] + ship.W*(1-a_kl_areas[k,l]), name=f"91_{k[-1]},{l[-1]}") #(91)
                m2.addConstr(x_areas[l]+w_areas[l]<=x_areas[k] + ship.W*(1-b_kl_areas[k,l]), name=f"92_{k[-1]},{l[-1]}") #(92)
                m2.addConstr(y_areas[k]+h_areas[k]<=y_areas[l] + ship.H*(1-c_kl_areas[k,l]), name=f"93_{k[-1]},{l[-1]}") #(93)
                m2.addConstr(y_areas[l]+h_areas[l]<=y_areas[k] + ship.H*(1-d_kl_areas[k,l]), name=f"94_{k[-1]},{l[-1]}") #(94)
                m2.addConstr(a_kl_areas[k,l]+b_kl_areas[k,l]+c_kl_areas[k,l]+d_kl_areas[k,l]>=1, name=f"95_{k[-1]},{l[-1]}") #(95)

    for k in ship.areas_id:
        if k != "area_0":
            m2.addConstr(BETA*w_areas[k]-h_areas[k]>=0, name=f'96_{k}') #(96)
            m2.addConstr(BETA*h_areas[k]-w_areas[k]>=0, name=f'97_{k}') #(97)

    # ##CNSTRS DE MIN E MAX
    # m2.addConstrs(w_areas[k]>=w_min_areas[k] for k in ship.areas_id)
    # m2.addConstrs(w_areas[k]<=w_max_areas[k] for k in ship.areas_id)
    # m2.addConstrs(h_areas[k]>=h_min_areas[k] for k in ship.areas_id)
    # m2.addConstrs(h_areas[k]<=h_max_areas[k] for k in ship.areas_id)

    m2.addConstrs((x_areas[k]+w_areas[k]<=ship.W for k in ship.areas_id), name="100")
    m2.addConstrs((y_areas[k]+h_areas[k]<=ship.H for k in ship.areas_id), name="101")

    m2.addConstr(w_areas["area_0"]==ship.W_CORREDOR, name="102")
    m2.addConstr(h_areas["area_0"]==ship.H, name="103")
    m2.addConstr(x_areas["area_0"]>=0.35*ship.W, name="104")
    m2.addConstr(x_areas["area_0"]<=0.65*ship.W, name="105") 

    m2.addConstr(x_areas[ship.dangerous_area]<=ship.H_DG, name="106")
    m2.addConstr(y_areas[ship.dangerous_area]==0, name="107")

    m2.addConstrs((x_areas[k]>=0 for k in ship.areas_id), name="108_x")
    m2.addConstrs((y_areas[k]>=0 for k in ship.areas_id), name="108_y")
    m2.addConstrs((w_areas[k]>=0 for k in ship.areas_id), name="108_w")
    m2.addConstrs((h_areas[k]>=0 for k in ship.areas_id), name="108_h")

    m2.setObjective(gp.quicksum(w_areas[k]*h_areas[k] for k in ship.areas_id)/(ship.W*ship.H), GRB.MAXIMIZE)
    m2.optimize()

    solution_x = m2.getAttr("X", x_areas)
    solution_y = m2.getAttr("X", y_areas)
    solution_w = m2.getAttr("X", w_areas)
    solution_h = m2.getAttr("X", h_areas)

    a_areas = m2.getAttr("X", a_kl_areas)
    b_areas = m2.getAttr("X", b_kl_areas)
    c_areas = m2.getAttr("X", c_kl_areas)
    d_areas = m2.getAttr("X", d_kl_areas)

    for k in ship.areas_id:
        ship.areas[k].x = solution_x[k]
        ship.areas[k].y = solution_y[k]
        ship.areas[k].w = solution_w[k]
        ship.areas[k].h = solution_h[k]

    return a_areas, b_areas, c_areas, d_areas

def stage_3(ship: Ship, optimal_cargos_stage1: list[Cargo], cargos: list[Cargo], 
            x_HS: dict, y_HS: dict, a_areas, b_areas, c_areas, d_areas) -> None:

    m3 = gp.Model("Estágio3")
    m3.setParam(GRB.Param.TimeLimit, 90)
    optimal_cargos_id_list = [c.cargo_id for c in optimal_cargos_stage1]
    z = m3.addVars(optimal_cargos_id_list, vtype=GRB.BINARY, name='z')
    x = m3.addVars(optimal_cargos_id_list, vtype=GRB.CONTINUOUS, name='x')
    y = m3.addVars(optimal_cargos_id_list, vtype=GRB.CONTINUOUS, name='y')

    a = m3.addVars(optimal_cargos_id_list,optimal_cargos_id_list, vtype=GRB.BINARY, name='a')
    b = m3.addVars(optimal_cargos_id_list,optimal_cargos_id_list, vtype=GRB.BINARY, name='b')
    c = m3.addVars(optimal_cargos_id_list,optimal_cargos_id_list, vtype=GRB.BINARY, name='c')
    d = m3.addVars(optimal_cargos_id_list,optimal_cargos_id_list, vtype=GRB.BINARY, name='d')

    w_areas = m3.addVars(ship.areas_id, vtype=GRB.CONTINUOUS, name='w_a')
    h_areas = m3.addVars(ship.areas_id, vtype=GRB.CONTINUOUS, name='h_a')
    x_areas = m3.addVars(ship.areas_id, vtype=GRB.CONTINUOUS, name='x_a')
    y_areas = m3.addVars(ship.areas_id, vtype=GRB.CONTINUOUS, name='y_a')

    C_AUX = get_C_AUX(optimal_cargos_stage1)

    for cargo_i,cargo_j in C_AUX:
        c_i = cargo_i.cargo_id
        c_j = cargo_j.cargo_id
        n_cargo_i = int(c_i.split("_")[-1])
        n_cargo_j = int(c_j.split("_")[-1])
        if n_cargo_i<n_cargo_j:
            m3.addConstr(a[c_i,c_j] <= 0.5*(z[c_i] + z[c_j]))
            m3.addConstr(b[c_i,c_j] <= 0.5*(z[c_i] + z[c_j]))
            m3.addConstr(c[c_i,c_j] <= 0.5*(z[c_i] + z[c_j]))
            m3.addConstr(d[c_i,c_j] <= 0.5*(z[c_i] + z[c_j]))
            
            m3.addConstr(a[c_i,c_j] + b[c_i,c_j] + c[c_i,c_j] + d[c_i,c_j] <= 1)
            m3.addConstr(a[c_i,c_j] + b[c_i,c_j] + c[c_i,c_j] + d[c_i,c_j] >= z[c_i] + z[c_j] - 1)

            m3.addConstr(x[c_i] + cargo_i.w <= x[c_j] + ship.W*(1 - a[c_i,c_j]))
            m3.addConstr(x[c_j] + cargo_j.w <= x[c_i] + ship.W*(1 - b[c_i,c_j]))
            m3.addConstr(y[c_i] + cargo_i.h <= y[c_j] + ship.H*(1 - c[c_i,c_j]))
            m3.addConstr(y[c_j] + cargo_j.h <= y[c_i] + ship.H*(1 - d[c_i,c_j]))

    for cargo_i in optimal_cargos_stage1:
        c_i = cargo_i.cargo_id
        a_i = cargo_i.area
        if not cargo_i.restricted_area:
            m3.addConstr(x[c_i] >= x_areas[a_i] - ship.W*(1-z[c_i]))
            m3.addConstr(x[c_i] + cargo_i.w <= x_areas[a_i] + w_areas[a_i] - ship.W*(1-z[c_i]))
            m3.addConstr(y[c_i] >= y_areas[a_i] - ship.H*(1-z[c_i]))
            m3.addConstr(y[c_i] + cargo_i.h <= y_areas[a_i] + h_areas[a_i] - ship.H*(1-z[c_i]))
        
        if cargo_i.urgent or cargo_i.restricted_area:
            m3.addConstr(z[c_i]==1, name='125')
        
        if cargo_i.restricted_area:
            m3.addConstr(x[c_i]==x_HS[c_i], name='126')
            m3.addConstr(y[c_i]==y_HS[c_i], name='127')

    C_REF = [c.cargo_id for c in optimal_cargos_stage1 if c.refrigerated]

    m3.addConstr(gp.quicksum(z[i] for i in C_REF) <= ship.T, name='128')

    m3.addConstrs((x_areas[k]+w_areas[k]<=ship.W for k in ship.areas_id), name="129")
    m3.addConstrs((y_areas[k]+h_areas[k]<=ship.H for k in ship.areas_id), name="130")

    m3.addConstr(w_areas["area_0"]==ship.W_CORREDOR, name="132")
    m3.addConstr(h_areas["area_0"]==ship.H, name="133")
    m3.addConstr(x_areas["area_0"]>=0.35*ship.W, name="134")
    m3.addConstr(x_areas["area_0"]<=0.65*ship.W, name="135")

    m3.addConstr(h_areas[ship.dangerous_area]<=ship.H_DG, name="136")
    m3.addConstr(y_areas[ship.dangerous_area]==0, name="137")

    # m3.addConstrs((x[i]>=0 for i in optimal_cargos_id_list), name="138_x")
    # m3.addConstrs((y[i]>=0 for i in optimal_cargos_id_list), name="138_y")

    #non-overlapping constraint
    for k in ship.areas_id:
        for l in ship.areas_id:
            if a_areas[k,l]==1:
                m3.addConstr(x_areas[k]+w_areas[k]<=x_areas[l])
            if b_areas[k,l]==1:
                m3.addConstr(x_areas[l]+w_areas[l]<=x_areas[k])
            if c_areas[k,l]==1:
                m3.addConstr(y_areas[k]+h_areas[k]<=y_areas[l])
            if d_areas[k,l]==1:
                m3.addConstr(y_areas[l]+h_areas[l]<=y_areas[k])

    m3.addConstrs((x_areas[k]>=0 for k in ship.areas_id), name="140_x")
    m3.addConstrs((y_areas[k]>=0 for k in ship.areas_id), name="140_y")
    m3.addConstrs((w_areas[k]>=0 for k in ship.areas_id), name="140_w")
    m3.addConstrs((h_areas[k]>=0 for k in ship.areas_id), name="140_h")

    m3.setObjective(gp.quicksum(z[c.cargo_id]*c.priority for c in optimal_cargos_stage1), GRB.MAXIMIZE)
    m3.optimize()

    solution_x = m3.getAttr("X", x)
    solution_y = m3.getAttr("X", y)
    solution_z = m3.getAttr("X", z)

    for c in cargos:
        if c.cargo_id in optimal_cargos_id_list:
            c.x = solution_x[c.cargo_id]
            c.y = solution_y[c.cargo_id]
            c.allocated = True if solution_z[c.cargo_id]==1 else False
            if c.allocated:
                ship.areas[c.area].cargos.append(c)