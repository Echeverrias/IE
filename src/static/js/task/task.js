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
            $('.sub_container').html(data)
            state = $('#state', '<div>' + data + '<div>').attr('data-state')
            console.log('state: ' + state)
            console.log(data)
            if(state !== running_state){
                $('#stop-crawler').hide();
                $('#run-crawler').removeAttr('hidden');
                $('#main-loader').hide();
                stop_ajax_request();
            }
        }
        else {
            console.log(data)
            stop_ajax_request();
        }
    }



    function get_info_running_crawler(){
       console.log('Ajax request')
       $.ajax({
            'url': '/task/crawl/?AJAX',
            'success': show_info_running_crawler,
            'error': e => console.error(e)
        })
        return false
    }



    function show_loader(velocity=''){
        console.log('show loader')
        $('#main-loader').removeClass();
        $('#main-loader').addClass("loader " + velocity);
        $('#main-loader').removeAttr('hidden');

    }

    function change_loader_velocity(velocity){
        classes = $('#main-loader').attr('class');
        classes = classes.replace('loader', '').trim();
        $('#main-loader').removeClass(classes);
        $('#main-loader').addClass(velocity);

    }

    function display_msg(msg){
        html = '<p>' + msg + '</p>' ;
        $('.sub-container').html(html);
    }


    function waiting_for_stop(msg){
        console.log('waiting_for_stop');
        stop_ajax_request();
    }



    $('#stop').click((e) => {
        console.log("stop...")
        $("#stop-crawler").hide();
        msg = 'Parando la araña...';
        display_msg(msg);
        $('#main-loader').show();
        waiting_for_stop(msg);
        change_loader_velocity('slow');
    })

    $('#start').click((e) => {
        console.log("start...")
        $("#run-crawler").hide();
        msg = 'Iniciando la araña...';
        display_msg(msg);
        show_loader('fast');
    })


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

    $('#AJAX').click(show_loader)

})