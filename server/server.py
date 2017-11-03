#!/usr/bin/env python3

import flask

app = flask.Flask(__name__)


@app.route('/')
def hello_world():
    return flask.render_template('index.html')


@app.route('/action/click')
def click():
    return flask.jsonify(
        ok=True
    )


@app.route('/board')
def get_board():
    board = [
        dict(
            coordinates=(2, 0, 0),
            piece='ant',
            player='white'
        ),
        dict(
            coordinates=(2, 1, 0),
            piece='queen',
            player='black'
        ),
        dict(
            coordinates=(3, 0, 0),
            piece='queen',
            player='white'
        ),
    ]

    return flask.jsonify(
        board=board,
        state={'color': 'white', 'your_turn': True, 'can_move': True, 'placed_queen': True}
    )
