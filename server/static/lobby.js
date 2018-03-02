jQuery(function($) {
    $('#invite_link')
        .html('Ссылка для подключения: ')
        .append(
            $('<code/>').html(
                $('<a/>')
                    .text(location.href)
                    .attr({href: location.href})
            )
        );

    window.setInterval(function() {
        $.get('/lobby/' + lobby_id + '/check')
            .done(function(data) {
                if (data.game_id !== undefined) {
                    location.href = '/game/' + data.game_id;
                }
            });
    }, 1000);
});
