from stowing_classes import Cargo

def get_C_AUX_1(optimal_cargos_stage1: list[Cargo]) -> list[tuple[Cargo, Cargo]]:
    C_AUX_1 = list()
    optimal_danger_cargos = [c for c in optimal_cargos_stage1 if c.dangerous]
    for c_i in optimal_danger_cargos:
        for c_j in optimal_danger_cargos:
            if c_i.cargo_id!=c_j.cargo_id:
                C_AUX_1.append((c_i,c_j))
    return C_AUX_1

def get_C_AUX_2(optimal_cargos_stage1: list[Cargo]) -> list[tuple[Cargo, Cargo]]:
    C_AUX_2 = list()
    optimal_restricted_cargos = [c for c in optimal_cargos_stage1 if c.restricted_area]
    for c_i in optimal_restricted_cargos:
        for c_j in optimal_cargos_stage1:
            if c_i.cargo_id!=c_j.cargo_id:
                C_AUX_2.append((c_i,c_j))
    return C_AUX_2

def get_C_AUX_3(optimal_cargos_stage1: list[Cargo]) -> list[tuple[Cargo, Cargo]]:
    C_AUX_3: list[tuple(Cargo, Cargo)] = list()
    optimal_cargos_not_special = [c for c in optimal_cargos_stage1 if not c.dangerous and not c.restricted_area]
    for c_i in optimal_cargos_not_special:
        for c_j in optimal_cargos_not_special:
            if c_i.cargo_id!=c_j.cargo_id and c_i.area==c_j.area:
                C_AUX_3.append((c_i,c_j))
    return C_AUX_3

def get_C_AUX(optimal_cargos_stage1: list[Cargo]) -> list[tuple[Cargo, Cargo]]:
    C_AUX: list[tuple(Cargo, Cargo)] = list()
    C_AUX_1 = get_C_AUX_1(optimal_cargos_stage1)
    C_AUX_2 = get_C_AUX_2(optimal_cargos_stage1)
    C_AUX_3 = get_C_AUX_3(optimal_cargos_stage1)
    C_AUX.extend(C_AUX_1)
    C_AUX.extend(C_AUX_2)
    C_AUX.extend(C_AUX_3)
    return C_AUX