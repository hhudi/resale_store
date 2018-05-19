$(function(){
    $('html').height($('body').height());
    var mySwiper = new Swiper ('.swiper-container', {
        direction: 'horizontal',
        loop: true,
        pagination: {
            el: '.swiper-pagination',
            clickable :true,
        },
        autoplay: true
    }); 
    /*for(var i=0;i<$('.digital_item_list').children().length; i++){
        if($('.digital_item_list').children().length > 4){
            $('.digital_item_list').children()[i+4].remove();
        }
        if($('.book_item_list').children().length > 4){
            $('.book_item_list').children()[i+4].remove();
        }
        if($('.other_item_list').children().length > 4){
            $('.other_item_list').children()[i+4].remove();
        }
    }*/
    $('.main-title').click(function(){
        window.location.href = '/page/edit_item';
    });
})