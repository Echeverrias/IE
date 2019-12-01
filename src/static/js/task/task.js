$(document).ready(function(){


    function show_info_running_crawler(data) {
        console.log('show_info_running_crawler')
        console.log(data)
        if (data !== 'not running'){
            $('#info-crawler').html(data)
          //  setTimeout(get_info_running_crawler, 10000);
        }
    }



    function get_info_running_crawler(){
       console.log('Getting crawler info')
       $.ajax({
            'url': '/task/crawl/?AJAX',
            'success': show_info_running_crawler,
            'error': e => console.error(e)
        })
        return false
    }
/*
    $('#run-crawler').submit(function(){
        console.log('Run Crawler');
        setTimeout(get_info_running_crawler, 5000);
        e.preventDefault;
    })
*/
    try{

        if (is_running){
            console.log('The crawler is running');
           // setTimeout(get_info_running_crawler, 5000);
        }
        else{
             console.log('The crawler is not running');
        }
    }
    catch(e){
        console.error(e)
    }

    $("#AJAX").click(get_info_running_crawler)

})