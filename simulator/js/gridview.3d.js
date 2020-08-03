class GridView3D {
    constructor() {
        this.modelData = [];
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
                    nticks: 10,
                    range: [0, 100]
                },
                yaxis: {
                    nticks: 10,
                    range: [0, 100]
                },
                zaxis: {
                    nticks: 2,
                    range: [0, 20]
                },
                camera: {
                    eye: { x: 1, y: 2, z: 1.5 }
                }
            }
        };
        this.batchCode = 1;
    }

    initialize() {
        this.modelData.push({
            name: 'user',
            text: 'user',
            x: [50],
            y: [100],
            z: [0],
            hoverinfo: 'text',
            mode: 'markers',
            marker: {
                size: 10,
            },
            type: 'scatter3d'
        });
        Plotly.newPlot('model-3d', this.modelData, this.layout);
    }

    generate(model) {
        console.log(model);

        let { height, width, resolution } = model;
        height /= 10;
        width /= 10;
        resolution /= 10;
        height += resolution;

        this.layout.scene.xaxis = {
            nticks: resolution,
            range: [0, width]
        };

        this.layout.scene.yaxis = {
            nticks: resolution,
            range: [0, height]
        };

        model.obstacles.forEach(({ class: clsName, coordinate }) =>
            this.insertByClsName(width, height, clsName, coordinate));

        const index = this.modelData
            .findIndex((item) => item.name === 'user');
        if (index >= 0) {
            this.modelData[index].x = [width / 2];
            this.modelData[index].y = [height];
        } else {
            this.modelData.push({
                name: 'user',
                text: 'user',
                x: [width / 2],
                y: [height],
                z: [0],
                hoverinfo: 'text',
                mode: 'markers',
                marker: {
                    size: 10,
                },
                type: 'scatter3d'
            });
        }

        console.log(this.modelData);
        Plotly.newPlot('model-3d', this.modelData, this.layout);

        this.batchCode += 1;
    }

    insertByClsName(width, height, clsName, coordinate) {
        let { lt, rt, lb, rb } = coordinate;
        lb.x /= 10;
        lb.y /= 10;
        rb.x /= 10;
        rb.y /= 10;
        const xCenter = (lb.x + rb.x) / 2;
        const r = xCenter - lb.x;

        const index = this.modelData
            .findIndex((item) => item.name === clsName);
        if (index >= 0) {
            this.modelData[index].text.push(`第${this.batchCode}次 - ${clsName}`);
            this.modelData[index].x.push(width - xCenter);
            this.modelData[index].y.push(lb.y);
            this.modelData[index].z.push(0);
            this.modelData[index].marker.size.push(r);
            this.modelData[index].marker.line.width.push(2);
        } else {
            this.modelData.push({
                name: clsName,
                text: [`第${this.batchCode}次 - ${clsName}`],
                x: [width - xCenter],
                y: [lb.y],
                z: [0],
                hoverinfo: 'text',
                mode: 'markers',
                marker: {
                    symbol: 'circle-open',
                    size: [r],
                    line: {
                        width: [2]
                    }
                },
                type: 'scatter3d'
            });
        }
    }
}

const gridview3d = new GridView3D();
const dynamicGenerateGridView = (model) => gridview3d.generate(model);