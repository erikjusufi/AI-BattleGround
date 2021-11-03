import requests

_gameId = None
_playerIndex = None
_playerId = None
url = 'http://localhost:9080/'
roads = {}
intersections = {}
tiles = {}
my_position = None
opponent_position = None
my_resources = {
    'WATER': 0,
    'DUST': 0,
    'SHEEP': 0,
    'WOOD': 0,
    'WHEAT': 0,
    'CLAY': 0,
    'IRON': 0,
}
opponent_resources = {
    'WATER': 0,
    'DUST': 0,
    'SHEEP': 0,
    'WOOD': 0,
    'WHEAT': 0,
    'CLAY': 0,
    'IRON': 0,
}
my_cities = {}
opponent_cities = {}
my_roads = {}
opponent_roads = {}
first = True


def get_resources(intersection):
    resources = {
        'WATER': 0,
        'DUST': 0,
        'SHEEP': 0,
        'WOOD': 0,
        'WHEAT': 0,
        'CLAY': 0,
        'IRON': 0,
    }

    for tile in intersections[intersection]:
        resources[tiles[tile][0]] += tiles[tile][1]

    return resources.values()


def own_cities():
    return my_cities


def get_opponent_cities():
    return opponent_cities


def get_own_resources():
    return my_resources.values()


def get_opponent_cities():
    return opponent_resources.values()


def get_own_roads_length():
    return len(list(my_roads))


def get_opponent_cities():
    return len(list(opponent_roads))


def get(url):
    r = requests.get(url)
    res = r.json()
    return res


def join(playerId, gameId):
    global _gameId, _playerIndex
    res = get(url + '/train/play?playerID=' + str(playerId) + '&gameID=' + str(gameId))
    print(res)
    return res


def update_resources():
    global my_resources, opponent_resources, my_cities, opponent_cities, tiles, intersections

    for intersection, level in my_cities.items():
        for polje in intersections[intersection]:
            my_resources[tiles[polje][0]] += tiles[polje][1] * level

    for intersection, level in opponent_cities.items():
        for polje in intersections[intersection]:
            opponent_resources[tiles[polje][0]] += tiles[polje][1] * level


def run():
    counter = 0
    global _playerIndex, _playerId, _gameId
    actions = ["initial 37 52", "initial 26 40", "move 10", "upgradetown "]
    while True:
        print("my resources:", my_resources)
        print("opponent resources", opponent_resources)
        if counter > 1:
            update_resources()

        move = None
        # After we send an action - we wait for response
        res = do_action(_playerId, _gameId, actions[counter])
        print("my:", actions[counter] + '\n')
        print("opponent:", res['result'] + '\n')

        if first and counter == 0:
            parts = res['result'].split()
            first_res = parts[0] + " " + parts[1] + " " + parts[2]
            second_res = parts[3] + " " + parts[4] + " " + parts[5]

            update(first_res, 2)
            update(second_res, 2)
            update_resources()
        if first and counter > 1:
            update(res['result'], 2)
        print("counter:", counter, ", first:", first)
        if (not first) and counter == 1:
            print("++++++++++++++++++++++++")
            parts = res['result'].split()
            first_res = parts[0] + " " + parts[1] + " " + parts[2]

            second_res = ""

            for i in range(3, len(parts)):
                second_res += parts[i] + " "

            second_res = second_res[:-1]

            update(first_res, 2)
            update_resources()
            update(second_res, 2)

        if not first and counter > 1:
            update(res['result'], 2)

        # Other player made their move - we send our move again

        print(possible_moves(1, my_position, roads, intersections, my_resources, my_cities, opponent_cities))

        counter = counter + 1


def build_town(intersection, playerId):
    intersection = int(intersection)
    global _playerId, cities, opponent_cities

    if _playerId == playerId:
        my_cities[intersection] = 1

    else:
        opponent_cities[intersection] = 1


def upgrade_town(intersection, playerId):
    global _playerId

    if _playerId == playerId:
        my_cities[intersection] = 2
    else:
        opponent_cities[intersection] = 2


def build_road(intersection1, intersection2, playerId):
    global _playerId, my_roads, opponent_roads

    intersection1 = int(intersection1)
    intersection2 = int(intersection2)
    playerId = int(playerId)
    roads[intersection1][intersection2] = playerId
    roads[intersection2][intersection1] = playerId

    my_roads[(intersection1, intersection2)] = playerId
    my_roads[(intersection2, intersection1)] = playerId


