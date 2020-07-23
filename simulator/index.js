const express = require('express');
const app = express();
const server = require('http').Server(app);
const io = require('socket.io')(server);
const fs = require('fs');
const port = 8090;

app.use('/js', express.static('js'));
app.use('/css', express.static('css'));

io.on('connection', (socket) => {
    console.log(`socket connect id: ${socket.id}`);

    socket.on('receiveEnvironmentalModel', (model) => {
        console.log('Environmental model received.');
        io.emit('environmentalModel', model);
    });

    socket.on('disconnect', () => console.log(`socket disconnect id: ${socket.id}`));
});

server.listen(port);

app.get('/', (req, res) => {
    fs.readFile(__dirname + '/index.html', (err, data) => {
        if (err) {
            res.writeHead(404, {
                'Content-Type': 'text/html'
            });
            return res.end('404 Not Found');
        }

        res.writeHead(200, {
            'Content-Type': 'text/html'
        });
        res.write(data);
        return res.end();
    });
});

process.on('SIGINT', () => {
    console.log('Process is terminated');
    process.exit();
});