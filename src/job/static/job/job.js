$(document).ready(function() {

        // JQuery code to be added in here.
        console.log('JS loaded from static')


        $(".job-inline div.card-body").addClass('hidden')

        function cleanInlineJobs(){
            $(".job-inline div.card-body").addClass('hidden')
            $('.job-inline').removeClass('lowlight')
        }
        function toggleInlineJob(currentTarget){
            var id = currentTarget.id
            $('#' + id + ' div.card-body').toggleClass('hidden');
            $('#' + id).toggleClass('lowlight');
            $('#' + id + ' div.card').toggleClass('lowlight');
        }

        $(".job-inline").click(function(event) {
            try{
                if (!this.className.includes('lowlight')){
                    cleanInlineJobs();
                }
                toggleInlineJob(this);
            }
            catch(e){
            }
            finally{
                event.stopPropagation();
            }
        });

        $('form').click(function(e){
            e.stopPropagation();
        })

        $("body").click(function(event) {
            try{
                 cleanInlineJobs();
            }
            catch(e){
            }
        })

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