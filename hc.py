import utils
import math
import random


def simulated_annealing(grid, T_min, T_initial, cooling_rate):
    """
    Optimize hospital positions using simulated annealing by exploring random moves
    and occasionally accepting worse states to escape local optima.

    Args:
        grid: Matrix (list of lists) representing the board.
        T_min: Minimum temperature at which the search stops.
        T_initial: Starting temperature for the annealing process.
        cooling_rate: Multiplicative factor used to cool the temperature each step.

    Returns:
        list[list]: A map configuration with locally minimized cost.
    """

    current_map = map
    current_cost = utils.cost(current_map)

    while True:
        best_map = current_map
        best_cost = current_cost

        for hospital in utils.find_objects(current_map, utils.OBJECT_HOSPITAL):
            for candidate_move in utils.actions(current_map, hospital):
                candidate_map = utils.result(current_map, hospital, candidate_move)
                candidate_cost = utils.cost(candidate_map)

                if candidate_cost < best_cost:
                    best_map = candidate_map
                    best_cost = candidate_cost

        if best_cost < current_cost:
            current_map = best_map
            current_cost = best_cost
        else:
            break

    return current_map

def simulated_annealing(grid, T_min, T_initial, cooling_rate):
    """
    Optimize hospital positions using simulated annealing by exploring random moves
    and occasionally accepting worse states to escape local optima.

    Args:
        grid: Matrix (list of lists) representing the board.
        T_min: Minimum temperature at which the search stops.
        T_initial: Starting temperature for the annealing process.
        cooling_rate: Multiplicative factor used to cool the temperature each step.

    Returns:
        list[list]: A grid configuration produced by the annealing search.
    """

    # current grid <- grid
    # current cost <- cost of the grid
    # temperature <- initial temperature

    # while temperature is greater than the minimum temperature
    #     movable hospitals <- hospitals that can move

    #     if movable hospitals is empty
    #         stop the process

    #     selected hospital <- a random movable hospital
    #     possible moves <- valid moves for that hospital
    #     selected move <- a random move
    #     neighbor solution <- new grid produced by that move
    #     neighbor cost <- cost of the neighbor solution
    #     cost difference <- neighbor cost - current cost

    #     if the neighbor is better
    #         accept the neighbor as the current solution
    #     otherwise
    #         acceptance probability <- value based on cost difference and temperature

    #         random value <- random number between 0 and 1
    #         if random value is less than the acceptance probability
    #             accept the neighbor as the current solution

    #     temperature <- temperature reduced by the cooling rate
    # return current grid

    current_map = grid
    current_cost = utils.cost(current_map)
    temperature = T_initial

    while temperature > T_min:

        movable_hospitals = []

        hospitals = utils.find_objects(current_map, utils.OBJECT_HOSPITAL)

        for hospital in hospitals:
            if utils.actions(current_map, hospital) != []:
                movable_hospitals.append(hospital)

        if movable_hospitals == []:
            return current_map

        selected_hospital = random.choice(movable_hospitals)
        possible_moves = utils.actions(current_map, selected_hospital)

        selected_move = random.choice(possible_moves)

        neighbor_solution = utils.result(current_map, selected_hospital, selected_move)
        neighbor_cost = utils.cost(neighbor_solution)

        cost_difference = neighbor_cost - current_cost

        if cost_difference < 0:
            current_map = neighbor_solution
            current_cost = neighbor_cost
        else:
            acceptance_probability = math.exp(-cost_difference / temperature)

            if (random.random() < acceptance_probability):
                current_map = neighbor_solution
                current_cost = neighbor_cost
        temperature *= cooling_rate
    return current_map
