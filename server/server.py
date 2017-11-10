#!/usr/bin/env python3

import flask
import os

app = flask.Flask(__name__)


class IncorrectMove(Exception):
    def __init__(self, message):
        super(IncorrectMove, self).__init__(message)


@app.errorhandler(IncorrectMove)
def handle_incorrect_move(error):
    response = flask.jsonify({"error_message": str(error)})
    response.status_code = 400
    return response


def random_string():
    return os.urandom(10).hex()


class Hive:
    joined_players = set()
    player_keys = {
        random_string(): 'white',
        random_string(): 'black'
    }
    player_by_color = {
        value: key for key, value in player_keys.items()
    }

    all_figures = {
            'queen': 1,
            'ant': 3,
            'spider': 2,
            'beetle': 2,
            'grasshopper': 3,
            'mosquito': 1,
            'ladybug': 1,
            'pillbug': 1
    }

    board = []
    state = {
            'current_turn': 'white',
            'is_opening_move': True,
            'white': {
                'available_figures': all_figures.copy()
            },
            'black': {
                'available_figures': all_figures.copy()
            }
    }


def check_player(data):
    if 'player_key' not in data:
        raise IncorrectMove('Player key not supplied')

    player = app.hive.player_keys.get(data['player_key'])

    if not player:
        raise IncorrectMove("Player key is incorrect")

    return player


@app.route('/')
def hello_world():
    return flask.render_template('index.html')


@app.route('/action/add', methods=['POST'])
def add():
    data = flask.request.json

    player_color = check_player(data)

    board = app.hive.board
    state = app.hive.state

    if player_color != state['current_turn']:
        raise IncorrectMove("Hey, that's not your turn!")

    pieces_at_these_coordinates = [piece for piece in board if piece['coordinates'][0:2] == data['coordinates'][0:2]]

    if pieces_at_these_coordinates:
        raise IncorrectMove("Nope, can't place atop of hive")

    available_figures = state[player_color]['available_figures']

    if not available_figures[data['figure']]:
        raise IncorrectMove("You don't have any more %s to place" % data['figure'])

    available_figures[data['figure']] = available_figures[data['figure']] - 1

    if len(board) > 1:
        state['is_opening_move'] = False

    piece = {
            'player': player_color,
            'id': len(board),
            'figure': data['figure'],
            'coordinates': data['coordinates'] + [0]
    }

    board.append(piece)
    board.sort(key=lambda piece: -piece['coordinates'][2])
    
    state['current_turn'] = 'white' if player_color == 'black' else 'black'

    return flask.jsonify(
            piece=piece,
            state=state
    )


@app.route('/action/move', methods=['POST'])
def move():
    data = flask.request.json

    player_color = check_player(data)

    state = app.hive.state

    if player_color != state['current_turn']:
        raise IncorrectMove("Hey, that's not your turn!")

    piece = next(piece for piece in app.hive.board if piece['id'] == data['id'])

    if piece['coordinates'][0:2] == data['coordinates'][0:2]:
        raise IncorrectMove('You cannot enter the same river twice')

    try:
        top_piece_at_these_coordinates = next(p for p in app.hive.board if p['coordinates'][0:2] == data['coordinates'][0:2])
    except StopIteration:
        top_piece_at_these_coordinates = None

    piece['coordinates'] = data['coordinates'] + [0]

    if top_piece_at_these_coordinates:
        piece['coordinates'][2] = top_piece_at_these_coordinates['coordinates'][2] + 1

    app.hive.board.sort(key=lambda piece: -piece['coordinates'][2])

    state['current_turn'] = 'white' if state['current_turn'] == 'black' else 'black'

    return flask.jsonify(
            piece=piece,
            state=state
    )


@app.route('/board', methods=['GET'])
def get_board():
    data = flask.request.args
    print('request data', data)

    if 'player_key' in data:
        current_player = data['player_key']
    else:
        # TODO: raise IncorrectMove("You can't join a game like THAT")

        if 'white' not in app.hive.joined_players:
            current_player = app.hive.player_by_color['white']
        elif 'black' not in app.hive.joined_players:
            current_player = app.hive.player_by_color['black']
        else:
            raise IncorrectMove("The game already started, you're late")

    if current_player not in app.hive.player_keys.keys():
        raise IncorrectMove('This player key is invalid')

    app.hive.joined_players.add(app.hive.player_keys[current_player])

    return flask.jsonify(
        board=app.hive.board,
        state=app.hive.state,
        player_key=current_player,
        player_color=app.hive.player_keys[current_player]
    )


if __name__ == '__main__':
    app.hive = Hive()
    app.run('0.0.0.0', debug=True)
