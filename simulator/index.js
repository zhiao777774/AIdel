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

    socket.on('writeEnvironmentalModel', (data) => {
        const path = __dirname + 'data/environmentalModel.txt';
        if (fs.existsSync(path))
            fs.mkdirSync(path)

        const fst = fs.createWriteStream(path);
        data.forEach((item, i) => {
            fst.write(`T${i + 1}\r\n`);
            fst.write('---------------\r\n');
            fst.write('class   x   y   angle   distance\r\n');
            item.forEach(({ x, y, clsName, angle, distance }) => {
                fst.write(clsName + '   ');
                fst.write(x + '   ');
                fst.write(y + '   ');
                fst.write(angle + '   ');
                fst.write(distance + '\r\n');
            });
            fst.write('\r\n');
        });
    });

    socket.on('disconnect', () => console.log(`socket disconnect id: ${socket.id}`));
});

server.listen(port, () => console.log('Simulator is start!'));

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