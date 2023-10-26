import gurobipy as gp
from gurobipy import GRB

def second_stage():
    m2 = gp.Model("Estágio2")
    m2.setParam(GRB.Param.TimeLimit, 20)
    m2.setParam(GRB.Param.NonConvex, 2)
    BETA= 1.5*H/W if H/W>W/H else 1.5*W/H
    H_DG = 4

    w_areas = m2.addVars(areas.keys(), vtype=GRB.CONTINUOUS, name='w')
    h_areas = m2.addVars(areas.keys(), vtype=GRB.CONTINUOUS, name='h')

    x_areas = m2.addVars(areas.keys(), vtype=GRB.CONTINUOUS, name='x')
    y_areas = m2.addVars(areas.keys(), vtype=GRB.CONTINUOUS, name='y')

    a_kl_areas = m2.addVars(areas.keys(), areas.keys(), vtype=GRB.BINARY, name='a')
    b_kl_areas = m2.addVars(areas.keys(), areas.keys(), vtype=GRB.BINARY, name='b')
    c_kl_areas = m2.addVars(areas.keys(), areas.keys(), vtype=GRB.BINARY, name='c')
    d_kl_areas = m2.addVars(areas.keys(), areas.keys(), vtype=GRB.BINARY, name='d')
        
    min_area_carga = {}
    for k in areas.keys():
        min_area_carga[k]=0    
        for carga in C_OTIMO:
            if relacao_carga_area[carga]==k:
                min_area_carga[k]+=w[carga]*h[carga]
        m2.addConstr(w_areas[k]*h_areas[k]>=min_area_carga[k], name=f"90_{k[-1]}") #(90)

    for k in areas.keys():
        for l in areas.keys():
            if int(k.split("_")[-1])<int(l.split("_")[-1]):
                m2.addConstr(x_areas[k]+w_areas[k]<=x_areas[l] + W*(1-a_kl_areas[k,l]), name=f"91_{k[-1]},{l[-1]}") #(91)
                m2.addConstr(x_areas[l]+w_areas[l]<=x_areas[k] + W*(1-b_kl_areas[k,l]), name=f"92_{k[-1]},{l[-1]}") #(92)
                m2.addConstr(y_areas[k]+h_areas[k]<=y_areas[l] + H*(1-c_kl_areas[k,l]), name=f"93_{k[-1]},{l[-1]}") #(93)
                m2.addConstr(y_areas[l]+h_areas[l]<=y_areas[k] + H*(1-d_kl_areas[k,l]), name=f"94_{k[-1]},{l[-1]}") #(94)
                m2.addConstr(a_kl_areas[k,l]+b_kl_areas[k,l]+c_kl_areas[k,l]+d_kl_areas[k,l]>=1, name=f"95_{k[-1]},{l[-1]}") #(95)

    for k in areas.keys():
        if k != "area_0":
            m2.addConstr(BETA*w_areas[k]-h_areas[k]>=0, name=f'96_{k}') #(96)
            m2.addConstr(BETA*h_areas[k]-w_areas[k]>=0, name=f'97_{k}') #(97)
    ##CNSTRS DE MIN E MAX
    m2.addConstrs(w_areas[k]>=w_min_areas[k] for k in areas.keys())
    m2.addConstrs(w_areas[k]<=w_max_areas[k] for k in areas.keys())
    m2.addConstrs(h_areas[k]>=h_min_areas[k] for k in areas.keys())
    m2.addConstrs(h_areas[k]<=h_max_areas[k] for k in areas.keys())

    m2.addConstrs((x_areas[k]+w_areas[k]<=W for k in areas.keys()), name="100") #(100)
    m2.addConstrs((y_areas[k]+h_areas[k]<=H for k in areas.keys()), name="101") #(101)

    m2.addConstr(w_areas["area_0"]==W_CORREDOR, name="102") #(102)
    m2.addConstr(h_areas["area_0"]==H, name="103") #(103)
    m2.addConstr(x_areas["area_0"]>=0.35*W, name="104") #(104)
    m2.addConstr(x_areas["area_0"]<=0.65*W, name="105") #(105)

    m2.addConstr(x_areas[area_dg]<=H_DG, name="106")
    m2.addConstr(y_areas[area_dg]==0, name="107")

    m2.addConstrs((x_areas[k]>=0 for k in areas.keys()), name="108_x")
    m2.addConstrs((y_areas[k]>=0 for k in areas.keys()), name="108_y")
    m2.addConstrs((w_areas[k]>=0 for k in areas.keys()), name="108_w")
    m2.addConstrs((h_areas[k]>=0 for k in areas.keys()), name="108_h")

    m2.setObjective(gp.quicksum(w_areas[k]*h_areas[k] for k in areas.keys())/(W*H), GRB.MAXIMIZE)
    m2.optimize()
    solution_x = m2.getAttr("X", x_areas)
    solution_y = m2.getAttr("X", y_areas)
    solution_w = m2.getAttr("X", w_areas)
    solution_h = m2.getAttr("X", h_areas)