document.addEventListener('DOMContentLoaded', function (){
    const webSocketClient = new WebSocket("ws://localhost7788/");

    webSocketClient.onopen = function (){
        console.log("Client connected!");
    }
})