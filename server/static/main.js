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

    selected: 'green',
    can_move_here: 'blue',
    cant_move_here: 'red'
};


jQuery(function ($) {
    var canvas = $('canvas')[0].getContext('2d'),
        b = 50,
        d = 20;

    var sqrt3 = Math.sqrt(3);

    var a = b - d / sqrt3;
    var g = sqrt3 / 2 * b;

    function DrawHex(options) {
        var hex_color = HEX_COLOR[options.player || 'nobody'];
        var text_color = TEXT_COLOR[options.player || 'nobody'];
        var border_color = BORDER[options.border || options.player || 'nobody'];

        console.log('DrawHex', options, '->', hex_color, text_color, border_color);

        var r = options.r;
        var q = options.q;

        var x = g * (1 + r + 2 * q);
        var y = b * (1 + 1.5 * r);

        if (hex_color !== border_color) {
            DoDrawHex(x, y, b, g, border_color);
        }

        DoDrawHex(x, y, a, sqrt3 / 2 * a, hex_color);

        var font_size = b / 2 - d / 4;

        canvas.fillStyle = text_color;
        canvas.textAlign = 'center';
        canvas.textBaseline = 'middle';
        canvas.font = font_size + 'px sans-serif';

        var text = (options.text || '') + ' (' + (r) + ', ' + (q) + ')';

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

    function Post(url, data) {
        return $.ajax(url, {
            data: JSON.stringify(data),
            contentType: 'application/json',
            type: 'POST'
        });
    }

    function OnHexClick(r, q) {
        console.log('Click at', r, q);

        /*
        var adding_piece = $('#add').val();

        if (adding_piece) {
            window.selected_hex = null;

            Post('/action/add', {
                piece: adding_piece,
                hex: {
                    r: r,
                    q: q
                }
            })
                .done(function() {

                });
        } else {
            if (window.selected_hex) {
                if (window.selected_hex.r === r && window.selected_hex.q === q) {
                    window.selected_hex = null;
                }
            } else {
                window.selected_hex = {r: r, q: q};

                DrawHex(r, q, 'black', 'green');
            }
        }

        window.last_selected_hex = {r: r, q: q};
        */
    }

    $.getJSON('/board').done(function(data) {
        console.log(data);

        for (var piece of data.board) {
            DrawHex({r: piece.coordinates[0], q: piece.coordinates[1], player: piece.player, text: piece.piece[0]});
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

        /*
        canvas.beginPath();
        canvas.fillStyle = 'blue';
        canvas.arc(x, y, 3, 0, 7);
        canvas.fill();
        */
    });

    window.last_selected_hex = null;
});
