import requests
_game = None
_gameId = None
_playerIndex = None
_playerId = None
url = 'http://localhost:9080/'
actions1 = ["initial 0 10", "initial 95 85", "move 10"]
actions2 = ["initial 87 77", "initial 39 54", "move 77"]
def get(url):
    r = requests.get(url)
    res = r.json()
    print(res)
    return res
def random_game(playerId):
    global _game, _gameId, _playerIndex
    res = get(url + '/train/random?playerId=' + str(playerId))
    print(res)
    _game = res['result']
    _gameId = _game['id']
    print("Game id: " + str(_gameId))
    _playerIndex = res['playerIndex']
    return res
def join(playerId, gameId):
    global _game, _gameId, _playerIndex
    res = get(url + '/game/play?playerID=' + str(playerId) + '&gameID=' + str(gameId))
    # print("Game id: " + _gameId)
    _playerIndex = res['playerID']
    return res
def run():
    counter = 0
    global _game, _playerIndex, _playerId, _gameId
    if _playerId is "1":
        actions = actions1
    else:
        actions = actions2
    while True:
        move = None
        # After we send an action - we wait for response
        res = do_action(_playerId, _gameId, actions[counter])
        print(actions[counter] + '\n')
        # Other player made their move - we send our move again
        counter = counter + 1
def do_action(playerId, gameId, action):
    return get(url + '/doAction?playerID=' + str(playerId) + '&gameID=' + str(gameId)
        + '&action=' + action)
def main():
    global _playerId, _gameId
    instance = input()
    _gameId = 1
    if instance is "1":
        _playerId = "1"
    elif instance is "2":
        _playerId = "2"
    join(_playerId, _gameId)
    run()
if __name__ == '__main__':
    main()
