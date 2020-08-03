const socket = io();

socket.on('environmentalModel', (model) => {
    $('.warn-text').hide();
    dynamicGenerateGridView(model);
});