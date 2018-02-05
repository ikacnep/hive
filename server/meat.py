import flask
import os
import traceback

from spine.Game.Settings.Figures import FigureTypes
from spine.Game.Utils.Action import Action
from spine.Game.Utils.Exceptions import HiveError, GameNotFoundException
from spine.GamesManipulator import GamesManipulator

app = flask.Flask(__name__)

games_manipulator = GamesManipulator()


class IncorrectMove(HiveError):
    pass


@app.errorhandler(HiveError)
def handle_incorrect_move(error):
    traceback.print_exc()

    response = flask.jsonify({"error_message": str(error)})
    response.status_code = 400
    return response


@app.route('/')
def main_page():
    data = flask.request.args
    session = flask.session

    if 'player_id' in session:  # Already logged-in users
        player_id = session['player_id']

        try:
            player = games_manipulator.GetPlayer(pid=player_id).player
        except:
            return flask.redirect(flask.url_for('login'))
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

    try:
        games = games_manipulator.GetGames(players=[player.id])
    except GameNotFoundException:
        games = []

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

    player = games_manipulator.GetPlayer(pid=player_id).player
    other_player = games_manipulator.GetPlayer(pid=other_player_id).player

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


@app.route('/game/<int:game_id>/act', methods=['POST'])
def game_action(game_id):
    data = flask.request.json

    game, player_id = verify_i_play_game(game_id)

    action = Action[data['action']]

    if action == Action.Place:
        result = games_manipulator.Place(
            gid=game_id,
            player=player_id,
            figure=FigureTypes.FigureType[data['figure']],
            position=tuple(data['position']),
            addState=True,
        )
    elif action == Action.Move:
        result = games_manipulator.Move(
            gid=game_id,
            player=player_id,
            fid=data['figure_id'],
            f=tuple(data['from']),
            t=tuple(data['to']),
            addState=True,
        )
    elif action == Action.Skip:
        result = games_manipulator.Skip(
            gid=game_id,
            player=player_id,
            addState=True,
        )
    elif action == Action.Concede:
        result = games_manipulator.Concede(
            gid=game_id,
            player=player_id,
            addState=True,
        )
    else:
        raise IncorrectMove('Unhandled action: {}'.format(action))

    return flask.jsonify(
        state=result.state.GetJson(),
        figure_id=result.fid
    )


@app.route('/game/<int:game_id>/moves', methods=['GET'])
def get_moves(game_id):
    game, player_id = verify_i_play_game(game_id)

    state = game.GetState()
    last_action = state.lastAction

    if not last_action or last_action['player'] == player_id:
        return flask.jsonify()

    return flask.jsonify(
            state=state.GetJson(),
            action=last_action['action'],
            coordinates_from=last_action.get('from'),
            coordinates=last_action.get('to') or last_action.get('position'),
            figure_id=last_action.get('fid'),
    )


@app.route('/game/<int:game_id>/board', methods=['GET'])
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
        return open('server/.well-known/acme-challenge/' + challenge).read()
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
