let width = 1000,
    height = 600,
    resolution = 100,
    r = 13;
const upperLimit = 20;

function initGridView(n) {
    console.log('隨機生成障礙物' + n + '個');
    if (!n) {
        alert('請輸入生成數量');
        return;
    }

    const impCoord = {
        user: { x: width / 2, y: height },
        end: { x: resolution, y: 0 }
    };

    const style = {
        line: 'stroke-width: 1px; stroke: rgb(212, 212, 212); shape-rendering: crispEdges;',
        circle: {
            default: 'stroke-width: 2px; stroke: rgb(95, 176, 228); fill: rgb(95, 176, 228);',
            activate: 'stroke-width: 2px; stroke: rgb(33, 106, 151); fill: rgb(33, 106, 151);',
            user: 'stroke-width: 2px; stroke: rgb(214, 131, 75); fill: rgb(214, 131, 75);',
            end: 'stroke-width: 2px; stroke: rgb(218, 41, 18); fill: rgb(218, 41, 18);'
        }
    };

    const points = d3.range(n).map(() => {
        const _random = ([x, y]) => {
            //避免生成與user及end同樣座標的障礙物
            if ((x !== impCoord.user.x || y !== impCoord.user.y) &&
                (x !== impCoord.end.x || y !== impCoord.end.y))
                return [x, y];

            x = Math.round(_round(Math.random() * width, resolution));
            y = Math.round(_round(Math.random() * height, resolution));
            return _random([x, y]);
        };

        let [x, y] = _random([width / 2, height]);
        return { x: x, y: y };
    });

    d3.select('#simulate-div').select('svg').remove();
    const svg = d3.select('#simulate-div').append('svg')
        .attr('id', 'grid')
        .attr('width', width)
        .attr('height', height);

    svg.selectAll('.vertical')
        .data(d3.range(1, width / resolution))
        .enter().append('line')
        .attr('class', 'vertical')
        .attr('x1', (d) => d * resolution)
        .attr('y1', 0)
        .attr('x2', (d) => d * resolution)
        .attr('y2', height)
        .attr('style', style.line);

    svg.selectAll('.horizontal')
        .data(d3.range(1, height / resolution))
        .enter().append('line')
        .attr('class', 'horizontal')
        .attr('x1', 0)
        .attr('y1', (d) => d * resolution)
        .attr('x2', width)
        .attr('y2', (d) => d * resolution)
        .attr('style', style.line);

    const obstacles = svg.selectAll('circle')
        .data(points)
        .enter().append('circle')
        .attr('cx', (d) => d.x)
        .attr('cy', (d) => d.y)
        .attr('r', r)
        .attr('style', style.circle.default);
    _activateObstacles(obstacles);

    svg.data([{ x: impCoord.user.x, y: impCoord.user.y }])
        .append('circle')
        .attr('id', 'user')
        .attr('cx', (d) => d.x)
        .attr('cy', (d) => d.y)
        .attr('r', r)
        .attr('style', style.circle.user);

    svg.data([{ x: impCoord.end.x, y: impCoord.end.y }])
        .append('circle')
        .attr('id', 'end')
        .attr('cx', (d) => d.x)
        .attr('cy', (d) => d.y)
        .attr('r', r)
        .attr('style', style.circle.end);

    const ripples = svg.append('g');
    svg.selectAll('circle').filter(function () {
        return !this.id;
    }).each(_transition);

    const text = svg.append('text')
        .attr('display', 'none')
        .attr('font-weight', 'bold');
    svg.on('mousemove', function () {
        let [x, y] = d3.mouse(this);

        text.attr('display', 'block')
            .attr('x', x + 15)
            .attr('y', y <= resolution / 2 ? y + 30 : y)
            .text('(' + x + ' , ' + y + ')');
    }).on('mouseout', () => text.attr('display', 'none'));

    function _round(p, n) {
        return p % n < n / 2 ? p - (p % n) : p + n - (p % n);
    }

    function _transition({ x, y }) {
        ripples.append('circle')
            .attr('class', 'ripple')
            .attr('cx', x)
            .attr('cy', y)
            .attr('r', r)
            .attr('opacity', .5)
            .attr('fill-opacity', .2)
            .attr('style', style.circle.default)
            .transition()
            .duration(() => 50 * 100) //調整波紋持續時間
            .ease(d3.easeExpOut, '.05') //調整波紋速率
            .attr('r', r + 50) //調整波紋大小
            .attr('opacity', 0)
            .remove();

        d3.select(this).transition().delay(300)
            .on('end', _transition); //動畫結束時再次執行_transition
    }

    function _activateObstacles(obstacles, n = 2) {
        for (let i = 0; i < n; i++) {
            const index = Math.floor(Math.random() * (obstacles.size() - 1));
            obstacles.each(function (obstacle, i) {
                if (i === index) {
                    d3.select(this).attr('class', 'activate')
                        .attr('style', style.circle.activate);
                    return true;
                }
            });
        }
    }
}

