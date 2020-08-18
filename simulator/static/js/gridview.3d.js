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
        if (this.useFile) {
            this.#data = [];
            this.useFile = false;
        }

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
        this._writeResult();

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
        this.lock = true;

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
        });

        console.log(this.#data);
        Plotly.newPlot('model-3d', this.#data, this.layout);

        this.useFile = true;
    }

    _writeResult() {
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

const gridview3d = new GridView3D();
const dynamicGenerateGridView = (model) => gridview3d.generate(model);

$(function () {
    $('#btnToggleReceive').click(function () {
        if ($(this).text() === '暫停接收') {
            gridview3d.lock = true;
            $(this).text('啟用接收');
        } else {
            gridview3d.lock = false;
            $(this).text('暫停接收');
        }
    });

    $('#btnChangePosition').click(() => {
        gridview3d.step++;
        gridview3d.lock = true;
        $('#position').text(`T${gridview3d.step}`);
        setTimeout(() => gridview3d.lock = false, 3000);
    });

    $('#position').text(`T${gridview3d.step}`);
});