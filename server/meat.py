import flask
import os
import traceback

from spine.GamesManipulator import GamesManipulator

app = flask.Flask(__name__)

games_manipulator = GamesManipulator()


class IncorrectMove(Exception):
    def __init__(self, message):
        super(IncorrectMove, self).__init__(message)


@app.errorhandler(IncorrectMove)
def handle_incorrect_move(error):
    response = flask.jsonify({"error_message": str(error)})
    response.status_code = 400
    return response


@app.route('/')
def main_page():
    data = flask.request.args
    session = flask.session

    player = None

    if 'player_id' in session:  # Already logged-in users
        player_id = session['player_id']
        player = games_manipulator.GetPlayer(id=player_id).player
    else:
        if 'telegram_id' in data or 'token' in data:  # opened link from telegram
            find_player = games_manipulator.GetOrCreatePlayer(
                token=data.get('token'),
                telegramId=data.get('telegram_id'),
            )
        else:
            return flask.redirect(flask.url_for('login'))

        player = find_player.player
        player_id = player.id
        session['player_id'] = player_id

    games = games_manipulator.GetGames(players=[player.id])

    return flask.render_template('lobby.html', games=games, player_id=player_id)


@app.route('/login', methods=['GET'])
def login():
    return flask.render_template('login.html')


@app.route('/do_login', methods=['POST'])
def do_login():
    data = flask.request.form

    try:
        login = data.get('login')
        password = data.get('password')

        if not login:
            raise Exception('А логинчик? :(')

        if not password:
            raise Exception('А парольчик? :(')

        player = games_manipulator.GetPlayer(login=login, password=password)

        flask.session['player_id'] = player.player.id
    except Exception as error:
        traceback.print_exc()
        return flask.render_template('login.html', error_message=str(error.args[0]))

    return flask.redirect(flask.url_for('main_page'))


@app.route('/register', methods=['GET'])
def register():
    return flask.render_template('register.html')


@app.route('/do_register', methods=['POST'])
def do_register():
    data = flask.request.form

    try:
        login = data.get('login')
        password = data.get('password')
        confirm = data.get('confirm')

        if not login:
            raise Exception('А логинчик? :(')

        if not password:
            raise Exception('А парольчик? :(')

        if not confirm:
            raise Exception('А подтверждалку? :(')

        if password != confirm:
            raise Exception('Одинаковые пароль и подтверждалку, пожалуйста')

        player = games_manipulator.CreatePlayer(login=login, password=password)

        flask.session['player_id'] = player.player.id
    except Exception as error:
        traceback.print_exc()
        return flask.render_template('register.html', error_message=str(error.args[0]))

    return flask.redirect(flask.url_for('main_page'))


@app.route('/start_game', methods=['GET', 'POST'])
def start_game():
    data = flask.request.values

    player_id = flask.session.get('player_id')
    other_player_id = data['other_player_id']

    player = games_manipulator.GetPlayer(id=player_id).player
    other_player = games_manipulator.GetPlayer(id=other_player_id).player

    game = games_manipulator.CreateGame(player.id, other_player.id, turn=player.id)

    if not game.result:
        raise Exception('something\'s wrong: {}'.format(game.message))

    return flask.redirect(flask.url_for('resume_game', game_id=game.gid))


@app.route('/game/<int:game_id>', methods=['GET'])
def resume_game(game_id):
    return flask.render_template('game.html', game_id=game_id)


def verify_i_play_game(game_id):
    player_id = flask.session.get('player_id')

    if not player_id:
        raise IncorrectMove(r'Залогиньтесь сперва')

    game = games_manipulator.GetGameInst(game_id)

    player_id = int(player_id)

    if player_id not in (game.player0, game.player1):
        raise IncorrectMove('Вы не участвуете в этой игре')

    return game, player_id


def get_player_color(game, player_id=None):
    if player_id is None:
        player_id = int(flask.session['player_id'])

    return 'white' if game.GetPlayer(player_id) == 0 else 'black'


@app.route('/action/add/<int:game_id>', methods=['POST'])
def add(game_id):
    # TODO
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


@app.route('/action/move/<int:game_id>', methods=['POST'])
def move(game_id):
    # TODO
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


@app.route('/moves/<int:game_id>', methods=['GET'])
def get_moves(game_id):
    # TODO
    player_color = check_player()

    if app.hive.last_move.get('player') == player_color:
        return flask.jsonify()

    last_move = app.hive.last_move
    app.hive.last_move = {'player': player_color}

    return flask.jsonify(
            state=app.hive.state,
            **last_move
    )


@app.route('/board/<int:game_id>', methods=['GET'])
def get_board(game_id):
    print('get_board')
    game, player_id = verify_i_play_game(game_id)

    print('State (json): %s' % game.GetState().GetJson())

    return flask.jsonify(
        state=game.GetState().GetJson(),
        player_id=player_id,
        player_color=get_player_color(game, player_id)
    )


@app.route('/.well-known/acme-challenge/<string:challenge>')
def letsencrypt(challenge):
    if '/' in challenge or '..' in challenge:
        return ''

    try:
        return open('.well-known/acme-challenge/' + challenge).read()
    except:
        return ''


def start(tls_cert, tls_key, secret_key):
    try:
        app.secret_key = open(secret_key, 'rb').read()
    except IOError as err:
        print('Cannot read secret key file: %s, will use developer\'s key' % err)
        app.secret_key = "developer's key. Yup, that's it."

    context = (tls_cert, tls_key)

    for path in context:
        if not os.path.exists(path):
            print('Cannot create TLS context: {} does not exist'.format(path))
            context = None
            break

    app.run('0.0.0.0', debug=True, port=5443, threaded=True, ssl_context=context)
