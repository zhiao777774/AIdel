class GridView3D {
    #data = [];

    constructor() {
        this.step = 1;
        this.rpi = {};
        this.layout = {
            margin: { l: 0, r: 0, b: 0, t: 0 },
            legend: {
                x: 0.97,
                y: 0.97,
                xanchor: 'right',
                font: { size: 15 }
            },
            scene: {
                xaxis: {
                    backgroundcolor: 'rgb(200, 200, 230)',
                    gridcolor: 'rgb(255, 255, 255)',
                    showbackground: true,
                    zerolinecolor: 'rgb(255, 255, 255)',
                    nticks: 15,
                    range: [90, 0]
                    //ticktext:['90', '75', '60', '45', '30', '15', '0'],
                    //tickvals:[90, 75, 60, 45, 30, 15, 0]
                },
                yaxis: {
                    backgroundcolor: 'rgb(230, 200, 230)',
                    gridcolor: 'rgb(255, 255, 255)',
                    showbackground: true,
                    zerolinecolor: 'rgb(255, 255, 255)',
                    nticks: 15,
                    range: [0, 180]
                    //ticktext:['0', '15', '30', '45', '60', '75', '90', '105', '120', '135', '150', '165', '180'],
                    //tickvals:[0, 15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165, 180]
                },
                zaxis: {
                    backgroundcolor: 'rgb(230, 230, 200)',
                    gridcolor: 'rgb(255, 255, 255)',
                    showbackground: true,
                    zerolinecolor: 'rgb(255, 255, 255)',
                    nticks: 2,
                    range: [0, 10]
                },
                camera: {
                    eye: { x: 1, y: 2, z: 1.8 }
                }
            }
        };

        this.lock = false;
    }

    initialize() {
        this.#data = [];
        Plotly.newPlot('model-3d', [{
            x: [45], y: [180], z: [0],
            hoverinfo: 'text',
            mode: 'markers',
            marker: { size: 10 },
            type: 'scatter3d'
        }], this.layout);
    }

    generate(model) {
        console.log(model);
        if (this.lock) return;

        this.height = 180;
        this.width = 90;
        this.resolution = 15;

        this.layout.scene.xaxis = {
            nticks: this.resolution,
            range: [this.width, 0]
        };

        this.layout.scene.yaxis = {
            nticks: this.resolution,
            range: [0, this.height]
        };

        const index = this.#data.findIndex(({ name }) => name === `T${this.step}`);
        const x = this.width / 2,
            y = this.height - this.resolution * (this.step - 1);
        if (index < 0) {
            this.rpi = { x, y };
            this.#data.push({
                name: `T${this.step}`,
                text: `T${this.step}`,
                x: [x], y: [y], z: [0],
                hoverinfo: 'text',
                mode: 'markers',
                marker: { size: 10 },
                type: 'scatter3d',
                obj: []
            });
        } else {
            this.#data[index].x = [x];
            this.#data[index].y = [y];
            this.#data[index].z = [0];
            this.#data[index].obj = [];
        }

        $('#position').text(`T${this.step}(${x},${y})`);

        model.obstacles.forEach(({
            class: clsName, distance, angle, coordinate
        }) => this.insert({
            scale: model.width / this.width,
            clsName, distance, angle, coordinate
        }));

        console.log(this.#data);
        this.#writeResult();

        Plotly.newPlot('model-3d', this.#data, this.layout);
        /*.then((gd) => {
            Plotly.toImage(gd, { height: 80, width: 80 })
                .then((url) => $(`#model-img-T${this.step}`)
                    .attr('src', url));
        });*/
    }

    insert({ scale, clsName, distance, angle, coordinate }) {
        const { lb, rb } = coordinate;
        lb.x /= scale;
        lb.y /= scale;
        rb.x /= scale;
        rb.y /= scale;

        const xCenter = (lb.x + rb.x) / 2;
        let y = this.rpi.y - distance;
        y += this.resolution * (this.step - 1);
        y = Math.round(y * 100) / 100;
        const radius = angle * Math.PI / 180;
        let x = this.rpi.x + (xCenter > this.rpi.x ?
            Math.tan(radius) : -Math.tan(radius)) * distance;
        x = Math.round(x * 100) / 100;

        const index = this.#data.findIndex(({ name }) => name === `T${this.step}`);
        this.#data[index].x.push(x);
        this.#data[index].y.push(y);
        this.#data[index].z.push(0);
        this.#data[index].obj.push({
            x, y, clsName,
            angle, distance
        });
    }

    readFile(model) {
        console.log(model);

        this.height = 180;
        this.width = 90;
        this.resolution = 15;

        this.layout.scene.xaxis = {
            nticks: this.resolution,
            range: [this.width, 0]
        };

        this.layout.scene.yaxis = {
            nticks: this.resolution,
            range: [0, this.height]
        };

        this.#data = [];

        const $body = $('#model-file-div div.card-body');

        Object.keys(model).forEach((n, i) => {
            const userX = this.width / 2,
                userY = this.height - this.resolution * i;
            const item = {
                name: n,
                text: n,
                x: [userX], y: [userY], z: [0],
                hoverinfo: 'text',
                mode: 'markers',
                marker: { size: 10 },
                type: 'scatter3d'
            };

            model[n].forEach(({ x, y }) => {
                item.x.push(x);
                item.y.push(y);
                item.z.push(0);
            });
            this.#data.push(item);

            let content = `
                <h5 style='font-weight: bold;'>${n}</h5>
                <table class="table" style="width: 450px;">
                    <thead>
                        <tr>
                            <th scope="col">class</th>
                            <th scope="col">x</th>
                            <th scope="col">y</th>
                            <th scope="col">angle</th>
                            <th scope="col">distance</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${
                model[n].map(({ x, y, class: clsName, angle, distance }) =>
                    `
                                    <tr>
                                        <th scope="row">${clsName}</th>
                                        <td>${x}</td>
                                        <td>${y}</td>
                                        <td>${angle}</td>
                                        <td>${distance}</td>
                                    </tr>
                                `)
                }
                    </tbody>
                </table>
            `;
            content = content.replace(new RegExp(',', 'g'), '').trim();

            $body.append(`
                <div id="model-file-${n}">
                    ${content}
                </div>
            `);
        });

        console.log(this.#data);
        Plotly.newPlot('model-3d', this.#data, this.layout);

        this.useFile = true;
    }

    #writeResult() {
        const $body = $('#model-result-div div.card-body');
        const index = this.#data
            .findIndex(({ name }) => name === `T${this.step}`);
        let content = `
            <h5 style='font-weight: bold;'>T${this.step}</h5>
            <table class="table" style="width: 500px;">
                <thead>
                    <tr>
                        <th scope="col">class</th>
                        <th scope="col">x</th>
                        <th scope="col">y</th>
                        <th scope="col">angle</th>
                        <th scope="col">distance</th>
                    </tr>
                </thead>
                <tbody>
                    ${
            this.#data[index].obj.map(({ x, y, clsName, angle, distance }) =>
                `
                                <tr>
                                    <th scope="row">${clsName}</th>
                                    <td>${x}</td>
                                    <td>${y}</td>
                                    <td>${angle}</td>
                                    <td>${distance}</td>
                                </tr>
                            `)
            }
                </tbody>
            </table>
            <!--img id='model-img-T${this.step}'-->
        `;
        content = content.replace(new RegExp(',', 'g'), '').trim();

        if ($body.has(`#model-T${this.step}`).length) {
            $body.children(`#model-T${this.step}`)
                .empty().html(content);
        } else {
            $body.append(`
                <div id="model-T${this.step}">
                    ${content}
                </div>
            `);
        }

        $body.animate({
            scrollTop: $(`#model-T${this.step}`).offset().top
        }, 800);

        socketEmit('writeEnvironmentalModel',
            this.#data.map(({ obj }) => obj));
    }
}

class GridView2D {
    #data = [];

    constructor() {
        this.step = 1;
        this.rpi = {};
        this.lock = false;

        this.layout = {
            height: 180,
            width: 90,
            resolution: 15,
            alertArea: 100,
            scale: {
                w: 8.8,
                h: 3.6,
                r: 3.6,
                alert: (8.5 + 3.6) / 2
            },
            color: {},
            style: {
                line: 'stroke-width: 1px; stroke: rgb(212, 212, 212); shape-rendering: crispEdges;'
            }
        };

        this.layout.height *= this.layout.scale.h || 1;
        this.layout.width *= this.layout.scale.w || 1;
        this.layout.resolution *= this.layout.scale.r || 1;
        this.layout.alertArea *= this.layout.scale.alert || 1;
    }

    initialize() {
        d3.select('#model-3d').select('svg').remove();
        $('#model-3d > div#model-color-chart').remove();

        const { width, height, resolution, style } = this.layout;
        const svg = d3.select('#model-3d').append('svg')
            .attr('id', 'model-grid')
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

        svg.append('text')
            .attr('display', 'none')
            .attr('font-weight', 'bold');
    }

    generate() {
        console.log(model);
        if (this.lock) return;

        const svg = d3.select('#model-grid');
        const { width, height, resolution, scale } = this.layout;

        const index = this.#data.findIndex(({ name }) => name === `T${this.step}`);
        const x = width / 2,
            y = height - resolution * (this.step - 1), r = 2.8 * scale.r;
        if (index < 0) {
            const color = this.#randomColor(70);

            this.rpi = { x, y };
            this.#data.push({
                name: `T${this.step}`,
                x: [x], y: [y], r: [r],
                color: color,
                obj: []
            });
            this.layout.color[`T${this.step}`] = color;
        } else {
            this.#data[index].x = [x];
            this.#data[index].y = [y];
            this.#data[index].r = [r];
            this.#data[index].obj = [];
        }

        const color = this.layout.color[`T${this.step}`];
        const style = `stroke-width: 2px; stroke: ${color}; fill: ${color};`;
        const self = this;

        svg.append('circle')
            .attr('id', `rpi-T${this.step}`)
            .attr('cx', x)
            .attr('cy', y)
            .attr('r', r)
            .attr('step', `T${this.step}`)
            .attr('cls', 'rpi')
            .attr('style', style);

        svg.select('g').remove();
        svg.selectAll('circle')
            .on('mousemove', function () {
                const target = d3.select(this);
                const step = target.attr('step'),
                    cls = target.attr('cls');
                const [x, y] = d3.mouse(this);

                text.attr('display', 'block')
                    .attr('x', x <= self.layout.width / 2 ? x + 15 : x - 80)
                    .attr('y', y <= self.layout.resolution / 2 ? y + 30 : y)
                    .text(`${step} - ${cls}`);

                if (target.attr('id')) {
                    const color = self.#data[
                        self.#data.findIndex(({ name }) => name === step)
                    ].color;
                    const style = `stroke-width: 2px; stroke: black; fill: ${color};`;
                    svg.selectAll('circle').filter(function () {
                        return d3.select(this).attr('step') === step;
                    }).attr('style', style);
                }
            }).on('mouseout', function () {
                text.attr('display', 'none');

                const target = d3.select(this);
                const step = target.attr('step');
                if (target.attr('id')) {
                    const color = self.#data[
                        self.#data.findIndex(({ name }) => name === step)
                    ].color;
                    const style = `stroke-width: 2px; stroke: ${color}; fill: ${color};`;
                    svg.selectAll('circle').filter(function () {
                        return d3.select(this).attr('step') === step;
                    }).attr('style', style);
                }
            });
        const ripples = svg.append('g');
        svg.selectAll('circle')
            .filter(function () {
                const len = self.#data.length;
                return this.id === `rpi-${self.#data[len - 1].name}`;
            })
            .each(_transition);

        model.obstacles.forEach(({
            class: clsName, distance, angle, coordinate
        }) => this.insert({
            scale: model.width / width,
            clsName, distance, angle, coordinate
        }));

        svg.selectAll('circle').filter(function () {
            return !this.id && this.step === `T${self.step}`;
        }).remove();

        svg.data(this.#data[index].obj)
            .enter().append('circle')
            .attr('cx', (d) => d.x * scale.w)
            .attr('cy', (d) => d.y - resolution * scale.r)
            .attr('r', (d) => d.r)
            .attr('step', `T${this.step}`)
            .attr('cls', (d) => d.clsName)
            .attr('style', style);

        const colorChart = this.#data.map(({ name, color }) => {
            return `
                <div>
                    <label class="color-chart" style="background: ${color};"></label>
                    <label>${name}</label>
                </div>
            `;
        }).join('\n');

        $('#model-3d > div#model-color-chart').remove();
        $('#model-3d').append(`
            <div id="model-color-chart" style="width: 80px; left: ${width}px">
                ${colorChart}
            </div>
        `);

        $('#position').text(`T${this.step}(${x},${y})`);

        console.log(this.#data);
        this.#writeResult();

        function _transition() {
            const target = d3.select(this);
            const x = target.attr('cx') || target.attr('x'),
                y = target.attr('cy') || target.attr('y'),
                r = target.attr('r') || target.attr('height'),
                step = target.attr('step');
            const color = self.layout.color[step];
            const style = `stroke-width: 2px; stroke: ${color}; fill: ${color};`;

            ripples.append('path')
                .attr('transform', 'translate(' + [x, y] + ')')
                .attr('d', d3.arc()
                    .innerRadius(0)
                    .outerRadius(r)
                    .startAngle(-Math.PI * 0.35)
                    .endAngle(Math.PI * 0.35))
                .attr('opacity', .7)
                .attr('fill-opacity', .4)
                .attr('style', style)
                .transition()
                .duration(() => 50 * 100) //調整波紋持續時間
                .ease(d3.easeExpOut, '1') //調整波紋速率
                .attr('d', d3.arc()
                    .innerRadius(0)
                    .outerRadius(self.layout.alertArea)
                    .startAngle(-Math.PI * 0.35)
                    .endAngle(Math.PI * 0.35)) //調整波紋大小
                .attr('opacity', 0)
                .remove();

            d3.select(this).transition().delay(300)
                .on('end', _transition); //動畫結束時再次執行_transition
        }
    }

    insert({ scale, clsName, distance, angle, coordinate }) {
        const { lb, rb } = coordinate;
        lb.x /= scale;
        lb.y /= scale;
        rb.x /= scale;
        rb.y /= scale;

        const xCenter = (lb.x + rb.x) / 2;
        let y = this.rpi.y - distance;
        y += this.resolution * (this.step - 1);
        y = Math.round(y * 100) / 100;
        const radius = angle * Math.PI / 180;
        let x = this.rpi.x + (xCenter > this.rpi.x ?
            Math.tan(radius) : -Math.tan(radius)) * distance;
        x = Math.round(x * 100) / 100;
        const r = Math.round(xCenter - lb.x);

        const index = this.#data.findIndex(({ name }) => name === `T${this.step}`);
        this.#data[index].x.push(x);
        this.#data[index].y.push(y);
        this.#data[index].r.push(r);
        this.#data[index].obj.push({
            x, y, r, clsName,
            angle, distance
        });
    }

    readFile(model) {
        console.log(model);

        this.#data = [];
        this.initialize();

        const self = this;
        const svg = d3.select('#model-grid');
        const text = svg.select('text');
        const $body = $('#model-file-div div.card-body');
        const { width, height, resolution, scale } = this.layout;

        Object.keys(model).forEach((n, i) => {
            const userX = width / 2,
                userY = height - resolution * i,
                userR = 2.8 * scale.r;
            const color = this.#randomColor(70);
            const style = `stroke-width: 2px; stroke: ${color}; fill: ${color};`;

            const item = {
                name: n,
                x: [userX], y: [userY], r: [userR],
                color: color,
                obj: []
            };

            svg.append('circle')
                .attr('id', `rpi-${n}`)
                .attr('cx', userX)
                .attr('cy', userY)
                .attr('r', userR)
                .attr('step', n)
                .attr('cls', 'rpi')
                .attr('style', style);
            /*svg.append('image')
                .attr('id', `rpi-${n}`)
                .attr('x', userX)
                .attr('y', userY)
                .attr('width', 30)
                .attr('height', 30)
                .attr('href', 'http://120.125.83.10:8090/static/assets/img/user2.png')
                .attr('step', n)
                .attr('cls', 'rpi')
                .attr('style', style);*/

            model[n].forEach(({ x, y, r = 4 * scale.r, class: clsName }) => {
                item.x.push(x);
                item.y.push(y);
                item.r.push(r);

                svg.append('circle')
                    .attr('cx', x * scale.w)
                    .attr('cy', y * scale.h - resolution * scale.r)
                    .attr('r', r)
                    .attr('step', n)
                    .attr('cls', clsName)
                    .attr('style', style);
            });
            this.#data.push(item);

            let content = `
                <h5 style='font-weight: bold;'>${n}</h5>
                <table class="table" style="width: 450px;">
                    <thead>
                        <tr>
                            <th scope="col">class</th>
                            <th scope="col">x</th>
                            <th scope="col">y</th>
                            <th scope="col">angle</th>
                            <th scope="col">distance</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${
                model[n].map(({ x, y, class: clsName, angle, distance }) =>
                    `
                                    <tr>
                                        <th scope="row">${clsName}</th>
                                        <td>${x}</td>
                                        <td>${y}</td>
                                        <td>${angle}</td>
                                        <td>${distance}</td>
                                    </tr>
                                `)
                }
                    </tbody>
                </table>
            `;
            content = content.replace(new RegExp(',', 'g'), '').trim();

            $body.append(`
                <div id="model-file-${n}">
                    ${content}
                </div>
            `);
        });

        svg.select('g').remove();
        svg.selectAll('circle')
            .on('mousemove', function () {
                const target = d3.select(this);
                const step = target.attr('step'),
                    cls = target.attr('cls');
                const [x, y] = d3.mouse(this);

                text.attr('display', 'block')
                    .attr('x', x <= self.layout.width / 2 ? x + 15 : x - 80)
                    .attr('y', y <= resolution / 2 ? y + 30 : y)
                    .text(`${step} - ${cls}`);

                if (target.attr('id')) {
                    const color = self.#data[
                        self.#data.findIndex(({ name }) => name === step)
                    ].color;
                    const style = `stroke-width: 2px; stroke: black; fill: ${color};`;
                    svg.selectAll('circle').filter(function () {
                        return d3.select(this).attr('step') === step;
                    }).attr('style', style);
                }
            }).on('mouseout', function () {
                text.attr('display', 'none');

                const target = d3.select(this);
                const step = target.attr('step');
                if (target.attr('id')) {
                    const color = self.#data[
                        self.#data.findIndex(({ name }) => name === step)
                    ].color;
                    const style = `stroke-width: 2px; stroke: ${color}; fill: ${color};`;
                    svg.selectAll('circle').filter(function () {
                        return d3.select(this).attr('step') === step;
                    }).attr('style', style);
                }
            });
        const ripples = svg.append('g');
        svg.selectAll('circle')
            .filter(function () {
                const len = self.#data.length;
                return this.id === `rpi-${self.#data[len - 1].name}`;
            })
            .each(_transition);

        const colorChart = this.#data.map(({ name, color }) => {
            return `
                <div>
                    <label class="color-chart" style="background: ${color};"></label>
                    <label>${name}</label>
                </div>
            `;
        }).join('\n');

        $('#model-3d').append(`
            <div id="model-color-chart" style="width: 80px; left: ${width}px">
                ${colorChart}
            </div>
        `);

        console.log(this.#data);
        this.useFile = true;

        function _transition() {
            const target = d3.select(this);
            const x = target.attr('cx') || target.attr('x'),
                y = target.attr('cy') || target.attr('y'),
                r = target.attr('r') || target.attr('height'),
                step = target.attr('step');
            const color = self.#data[
                self.#data.findIndex(({ name }) => name === step)
            ].color;
            const style = `stroke-width: 2px; stroke: ${color}; fill: ${color};`;

            ripples.append('path')
                .attr('transform', 'translate(' + [x, y] + ')')
                .attr('d', d3.arc()
                    .innerRadius(0)
                    .outerRadius(r)
                    .startAngle(-Math.PI * 0.35)
                    .endAngle(Math.PI * 0.35))
                .attr('opacity', .7)
                .attr('fill-opacity', .4)
                .attr('style', style)
                .transition()
                .duration(() => 50 * 100) //調整波紋持續時間
                .ease(d3.easeExpOut, '1') //調整波紋速率
                .attr('d', d3.arc()
                    .innerRadius(0)
                    .outerRadius(self.layout.alertArea)
                    .startAngle(-Math.PI * 0.35)
                    .endAngle(Math.PI * 0.35)) //調整波紋大小
                .attr('opacity', 0)
                .remove();

            d3.select(this).transition().delay(300)
                .on('end', _transition); //動畫結束時再次執行_transition
        }
    }

    #writeResult() {
        const $body = $('#model-result-div div.card-body');
        const index = this.#data
            .findIndex(({ name }) => name === `T${this.step}`);
        let content = `
            <h5 style='font-weight: bold;'>T${this.step}</h5>
            <table class="table" style="width: 500px;">
                <thead>
                    <tr>
                        <th scope="col">class</th>
                        <th scope="col">x</th>
                        <th scope="col">y</th>
                        <th scope="col">angle</th>
                        <th scope="col">distance</th>
                    </tr>
                </thead>
                <tbody>
                    ${
            this.#data[index].obj.map(({ x, y, clsName, angle, distance }) =>
                `
                                <tr>
                                    <th scope="row">${clsName}</th>
                                    <td>${x}</td>
                                    <td>${y}</td>
                                    <td>${angle}</td>
                                    <td>${distance}</td>
                                </tr>
                            `)
            }
                </tbody>
            </table>
            <!--img id='model-img-T${this.step}'-->
        `;
        content = content.replace(new RegExp(',', 'g'), '').trim();

        if ($body.has(`#model-T${this.step}`).length) {
            $body.children(`#model-T${this.step}`)
                .empty().html(content);
        } else {
            $body.append(`
                <div id="model-T${this.step}">
                    ${content}
                </div>
            `);
        }

        $body.animate({
            scrollTop: $(`#model-T${this.step}`).offset().top
        }, 800);

        socketEmit('writeEnvironmentalModel',
            this.#data.map(({ obj }) => obj));
    }

    #randomColor(brightness) {
        function randomChannel(brightness) {
            const r = 255 - brightness,
                n = 0 | ((Math.random() * r) + brightness),
                s = n.toString(16);
            return (s.length == 1) ? '0' + s : s;
        }
        return '#' + randomChannel(brightness) +
            randomChannel(brightness) + randomChannel(brightness);
    }
}

