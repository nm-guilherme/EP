from stowing_classes import Cargo

def get_C_AUX_1(cargo_list: list[Cargo]) -> list[tuple[Cargo, Cargo]]:
    C_AUX_1 = list()
    dangerous_cargos_list = [c for c in cargo_list if c.dangerous]
    for c_i in dangerous_cargos_list:
        for c_j in dangerous_cargos_list:
            if c_i.cargo_id!=c_j.cargo_id:
                C_AUX_1.append((c_i,c_j))
    return C_AUX_1

def get_C_AUX_2(cargo_list: list[Cargo]) -> list[tuple[Cargo, Cargo]]:
    C_AUX_2 = list()
    restricted_cargos_list = [c for c in cargo_list if c.restricted_area]
    for c_i in restricted_cargos_list:
        for c_j in cargo_list:
            if c_i.cargo_id!=c_j.cargo_id and not c_j.restricted_area:
                C_AUX_2.append((c_i,c_j))
    return C_AUX_2

def get_C_AUX_3(cargos_list: list[Cargo]) -> list[tuple[Cargo, Cargo]]:
    C_AUX_3: list[tuple(Cargo, Cargo)] = list()
    normal_cargos_list = [c for c in cargos_list if not c.dangerous and not c.restricted_area]
    for c_i in normal_cargos_list:
        for c_j in normal_cargos_list:
            if c_i.cargo_id!=c_j.cargo_id and c_i.area==c_j.area:
                C_AUX_3.append((c_i,c_j))
    return C_AUX_3

def get_C_AUX(cargos_list: list[Cargo]) -> list[tuple[Cargo, Cargo]]:
    C_AUX: list[tuple(Cargo, Cargo)] = list()
    C_AUX_1 = get_C_AUX_1(cargos_list)
    C_AUX_2 = get_C_AUX_2(cargos_list)
    C_AUX_3 = get_C_AUX_3(cargos_list)
    C_AUX.extend(C_AUX_1)
    C_AUX.extend(C_AUX_2)
    C_AUX.extend(C_AUX_3)
    return list(set(C_AUX))