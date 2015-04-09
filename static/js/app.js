$(function() {
    var ws = null,
        $tableBody = $('#dataTable tbody'),
        $statusBar = $('#statusBar');

    function notify(message, state, empty) {
        if (empty) {
           $statusBar.empty();
        }
        state = state ? 'alert-'+state: 'alert-info';
        $('<div class="alert ' + state + ' alert-dismissible" role="alert">' +
        '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' +
        '<span aria-hidden="true">&times;</span></button>' +
        message +
        '</div>').appendTo($statusBar);
    }

    function webSocketOpen() {
        notify('Connected', null, true);
    }

    function webSocketClose() {
        ws = null;
        notify('Connection closed');
    }

    function webSocketMessage(e) {
        var message = JSON.parse(e.data);
        if (message.messageType === 'data') {
            $('<tr>' +
              '<td>' + message.timeStamp + '</td>' +
              '<td>' + message.sourceAddr + '</td>' +
              '<td>' + message.destinationAddr + '</td>' +
              '<td>' + message.hopCount + '</td>' +
              '<td>' + message.proprity + '</td>' +
              '<td>' + message.decodedData + '</td>' +
              '</tr>').appendTo($tableBody);
        } else if (message.messageType === 'error') {
            notify(message.message, 'danger', true)
        } else if (message.messageType === 'info') {
            notify(message.message)
        }
    }

    function doDisconnect() {
        if (ws !== null) {
            ws.close();
            ws = null;
        }
    }

    function doClear() {
        $tableBody.empty();
        $statusBar.empty();
    }

    function doConnect(host, port) {
        doDisconnect();
        ws = new WebSocket('ws://' + document.location.host + '/websocket/'
        + host + ':' + port);
        ws.onopen = webSocketOpen;
        ws.onclose = webSocketClose;
        ws.onmessage = webSocketMessage;
    }


    $('#btnConnect').click(function() {
        doConnect(
            $('#hostInput').val().trim(),
            $('#portInput').val().trim()
        );
        return false;
    });

    $('#btnDisconnect').click(function() {
        doDisconnect();
        return false;
    });

    $('#btnClear').click(function() {
        doClear();
        return false;
    });

});