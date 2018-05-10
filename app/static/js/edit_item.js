
var current_item_sn = "";
var url_sn = new URL(document.URL).searchParams.get("sn");
if (url_sn!=null){current_item_sn=url_sn}

refresh_data(current_item_sn);
$('.save_btn').click(function(){
    var upload_success_callback=function(){
        alert('保存成功');
    };
    upload_data(get_form_data(), 0, upload_success_callback);
});
$('.publish_btn').click(function(){
    var upload_success_callback=function(){
        alert('发布成功');
    };
    upload_data(get_form_data(), 1, upload_success_callback);
});
$('.cancel_publish_btn').click(function(){
    var upload_success_callback=function(){
        alert('已取消发布');
    };
    upload_data(get_form_data(), 0, upload_success_callback);
});

$('.add_image_btn input').change(function(){
    var form_data = get_form_data();
    var files=$(this).prop('files');
    if (files.length > 0){
        var file = files[0];
        for (i = 0; i < files.length; i++) {
            form_data.append('file_' + i, files[i]);
        }
    };
    upload_data(form_data, 0, function(){});
});

function get_form_data(){
    
    if($('#item_name').val() != null && $('#item_price').val()!=null && $('#item_describe').val()!=null){
        console.log($('#item_category').val());
        var form_data = new FormData();
        form_data.append('item_sn', current_item_sn);
        form_data.append('item_name', $('#item_name').val());
        form_data.append('item_price', $('#item_price').val());
        form_data.append('item_category', $('#item_category').val());
        form_data.append('item_describe', $('#item_describe').val());
        return form_data;
    }else{
        alert('请填入完整信息');
    }
    
}

function upload_data(form_data, status, success_callback){
    form_data.append('item_status', status);
    console.log(form_data);
    $('input,button,textarea').attr('disabled','disabled');
    $.ajax({
            url:"/item",
            type:'POST',
            data: form_data,
            cache:false,
            processData:false,
            contentType:false,
            dataType: 'json',
            success:function(Data){
                console.log(Data);
                if (Data.code==0){
                    current_item_sn = Data.item_sn;
                    refresh_data(Data.item_sn);
                    success_callback();
                }else{
                    alert(Data.msg);
                }
            },
            error:function(){
              alert("upload error");
            },
            complete:function(){
                $('input,button,textarea').removeAttr('disabled');
            }
        });
}

function refresh_data(item_sn){
    if (item_sn == '' || item_sn == null){return;}
    $('.item_images_container').empty();
    $.ajax({
        url:"/item/"+item_sn,
        type:'GET',
        cache:false,
        processData:false,
        contentType:false,
        dataType: 'json',
        success:function(Data){
            if (Data.code==0){
                var item = Data.item;
                $('#item_name').val(item.name);
                $('#item_price').val(item.price);
                $('#item_category').val(item.category);
                $('#item_describe').val(item.describe);

                for (var i=0;i<Data.images.length;i++){
                    var f = Data.images[i];
                    console.log(f.is_main);
                    var path = '/var/item_images/'+ f.filename;
                    var class_name="";
                    if (f.is_main) {
                        class_name="item_image_div_main";
                    }
                    $('.item_images_container').append('<div class="item_image_div '+class_name+'"><img src="'+path+'"/><div><div onclick="set_main_image(\''+f.filename+'\')">设为主图</div><div onclick="delete_image(\''+f.filename+'\')">删除</div></div></div>');
                }
                if(Data.images.length==0){
                    $('.item_images_container').append('请添加图片');
                }
            }else{
                alert(Data.msg);
                location.href="/my_home";
            }
        },
        error:function(){
          alert("refresh data error");
        }
    });
}

function set_main_image(filename){
    $.ajax({
        url:"/item/"+current_item_sn+'/main_image/'+filename,
        type:'GET',
        cache:false,
        processData:false,
        contentType:false,
        dataType: 'json',
        success:function(Data){
            if (Data.code==0){
                refresh_data(current_item_sn);
            }else{
                alert(Data.msg);
            }
        },
        error:function(){
          alert("set main image error");
        }
    });
}

function delete_image(filename){
    $.ajax({
        url:"/item/"+current_item_sn+'/item_image/'+filename,
        type:'DELETE',
        dataType: 'json',
        success:function(Data){
            console.log(Data);
            if (Data.code==0){
                refresh_data(current_item_sn);
            }else{
                alert(Data.msg);
            }
        },
        error:function(){
          alert("delete image error");
        }
    });
}