let intervalID = undefined;
let timeoutID = undefined;
let isEnd = false;
function simulate(count) {
    if (isEnd) {
        isEnd = false;
        initGridView(Number($('#n-random').val()) ||
            Math.floor(Math.random() * (upperLimit - 1)) + 1);
    }

    const svg = d3.select('#simulate-div').select('svg'),
        user = svg.select('#user'),
        end = svg.select('#end'),
        $body = $('#info-div div.card-body');
    let step = 1, time = 0;

    $('#info-div div.card-body').append(`
        <div id='${count}'>
            <h5 style='font-weight: bold;'>第${count}次模擬</h5>
            <span>
                ${svg.selectAll('circle').filter(function () {
        return !this.id && (!this.className.animVal ||
            this.className.animVal === 'activate');
    }).size()}個障礙物
            </span><br />
            <span class='step'></span><br />
            <span class='time'></span>
        </div>
        <hr />
    `).animate({
        scrollTop: $(`div#${count}`).offset().top
    }, 800);


    const dodger = new Dodger(user, end, width, height, resolution, count);
    dodger.start();

    /*
        const planner = new PathPlanner(user, end);
        _calculate();
        intervalID = setInterval(_calculate, 1000);
    
        function _calculate() {
            $body.find(`div#${count}`)
                .children('.step')
                .text(`共走了${step++}步`);
            $body.find(`div#${count}`)
                .children('.time')
                .text(`共花費${time++}秒`);
    
            const { x, y } = planner.calculate();
    
            //更換位置
            user.attr('cx', x).attr('cy', y);
            //判斷是否抵達終點
            isEnd = user.attr('cx') === end.attr('cx') &&
                user.attr('cy') === end.attr('cy');
            //繪製行走路徑
            planner.draw({ x: x, y: y });
            //抵達終點
            if (isEnd) {
                clearInterval(intervalID);
                intervalID = undefined;
    
                $body.find(`div#${count}`)
                    .append('<span style="color: crimson; font-weight: bold;">抵達終點!</span>')
                    .append(`<img id='img${count}'>`)
                    .find('h5').addClass('success');
                svgSaveAsImg(count);
                $('#btnSimulate').text('開始模擬');
                setTimeout(() => alert('成功抵達終點!'), 200);
            }
        }
    */
}

