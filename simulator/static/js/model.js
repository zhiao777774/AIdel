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
            xScale: model.width / this.width,
            yScale: model.height / this.height,
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

    insert({ xScale, yScale, clsName, distance, angle, coordinate }) {
        const { lb, rb } = coordinate;
        lb.x /= xScale;
        lb.y /= yScale;
        rb.x /= xScale;
        rb.y /= yScale;

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
            alertArea: 60,
            scale: {
                w: 8.9,
                h: 3.5,
                r: 3.5,
                alert: (8.5 + 3.5) / 2
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
        this.layout.minAlertArea = this.layout.resolution * 3.3;
        this.layout.alertAreaAngle = Math.PI * 0.18;
    }

    initialize() {
        this.#data = [];
        $('#model-3d > svg').remove();
        $('#model-3d').children('#model-color-chart').remove();

        const { width, height, resolution, scale, style } = this.layout;
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

        svg.selectAll('.coordinateY')
            .data(d3.range(0, height / resolution + 2))
            .enter().append('text')
            .attr('class', 'coordinateY')
            .attr('x', width - 60)
            .attr('y', (d) => d * resolution - 5)
            .attr('font-weight', 'bold')
            .text((d) => Math.round((height / resolution - d) * resolution / scale.r) + ' cm');

        svg.append('text')
            .attr('id', 'tooltip')
            .attr('display', 'none')
            .attr('font-weight', 'bold');
    }

    generate(model) {
        console.log(model);
        if (this.lock) return;

        const self = this;
        const svg = d3.select('#model-grid');
        const text = svg.select('text#tooltip');
        const { width, height, resolution, scale, 
            alertArea, alertAreaAngle, minAlertArea } = this.layout;

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
            $('#model-grid').children(`circle#rpi-T${self.step}`).remove();
        }

        const color = this.layout.color[`T${this.step}`];
        const style = `stroke-width: 2px; stroke: ${color}; fill: ${color};`;

        model.obstacles.forEach(({
            class: clsName, distance, angle, coordinate
        }) => this.insert({
            xScale: model.width / width,
            yScale: model.height / height,
            clsName, distance, angle, coordinate
        }));

        $('#model-grid').children(`circle[step="T${this.step}"]`).remove();
        svg.selectAll('circle').filter(function () {
            return !this.id && this.step === `T${self.step}`;
        }).data(this.#data[
            this.#data.findIndex(({ name }) => name === `T${this.step}`)
        ].obj)
            .enter().append('circle')
            .attr('cx', (d) => d.x)
            .attr('cy', (d) => d.y)
            .attr('r', (d) => d.r || 4 * scale.r)
            .attr('step', `T${this.step}`)
            .attr('cls', (d) => d.clsName)
            .attr('style', style);

        svg.append('circle')
            .attr('id', `rpi-T${this.step}`)
            .attr('cx', x)
            .attr('cy', y)
            .attr('r', r)
            .attr('step', `T${this.step}`)
            .attr('cls', 'rpi')
            .attr('style', style);

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
                    svg.selectAll('circle').filter(function () {
                        return d3.select(this).attr('step') === step;
                    }).attr('style', `stroke-width: 2px; stroke: black; fill: ${color};`);
                }
            })
            .on('mouseout', function () {
                text.attr('display', 'none');

                const target = d3.select(this);
                const step = target.attr('step');
                if (target.attr('id')) {
                    const color = self.#data[
                        self.#data.findIndex(({ name }) => name === step)
                    ].color;
                    svg.selectAll('circle').filter(function () {
                        return d3.select(this).attr('step') === step;
                    }).attr('style', `stroke-width: 2px; stroke: ${color}; fill: ${color};`);
                }
            });

        svg.select('g').remove();
        const ripples = svg.append('g');
        svg.selectAll('circle').filter(function () {
            const len = self.#data.length;
            return this.id === `rpi-${self.#data[len - 1].name}`;
        }).each(_transition);
        _appendMinAlertArea(this.step);

        const colorChart = this.#data.filter(({ name }) => name !== 'Real')
            .map(({ name, color }) => {
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

        $('#position').text(`T${this.step}(${Math.round(x)},${Math.round(y)})`);

        console.log(this.#data);
        this.#writeResult();
        this.#writeImage(model.image);

        function _transition() {
            const target = d3.select(this);
            const x = target.attr('cx') || target.attr('x'),
                y = target.attr('cy') || target.attr('y'),
                step = target.attr('step');
            const color = self.layout.color[step];
            const style = `stroke-width: 2px; stroke: ${color}; fill: ${color};`;

            ripples.append('path')
                .attr('transform', 'translate(' + [x, y] + ')')
                .attr('d', d3.arc()
                    .innerRadius(minAlertArea)
                    .outerRadius(minAlertArea + 10)
                    .startAngle(-alertAreaAngle)
                    .endAngle(alertAreaAngle))
                .attr('opacity', .7)
                .attr('fill-opacity', .4)
                .attr('style', style)
                .transition()
                .duration(() => 50 * 100) //調整波紋持續時間
                .ease(d3.easeExpOut, '1') //調整波紋速率
                .attr('d', d3.arc()
                    .innerRadius(minAlertArea)
                    .outerRadius(alertArea)
                    .startAngle(-alertAreaAngle)
                    .endAngle(alertAreaAngle)) //調整波紋大小
                .attr('opacity', 0)
                .remove();

            d3.select(this).transition().delay(300)
                .on('end', _transition); //動畫結束時再次執行_transition
        }

        function _appendMinAlertArea(step) {
            const target = svg.select(`circle#rpi-T${step}`);
            svg.select('path#min-line').remove();
            svg.append('path')
                .attr('id', 'min-line')
                .attr('transform', 'translate(' +
                    [target.attr('cx'), target.attr('cy')] + ')')
                .attr('d', d3.arc()
                    .innerRadius(r)
                    .outerRadius(minAlertArea)
                    .startAngle(-alertAreaAngle)
                    .endAngle(alertAreaAngle))
                .attr('opacity', .7)
                .attr('fill-opacity', .4)
                .attr('style', 'stroke-width: 2px; stroke: red; fill: red;');
        }
    }

    insert({ xScale, yScale, clsName, distance, angle, coordinate }) {
        const { lb, rb } = coordinate;
        lb.x /= xScale;
        lb.y /= yScale;
        rb.x /= xScale;
        rb.y /= yScale;

        const xCenter = (lb.x + rb.x) / 2;

        let y = this.rpi.y - distance * this.layout.scale.h;
        y += this.layout.resolution * (this.step - 1);
        //y -= this.layout.resolution * ((distance - 30) / 10);
        y = Math.round(y * 100) / 100;
        const radius = angle * Math.PI / 180;
        let x = this.rpi.x + (xCenter > this.rpi.x ?
            Math.tan(radius) : -Math.tan(radius)) * distance;
        x = -(this.layout.resolution * this.layout.scale.r / 1.5 +
            (xCenter > this.rpi.x ? -x : +x));
        if (xCenter > this.rpi.x) x = this.layout.width - x;
        if (x < 0) x += this.layout.width;
        x = Math.round(x * 100) / 100;
        const r = Math.round((xCenter - lb.x) / this.layout.scale.w);

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
        this.initialize();

        const self = this;
        const svg = d3.select('#model-grid');
        const text = svg.select('text#tooltip');
        const $body = $('#model-file-div div.card-body');
        const { width, height, resolution, scale, 
            alertArea, alertAreaAngle, minAlertArea } = this.layout;

        if (model['Real']) {
            const obj = [];
            model['Real'].forEach(({ x, y, r = 4 * scale.r, class: clsName }) => {
                svg.append('circle')
                    .attr('cx', x * scale.w)
                    .attr('cy', y * scale.h)
                    .attr('r', r)
                    .attr('step', 'Real')
                    .attr('cls', clsName)
                    .attr('style', 'stroke-width: 2px; stroke: black; fill: black;');

                obj.push({
                    clsName,
                    x: x * scale.w,
                    y: y * scale.h,
                    r: 'x',
                    angle: 'x',
                    distance: 'x'
                });
            });

            if (Object.keys(model).length === 1) {
                this.lock = false;
                this.useFile = false;
                this.#data.push({
                    name: 'Real',
                    x: obj.map(({ x }) => x),
                    y: obj.map(({ y }) => y),
                    r: obj.map(({ r }) => r),
                    color: 'balck',
                    obj
                });

                $('#btnToggleReceive').text('暫停接收');
                $('.warn-text').text('目前socket沒有連線');
                $('#model-file-div').hide();
                $('#btnChangePosition').removeAttr('disabled');

                console.log(this.#data);
                return;
            }

            delete model['Real'];
        }

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

            model[n].forEach(({ x, y, r = 4 * scale.r, class: clsName }) => {
                item.x.push(x);
                item.y.push(y);
                item.r.push(r);

                svg.append('circle')
                    .attr('cx', x <= width / scale.w ? x * scale.w : x)
                    .attr('cy', y <= height / scale.h ?
                        y * scale.h - resolution * scale.r : y)
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
                    svg.selectAll('circle').filter(function () {
                        return d3.select(this).attr('step') === step;
                    }).attr('style', `stroke-width: 2px; stroke: black; fill: ${color};`);
                }
            })
            .on('mouseout', function () {
                text.attr('display', 'none');

                const target = d3.select(this);
                const step = target.attr('step');
                if (target.attr('id')) {
                    const color = self.#data[
                        self.#data.findIndex(({ name }) => name === step)
                    ].color;
                    svg.selectAll('circle').filter(function () {
                        return d3.select(this).attr('step') === step;
                    }).attr('style', `stroke-width: 2px; stroke: ${color}; fill: ${color};`);
                }
            });

        let step = 1;
        svg.select('g').remove();
        let ripples = svg.append('g');
        svg.select(`circle#rpi-T${step}`).each(_transition);
        svg.selectAll('circle').attr('visibility', 'hidden');
        svg.selectAll(`circle[step="T${step}"]`).attr('visibility', 'visible');
        svg.selectAll('circle[step="Real"]').attr('visibility', 'visible');
        _appendMinAlertArea(step);

        let intervalID = setInterval(() => {
            if ($('#btnToggleAnimate').text() === '啟用動畫') return;
            if (!this.useFile) clearInterval(intervalID);

            svg.select(`circle#rpi-T${step}`).interrupt();
            svg.select('g').remove();
            ripples = svg.append('g');

            if (++step > this.#data.length) step = 1;
            svg.select(`circle#rpi-T${step}`).each(_transition);
            svg.selectAll('circle').attr('visibility', 'hidden');
            svg.selectAll(`circle[step="T${step}"]`).attr('visibility', 'visible');
            svg.selectAll('circle[step="Real"]').attr('visibility', 'visible');
            $('#model-color-chart > div').hide();
            $(`#model-color-chart > div:nth-of-type(${step})`).show();
            for (let i = 1; i < step; i++) {
                svg.selectAll(`circle[step="T${i}"]`).attr('visibility', 'visible');
                //svg.selectAll(`circle#rpi-T${i}`).attr('visibility', 'visible');
                $(`#model-color-chart > div:nth-of-type(${i})`).show();
            }

            _appendMinAlertArea(step);
        }, 1500);

        const colorChart = this.#data.map(({ name, color }, i) => {
            return `
                <div style="display: ${i ? 'none' : 'block'}">
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
            const x = target.attr('cx'),
                y = target.attr('cy'),
                step = target.attr('step');
            const color = self.#data[
                self.#data.findIndex(({ name }) => name === step)
            ].color;
            const style = `stroke-width: 2px; stroke: ${color}; fill: ${color};`;

            ripples.append('path')
                .attr('transform', 'translate(' + [x, y] + ')')
                .attr('d', d3.arc()
                    .innerRadius(minAlertArea)
                    .outerRadius(minAlertArea + 10)
                    .startAngle(-alertAreaAngle)
                    .endAngle(alertAreaAngle))
                .attr('opacity', .7)
                .attr('fill-opacity', .4)
                .attr('style', style)
                .transition()
                .duration(() => 50 * 100) //調整波紋持續時間
                .ease(d3.easeExpOut, '1') //調整波紋速率
                .attr('d', d3.arc()
                    .innerRadius(minAlertArea)
                    .outerRadius(alertArea)
                    .startAngle(-alertAreaAngle)
                    .endAngle(alertAreaAngle)) //調整波紋大小
                .attr('opacity', 0)
                .remove();

            d3.select(this).transition().delay(300)
                .on('end', _transition); //動畫結束時再次執行_transition
        }

        function _appendMinAlertArea(step) {
            const target = svg.select(`circle#rpi-T${step}`);
            svg.select('path#min-line').remove();
            svg.append('path')
                .attr('id', 'min-line')
                .attr('transform', 'translate(' +
                    [target.attr('cx'), target.attr('cy')] + ')')
                .attr('d', d3.arc()
                    .innerRadius(r)
                    .outerRadius(minAlertArea)
                    .startAngle(-alertAreaAngle)
                    .endAngle(alertAreaAngle))
                .attr('opacity', .7)
                .attr('fill-opacity', .4)
                .attr('style', 'stroke-width: 2px; stroke: red; fill: red;');
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

    #writeImage(base64) {
        const src = (base64 && `data:image/jpg;base64,${base64}`)
            || 'https://i.ibb.co/JtS24qP/food-inside-bowl-1854037.jpg';
            
        $('#model-image-div').show();
        $('#model-image-div').empty().html(`
            <img id="model-image-frame" alt="即時影像" src="${src}">
        `).dialog({
            width: 'auto',
            title: '即時影像',
            position: {
                my: 'right bottom',
                at: 'center+400px center+100px',
                of: window
            },
            autoOpen: true,
            resizable: false,
            close: () => {
                $('#model-image-div')
                    .empty().removeAttr('style');
            }
        }).dialog('open');

        $('#model-image-div').parent('div').css('width', '400px');
        $('.ui-dialog .ui-widget-header, .ui-dialog .ui-button').css({
            'background': 'rgb(247 247 254)',
            'color': 'balck',
            'font-weight': 'bold',
            'border': '0px'
        });
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

    $('#btnToggleAnimate').click(function () {
        if ($(this).text() === '暫停動畫') {
            $(this).text('啟用動畫');
        } else {
            $(this).text('暫停動畫');
        }
    });
});