def update(action, playerId):
    global _playerId, _gameId, roads, intersections, tiles, my_position, opponent_position, roads
    if action.startswith("initial"):
        params = action.split()
        intersection1 = int(params[1])
        intersection2 = int(params[2])
        build_town(intersection1, playerId)
        build_road(intersection1, intersection2, playerId)

        if _playerId == playerId:
            if my_position is None:
                my_position = intersection1
        else:
            if opponent_position is None:
                opponent_position = intersection1

    if action.startswith("move"):
        params = action.split()

        if _playerId == playerId:
            if int(params[1]) not in roads[my_position] or roads[my_position][int(params[1])] != playerId:
                my_resources['SHEEP'] -= 50
                my_resources['WHEAT'] -= 50

            my_position = int(params[1])
        else:
            if roads[opponent_position][int(params[1])] != playerId:
                opponent_resources['SHEEP'] -= 50
                opponent_resources['WHEAT'] -= 50
            opponent_position = int(params[1])

    if action.startswith("buildroad"):
        params = action.split()
        intersection2 = int(params[1])

        if _playerId == playerId:
            my_resources['WOOD'] -= 100
            my_resources['CLAY'] -= 100
            build_road(my_position, intersection2, playerId)
        else:
            opponent_resources['WOOD'] -= 100
            opponent_resources['CLAY'] -= 100
            build_road(opponent_position, intersection2, playerId)

    if action.startswith("buildtown"):
        if _playerId == playerId:
            my_resources['SHEEP'] -= 100
            my_resources['WOOD'] -= 100
            my_resources['WHEAT'] -= 100
            my_resources['CLAY'] -= 100
            build_town(my_position, playerId)
        else:
            opponent_resources['SHEEP'] -= 100
            opponent_resources['WOOD'] -= 100
            opponent_resources['WHEAT'] -= 100
            opponent_resources['CLAY'] -= 100
            build_town(opponent_position, playerId)

    if action.startswith("upgradetown"):
        params = action.split()
        intersection1 = int(params[1])
        if _playerId == playerId:
            my_resources['WHEAT'] -= 200
            my_resources['IRON'] -= 300
        else:
            opponent_resources['WHEAT'] -= 200
            opponent_resources['IRON'] -= 300
        upgrade_town(intersection1, playerId)


def do_action(playerId, gameId, action):
    update(action, 1)
    return get(url + '/train/doAction?playerID=' + str(playerId) + '&gameID=' + str(gameId) + '&action=' + action)


def can_do_action(playerId, gameId, action):
    return get(url + '/train/canAction?playerID=' + str(playerId) + '&gameID=' + str(gameId) + '&action=' + action)


def possible_moves(playerId, position, roads, intersections, resources, my_cities, opponent_cities):
    moves = []

    for move in possible_move_moves(playerId, position, roads, resources):
        moves.append(move)
    for move in possible_buildroad_moves(playerId, position, roads, intersections, resources, opponent_cities):
        moves.append(move)
    for move in possible_buildtown_moves(playerId, position, roads, resources, my_cities, opponent_cities):
        moves.append(move)
    for move in possible_upgradetown_moves(playerId, my_cities):
        moves.append(move)

    moves.append("empty")

    return moves


def possible_move_moves(playerId, position, roads, resources):
    moves = []
    possible_intersections = roads[position]
    for intersection, ownership in possible_intersections.items():
        if intersection in roads[position] and roads[position][intersection] == playerId or resources['SHEEP'] >= 50 and \
                resources['WHEAT'] >= 50:
            moves.append("move " + str(intersection))

    return moves


