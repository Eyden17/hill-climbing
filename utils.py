import copy


OBJECT_EMPTY = None
OBJECT_HOUSE = "🏠"
OBJECT_HOSPITAL = "🏥"


MOVE_UP = (0, -1)
MOVE_DOWN = (0, 1)
MOVE_LEFT = (-1, 0)
MOVE_RIGHT = (1, 0)


def is_free_to_move(map, move):
    """
    Check whether a target position is empty and can be moved into.

    Args:
        map: Matrix (list of lists) representing the board.
        move: Position as (x, y), where x is horizontal and y is vertical.

    Returns:
        bool: True if the target cell is empty (None), False otherwise.
    """
    y, x = move
    return True if map[x][y] == None else False


def is_valid_move(map, move):
    """
    Check whether a position is inside the matrix boundaries.

    Args:
        map: Matrix (list of lists) representing the board.
        move: Position as (x, y), where x is horizontal and y is vertical.

    Returns:
        bool: True if the position is within bounds, False otherwise.
    """

    x,y = move
    return True if 0 <= y < len(map) and 0 <= x < len(map[0]) else False


def find_objects(map, target_object_symbol):
    """
    Find all coordinates where a given object symbol appears.

    Args:
        map: Matrix (list of lists) representing the board.
        target_object_symbol: Symbol to search for (None, 🏠, or 🏥).

    Returns:
        list[tuple[int, int]]: All matching coordinates as (x, y).
    """

    coordinates = []

    for y in range(len(map)):
        for x in range(len(map[0])):
            if map[y][x] == target_object_symbol:
                coordinates.append((x, y))

    return coordinates


def result(map, hospital_coordinates, target_move):
    """
    Create and return a new map after moving one hospital to a target position.

    Args:
        map: Matrix (list of lists) representing the board.
        hospital_coordinates: Current hospital position as (x, y).
        target_move: Destination position as (x, y).

    Returns:
        list[list]: A deep-copied map with the move applied.
    """

    new_map = copy.deepcopy(map)
    hospital_x, hospital_y = hospital_coordinates
    target_x, target_y = target_move
    new_map[target_y][target_x] = OBJECT_HOSPITAL
    new_map[hospital_y][hospital_x] = OBJECT_EMPTY
    return new_map

def manhattan(pos, pos_2):
    """
    Compute the Manhattan distance between two coordinates.

    Args:
        pos: First coordinate as (x, y).
        pos_2: Second coordinate as (x, y).

    Returns:
        int: Distance computed as abs(x2 - x1) + abs(y2 - y1).
    """
    return abs(pos[0] - pos_2[0]) + abs(pos[1] - pos_2[1])

    raise NotImplementedError("manhattan is not implemented yet")


def cost(map):
    """
    Compute total cost as the sum of distances from each hospital to each house.

    Args:
        map: Matrix (list of lists) representing the board.

    Returns:
        int: Total Manhattan-distance cost.
    """

    hospitals = find_objects(map, OBJECT_HOSPITAL)
    houses = find_objects(map, OBJECT_HOUSE)

    total_cost = 0
    for hospital in hospitals:
        for house in houses:
            total_cost += manhattan(hospital, house)

    return total_cost


def move(pos, pos_2):
    """
    Add two coordinates component-wise.

    Args:
        pos: First coordinate as (x, y).
        pos_2: Second coordinate as (x, y).

    Returns:
        tuple[int, int]: New coordinate as (x1 + x2, y1 + y2).
    """



    return (pos[0] + pos_2[0], pos[1] + pos_2[1])


def actions(map, hospital_position):
    """
    Return all valid adjacent moves for a hospital in up, down, left, right order.

    Args:
        map: Matrix (list of lists) representing the board.
        hospital_position: Hospital coordinate as (x, y).

    Returns:
        list[tuple[int, int]]: Valid neighboring positions that are in bounds and free.
    """

    x, y = hospital_position
    adjacent_positions = [(x, y - 1), (x, y + 1), (x - 1, y), (x + 1, y)]

    valid_actions = []
    for pos in adjacent_positions:
        if is_valid_move(map, pos) and is_free_to_move(map, pos):
            valid_actions.append(pos)

    return valid_actions
