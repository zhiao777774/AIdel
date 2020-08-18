$(function () {
    $('#info-div div.card-header').append(`
        <h3 style='font-weight: bold; display: inline;'>資訊欄</h3>
        <span>
            <label class='color-chart' style='background: rgb(214, 131, 75);'></label>
            <label>視障者</label>
        </span>
        <span>
            <label class='color-chart' style='background: rgb(218, 41, 18);'></label>
            <label>終點</label>
        </span>
        <span>
            <label class='color-chart' style='background: rgb(95, 176, 228);'></label>
            <label>障礙物</label>
        </span>
        <button id='btnClear' class='btn btn-xs btn-danger'>清空資訊欄</button>
        <div class='input-group mt-1'>
            <div class='input-group-prepend'>
                <label class='input-group-text' for='data-visibility'>模擬資料查看</label>
            </div>
            <select id='data-visibility' class='custom-select'>
                <option value='all' selected>全部</option>
                <option value='success'>模擬成功</option>
                <option value='failure'>模擬失敗</option>
            </select>
        </div>
    `);

    $('#btnClear').click((e) => {
        $('#info-div div.card-body').empty();
        count = 1;
        clearInterval(intervalID);
        intervalID = undefined;
        clearTimeout(timeoutID);
        timeoutID = undefined;
        initGridView(Number($('#n-random').val()) ||
            Math.floor(Math.random() * (upperLimit - 1)) + 1);
    });

    $('#data-visibility').change(({ target }) => {
        const condition = ((type) => {
            switch (type) {
                case 'success':
                    return (div) => !$(div).children('h5').hasClass('success');
                case 'failure':
                    return (div) => $(div).children('h5').hasClass('success');
                default:
                    return (div) => false;
            }
        })($(target).children('option:selected').val());

        $('#info-div div.card-body')
            .children('div').each((i, div) => {
                if (condition(div)) {
                    $(div).hide().next().hide();
                } else {
                    $(div).show().next().show();
                }
            });
    });
});