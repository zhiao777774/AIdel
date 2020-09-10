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
    //_activateObstacles(obstacles);

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
        end = svg.select('#end');

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

    const maze = generateMaze(width, height, resolution);
    console.log(maze);
    $.ajax({
        type: 'POST',
        url: '/calculatePath',
        dataType: 'JSON',
        data: JSON.stringify({ maze }),
        headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '120.125.83.10'
        },
        success: function ({ error, directions }) {
            if (error) {
                console.log(error);
                alert('無法規劃路徑');
                return;
            }

            console.log(directions.join('->'));
            const planner = new PathPlanner(user, resolution, count, directions);
            planner.solve();
        }
    });
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

function generateMaze(width, height, resolution) {
    const maze = [];
    for (let i = 0; i <= height; i += resolution) {
        const row = [];
        for (let j = 0; j <= width; j += resolution) {
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
                row.push('S');
            } else if (id === 'end') {
                row.push('E');
            }
        }
        maze.push(row);
    }

    return maze;
}

class PathPlanner {
    constructor(user, resolution, count, directions) {
        this.user = user;
        this.resolution = resolution;
        this.directions = directions;

        this.count = count;
        this.time = 0;
        this.step = 1;
    }

    solve() {
        let i = 0;
        this._transformUserCoordinate(this.directions[i]);
        i++;
        intervalID = setInterval(() => {
            this._transformUserCoordinate(this.directions[i]);
            i++;
        }, 1000);

        timeoutID = setTimeout(() => {
            clearInterval(intervalID);
            intervalID = undefined;
            clearTimeout(timeoutID);
            timeoutID = undefined;
            isEnd = true;

            $('#info-div div.card-body').find(`div#${this.count}`)
                .append('<span style="color: crimson; font-weight: bold;">抵達終點!</span>')
                .append(`<img id='img${this.count}'>`)
                .find('h5').addClass('success');
            svgSaveAsImg(this.count);
            $('#btnSimulate').text('開始模擬');
            setTimeout(() => alert('成功抵達終點!'), 200);
        }, 1000 * this.directions.length - 1000);
    }

    _transformUserCoordinate(direction) {
        let x = Number(this.user.attr('cx')),
            y = Number(this.user.attr('cy'));
        this.oldCoord = { x: x, y: y };

        switch (direction) {
            case '^':
                y -= this.resolution; //往前走
                break;
            case 'v':
                y += this.resolution; //往下走
                break;
            case '<':
                x -= this.resolution; //往左走
                break;
            case '>':
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
}