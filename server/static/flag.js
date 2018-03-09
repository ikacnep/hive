jQuery(function($) {
    var AUTO_CLOSE_TIME = 5000;
    var ID_FLAG_CONTAINER = 'aui-flag-container';

    var defaultOptions = {
        body: '',
        close: 'auto',
        title: '',
        type: 'info'
    };

    function flag(options) {
        options = $.extend({}, defaultOptions, options);

        var $flag = renderFlagElement(options);
        extendFlagElement($flag);

        if (options.close === 'auto') {
            makeCloseable($flag);
            makeAutoClosable($flag);
        } else if (options.close === 'manual') {
            makeCloseable($flag);
        }

        pruneFlagContainer();

        return insertFlag($flag);
    }

    function extendFlagElement($flag) {
        var flag = $flag[0];

        flag.close = function () {
            closeFlag($flag);
        };
    }

    function renderFlagElement(options) {
        var html = '<div class="aui-flag">'
            + '<div class="aui-message aui-message-{type} {type} {closeable} shadowed">'
            + '<p class="title">'
            + '<strong>{title}</strong>'
            + '</p>'
            + '{body}'
            + '</div>'
            + '</div>';

        var rendered = html
            .replace(/{body}/g, options.body || '')
            .replace(/{closeable}/g, options.close === 'never' ? '' : 'closeable')
            .replace(/{title}/g, options.title || '')
            .replace(/{type}/g, options.type);

        return $(rendered);
    }

    function makeCloseable($flag) {
        $flag.click(function () {
            closeFlag($flag);
        });
    }

    function makeAutoClosable($flag) {
        $flag.find('.aui-message').addClass('aui-will-close');
        setTimeout(function () {
            $flag[0].close();
        }, AUTO_CLOSE_TIME);
    }

    function closeFlag($flagToClose) {
        var flag = $flagToClose.get(0);

        flag.setAttribute('aria-hidden', 'true');

        return flag;
    }

    function pruneFlagContainer() {
        var $container = findContainer();
        var $allFlags = $container.find('.aui-flag');

        $allFlags.get().forEach(function (flag) {
            var isFlagAriaHidden = flag.getAttribute('aria-hidden') === 'true';

            if (isFlagAriaHidden) {
                $(flag).remove();
            }
        });
    }

    function findContainer() {
        return $('#' + ID_FLAG_CONTAINER);
    }

    function insertFlag($flag) {
        var $flagContainer = findContainer();

        if (!$flagContainer.length) {
            $flagContainer = $('<div id="' + ID_FLAG_CONTAINER + '"></div>');
            $('body').prepend($flagContainer);
        }

        $flag.appendTo($flagContainer);
        recomputeStyle($flag);

        return $flag.attr('aria-hidden', 'false')[0];
    }

    function recomputeStyle(el) {
        el = el.length ? el[0] : el;
        window.getComputedStyle(el, null).getPropertyValue('left');
    }

    var keyCode = {
        ENTER: 13,
        SPACE: 32,
    };

    AJS.flag = flag;
});