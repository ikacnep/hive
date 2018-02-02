if (window.console && console.log) {
    window.log = function() {
        console.log.apply(console.log, arguments);
    }
}

jQuery(function ($) {
    log('initializing');

    var sqrt3 = Math.sqrt(3);

    var b = 64;
    var g = sqrt3 / 2 * b;

    var board = $('.table .board');

    var game = {};

    function MoveToCoordinates(hex, coordinates) {
        var r = coordinates[0];
        var q = coordinates[1];

        var x = g * (1 + r + 2 * q);
        var y = b * (1 + 1.5 * r) + b / 2;

        hex.css({top: x, left: y});
    }

    function AddHex(options) {
        log('AddHex:', options);

        var hex = $('<hex><i><b></b></i>');

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
        MakeBoardFromFigures();

        board.find('hex').filter('.selected, .moved, .placed, .can_move_here').removeClass('selected moved placed can_move_here');

        for (var piece of game.board) {
            if (piece.id === data.figure_id) {
                break;
            }
        }

        AddPiece(piece, 'placed');

        var adding_figure_element = $('.add_piece.selected');
        adding_figure_element.removeClass('selected');

        if (data.figure && game.state.available_figures[game.player_id][data.figure] === 0) {
            adding_figure_element.hide();
        }
    }

    function MovePiece(data) {
        log('MovePiece', [].slice.apply(arguments));

        game.state = data.state;
        MakeBoardFromFigures();

        board.find('hex').filter('.selected, .moved, .placed, .can_move_here').removeClass('selected moved placed can_move_here');

        for (var figure of game.board) {
            if (figure.id === data.figure_id) {
                break;
            }
        }

        var piece = board.find('hex#piece_' + data.figure_id);
        board.append(piece);
        MoveToCoordinates(piece, figure.coordinates);
        piece.addClass('moved');

        game.selected_piece = null;
    }

    function OnHexClick(r, q) {
        log('OnHexClick', [].slice.apply(arguments));

        if (game.player_id !== game.state.next_player) {
            alert("That's not your turn");
            return;
        }

        if (game.board.length === 0) {
            r = 0;
            q = 0;
        }

        var adding_figure = $('.add_piece.selected').data('figure');

        if (adding_figure) {
            Post('/action/add/' + game_id, {
                figure: adding_figure,
                coordinates: [r, q]
            }).done(AddPieceToBoard);
        } else {
            if (game.selected_piece) {
                var coordinates = game.selected_piece.coordinates;

                if (coordinates[0] === r && coordinates[1] === q) {
                    board.find('hex').filter('.selected, .moved, .placed, .can_move_here').removeClass('selected moved placed can_move_here');
                    game.selected_piece = null;
                } else {
                    Post('/action/move/' + game_id, {
                        figure_id: game.selected_piece.id,
                        from: coordinates.slice(0, 2),
                        to: [r, q],
                        player_id: game.player_id
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

    function MakeBoardFromFigures() {
        log('MakeBoardFromFigures', game.state.figures);

        game.board = [];

        for (var player_id of Object.keys(game.state.figures)) {
            var player_figures = game.state.figures[player_id];

            var color = game.player_color;

            if (+player_id !== game.player_id) {
                color = color === 'white' ? 'black' : 'white';
            }

            for (var figure_id in player_figures) {
                var figure = player_figures[figure_id];

                game.board.push({
                    player: color,
                    id: figure.id,
                    figure: figure.type,
                    coordinates: figure.position.concat([-figure.layer])
                });
            }
        }

        SortBoard();
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

            MakeBoardFromFigures();

            DrawBoard();

            log('Setting player id to', game.player_id, 'and color to', game.player_color);

            $('#your_player').text(game.player_id).addClass(game.player_color);
            var all_pickers = $('.add_piece').addClass(game.player_color);

            var available_figures = game.state.available_figures[game.player_id];

            for (var figure in available_figures) {
                var picker_el = $('.add_piece[data-figure=' + figure + ']');
                all_pickers = all_pickers.not(picker_el);
            }

            all_pickers.hide();
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
        if (game.state.next_player === game.player_id) {
            return;
        }

        $.getJSON('/moves/' + game_id, function(data) {
            log('Other player move:', data);

            if (!data.action) {
                return;
            }

            if (data.action === 'Place') {
                AddPieceToBoard(data);
            } else if (data.action === 'Move') {
                MovePiece(data);
            } else {
                log('Unhandled action:', data.action)
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
        };

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
        board_position.scale = new_scale;
    }

    controls.find('.left').click(BoardMovement(function(w, h, step) { board_position.x -= step / board_position.scale; }));
    controls.find('.right').click(BoardMovement(function(w, h, step) { board_position.x += step / board_position.scale; }));
    controls.find('.up').click(BoardMovement(function(w, h, step) { board_position.y -= step / board_position.scale; }));
    controls.find('.down').click(BoardMovement(function(w, h, step) { board_position.y += step / board_position.scale; }));

    controls.find('.out').click(BoardMovement(function(w, h, step) { ChangeScale(true); }));
    controls.find('.in').click(BoardMovement(function(w, h, step) { ChangeScale(false); }));

    BoardMovement();

    $('#debug_board').click(function(e) {
        e.preventDefault();
        board.empty();

        $.each('- selected moved placed'.split(' '), function(state_id, state) {
            $.each(['white', 'black'], function (color_id, color) {
                $.each('Queen Ant Spider Beetle Grasshopper Mosquito Ladybug Pillbug'.split(' '), function (figure_id, figure) {
                    AddHex({
                        player: color,
                        figure: figure,
                        state: state,
                        coordinates: [figure_id, color_id  - (((figure_id + 1) / 2)|0) + 2 * state_id, 0],
                    });
                });
            });
        });

        var state_id = 4;

        $.each('Queen Ant Spider Beetle Grasshopper Mosquito Ladybug Pillbug'.split(' '), function (figure_id, figure) {
            AddHex({
                player: '',
                figure: '',
                state: 'can_move_here',
                coordinates: [figure_id, -(((figure_id + 1) / 2)|0) + 2 * state_id, 0],
            });
        });

        return false;
    })
});
