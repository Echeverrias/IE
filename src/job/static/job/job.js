$(document).ready(function() {

        // JQuery code to be added in here.
        console.log('JS loaded from static')


        $(".job-inline div.card-body").addClass('hidden')

        $(".job-inline").click(function(event) {
            try{
                $(".job-inline div.card-body").addClass('hidden')
                $('.job-inline').removeClass('lowlight')
                $('#' + this.id + ' div.card-body').toggleClass('hidden');
                $('#' + this.id).toggleClass('lowlight');
                $('#' + this.id + ' div.card').toggleClass('lowlight');
            }
            catch(e){
            }
        });

        $("div.job-inline").hover(function(event) {
            $(this).toggleClass('highlight');
        });

        $('#btn-filters').hover(function(event){
            console.log("('#btn-filters').hover")
            $(this).toggleClass('highlight');
        });

        $('#btn-filters').click(function(event){
           console.log("('#btn-filters').click")
           $(this).toggleClass('highlight');
           $('#filters').toggleClass('hidden');
        });

         $('#btn-filters').mouseleave(function(event){
           $(this).removeClass('highlight');
        });

        $('a').click(function(e){
            e.stopPropagation();
        });

});