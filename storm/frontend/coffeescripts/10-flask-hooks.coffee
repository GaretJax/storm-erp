(($) ->
    csrftoken = $('meta[name=csrf-token]').attr('content')

    $.ajaxSetup({
        beforeSend: (xhr, settings) ->
            console.log 'send'
            if not /^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)
                xhr.setRequestHeader("X-CSRFToken", csrftoken)
    })
)(jQuery)
