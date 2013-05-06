var ws;
var list;
setupSocket();
function setupSocket(){
  ws = new WebSocket("ws://schwiz.chickenkiller.com:8888/list/socket");
  ws.onmessage = function(evt){
    var data = JSON.parse(evt.data);
    if(data.action == "connect"){
      document.getElementById("listbox").innerHTML = '';
      data.list.map(AddItem);
      list = data.list;
      HeartBeat();
    }
    else if(data.action == "add") {
      AddItem(data.name);
    }
    else if(data.action == "delete") {
      DeleteItem(data.name);
    }
  }
  ws.onclose = setupSocket
}

function DispatchText(){
  var userInput = document.getElementById("message").value;
  document.getElementById("message").value = "";
  if(userInput == "" || list.indexOf(userInput) != -1) return;
  AddItem(userInput);
  list.push(userInput);
  var dispatch = { };
  dispatch.action = "add";
  dispatch.name = userInput;
  ws.send(JSON.stringify(dispatch));
}

function AddItem(item) {
  div = document.createElement("div");
  div.setAttribute("id", item);
  div.setAttribute("class", "item");
  p = document.createElement("span");
  p.setAttribute("class", "actualtext");
  p.innerHTML = item;
  div.appendChild(p);
  a = document.createElement("a");
  a.setAttribute("href", "javaScript:void(0);");
  a.onclick = DispatchDelete;
  a.setAttribute("class", "trash");
  img = document.createElement("img");
  img.setAttribute("src", "static/ic_action_delete.png" );
  a.appendChild(img);
  div.appendChild(a);
  document.getElementById("listbox").appendChild(div);
}

function DispatchDelete(event){
  var div = event.target.parentNode.parentNode;
  var item = div.querySelector(".actualtext").innerHTML;
  var dispatch = { };
  list.splice(list.indexOf(item),1)
  dispatch.action = "delete";
  dispatch.name = item;
  ws.send(JSON.stringify(dispatch));
  DeleteItem(item);
}

function HeartBeat(){
  var ping = { };
  ping.action = "ping";
  ws.send(JSON.stringify(ping));
  window.setInterval(HeartBeat, 1800000);
}

function DeleteItem(item) {
  div = document.getElementById(item);
  document.getElementById("listbox").removeChild(div);        
}
