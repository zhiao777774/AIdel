let modelData = [];
const layout = {
    margin: {
        l: 0, r: 0,
        b: 0, t: 0
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
            eye: {
                x: 1,
                y: 2,
                z: 0
            }
        }
    }
};

function init3dGridView() {
    modelData.push({
        name: 'user',
        x: [50],
        y: [100],
        z: [0],
        mode: 'markers',
        marker: {
            size: 10,
            opacity: 0.8
        },
        type: 'scatter3d'
    });
    Plotly.newPlot('model-3d', modelData, layout);
    $('.main-svg').css('background', '');
}

function dynamicGenerateGridView(model) {
    $('.warn-text').hide();
    console.log(model);

    let { height, width, resolution } = model;
    height /= 10;
    width /= 10;
    resolution /= 10;
    height += resolution;

    layout.scene.xaxis = {
        nticks: resolution,
        range: [0, width]
    };

    layout.scene.yaxis = {
        nticks: resolution,
        range: [0, height]
    };

    model.obstacles.forEach(({ class: clsName, coordinate }) => {
        let { lt, rt, lb, rb } = coordinate;
        lb.x /= 10;
        lb.y /= 10;
        rb.x /= 10;
        rb.y /= 10;
        const xCenter = (lb.x + rb.x) / 2;
        const r = xCenter - lb.x;

        modelData = [];
        const index = modelData.findIndex((item) => item.name === clsName);
        if (index >= 0) {
            modelData[index].x.push(xCenter);
            modelData[index].y.push(lb.y);
            modelData[index].z.push(0);
        } else {
            modelData.push({
                name: clsName,
                x: [xCenter],
                y: [lb.y],
                z: [0],
                mode: 'markers',
                marker: {
                    size: r,
                    opacity: 0.8
                },
                type: 'scatter3d'
            });
        }
    });

    const userIndex = modelData.findIndex((item) => item.name === 'user');
    if (userIndex >= 0) {
        modelData[userIndex].x = [width / 2];
        modelData[userIndex].y = [height];
    } else {
        modelData.push({
            name: 'user',
            x: [width / 2],
            y: [height],
            z: [0],
            mode: 'markers',
            marker: {
                size: 10,
                opacity: 0.8
            },
            type: 'scatter3d'
        });
    }

    console.log(modelData);
    Plotly.newPlot('model-3d', modelData, layout);
    $('.main-svg').css('background', '');
}