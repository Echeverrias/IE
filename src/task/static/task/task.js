$(document).ready(function(){

    console.log("LOADING JQUERY")
    var ajax_request;

    function start_ajax_request() {
        console.log('start ajax request')
        return setInterval(get_info_running_crawler, 10000);
    }

    function stop_ajax_request() {
        console.log('stop_ajax_request')
        clearInterval(ajax_request);
    }

    function show_info_running_crawler(data) {
        console.log('show_info_running_crawler')
        if(data !== 'not running'){
            $('.sub-container').html(data)
            state = $('#state', '<div>' + data + '<div>').attr('data-state')
            console.log('state: ' + state)
            console.log(data)
            if(state !== running_state){
                $('#stop-crawler').hide();
                $('#run-job-spider').removeAttr('hidden');
                $('#run-company-spider').removeAttr('hidden');
                $('#main-loader').hide();
                stop_ajax_request();
            }
        }
        else {
            console.log(data)
            stop_ajax_request();
        }
    }

    function handle_error(error){
        stop_ajax_request();
        $('#main-loader').hide();
        console.log(error)
        if (error.status === 500){
            display_msg('Error: Se ah producido un error en el servidor', 'h4', 'title alert alert-danger');
        }
        else if (error.status === 0){
            display_msg('Error: La conexión ha sido rechazada', 'h4', 'title alert alert-danger');
        }
        else{
            display_msg('Error', 'h4', 'title alert alert-danger');
        }
    }

    function get_info_running_crawler(){
       console.log('Ajax request')
       $.ajax({
            'url': '/task/scraping/?AJAX',
            'success': show_info_running_crawler,
            'error': e => handle_error(e)
        })
        return false
    }

    function show_loader(velocity=''){
        console.log('show loader')
        if (velocity){
            change_loader_velocity(velocity);
        }
        $('#main-loader').show();
        $('#main-loader').removeAttr('hidden');
    }

    function change_loader_velocity(velocity){
        classes = $('#main-loader').attr('class');
        classes = classes.replace('loader', '').trim();
        $('#main-loader').removeClass(classes);
        $('#main-loader').addClass(velocity);
    }

    function display_msg(msg, tag, classes){
        html = `<${tag} class="${classes}">  ${msg}  </${tag}>` ;
        $('.sub-container').html(html);
    }

    function waiting_for_stop(msg){
        console.log('waiting_for_stop');
        stop_ajax_request();
    }

    function set_attribute(element, attribute, value){
        try{
            element.attr(attribute, value)
            alert('set ' + attribute + ' -> ' + value)
        }
        catch(e){
             alert('Error: set ' + attribute + ' -> ' + value)
        }
    }

    function start_spider() {
        console.log("starting spider...")
        $("#run-job-spider").hide();
        $("#run-company-spider").hide();
        msg = 'Iniciando el proceso ...';
        display_msg(msg, 'h4', 'title');
        show_loader('fast');
    }

    $('#start-job-spider').click(start_spider)

    $('#start-company-spider').click(start_spider)

    try{
        $('#stop').click((e) => {
            console.log("stop...")
            $("#stop-crawler").hide();
            msg = 'Parando el proceso...';
            display_msg(msg, 'h4', 'title');
            change_loader_velocity('slow');
            waiting_for_stop(msg);
        })
    }
     catch(e){
        console.error(e)
    }

    try{
        if (is_running === 'True'){
            console.log('The crawler is running');
            console.log('is_running: ' + is_running)
            ajax_request = start_ajax_request();
        }
        else{
             console.log('The crawler is not running');
        }
    }
    catch(e){
        console.error(e)
    }

})