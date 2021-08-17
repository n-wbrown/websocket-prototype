var host = "ws:" + "//" + window.location.host + window.location.pathname + "/ws";
console.log("Connecting to: " + host);
var ws = new WebSocket(host);

function sendMessageFromForm(event, id) {
    event.preventDefault()
    var input = document.getElementById(id)
    ws.send(input.value)
    input.value = ''
}

function sendMessageWPrefix(event, prefix, id) {
    event.preventDefault()
    var input = document.getElementById(id)
    ws.send("".concat(prefix, " ", input.value))
    input.value = ''
}


