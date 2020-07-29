const socket = io();

socket.on('environmentalModel', (model) => {
    dynamicGenerateGridView(model);
});