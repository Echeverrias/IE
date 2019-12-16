$(document).ready(function(){
    container = $('main div.container:nth-child(1)');
    console.log(container);
    container.addClass('app-container');
    container.removeClass('container');
})