function svgSaveAsImg(id) {
    let svg = '<svg id="grid" width="1000" height="600" ' +
        'version="1.1" xmlns="http://www.w3.org/2000/svg">' +
        d3.select('svg').node().innerHTML + '</svg>';
    d3.select('.card-body')
        .select(`div:nth-of-type(${id})`)
        .select(`#img${id}`)
        .attr('src', `data:image/svg+xml;base64,${btoa(svg)}`);
}
/*
class PathPlanner {
    constructor(user, end) {
        this.user = user;
        this.end = end;

        this.prioirty = undefined;
        this.restriction = {};
        this.restriction.top = this.restriction.down =
            this.restriction.left = this.restriction.right = false;
    }

    calculate() {
        let x = Number(this.user.attr('cx')),
            y = Number(this.user.attr('cy'));
        const obstacles = [];
        this.oldCoord = { x: x, y: y }

        d3.select('#simulate-div').select('svg')
            .selectAll('circle').filter(function () {
                return !this.id && (!this.className.animVal ||
                    this.className.animVal === 'activate');
            }).each(({ x, y }) => {
                obstacles.push({ x: Math.round(x), y: Math.round(y) });
            });

        const hasObstacles = (func) => obstacles.filter(func).length > 0;
        const hasObstacle = {
            above: (x, y) => hasObstacles((p) => p.x === x && p.y === y - resolution),
            below: (x, y) => hasObstacles((p) => p.x === x && p.y === y + resolution),
            left: (x, y) => hasObstacles((p) => p.y === y && p.x === x - resolution),
            right: (x, y) => hasObstacles((p) => p.y === y && p.x === x + resolution)
        };

        if (this.priority) {
            console.log(`優先往${this.priority}走`);
            const coord = this.priorPath(x, y);
            x = coord.x;
            y = coord.y;
        } else {
            if (y <= 0 || hasObstacle.above(x, y)) { //如果y座標位於上邊界 或 前方有障礙物
                if (hasObstacle.left(x, y)) { //如果左方有障礙物
                    if (hasObstacle.right(x, y)) { //如果右方有障礙物
                        y += resolution; //往下走
                        this.restriction.top = true; //標記為下次不能往上走
                    } else { //右方沒有障礙物
                        if (hasObstacle.below(x, y)) { //如果下方有障礙物
                            x += resolution; //往右走
                            this.restriction.left = true; //標記為下次不能往左走
                        } else { //下方沒有障礙物
                            if (y >= height) { //如果y座標位於下邊界
                                x += resolution; //往右走
                                this.restriction.left = true; //標記為下次不能往左走
                            } else {
                                y += resolution; //往下走
                                this.restriction.top = true; //標記為下次不能往上走
                            }
                        }
                    }
                } else { //左方沒有障礙物
                    if (this.restriction.left) { //不能往左走
                        if (hasObstacle.below(x, y)) { //如果下方有障礙物
                            x += resolution; //往右走
                            this.restriction.left = true; //標記為下次不能往左走
                        } else {
                            if (y >= height) { //如果y座標位於下邊界
                                x += resolution; //往右走
                                this.restriction.left = true; //標記為下次不能往左走
                            } else {
                                y += resolution; //往下走
                                this.restriction.top = true; //標記為下次不能往上走
                                this.restriction.left = false;
                            }
                        }
                    } else {
                        x -= resolution; //往左走
                    }
                }
            } else { //y座標沒有位於上邊界 且 前方也沒有障礙物
                if (this.restriction.top) {  //不能往上走
                    if (hasObstacle.left(x, y)) { //如果左方有障礙物
                        y += resolution; //往下走
                    } else {
                        x -= resolution; //往左走
                    }
                    this.restriction.top = false;
                    this.restriction.left = false;

                    if (hasObstacle.left(x, y)) { //如果左方有障礙物
                        this.priority = 'down'; //下次優先往下走
                        this.restriction.top = true;
                    } else {
                        this.priority = 'left'; //下次優先往左走
                    }
                } else { //能往上走
                    y -= resolution; //往上走
                    this.restriction.top = false;
                }
            }
        }

        return { x: x, y: y };
    }

    priorPath(x, y) {
        switch (this.priority) {
            case 'top':
                y -= resolution; //往前走
                break;
            case 'down':
                y += resolution; //往下走
                break;
            case 'left':
                x -= resolution; //往左走
                break;
            case 'right':
                x += resolution; //往右走
                break;
        }

        this.priority = undefined;
        return { x: x, y: y };
    }

    draw(newCoord) {
        const svg = d3.select('#simulate-div').select('svg'),
            line = svg.append('line');
        const oldCoord = this.oldCoord;

        if (oldCoord.x === newCoord.x && oldCoord.y !== newCoord.y) {
            line.attr('class', 'vertical path');
        } else {
            line.attr('class', 'horizontal path');
        }

        line.attr('x2', oldCoord.x)
            .attr('y2', oldCoord.y)
            .attr('x1', newCoord.x)
            .attr('y1', newCoord.y)
            .attr('style', `stroke-width: ${(oldCoord.x !== newCoord.x && newCoord.y === oldCoord.y &&
                newCoord.y === Number(svg.style('height').substring(0, 3))) ? 10 : 3}px; ` +
                'stroke: rgb(248, 18, 18); shape-rendering: crispEdges;');
    }
}
*/
class Dodger {
    constructor(user, end, width, height, resolution, count) {
        this.user = user;
        this.end = end;
        this.width = width;
        this.height = height;
        this.resolution = resolution;

        this.count = count;
        this.time = 0;
        this.step = 1;
    }

