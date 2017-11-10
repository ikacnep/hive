const PLAYER = {
    white: 'white',
    black: 'black',
    nobody: ''
};

const HEX_COLOR = {
    white: '#FFF',
    black: '#333',
    nobody: '#FFF'
};

const TEXT_COLOR = {
    white: '#555',
    black: '#DDD',
    nobody: '#FFF'
};

const BORDER = {
    reset: '-',

    white: '#DDD',
    black: '#000',
    nobody: '#FFF',

    placed: 'magenta',
    selected: 'green',
    moved: 'yellow',
    can_move_here: 'blue',
    cant_move_here: 'red'
};

if (window.console && console.log) {
    window.log = function() {
        console.log.apply(console.log, arguments);
    }
}

jQuery(function ($) {
    log('initializing');

    var canvas = $('canvas')[0].getContext('2d'),
        b = 50,
        d = 20;

    var game = 'not loaded yet';

    var sqrt3 = Math.sqrt(3);

    var a = b - d / sqrt3;
    var g = sqrt3 / 2 * b;

    function DrawHex(options) {
        log('DrawHex:', options);

        var hex_color = HEX_COLOR[options.player || 'nobody'];
        var text_color = TEXT_COLOR[options.player || 'nobody'];
        var border_color = options.border || BORDER[options.player || 'nobody'];

        var r = options.coordinates[0];
        var q = options.coordinates[1];

        var x = g * (1 + r + 2 * q);
        var y = b * (1 + 1.5 * r);

        DoDrawHex(x, y, b, g, border_color);

        if (hex_color !== border_color) {
            DoDrawHex(x, y, a, sqrt3 / 2 * a, hex_color);
        }

        var font_size = b / 2 - d / 4;

        canvas.fillStyle = text_color;
        canvas.textAlign = 'center';
        canvas.textBaseline = 'middle';
        canvas.font = font_size + 'px sans-serif';

        var text = options.text || '';

        canvas.fillText(text, x, y);
    }

    function DoDrawHex(x, y, b, g, fill_style) {
        canvas.beginPath();
        canvas.fillStyle = fill_style;
        canvas.strokeStyle = fill_style;

        canvas.moveTo(x - g, y + b / 2);
        canvas.lineTo(x, y + b);
        canvas.lineTo(x + g, y + b / 2);
        canvas.lineTo(x + g, y - b / 2);
        canvas.lineTo(x, y - b);
        canvas.lineTo(x - g, y - b / 2);
        canvas.lineTo(x - g, y + b / 2);
        canvas.fill();
    }

    function DrawPiece(piece, border) {
        log('DrawPiece', [].slice.apply(arguments));

        if (!piece.player) {
            var piece_on_board = FindPieceAt(piece.coordinates);

            if (piece_on_board) {
                piece = piece_on_board;
            }
        }
       
        DrawHex({
            coordinates: piece.coordinates,
            player: piece.player,
            text: piece.figure ? (piece.figure[0] + ':' + (piece.id) + '/' + (piece.coordinates[2] || 0)) : '',
            border: border
        });
    }

    function SortBoard() {
        game.board.sort(function(a, b) {
            return a.coordinates[2] - b.coordinates[2];
        });
    }

    function DrawBoard() {
        log('DrawBoard', [].slice.apply(arguments));

        for (var piece of game.board) {
            DrawPiece(piece);
        }
    }

    function FindPieceAt(coordinates) {
        for (var i = game.board.length; i > 0; --i) {
            var piece = game.board[i - 1];

            if (piece.coordinates[0] === coordinates[0] && piece.coordinates[1] === coordinates[1]) {
                return piece;
            }
        }
    }

    function Post(url, data) {
        log('Post', [].slice.apply(arguments));
        
        return $.ajax(url, {
            data: JSON.stringify(data),
            contentType: 'application/json',
            type: 'POST'
        });
    }

    function CoordinatesEqual(c1, c2) {
        return c1[0] === c2[0] && c1[1] === c2[1];
    }

    function OnHexClick(r, q) {
        log('OnHexClick', [].slice.apply(arguments));

        var adding_figure_element = $('.add_piece.selected');
        var adding_figure = adding_figure_element.data('figure');

        if (adding_figure) {
            Post('/action/add', {
                figure: adding_figure,
                coordinates: [r, q],
                player_key: game.player_key
            })
                .done(function(data) {
                    game.state = data.state;

                    if (game.last_highlighted_piece) {
                        DrawPiece(game.last_highlighted_piece);
                    }

                    game.board.push(data.piece);
                    SortBoard();

                    DrawPiece(data.piece, BORDER.placed);

                    game.last_highlighted_piece = data.piece;

                    adding_figure_element.removeClass('selected');

                    if (game.state[game.player_color].available_figures[adding_figure] === 0) {
                        adding_figure_element.addClass('disabled');
                    }
                });
        } else {
            if (game.selected_piece) {
                var coordinates = game.selected_piece.coordinates;

                if (coordinates[0] === r && coordinates[1] === q) {
                    DrawPiece(game.selected_piece);
                    game.selected_piece = null;

                    if (game.last_highlighted_piece) {
                        DrawPiece(game.last_highlighted_piece);
                    }
                } else {
                    Post('/action/move', {
                        id: game.selected_piece.id,
                        coordinates: [r, q],
                        player_key: game.player_key
                    })
                        .done(function(data) {
                            game.state = data.state;

                            game.board = game.board.filter(piece => piece.id != data.piece.id);
                            game.board.push(data.piece);

                            SortBoard();

                            DrawPiece({coordinates: game.selected_piece.coordinates});

                            if (game.last_highlighted_piece &&
                                    !CoordinatesEqual(game.last_highlighted_piece.coordinates, game.selected_piece.coordinates)
                            ) {
                                DrawPiece(game.last_highlighted_piece);
                            }

                            DrawPiece(data.piece, BORDER.moved);

                            game.selected_piece = null;
                            game.last_highlighted_piece = data.piece;
                        });
                }
            } else {
                game.selected_piece = FindPieceAt([r, q]);

                if (game.selected_piece) {
                    DrawPiece(game.selected_piece, BORDER.selected);
                }
            }
        }
    }

    $(document).ajaxError(function(event, jqxhr, settings, error) {
        log('Ajax error', arguments);

        var error_message = 'Well, fuck.';

        if (jqxhr.responseJSON) {
            error_message = jqxhr.responseJSON.error_message;
        }

        alert(error_message);
    });

    $.getJSON('/board')
        .done(function(game_response) {
            game = game_response;
            SortBoard();
            DrawBoard(game_response.board);

            log('Setting player key to', game.player_key, 'and color to', game.player_color);

            $('#your_player').text(game.player_key).addClass(game.player_color);
            $('.add_piece').addClass(game.player_color);

            let available_figures = game.state[game.player_color].available_figures;

            for (var figure in available_figures) {
                if (available_figures[figure] === 0) {
                    $('.add_piece[data-figure=' + figure + ']').addClass('disabled');
                }
            }
        });

    $(document).on('click', '.add_piece:not(.disabled)', function() {
        var selected = $('.add_piece.selected').removeClass('selected');

        if (!$(this).is(selected)) {
            $(this).addClass('selected');
        }
    });

    $('#canvas').click(function (event) {
        var offset = $(this).offset();
        var x = event.pageX - offset.left;
        var y = event.pageY - offset.top;

        var x1 = x - g;
        var y1 = y - b;

        var m = Math.ceil(x1 / g);
        var v = Math.ceil(1 / (2 * g) * (x1 + sqrt3 * y1));
        var l = Math.ceil(1 / (2 * g) * (x1 - sqrt3 * y1));

        var r = Math.floor((v - l + 1) / 3);
        var q = Math.floor((m + l) / 3);

        OnHexClick(r, q);
    });
});
