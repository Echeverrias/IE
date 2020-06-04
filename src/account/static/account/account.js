$(document).ready(function(){

    alerts = $('div.alert.alert-danger');

    if (alerts.length > 1){ // An error message is displayed
        for (let i = 1; i < alerts.length; i++) {
            alerts[i].setAttribute('hidden', true)
        }
    }
    else{
        alerts.attr("hidden", true);
    }

})