    start() {
        const width = this.width,
            resolution = this.resolution,
            cx = Number(this.user.attr('cx')),
            cy = Number(this.user.attr('cy'));
        const bound = {
            lt: {
                x: (cx - resolution * 4) < 0 ? 0 : (cx - resolution * 4),
                y: (cy - resolution * 3) < 0 ? 0 : (cy - resolution * 3)
            },
            rt: {
                x: (cx + resolution * 4) > width ? width : (cx + resolution * 4),
                y: (cy - resolution * 3) < 0 ? 0 : (cy - resolution * 3)
            },
            lb: {
                x: (cx - resolution * 3) < 0 ? 0 : (cx - resolution * 3),
                y: cy
            },
            rb: {
                x: (cx + resolution * 4) > width ? width : (cx + resolution * 4),
                y: cy
            }
        };
        this.oldCoord = { x: cx, y: cy };

        let maze = [];
        for (let i = bound.lt.y; i <= bound.lb.y; i += resolution) {
            const row = [];
            for (let j = bound.lt.x; j <= bound.rt.x; j += resolution) {
                const circles = d3.select('#simulate-div').select('svg')
                    .selectAll('circle').filter(function () {
                        return Number(d3.select(this).attr('cx')) === j &&
                            Number(d3.select(this).attr('cy')) === i;
                    });

                const len = circles.size();
                let id = '';
                circles.each(function () { id = this.id; });

                if (len === 0) {
                    row.push(' ');
                } else if (!id) {
                    row.push('#');
                } else if (id === 'user') {
                    row.push('O');
                } else if (id === 'end') {
                    row.push('X');
                }
            }
            maze.push(row);
        }

        isEnd = this._containEnd(maze);
        if (!isEnd) maze = this._setEndCoordinate(maze, cx, cy, resolution);
        console.log(maze);

        const planner = new PathPlanner(maze);
        planner.calculate();
        const directions = planner.directions;

        let i = 0;
        this._transformUserCoordinate(directions.charAt(i));
        i++;
        intervalID = setInterval(() => {
            this._transformUserCoordinate(directions.charAt(i));
            i++;
        }, 1000);

        if (!isEnd) {
            timeoutID = setTimeout(() => {
                clearInterval(intervalID);
                intervalID = undefined;
                clearTimeout(timeoutID);
                timeoutID = undefined;
                this.start();
            }, 1000 * directions.length);
        } else {
            timeoutID = setTimeout(() => {
                clearInterval(intervalID);
                intervalID = undefined;
                clearTimeout(timeoutID);
                timeoutID = undefined;

                $('#info-div div.card-body').find(`div#${this.count}`)
                    .append('<span style="color: crimson; font-weight: bold;">抵達終點!</span>')
                    .append(`<img id='img${this.count}'>`)
                    .find('h5').addClass('success');
                svgSaveAsImg(this.count);
                $('#btnSimulate').text('開始模擬');
                setTimeout(() => alert('成功抵達終點!'), 200);
            }, 1000 * directions.length - 1000);
        }
    }

    _transformUserCoordinate(direction) {
        let x = Number(this.user.attr('cx')),
            y = Number(this.user.attr('cy'));
        this.oldCoord = { x: x, y: y };

        switch (direction) {
            case 'U':
                y -= this.resolution; //往前走
                break;
            case 'D':
                y += this.resolution; //往下走
                break;
            case 'L':
                x -= this.resolution; //往左走
                break;
            case 'R':
                x += this.resolution; //往右走
                break;
        }

        const $body = $('#info-div div.card-body');
        $body.find(`div#${this.count}`)
            .children('.step')
            .text(`共走了${this.step++}步`);
        $body.find(`div#${this.count}`)
            .children('.time')
            .text(`共花費${this.time++}秒`);

        this.user.attr('cx', x);
        this.user.attr('cy', y);
        this._drawPath({ x, y });
    }

    _drawPath(newCoord) {
        const svg = d3.select('#simulate-div').select('svg'),
            line = svg.append('line');
        const oldCoord = this.oldCoord;

        if (oldCoord.x === newCoord.x && oldCoord.y !== newCoord.y) {
            line.attr('class', 'vertical path');
        } else {
            line.attr('class', 'horizontal path');
        }

        line.attr('x2', oldCoord.x)
            .attr('y2', oldCoord.y)
            .attr('x1', newCoord.x)
            .attr('y1', newCoord.y)
            .attr('style', `stroke-width: ${(oldCoord.x !== newCoord.x && newCoord.y === oldCoord.y &&
                newCoord.y === Number(svg.style('height').substring(0, 3))) ? 10 : 3}px; ` +
                'stroke: rgb(248, 18, 18); shape-rendering: crispEdges;');
    }

    _containEnd(maze) {
        for (const row of maze) {
            for (const symbol of row) {
                if (symbol === 'X') {
                    return true;
                }
            }
        }
        return false;
    }

