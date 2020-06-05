$(document).ready(function() {

    // CHANGING THE TITLE

    if ($('.breadcrumbs a')[0]){
        try{
            $('.breadcrumbs a')[0].innerText = "Panel de administración"
            var text =  $('.breadcrumbs').text();
            var new_text = "";
            if (text){
                var a = text.split('›');
                var model_name = a[a.length - 1];
                new_text = model_name;
            }
        }
        catch(e){}
    }
    else{
        new_text = "Panel de administración";
    }
    try{
        var title = $('#content h1');
        title.text(new_text);
    }
    catch(e){}


    // FILTERS TRANSLATION

    var filter =  $('#changelist-filter')
    if (filter){
        $('#changelist-filter h2').text('Filtro');
        filters = $('#changelist-filter h3');
        for(filter of filters){
            text = filter.innerText;
            filter.innerText = text.replace('By', 'Por');
        }
        choices = $('#changelist-filter ul li a');
        for(choice of choices){
            if (choice.innerText === 'All'){
                choice.innerText = 'Todos';
            }
        }
    }

    try{
        $("#changelist-search input[type=submit]:nth-child(3)")[0].value='Buscar'
    }
    catch(e){}

})