const gridview = new GridView2D();
const dynamicGenerateGridView = (model) => gridview.generate(model);

$(function () {
    $('#btnToggleReceive').click(function () {
        if ($(this).text() === '暫停接收') {
            gridview.lock = true;
            $(this).text('啟用接收');
            $('.warn-text').text('目前socket沒有連線 / socket接收已禁用');
        } else {
            gridview.lock = false;
            $(this).text('暫停接收');
            $('.warn-text').text('目前socket沒有連線');

            if (gridview.useFile) {
                gridview.useFile = false;
                gridview.initialize();
                $('#model-file-div').hide();
                $('#btnChangePosition').removeAttr('disabled');
            }
        }
    });

    if (gridview.useFile) {
        $('#btnChangePosition').attr('disabled', true);
        $('#btnToggleReceive').click();
    }

    $('#btnChangePosition').click(() => {
        gridview.step++;
        gridview.lock = true;
        $('#position').text(`T${gridview.step}`);
        $('#btnToggleReceive').attr('disabled', true);
        if ($('#btnToggleReceive').text() === '暫停接收') {
            $('#btnToggleReceive').click();
        }

        setTimeout(() => {
            gridview.lock = false;
            $('#btnToggleReceive').removeAttr('disabled');
            if ($('#btnToggleReceive').text() === '啟用接收') {
                $('#btnToggleReceive').click();
            }
        }, 3000);
    });

    $('#position').text(`T${gridview.step}`);

    const fileDivWidth = {
        max: 'calc(100vw - 1020px)',
        min: '20px'
    };
    $('#model-file-div').click(function () {
        if ($(this).width() <= 20) {
            $('#model-file-div').width(fileDivWidth.max)
                .css('cursor', '');
        }
    });

    $('#model-file-div .card-header img').click(() => {
        $('#model-file-div').width(fileDivWidth[
            $('#model-file-div').width() <= 20 ? 'max' : 'min'
        ]).css('cursor', 'pointer');

        if ($('#model-file-div').width() <= 20) {
            $('#model-file-div').css('cursor', 'pointer');
        }
    });
});