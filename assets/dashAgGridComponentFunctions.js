var dagcomponentfuncs = window.dashAgGridComponentFunctions = window.dashAgGridComponentFunctions || {};

dagcomponentfuncs.ImgPairRenderer = function(params) {
    const data = params.data;

    if (!data) return "";

    const img1 = data.img1 || data.img11;
    const img2 = data.img2 || data.img22;

    return React.createElement(
        'div',
        {style: {display: 'flex', gap: '10px'}},
        [
            React.createElement('img', {src: img1, style: {height: '80px'}}),
            React.createElement('img', {src: img2, style: {height: '80px'}})
        ]
    );
};