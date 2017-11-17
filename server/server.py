#!/usr/bin/env python3

import flask
import os

app = flask.Flask(__name__)
app.secret_key = open('secret_key.txt', 'rb').read()


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

    last_move = {
    }


def check_player():
    if 'player_key' not in flask.session:
        raise IncorrectMove("You haven't joined the game yet")

    player = app.hive.player_keys.get(flask.session['player_key'])

    if not player:
        raise IncorrectMove("Player key is incorrect")

    return player


@app.route('/')
def hello_world():
    data = flask.request.args
    session = flask.session

    if 'player_key' in data:
        session['player_key'] = data['player_key']
        return flask.redirect('/')

    try:
        session['player_key'] = choose_player_key(True)
    except:
        pass

    return flask.render_template('index.html')


@app.route('/action/add', methods=['POST'])
def add():
    data = flask.request.json

    player_color = check_player()

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

    app.hive.last_move = {'action': 'add', 'piece': piece}

    return flask.jsonify(
            piece=piece,
            state=state
    )


@app.route('/action/move', methods=['POST'])
def move():
    data = flask.request.json

    player_color = check_player()

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

    app.hive.last_move = {'action': 'move', 'piece': piece}

    return flask.jsonify(
            piece=piece,
            state=state
    )


@app.route('/moves', methods=['GET'])
def get_moves():
    player_color = check_player()

    if app.hive.last_move.get('player') == player_color:
        return flask.jsonify()

    last_move = app.hive.last_move
    app.hive.last_move = {'player': player_color}

    return flask.jsonify(
            state=app.hive.state,
            **last_move
    )


@app.route('/board', methods=['GET'])
def get_board():
    print('get_board')
    current_player = choose_player_key()

    return flask.jsonify(
        board=app.hive.board,
        state=app.hive.state,
        player_key=current_player,
        player_color=app.hive.player_keys[current_player]
    )


def choose_player_key(can_start=False):
    print('choose_player_key(%s)' % can_start)
    current_player = None

    if 'player_key' in flask.request.args:
        current_player = flask.request.args['player_key']
        print('Got player from args: %s' % current_player)

    if 'player_key' in flask.session:
        current_player = flask.session['player_key']
        print('Got player from session: %s' % current_player)

    print('Player keys: {}'.format(list(app.hive.player_keys.keys())))

    if can_start and current_player not in app.hive.player_keys.keys():
        current_player = generate_player_key()
        flask.session['player_key'] = current_player
        print('Generated new player: %s' % current_player)

    if current_player not in app.hive.player_keys.keys():
        raise IncorrectMove('This player key is invalid')

    app.hive.joined_players.add(app.hive.player_keys[current_player])

    return current_player


def generate_player_key():
    if 'white' not in app.hive.joined_players:
        return app.hive.player_by_color['white']
    elif 'black' not in app.hive.joined_players:
        return app.hive.player_by_color['black']
    else:
        raise IncorrectMove("The game already started, you're late")


@app.route('/.well-known/acme-challenge/<string:challenge>')
def letsencrypt(challenge):
    try:
        return open('.well-known/acme-challenge/' + challenge).read()
    except:
        return ''


if __name__ == '__main__':
    app.hive = Hive()

    context = ('../conf/fullchain.pem', '../conf/privkey.pem')

    app.run('0.0.0.0', debug=True, port=5443, threaded=True, ssl_context=context)
