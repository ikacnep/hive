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

    var b = 120;
    var d = 8;
    var board = $('.table .board');

    var game = 'not loaded yet';

    var sqrt3 = Math.sqrt(3);

    var a = b - d / sqrt3;
    var g = sqrt3 / 2 * b;

    function MoveToCoordinates(hex, coordinates) {
        var r = coordinates[0];
        var q = coordinates[1];

        var x = g * (1 + r + 2 * q);
        var y = b * (1 + 1.5 * r);

        hex.css({top: x, left: y});
    }

    function AddHex(options) {
        log('AddHex:', options);

        var hex = $('<hex><b><i></b></i>');

        hex.addClass(options.player || '');
        hex.addClass(options.figure || '');
        hex.addClass(options.state || '');

        if (options.id) {
            hex.attr({id: 'piece_' + options.id});
        }

        MoveToCoordinates(hex, options.coordinates);
        board.append(hex);
    }

    function AddPiece(piece, state) {
        log('AddPiece', [].slice.apply(arguments));

        if (!piece.player) {
            var piece_on_board = FindPieceAt(piece.coordinates);

            if (piece_on_board) {
                piece = piece_on_board;
            }
        }
       
        AddHex({
            coordinates: piece.coordinates,
            player: piece.player,
            figure: piece.figure,
            state: state
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
            AddPiece(piece);
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

    function AddPieceToBoard(data) {
        game.state = data.state;

        for (var piece of game.board) {
            if (piece.id === data.piece.id) {
                return;
            }
        }

        board.find('hex').filter('.selected, .moved, .placed, .can_move_here').removeClass('selected moved placed can_move_here');

        game.board.push(data.piece);
        SortBoard();

        AddPiece(data.piece, 'placed');

        var adding_figure_element = $('.add_piece.selected');
        adding_figure_element.removeClass('selected');

        if (game.state[game.player_color].available_figures[data.piece.figure] === 0) {
            adding_figure_element.addClass('disabled');
        }
    }

    function MovePiece(data) {
        game.state = data.state;

        var old_piece = null;

        for (var piece of game.board) {
            if (piece.id === data.piece.id) {
                old_piece = piece;

                if (CoordinatesEqual(piece.coordinates, data.piece.coordinates)) {
                    return;
                }

                break;
            }
        }

        board.find('hex').filter('.selected, .moved, .placed, .can_move_here').removeClass('selected moved placed can_move_here');

        game.board = game.board.filter(piece => piece.id != data.piece.id);
        game.board.push(data.piece);

        SortBoard();

        var piece = board.find('hex#piece_' + piece.id);
        MoveToCoordinates(piece, piece.coordinates);
        piece.addClass('moved');
    }

    function OnHexClick(r, q) {
        log('OnHexClick', [].slice.apply(arguments));

        var adding_figure = $('.add_piece.selected').data('figure');

        if (adding_figure) {
            Post('/action/add', {
                figure: adding_figure,
                coordinates: [r, q],
                player_key: game.player_key
            }).done(AddPieceToBoard);
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
                    }).done(MovePiece);
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

    $('.table').click(function (event) {
        var offset = $(this).offset();
        var y = event.pageX - offset.left;
        var x = event.pageY - offset.top;

        var x1 = x - g;
        var y1 = y - b;

        var m = Math.ceil(x1 / g);
        var v = Math.ceil(1 / (2 * g) * (x1 + sqrt3 * y1));
        var l = Math.ceil(1 / (2 * g) * (x1 - sqrt3 * y1));

        var r = Math.floor((v - l + 1) / 3);
        var q = Math.floor((m + l) / 3);

        OnHexClick(r, q);
    });

    function PollForChanges() {
        if (game.state.current_turn === game.player_color) {
            return;
        }

        $.getJSON('/moves', function(data) {
            log('other player action:', data.action);

            if (!data.action) {
                return;
            }

            if (data.action === 'add') {
                AddPieceToBoard(data);
            } else if (data.action === 'move') {
                MovePiece(data);
            }
        });
    }

    window.setInterval(PollForChanges, 1000);
});
