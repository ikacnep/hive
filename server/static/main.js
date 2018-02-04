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

        var x = g * (r + 2 * q);
        var y = b * (3 * r - 1) / 2 + b / 2;

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
            Post('/game/' + game_id + '/act', {
                action: 'Place',
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
                    Post('/game/' + game_id + '/act', {
                        action: 'Move',
                        figure_id: game.selected_piece.id,
                        from: coordinates.slice(0, 2),
                        to: [r, q],
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

    function CanIMove() {
        if (game.state.next_player !== game.player_id) {
            return;
        }

        if (game.state.ended) {
            window.clearInterval(poll_for_moves_interval);

            if (game.state.lost[game.player_id]) {
                var players_lost = 0;

                for (var player_id in game.state.lost) {
                    players_lost += game.state.lost[player];
                }

                if (players_lost == 2) {
                    alert("Tie some tie");
                } else {
                    alert('Oh shi~');
                }
            } else {
                alert('Congrats!');
            }

            window.location = '/';
        }

        if (Object.keys(game.state.available_actions[game.player_id]).length === 0
                && game.state.available_placements[game.player_id].length === 0) {
            log("Player can't move");

            Post('/game/' + game_id + '/act', {
                action: 'Skip',
            }).done(function(data) {
                game.state = data.state;
                board.find('hex').filter('.selected, .moved, .placed, .can_move_here').removeClass('selected moved placed can_move_here');
            });
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

    $.getJSON('/game/' + game_id + '/board')
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

            CanIMove();
        });

    $(document).on('click', '.add_piece:not(.disabled)', function() {
        var selected = $('.add_piece.selected').removeClass('selected');

        if (!$(this).is(selected)) {
            $(this).addClass('selected');
        }
    });

    function ConvertScreenToCoordinates(click_x, click_y) {
        var bs = b;
        var gs = g;

        // Я понятия не имею, откуда это берётся. Подобрано опытным путём.
        var x_discrepancy = board_position.width / 2 * (1 - 1 / board_position.scale);

        var x = (click_x) / board_position.scale - board_position.x - bs + x_discrepancy;
        var y = (click_y) / board_position.scale - board_position.y - gs;

        var m = Math.ceil(y / gs);
        var v = Math.ceil((y + sqrt3 * x) / (2 * gs));
        var l = Math.ceil((y - sqrt3 * x) / (2 * gs));

        var r = Math.floor((v - l + 1) / 3);
        var q = Math.floor((m + l) / 3);

        return [r, q];
    }

    $('.table').click(function (event) {
        var coordinates = ConvertScreenToCoordinates(event.pageX, event.pageY);
        OnHexClick.apply(null, coordinates);
    });

    function PollForChanges() {
        if (game.state.next_player === game.player_id) {
            return;
        }

        $.getJSON('/game/' + game_id + '/moves', function(data) {
            log('Other player move:', data);

            if (!data.action) {
                return;
            }

            if (data.action === 'Place') {
                AddPieceToBoard(data);
            } else if (data.action === 'Move') {
                MovePiece(data);
            } else if (data.action === 'Skip') {
                game.state = data.state;
                board.find('hex').filter('.selected, .moved, .placed, .can_move_here').removeClass('selected moved placed can_move_here');
            } else {
                log('Unhandled action:', data.action);
                return;
            }

            CanIMove();
        });
    }

    var poll_for_moves_interval = window.setInterval(PollForChanges, 1000);

    // Движение доски
    var board_position = {
        scale: 1,
        x: 0,
        y: 0,
        width: 800,
        height: 600,
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
            log('Board movement:', board_position);

            board.css({
                'transform': ' scale(' + board_position.scale + ') ' + 'translate(' + board_position.x + 'px, ' + board_position.y + 'px)'
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

    function OnResize(is_initial) {
        log('OnResize', is_initial);

        var table = board.parent();

        var new_width = $(window).width() - $('#right').outerWidth();
        var new_height = $(window).height();

        var current_width = table.width();
        var current_height = table.height();

        table.width(new_width);
        table.height(new_height);

        if (is_initial === true) {
            board_position.x = new_width / 2 - b;
            board_position.y = new_height / 2 - g;
        } else {
            board_position.x += new_width / 2 - current_width / 2;
            board_position.y += new_height / 2 - current_height / 2;
        }

        board_position.width = new_width;
        board_position.height = new_height;

        BoardMovement(function() {})();
    }

    OnResize(true);

    $(window).resize(OnResize);

    $('#debug_board').click(function(e) {
        e.preventDefault();
        board.empty();

        $.each('- selected moved placed can_move_here'.split(' '), function(state_id, state) {
            $.each(['white', 'black'], function (color_id, color) {
                $.each('Queen Ant Spider Beetle Grasshopper Mosquito Ladybug Pillbug'.split(' '), function (figure_id, figure) {
                    AddHex({
                        player: state == 'can_move_here' ? '' : color,
                        figure: state == 'can_move_here' ? '' : figure,
                        state: state,
                        coordinates: [figure_id, color_id  - (((figure_id + 1) / 2)|0) + 2 * state_id, 0],
                    });
                });
            });
        });
    });
});
