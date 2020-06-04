$(document).ready(function() {
    console.log('admin.js')
    // CHANGING THE TITLE
    try{
        var breadcrumbs = $('.breadcrumbs')
        var text = breadcrumbs.text()
        var new_text = ""
        if (text){
            var a = text.split('›')
            var model_name = a[a.length - 1]
            new_text = model_name
        }
        else{
            new_text = "Panel de administración"
        }
        var title = $('#content h1');
        title.text(new_text)
    }
    catch(e){}

})