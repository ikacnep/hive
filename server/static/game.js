if (window.console && console.log) {
    window.log = function() {
        console.log.apply(console.log, arguments);
    }
}

jQuery(function ($) {
    log('initializing');

    var sqrt3 = Math.sqrt(3);

    /*     b
     *    ←——→
     *    ____
     *   /    \     ↑
     *  /      \    ↓ g
     *  \      /
     *   \____/
     */
    var b = 64;
    var g = sqrt3 / 2 * b;

    var table = $('.table');
    var board = table.find('.board');
    var controls = $('#right').find('.controls');
    var available_area = $('#available_figures');

    var game = {};

    var is_mobile = window.matchMedia("only screen and (max-width: 760px)");
    is_mobile = is_mobile ? is_mobile.matches : false;

    function MoveToCoordinates(hex, position, layer) {
        var r = position[0];
        var q = position[1];

        var top = g * (r + 2 * q);
        var left = b * (3 * r - 1) / 2 + b / 2;

        hex.css({
            top: top,
            left: left,
            zIndex: layer
        }).data({
            position_top: top,
            position_left: left,
            layer: layer,
        });

        if (layer !== 0) {
            hex.addClass('elevated');
        } else {
            hex.removeClass('elevated');
        }
    }

    function MakeHex(options) {
        log('MakeHex:', options);

        var hex = $('<hex><i><b></b></i>');

        hex.addClass(options.player || '');
        hex.addClass(options.figure || '');
        hex.addClass(options.state || '');

        if (options.id !== undefined) {
            hex.attr({id: 'piece_' + options.id});
        }

        return hex;
    }

    function AddHex(options) {
        log('AddHex:', options);

        var hex = MakeHex(options);

        MoveToCoordinates(hex, options.position, options.layer);
        board.append(hex);

        return hex;
    }

    function AddPiece(piece, state) {
        log('AddPiece', [].slice.apply(arguments));

        if (!piece.player) {
            var piece_on_board = FindPieceAt(piece.position);

            if (piece_on_board) {
                piece = piece_on_board;
            }
        }

        AddHex({
            position: piece.position,
            layer: piece.layer,
            player: piece.player,
            figure: piece.figure,
            id: piece.id,
            state: state
        });
    }

    function SortBoard() {
        game.board.sort(function(a, b) {
            return a.layer - b.layer;
        });
    }

    function DrawBoard() {
        log('DrawBoard', [].slice.apply(arguments));

        for (var piece of game.board) {
            AddPiece(piece);
        }
    }

    function FindPieceAt(position) {
        for (var i = game.board.length; i > 0; --i) {
            var piece = game.board[i - 1];

            if (IsSamePosition(piece.position, position)) {
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

    function IsSamePosition(c1, c2) {
        return c1[0] === c2[0] && c1[1] === c2[1];
    }

    function ClearSelection() {
        var hexes = board.find('hex');
        hexes.filter('.selected, .moved, .placed').removeClass('selected moved placed');
        hexes.filter('.can_move_here').remove();
    }

    function AddPieceToBoard(data) {
        log('AddPieceToBoard', [].slice.apply(arguments));

        game.state = data.state;
        MakeBoardFromFigures();

        ClearSelection();

        for (var piece of game.board) {
            if (piece.id === data.figure_id) {
                break;
            }
        }

        AddPiece(piece, 'placed');

        available_area.find('hex.selected').removeClass('selected');

        if (data.figure) {
            var hex = available_area.find('hex.' + data.figure + ':last');
            var area = hex.closest('.select_figure');

            hex.remove();

            if (area.empty()) {
                area.remove();
            }
        }
    }

    function MovePiece(data) {
        log('MovePiece', [].slice.apply(arguments));

        game.state = data.state;
        MakeBoardFromFigures();

        ClearSelection();

        for (var figure of game.board) {
            if (figure.id === data.figure_id) {
                break;
            }
        }

        var piece = board.find('hex#piece_' + data.figure_id);
        board.append(piece);
        MoveToCoordinates(piece, figure.position, figure.layer);
        piece.addClass('moved');

        game.selected_piece = null;
    }

    function OnHexClick(r, q) {
        log('OnHexClick', [].slice.apply(arguments));

        if (game.player_id !== game.state.next_player) {
            AJS.flag({body: "That's not your turn", type: 'info'});
            return;
        }

        if (game.board.length === 0) {
            r = 0;
            q = 0;
        }

        var adding_figure_el = available_area.find('hex.selected');
        var adding_figure_area = adding_figure_el.closest('.select_figure');
        var adding_figure = adding_figure_area.data('figure');

        if (adding_figure) {
            Post('/game/' + game_id + '/act', {
                action: 'Place',
                figure: adding_figure,
                position: [r, q]
            }).done(function(data) {
                AddPieceToBoard(data);

                adding_figure_el.remove();

                if (adding_figure_area.children().length === 0) {
                    adding_figure_area.remove();
                }

                CanIMove();
            });
        } else {
            if (game.selected_piece) {
                var position = game.selected_piece.position;

                if (IsSamePosition(position, [r, q])) {
                    ClearSelection();
                    game.selected_piece = null;
                } else {
                    Post('/game/' + game_id + '/act', {
                        action: 'Move',
                        figure_id: game.selected_piece.id,
                        from: position,
                        to: [r, q],
                    }).done(function(data) {
                        MovePiece(data);
                        CanIMove();
                    });
                }
            } else {
                ClearSelection();

                game.selected_piece = FindPieceAt([r, q]);

                if (game.selected_piece) {
                    var available_actions = game.state.available_actions[game.player_id][game.selected_piece.id];

                    if (available_actions) {
                        board.find('#piece_' + game.selected_piece.id).addClass('selected');

                        for (var can_move_here of available_actions) {
                            AddHex({
                                position: can_move_here,
                                layer: 10,
                                state: 'can_move_here'
                            });
                        }
                    } else {
                        game.selected_piece = null;
                    }
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
                    position: figure.position,
                    layer: figure.layer,
                });
            }
        }

        SortBoard();
    }

    function CanIMove() {
        if (game.state.ended) {
            window.clearInterval(poll_for_moves_interval);

            if (game.state.lost[game.player_id]) {
                var players_lost = 0;

                for (var player_id in game.state.lost) {
                    players_lost += game.state.lost[player_id];
                }

                if (players_lost === 2) {
                    AJS.flag({body: "Well, that's a tie", type: 'info'});
                } else {
                    AJS.flag({body: "Sorry, you've lost", type: 'info'});
                }
            } else {
                AJS.flag({body: "Congratulations, you've won", type: 'info'});
            }

            window.setTimeout(function() {
                window.location = '/';
            }, 3000);
        }

        if (game.state.next_player !== game.player_id) {
            return;
        }

        if (Object.keys(game.state.available_actions[game.player_id]).length === 0
                && game.state.available_placements[game.player_id].length === 0) {
            log("Player can't move");

            Post('/game/' + game_id + '/act', {
                action: 'Skip',
            }).done(function(data) {
                game.state = data.state;
                ClearSelection();
            });
        }
    }

    function DisplayAvailableFigures() {
        available_area.html('');

        var available_figures = game.state.available_figures[game.player_id];

        var figures = ['Queen', 'Ant', 'Grasshopper', 'Beetle', 'Spider', 'Mosquito', 'Ladybug', 'Pillbug'];

        for (var figure of figures) {
            if (!available_figures[figure]) {
                continue;
            }

            var this_figure = $('<div class="select_figure" data-figure="' + figure + '"/>');

            for (var i = 0; i < available_figures[figure]; ++i) {
                this_figure.append(
                    MakeHex({
                        player: game.player_color,
                        figure: figure,
                    }).css({left: 50 * i})
                );
            }

            available_area.append(this_figure);
        }
    }

    $(document).ajaxError(function(event, jqxhr, settings, error) {
        log('Ajax error', arguments);

        var error_message = 'Well, fuck.';

        if (jqxhr.responseJSON) {
            error_message = jqxhr.responseJSON.error_message;
        }

        AJS.flag({body: error_message, type: 'error'});
    });

    $.getJSON('/game/' + game_id + '/board')
        .done(function(game_response) {
            game = game_response;

            MakeBoardFromFigures();

            DrawBoard();

            log('Setting player id to', game.player_id, 'and color to', game.player_color);

            $('#your_player').text(game.player_id).addClass(game.player_color);

            DisplayAvailableFigures();
            CanIMove();
        });

    available_area.on('click', '.select_figure', function() {
        if (game.player_id !== game.state.next_player) {
            AJS.flag({body: "That's not your turn", type: 'info'});
            return;
        }

        ClearSelection();

        var selected = available_area.find('.selected').removeClass('selected');

        if (!$(this).is(selected.closest('.select_figure'))) {
            var available_actions = game.state.available_placements[game.player_id];

            if (available_actions.length > 0) {
                $(this).find('hex:last').addClass('selected');

                for (var can_move_here of available_actions) {
                    AddHex({
                        position: can_move_here,
                        layer: 10,
                        state: 'can_move_here'
                    });
                }
            } else {
                AJS.flag({body: 'You cannot put that anywhere', type: 'warning'});
            }
        }
    });

    function ScreenToBoardCoordinates(screen_x, screen_y) {
        var board_x = (screen_x) / board_position.scale - board_position.x + board_position.x_discrepancy();
        var board_y = (screen_y) / board_position.scale - board_position.y;

        return [board_x, board_y];
    }

    function ConvertScreenToPosition(click_x, click_y) {
        var board_coordinates = ScreenToBoardCoordinates(click_x, click_y);

        var x = board_coordinates[0] - b;
        var y = board_coordinates[1] - g;

        var m = Math.ceil(y / g);
        var v = Math.ceil((y + sqrt3 * x) / (2 * g));
        var l = Math.ceil((y - sqrt3 * x) / (2 * g));

        var r = Math.floor((v - l + 1) / 3);
        var q = Math.floor((m + l) / 3);

        return [r, q];
    }

    table.click(function (event) {
        if (board_position.prevent_click) {
            return;
        }

        var position = ConvertScreenToPosition(event.pageX, event.pageY);
        OnHexClick.apply(null, position);
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
                ClearSelection();
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
        showing_hidden: false,
        x_discrepancy: function() {
            // Я понятия не имею, откуда это берётся. Подобрано опытным путём.
            return board_position.width / 2 * (1 - 1 / board_position.scale);
        }
    };

    function BoardMovement(action_on_board_position) {
        return function() {
            var step = board_position.width / 6;

            action_on_board_position(step);

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

    function ChangeScale(new_scale, fixed_point) {
        if (fixed_point === undefined) {
            fixed_point = [board_position.width / 2, board_position.height / 2]
        }

        var on_board = ScreenToBoardCoordinates.apply(null, fixed_point);

        board_position.scale = new_scale;

        board_position.x = fixed_point[0] / board_position.scale - on_board[0] + board_position.x_discrepancy();
        board_position.y = fixed_point[1] / board_position.scale - on_board[1];
    }

    controls.find('.left').click(BoardMovement(function(step) { board_position.x -= step / board_position.scale; }));
    controls.find('.right').click(BoardMovement(function(step) { board_position.x += step / board_position.scale; }));
    controls.find('.up').click(BoardMovement(function(step) { board_position.y -= step / board_position.scale; }));
    controls.find('.down').click(BoardMovement(function(step) { board_position.y += step / board_position.scale; }));

    controls.find('.out').click(BoardMovement(function() { ChangeScale(board_position.scale / 1.1); }));
    controls.find('.in').click(BoardMovement(function() { ChangeScale(board_position.scale * 1.1); }));

    table.bind('mousewheel DOMMouseScroll', function(event) {
        log('Mouse wheel action', event.originalEvent);

        var point = [event.originalEvent.pageX, event.originalEvent.pageY];

        var new_scale = board_position.scale / 1.1;

        if (event.originalEvent.wheelDelta > 0 || event.originalEvent.detail < 0) {
            new_scale = board_position.scale * 1.1;
        }

        BoardMovement(function() { ChangeScale(new_scale, point); })();
    });

    function StartDrag(x, y) {
        board_position.drag = {x: x, y: y};
        board_position.drag_start = {x: x, y: y};
        board_position.drag_moved = false;
    }

    function MoveDrag(x, y) {
        if (!board_position.drag) {
            return;
        }

        board_position.drag_moved = true;

        BoardMovement(function() {
            board_position.x += (x - board_position.drag.x) / board_position.scale;
            board_position.y += (y - board_position.drag.y) / board_position.scale;

            board_position.drag = {x: x, y: y};
        })();
    }

    function EndDrag() {
        if (board_position.drag_moved) {
            board_position.prevent_click = true;
        } else {
            board_position.prevent_click = false;
        }

        board_position.drag = undefined;
    }

    table.mousedown(function(event) {
        StartDrag(event.pageX, event.pageY);
    });

    table.mouseup(EndDrag);

    table.mousemove(function(event) {
        MoveDrag(event.pageX, event.pageY);
    });

    table.on('touchstart', function(event) {
        var touches = event.originalEvent.touches;

        if (touches.length == 1) {
            StartDrag(touches[0].pageX, touches[0].pageY);
        }
    });

    table.on('touchend', function(event) {
        var touches = event.originalEvent.changedTouches;

        if (touches.length == 1) {
            EndDrag();
        }
    });

    table.on('touchmove', function(event) {
        var touches = event.originalEvent.touches;

        if (touches.length == 1) {
            MoveDrag(touches[0].pageX, touches[0].pageY);
        }
    });

    $('#debug_touches').click(function(e) {
        e.preventDefault();

        $('#touch_log').remove();

        $('#right').prepend(
            $('<div id="touch_log" />')
                .attr('id', 'touch_log')
                .css({
                    whiteSpace: 'pre-wrap',
                    height: 200,
                    fontSize: 6,
                    overflowY: 'hidden',
                    fontFamily: 'monospace',
                })
        );
    });

    function LogTouch(message, touches) {
        var touch_string = '[' + touches.length + '] ';

        for (var touch of touches) {
            if (touch) {
                touch_string += touch.identifier + ':' + Math.round(touch.pageX) + ',' + Math.round(touch.pageY) + '  ';
            }
        }

        $('#touch_log').prepend(message + ': ' + touch_string + '\n');
    }

    function LogTouchesFromEvent(message, key) {
        return function(event) {
            LogTouch(message, event.originalEvent[key]);
        };
    }

    table.on('touchstart', LogTouchesFromEvent('s', 'touches'));
    table.on('touchmove', LogTouchesFromEvent('m', 'touches'));
    table.on('touchend', LogTouchesFromEvent('e', 'changedTouches'));

    function OnResize(is_initial) {
        log('OnResize', is_initial);

        var table = board.parent();

        var new_width = $(window).width() - $('#right').outerWidth() + 20;
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

        $('#right').height(board_position.height);

        if (is_initial === true && is_mobile) {
            ChangeScale(board_position.scale / 2);
        }

        BoardMovement(function() {})();
    }

    if (is_mobile) {
        $('body').addClass('mobile');
    }

    OnResize(true);

    $(window).resize(OnResize);

    $('#debug_board').click(function(e) {
        e.preventDefault();
        board.empty();

        available_area.empty();
        window.clearInterval(poll_for_moves_interval);

        $.each('- selected moved placed can_move_here'.split(' '), function(state_id, state) {
            $.each(['white', 'black'], function (color_id, color) {
                $.each('Queen Ant Spider Beetle Grasshopper Mosquito Ladybug Pillbug'.split(' '), function (figure_id, figure) {
                    var position = [-3 + color_id + 2 * state_id, -2 + figure_id - state_id];

                    AddHex({
                        player: state === 'can_move_here' ? '' : color,
                        figure: state === 'can_move_here' ? '' : figure,
                        state: state,
                        position: position,
                        layer: 0,
                    }).find('b').text(JSON.stringify(position));
                });
            });
        });
    });

    function ShowHiddenFigures(is_show) {
        board_position.showing_hidden = is_show;

        var factor = is_show ? 0.7 : 0;

        board.find('hex.elevated').each(function() {
            var el = $(this);
            var layer = el.data('layer');

            el.stop();

            el.animate({
                top: el.data('position_top') - factor * g * layer,
                left: el.data('position_left') - factor * b * layer,
            });
        });
    }

    $('#show_hidden').click(function(e) {
        e.preventDefault();

        if (board_position.showing_hidden) {
            ShowHiddenFigures(false);
        } else {
            ShowHiddenFigures(true);
        }
    });
});
