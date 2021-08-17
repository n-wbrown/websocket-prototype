ws.onmessage = function(event) {
    var messages = document.getElementById('messages')
    var message = document.createElement('li')
    var content = document.createTextNode(event.data)
    console.log(event)
    message.appendChild(content)
    messages.appendChild(message)
};
