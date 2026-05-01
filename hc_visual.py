import utils
import math
import random


def hill_climbing_steps(grid):
    """
    Generator that yields intermediate states for each candidate evaluated
    during Hill Climbing.

    Each yielded dict has:
        grid          – current map
        current_cost  – cost of the current map
        hospital      – hospital being evaluated
        candidate_move– move being evaluated
        candidate_map – resulting map from that move
        candidate_cost– cost of the candidate map
        best_map      – best map found in this outer iteration
        best_cost     – best cost found in this outer iteration
        accepted      – whether this candidate became the new best
        done          – True only on the final yield
        message       – human-readable description
    """
    current_map = grid
    current_cost = utils.cost(current_map)

    while True:
        best_map = current_map
        best_cost = current_cost
        improved = False

        for hospital in utils.find_objects(current_map, utils.OBJECT_HOSPITAL):
            for candidate_move in utils.actions(current_map, hospital):
                candidate_map = utils.result(current_map, hospital, candidate_move)
                candidate_cost = utils.cost(candidate_map)
                accepted = candidate_cost < best_cost

                if accepted:
                    best_map = candidate_map
                    best_cost = candidate_cost
                    improved = True

                yield {
                    "grid": current_map,
                    "current_cost": current_cost,
                    "hospital": hospital,
                    "candidate_move": candidate_move,
                    "candidate_map": candidate_map,
                    "candidate_cost": candidate_cost,
                    "best_map": best_map,
                    "best_cost": best_cost,
                    "accepted": accepted,
                    "done": False,
                    "message": (
                        f"✓ Mejor: {candidate_cost} < {best_cost + (best_cost - candidate_cost)}"
                        if accepted
                        else f"✗ Rechazado: {candidate_cost} ≥ {best_cost}"
                    ),
                }

        if improved:
            current_map = best_map
            current_cost = best_cost
        else:
            # No improvement found – local optimum reached
            yield {
                "grid": current_map,
                "current_cost": current_cost,
                "hospital": None,
                "candidate_move": None,
                "candidate_map": current_map,
                "candidate_cost": current_cost,
                "best_map": current_map,
                "best_cost": current_cost,
                "accepted": False,
                "done": True,
                "message": "🏁 Óptimo local encontrado",
            }
            return


def hill_climbing(grid):
    """
    Optimize hospital positions using hill climbing.
    Iteratively moves to the best neighbour until no improvement is possible.

    Args:
        grid: Matrix (list of lists) representing the board.

    Returns:
        list[list]: A map configuration with locally minimised cost.
    """
    # Drive the generator to completion and return the final grid.
    last_state = None
    for state in hill_climbing_steps(grid):
        last_state = state
    return last_state["grid"] if last_state else grid


def simulated_annealing_steps(grid, T_min, T_initial, cooling_rate):
    """
    Generator version of simulated annealing that yields one state per move
    evaluated.
    """
    current_map = grid
    current_cost = utils.cost(current_map)
    temperature = T_initial

    while temperature > T_min:
        movable_hospitals = [
            h for h in utils.find_objects(current_map, utils.OBJECT_HOSPITAL)
            if utils.actions(current_map, h)
        ]

        if not movable_hospitals:
            break

        selected_hospital = random.choice(movable_hospitals)
        possible_moves = utils.actions(current_map, selected_hospital)
        selected_move = random.choice(possible_moves)

        neighbor_solution = utils.result(current_map, selected_hospital, selected_move)
        neighbor_cost = utils.cost(neighbor_solution)
        cost_difference = neighbor_cost - current_cost

        if cost_difference < 0:
            accepted = True
            current_map = neighbor_solution
            current_cost = neighbor_cost
            prob = 1.0
        else:
            prob = math.exp(-cost_difference / temperature)
            accepted = random.random() < prob
            if accepted:
                current_map = neighbor_solution
                current_cost = neighbor_cost

        yield {
            "grid": current_map,
            "current_cost": current_cost,
            "hospital": selected_hospital,
            "candidate_move": selected_move,
            "candidate_map": neighbor_solution,
            "candidate_cost": neighbor_cost,
            "best_map": current_map,
            "best_cost": current_cost,
            "accepted": accepted,
            "done": False,
            "temperature": temperature,
            "acceptance_prob": prob,
            "message": (
                f"✓ Aceptado (mejor)" if cost_difference < 0
                else f"{'✓' if accepted else '✗'} P={prob:.3f} T={temperature:.2f}"
            ),
        }

        temperature *= cooling_rate

    yield {
        "grid": current_map,
        "current_cost": current_cost,
        "hospital": None,
        "candidate_move": None,
        "candidate_map": current_map,
        "candidate_cost": current_cost,
        "best_map": current_map,
        "best_cost": current_cost,
        "accepted": False,
        "done": True,
        "temperature": temperature,
        "acceptance_prob": 0.0,
        "message": "🏁 Temperatura mínima alcanzada",
    }


def simulated_annealing(grid, T_min, T_initial, cooling_rate):
    """
    Optimize hospital positions using simulated annealing.

    Args:
        grid: Matrix (list of lists) representing the board.
        T_min: Minimum temperature at which the search stops.
        T_initial: Starting temperature for the annealing process.
        cooling_rate: Multiplicative factor used to cool the temperature each step.

    Returns:
        list[list]: A grid configuration produced by the annealing search.
    """
    last_state = None
    for state in simulated_annealing_steps(grid, T_min, T_initial, cooling_rate):
        last_state = state
    return last_state["grid"] if last_state else grid