    _setEndCoordinate(maze, cx, cy, resolution) {
        let isFindEnd = false;

        if (Number(this.end.attr('cx')) <= cx) {
            for (const [j, row] of maze.entries()) {
                for (const [i, symbol] of row.entries()) {
                    const symbolX = cx - (Math.floor(maze[0].length / 2) * resolution) + (resolution * i);
                    if (symbolX > cx) break;

                    if (symbol === ' ') {
                        maze[j][i] = 'X';
                        break;
                    }
                }

                if (maze[j].indexOf('X') >= 0) {
                    isFindEnd = true;
                    break;
                }
            }

            if (!isFindEnd) {
                for (const [j, row] of maze.entries()) {
                    for (const [i, symbol] of row.entries()) {
                        const symbolX = cx - (Math.floor(maze[0].length / 2) * resolution) + (resolution * i);
                        if (symbolX <= cx) continue;

                        if (symbol === ' ') {
                            maze[j][i] = 'X';
                            break;
                        }
                    }
                }
            }
        } else {
            for (const [j, row] of maze.entries()) {
                for (const [i, symbol] of row.entries()) {
                    const symbolX = cx - (Math.floor(maze[0].length / 2) * resolution) + (resolution * i);
                    if (symbolX <= cx) continue;

                    if (symbol === ' ') {
                        maze[j][i] = 'X';
                        break;
                    }
                }

                if (maze[j].indexOf('X') >= 0) {
                    isFindEnd = true;
                    break;
                }
            }

            if (!isFindEnd) {
                for (const [j, row] of maze.entries()) {
                    for (const [i, symbol] of row.entries()) {
                        const symbolX = cx - (Math.floor(maze[0].length / 2) * resolution) + (resolution * i);
                        if (symbolX > cx) break;

                        if (symbol === ' ') {
                            maze[j][i] = 'X';
                            break;
                        }
                    }
                }
            }
        }

        return maze;
    }
}

class PathPlanner {
    constructor(maze) {
        this.seq = new Queue();
        this.seq.put('');
        this.maze = maze;
        this.directions = '';
    }

    calculate() {
        let s = '';
        while (!this.end(s)) {
            s = this.seq.pop();
            for (const direction of ['L', 'R', 'U', 'D']) {
                const data = s + direction;
                if (this.validate(data)) {
                    this.seq.put(data);
                }
            }
        }
    }

    end(directions) {
        const maze = this.maze;
        const len = maze.length;
        let start = 0;

        maze[len - 1].forEach((symbol, i) => {
            if (symbol === 'O') {
                start = i;
                return false;
            }
        });

        let x = start,
            y = len - 1;
        for (const direction of directions) {
            if (direction === 'L')
                x -= 1;
            else if (direction === 'R')
                x += 1;
            else if (direction === 'U')
                y -= 1;
            else if (direction === 'D')
                y += 1;
        }

        if (maze[y][x] === 'X') {
            console.log('Found: ' + directions);
            this.directions = directions;
            return true;
        }
        return false;
    }

    validate(directions) {
        const maze = this.maze;
        const len = maze.length;
        let start = 0;

        maze[len - 1].forEach((symbol, i) => {
            if (symbol === 'O') {
                start = i;
                return false;
            }
        });

        let x = start,
            y = len - 1;
        for (const direction of directions) {
            if (direction === 'L')
                x -= 1;
            else if (direction === 'R')
                x += 1;
            else if (direction === 'U')
                y -= 1;
            else if (direction === 'D')
                y += 1;

            if (!((0 <= x && x < maze[0].length) && (0 <= y && y < len)))
                return false;
            else if (maze[y][x] === '#')
                return false;
        }

        return true;
    }

    print_maze() {
        const maze = this.maze;
        const len = maze.length;
        let start = 0;

        maze[len - 1].forEach((symbol, i) => {
            if (symbol === 'O') {
                start = i;
                return false;
            }
        });

        let x = start,
            y = len - 1;
        const sequence = new Set();
        for (const direction of this.directions) {
            if (direction === 'L')
                x -= 1;
            else if (direction === 'R')
                x += 1;
            else if (direction === 'U')
                y -= 1;
            else if (direction === 'D')
                y += 1;

            sequence.add([y, x].toString());
        }

        let result = '';
        for (const [y, row] of maze.entries()) {
            for (const [x, col] of row.entries()) {
                if (sequence.has([y, x].toString()))
                    result += '+ ';
                else
                    result += col + ' ';
            }
            result += '\r\n';
        }
        console.log(result);
    }
}

class Queue {
    constructor() {
        this.queue = [];
    }

    put(val) {
        this.queue.unshift(val);
    }

    pop() {
        return this.queue.pop();
    }
}