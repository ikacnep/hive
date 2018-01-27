if (window.console && console.log) {
    window.log = function() {
        console.log.apply(console.log, arguments);
    }
}

jQuery(function ($) {
    log('initializing');

    var b = 60;
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
        var y = b * (1 + 1.5 * r) + b / 2;

        hex.css({top: x, left: y});
    }

    function AddHex(options) {
        log('AddHex:', options);

        var hex = $('<hex><b><i></b></i>');

        hex.addClass(options.player || '');
        hex.addClass(options.figure || '');
        hex.addClass(options.state || '');

        if (options.id !== undefined) {
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
            id: piece.id,
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

        data.game_id = game_id;
        
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
        log('AddPieceToBoard', [].slice.apply(arguments));
        
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
        log('MovePiece', [].slice.apply(arguments));

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
        board.append(piece);
        MoveToCoordinates(piece, data.piece.coordinates);
        piece.addClass('moved');

        game.selected_piece = null;
    }

    function OnHexClick(r, q) {
        log('OnHexClick', [].slice.apply(arguments));

        var adding_figure = $('.add_piece.selected').data('figure');

        if (adding_figure) {
            Post('/action/add/' + game_id, {
                figure: adding_figure,
                coordinates: [r, q],
                player_key: game.player_key
            }).done(AddPieceToBoard);
        } else {
            if (game.selected_piece) {
                var coordinates = game.selected_piece.coordinates;

                if (coordinates[0] === r && coordinates[1] === q) {
                    board.find('hex').filter('.selected, .moved, .placed, .can_move_here').removeClass('selected moved placed can_move_here');
                    game.selected_piece = null;
                } else {
                    Post('/action/move/' + game_id, {
                        id: game.selected_piece.id,
                        coordinates: [r, q],
                        player_key: game.player_key
                    }).done(MovePiece);
                }
            } else {
                board.find('hex').filter('.selected, .moved, .placed, .can_move_here').removeClass('selected moved placed can_move_here');

                game.selected_piece = FindPieceAt([r, q]);

                if (game.selected_piece) {
                    board.find('#piece_' + game.selected_piece.id).addClass('selected');
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

    $.getJSON('/board/' + game_id)
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
        var x = event.pageX - offset.left - board_position.x;
        var y = event.pageY - offset.top - board_position.y;

        var x1 = x - b;
        var y1 = y - g;

        var m = Math.ceil(y1 / g);
        var v = Math.ceil(1 / (2 * g) * (y1 + sqrt3 * x1));
        var l = Math.ceil(1 / (2 * g) * (y1 - sqrt3 * x1));

        var r = Math.floor((v - l - 2) / 3);
        var q = Math.floor((m + l) / 3);

        OnHexClick(r, q);
    });

    function PollForChanges() {
        if (true || game.state.current_turn === game.player_color) {
            return;
        }

        $.getJSON('/moves/' + game_id, function(data) {
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

    // Движение доски
    var board_position = {
        scale: 1,
        x: 0,
        y: 0,
    };

    var table = $('.table');
    var controls = $('#right .controls');

    function BoardMovement(action_on_board_position) {
        return function() {
            var table_width = table.width();
            var table_height = table.height();
            var step = table_width / 6;

            action_on_board_position(table_width, table_height, step);

            Apply();

            return false;
        }

        function Apply() {
            log('Board movement: ' + board_position);

            board.css({
                'transform': 'translate(' + board_position.x + 'px, ' + board_position.y + 'px)' + ' scale(' + board_position.scale + ')'
            });
        }
    }

    function ChangeScale(is_out) {
        var new_scale = is_out ? board_position.scale / 1.1 : board_position.scale * 1.1;

        // TODO: придумать правильную формулу для интуитивно понятного приближения/удаления, как в картах
        // Плюс вылезают артефакты на гексах. Пока что отключено.
        // board_position.scale = new_scale;
    }

    controls.find('.left').click(BoardMovement(function(w, h, step) { board_position.x -= step / board_position.scale; }));
    controls.find('.right').click(BoardMovement(function(w, h, step) { board_position.x += step / board_position.scale; }));
    controls.find('.up').click(BoardMovement(function(w, h, step) { board_position.y -= step / board_position.scale; }));
    controls.find('.down').click(BoardMovement(function(w, h, step) { board_position.y += step / board_position.scale; }));

    controls.find('.out').click(BoardMovement(function(w, h, step) { ChangeScale(true); }));
    controls.find('.in').click(BoardMovement(function(w, h, step) { ChangeScale(false); }));

    BoardMovement();
});
