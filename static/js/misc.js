(function( $ ){

    $.fn.esCodigoPostal = function() {
        var regex = /^\d{5}$/;
        return regex.test($(this).val());
    };

    $.fn.validarCampoObligatorio = function() {
        return $.trim($(this).val());
    }

    $.fn.esEmail = function() {
        var regex = /^(?:[\w\!\#\$\%\&\'\*\+\-\/\=\?\^\`\{\|\}\~]+\.)*[\w\!\#\$\%\&\'\*\+\-\/\=\?\^\`\{\|\}\~]+@(?:(?:(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-](?!\.)){0,61}[a-zA-Z0-9]?\.)+[a-zA-Z0-9](?:[a-zA-Z0-9\-](?!$)){0,61}[a-zA-Z0-9]?)|(?:\[(?:(?:[01]?\d{1,2}|2[0-4]\d|25[0-5])\.){3}(?:[01]?\d{1,2}|2[0-4]\d|25[0-5])\]))$/;
        return regex.test($(this).val());
    };

    $.fn.marcarError = function(mensaje, valor) {
        if (!valor) {
            $(this).text(mensaje);
        } else {
            $(this).text('');
        }
    };

})( jQuery );
