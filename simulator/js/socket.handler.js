const socket = io();

socket.on('environmentalModel', (model) => {
    $('.warn-text').hide();
    dynamicGenerateGridView(model);
});

function socketEmit(event, data) {
    socket.emit(event, data);
}