def possible_buildroad_moves(playerId, position, roads, intersections, resources, opponent_cities):
    moves = []

    if resources['WOOD'] < 100 and resources['CLAY'] <= 100:
        return []

    # ako su 2 protivnikove ceste iz trenutnog raskrizja
    num_opponent_roads = 0
    possible_intersections = roads[position]
    for intersection, ownership in possible_intersections.items():
        if intersection in roads[position] and roads[position][intersection] != 0 and roads[position][
            intersection] != playerId:
            num_opponent_roads += 1

    if num_opponent_roads > 1:
        return []

    can_build = False

    # jel ima barem jedna nasa cesta u raskrizju
    possible_intersections = roads[position]
    for intersection, ownership in possible_intersections.items():
        if intersection in roads[position] and roads[position][intersection] == playerId:
            can_build = True

    if not can_build:
        # ima li barem jedna nasa u sudjednima od susjeda
        for intersection, ownership in possible_intersections.items():
            for intersection2, ownership2 in possible_intersections.items():
                if intersection in roads[position] and roads[intersection][intersection2] == playerId and \
                        roads[position][intersection] == 0:
                    if intersection in list(opponent_cities.keys()):
                        break

                    same = []
                    tiles1 = intersections[position]
                    tiles2 = intersections[position]

                    for t in tiles1:
                        if t in tiles2:
                            same.append(t)

                    for t in same:
                        if tiles[t][type] != 'WATER':
                            moves.append("buildroad " + str(intersection))
                            break

    else:
        for intersection, ownership in possible_intersections.items():
            if intersection in roads[position] and roads[position][intersection] == 0:
                curr_can_build = False

                for intersection2, ownership2 in possible_intersections.items():
                    if intersection2 != position and (
                            roads[intersection][intersection2] == playerId or roads[position][intersection] == 0):
                        curr_can_build = True

                if curr_can_build:
                    break

                if intersection in list(opponent_cities.keys()):
                    break

                same = []
                tiles1 = intersections[position]
                tiles2 = intersections[position]

                for t in tiles1:
                    if t in tiles2:
                        same.append(t)

                for t in same:
                    if tiles[t][type] != 'WATER':
                        moves.append("buildroad " + str(intersection))
                        break

    return moves


def possible_buildtown_moves(playerId, position, roads, resources, my_cities, opponent_cities):
    num_opponent_roads = 0
    possible_intersections = roads[position]
    for intersection, ownership in possible_intersections.items():
        if intersection in roads[position] and roads[position][intersection] != 0 and roads[position][
            intersection] != playerId:
            num_opponent_roads += 1

    if num_opponent_roads > 1:
        return []

    neighbours = list(roads[position].keys())

    can_build = True

    if position in my_cities:
        can_build = False

    for intersection in neighbours:
        if intersection in my_cities.keys() or intersection in opponent_cities.keys():
            can_build = False

    if can_build:
        if resources['SHEEP'] >= 100 and resources['WOOD'] >= 100 and resources['WHEAT'] >= 100 and \
                resources['CLAY'] >= 100:
            return ["buildtown " + str(position)]
        else:
            return []
    else:
        return []


def possible_upgradetown_moves(playerId, my_cities):
    moves = []

    for city, level in my_cities.items():
        if level == 1 and my_resources['IRON'] >= 300 and my_resources['WHEAT'] >= 200:
            moves.append("upgradetown " + str(city))

    return moves


def viable_intersections():
    forbidden = set()
    for city in list(opponent_cities.keys()):
        forbidden.add(city)
        for neighbour in list(roads[city].keys()):
            forbidden.add(neighbour)

    for city in list(my_cities.keys()):
        forbidden.add(city)
        for neighbour in list(roads[city].keys()):
            forbidden.add(neighbour)

    cities = []

    for intersection in list(intersections.keys()):
        if intersection not in forbidden:
            cities.append(intersection)

    return cities


# TODO viable potezi

# roads intersection : [{ intersection1 : ownership1, (intersection2, ownership2)]
# intersections intersection: ((x1, y1), (x2, y2), (x3, y3), level, ownership)
# tiles (x, y): (type, weight)

def main():
    global _playerId, _gameId, roads, intersections, tiles, my_position, opponent_position, resources, my_cities, opponent_cities, my_roads, opponent_roads, first
    _gameId = 1
    _playerId = 1

    json = join(_playerId, _gameId)
    result = json['result']
    indexMap = result['indexMap']

    for i, neighbours in enumerate(indexMap):
        roads[i] = {}

        for neighbour in neighbours:
            roads[i][neighbour] = 0

        if len(roads[i].items()) == 0:
            del roads[i]

    intersectionCoordinates = result['intersectionCoordinates']

    for i, neighbours in enumerate(intersectionCoordinates):
        neigh = []

        for neighbour in neighbours:
            neigh.append((neighbour['x'], neighbour['y']))

        intersections[i] = neigh

    json_tiles = result['map']['tiles']

    for neighbours in json_tiles:
        for tile in neighbours:
            if tile is not None:
                tiles[(tile['x'], tile['y'])] = (tile['resourceType'], tile['resourceWeight'])

    first_action = result['action']
    if first_action is not None:
        update(first_action, 2)

    first = first_action is None

    run()


main()
