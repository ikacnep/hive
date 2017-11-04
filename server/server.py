#!/usr/bin/env python3

import flask

app = flask.Flask(__name__)


class IncorrectMove(Exception):
    def __init__(self, message):
        super(IncorrectMove, self).__init__(message)


@app.errorhandler(IncorrectMove)
def handle_incorrect_move(error):
    response = flask.jsonify({"error_message": str(error)})
    response.status_code = 400
    return response


class Hive:
    board = []
    state = {
            'current_turn': 'white',
            'is_opening_move': True,
            'white': {
                'available_figures': {
                    'ant': 3,
                    'spider': 2,
                    'beetle': 2,
                    'grasshopper': 3,
                    'queen': 1,
                }
            },
            'black': {
                'available_figures': {
                    'ant': 3,
                    'spider': 2,
                    'beetle': 2,
                    'grasshopper': 3,
                    'queen': 1,
                }
            }
    }


@app.route('/')
def hello_world():
    return flask.render_template('index.html')


@app.route('/action/add', methods=['POST'])
def add():
    data = flask.request.json

    board = app.hive.board
    state = app.hive.state

    pieces_at_these_coordinates = [piece for piece in board if piece['coordinates'][0:1] == data['coordinates']]

    if pieces_at_these_coordinates:
        raise IncorrectMove("Nope, can't place atop of hive")

    available_figures = state[state['current_turn']]['available_figures']

    if not available_figures[data['figure']]:
        raise IncorrectMove("You don't have any more %s to place" % data['figure'])

    available_figures[data['figure']] = available_figures[data['figure']] - 1

    if len(board) > 1:
        state['is_opening_move'] = False

    piece = {
            'player': state['current_turn'],
            'id': len(board),
            'figure': data['figure'],
            'coordinates': data['coordinates'] + [0]
    }

    board.append(piece)
    board.sort(key=lambda piece: piece['coordinates'][2])
    
    state['current_turn'] = 'white' if state['current_turn'] == 'black' else 'black'

    return flask.jsonify(
            piece=piece,
            state=state
    )


@app.route('/action/move', methods=['POST'])
def move():
    data = flask.request.json

    board = app.hive.board
    state = app.hive.state

    piece = next(piece for piece in app.hive.board if piece['id'] == data['id'])

    piece['coordinates'] = data['coordinates'] + [0]

    pieces_at_these_coordinates = [piece for piece in app.hive.board if piece['coordinates'][0:1] == data['coordinates']]

    if pieces_at_these_coordinates:
        piece['coordinates'][2] = pieces_at_these_coordinates[0][2] + 1

    app.hive.board.sort(key=lambda piece: piece['coordinates'][2])

    state['current_turn'] = 'white' if state['current_turn'] == 'black' else 'black'

    return flask.jsonify(
            piece=piece,
            state=state
    )


@app.route('/board')
def get_board():
    return flask.jsonify(board=app.hive.board, state=app.hive.state)


if __name__ == '__main__':
    app.hive = Hive()
    app.run('0.0.0.0', debug=True)
