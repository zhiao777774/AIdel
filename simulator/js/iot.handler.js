let socket = undefined;

function enableSocket() {
    socket = io();
    socket.on('environmentalModel', (model) => {
        dynamicGenerateGridView(model);
    });
}

function disableSocket() {
    if (socket) {
        socket.disconnect();
        socket = undefined;
    }
}