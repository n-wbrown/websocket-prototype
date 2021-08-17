// empty databuffer 
data = new Array(15).fill(0);

ws.onmessage = function(event) {
    var messages = document.getElementById('messages')
    var message = document.createElement('li')
    var content = document.createTextNode(event.data)
    data.push(parseFloat(event.data))
    data.shift()
    var div = d3.select('#plot_area')
    div.selectAll("div")
      .data(data)
      .join("div")
        .style("background", "steelblue")
        .style("padding", "3px")
        .style("margin", "1px")
        .style("width", d => `${d * 100}px`)
        .text(d => d);
    console.log(data)
    message.appendChild(content)
    messages.appendChild(message)
};

function sendMessage(event, prefix, id) {
    event.preventDefault()
    var input = document.getElementById(id)
    ws.send("".concat(prefix, " ", input.value))
    input.value = ''
}



function make_div() {
  // fill the div with blank data 
  console.log("making div");
  var div = d3.select('#div')
      .style("font", "10px sans-serif")
      .style("text-align", "right")
      .style("color", "white");

  div.selectAll("div")
    .data(data)
    .join("div")
      .style("background", "steelblue")
      .style("padding", "3px")
      .style("margin", "1px")
      .style("width", d => `${d * 100}px`)
      .text(d => d);

  return div.node();
}
make_div();
