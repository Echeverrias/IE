$(document).ready(function(){

    alerts = $('div.alert.alert-danger');

    if (alerts.length > 1){ // An error message is displayed
        for (let i = 1; i < alerts.length; i++) {
            alerts[i].setAttribute('hidden', true);
        }
        inputs = $('.form-group input')
        for (let i = 0; i < inputs.length; i++) {
            inputs[i].className = inputs[i].className.replace('is-valid', 'is-invalid');
        }
    }
    else{
        alerts.attr("hidden", true);
    }

})