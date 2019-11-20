$(document).ready(function() {

        // JQuery code to be added in here.
        console.log('JS loaded from static')

        $("div.card-body").addClass('hidden')
        $(".job").click(function(event) {
            console.log(this);
            try{
                //$('#' + this.id).toggleClass('details');
                $('#' + this.id + ' div.card-body').toggleClass('hidden');
                $('#' + this.id).toggleClass('lowlight');
                $('#' + this.id + ' div.card').toggleClass('lowlight');
            }
            catch(e){
            }
            //$( this ).toggleClass( "highlight" );

        });
        $("div.card").hover(function(event) {
            console.log('hover');
            //$('#' +this.id).toggleClass('highlight');
            $(this).toggleClass('highlight');
            //$('#' +this.id).css('color', 'blue');
            //$('#' +this.id).addClass('highlight');
            //$( this ).toggleClass( "highlight" );

        });
        /*
         $(".card.job").mouseleave(function(event) {
            $('#' + this.id).removeClass('highlight');
            $('#' + this.id).removeClass('lowlight');
            //$('#' +this.id).css('color', 'blue');
            //$('#' +this.id).addClass('highlight');
            //$( this ).toggleClass( "highlight" );

        });
        */
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


        });


//.rgba-lime-strong

});