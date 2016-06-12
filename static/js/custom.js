$(document).ready(function () {
    /***************** Navbar-Collapse ******************/

    $(window).scroll(function () {
        if ($(".navbar").offset().top > 50) {
            $(".navbar-fixed-top").addClass("top-nav-collapse");
        } else {
            $(".navbar-fixed-top").removeClass("top-nav-collapse");
        }
    });

    /***************** Page Scroll ******************/

    $(function () {
        $('a.page-scroll').bind('click', function (event) {
            var $anchor = $(this);
            $('html, body').stop().animate({
                scrollTop: $($anchor.attr('href')).offset().top
            }, 1500, 'easeInOutExpo');
            event.preventDefault();
        });
    });

    /***************** Scroll Spy ******************/

    $('body').scrollspy({
        target: '.navbar-fixed-top',
        offset: 51
    })

    /***************** Owl Carousel ******************/

    $("#owl-hero").owlCarousel({

        navigation: true, // Show next and prev buttons
        slideSpeed: 300,
        paginationSpeed: 400,
        singleItem: true,
        transitionStyle: "fadeUp",
        autoPlay: 10000,
        navigationText: ["<i class='fa fa-angle-left'></i>", "<i class='fa fa-angle-right'></i>"]

    });


    /***************** Full Width Slide ******************/

    var slideHeight = $(window).height();

    $('#owl-hero .item').css('height', slideHeight);

    $(window).resize(function () {
        $('#owl-hero .item').css('height', slideHeight);
    });
    /***************** Owl Carousel Testimonials ******************/

    $("#owl-testi").owlCarousel({

        navigation: false, // Show next and prev buttons
        paginationSpeed: 400,
        singleItem: true,
        transitionStyle: "backSlide",
        autoPlay: true

    });
    /***************** Countdown ******************/

    $('#fun-facts').bind('inview', function (event, visible, visiblePartX, visiblePartY) {
        if (visible) {
            $(this).find('.timer').each(function () {
                var $this = $(this);
                $({
                    Counter: 0
                }).animate({
                    Counter: $this.text()
                }, {
                    duration: 2000,
                    easing: 'swing',
                    step: function () {
                        $this.text(Math.ceil(this.Counter));
                    }
                });
            });
            $(this).unbind('inview');
        }
    });

    /***************** Wow.js ******************/
    
    new WOW().init();
    
    /***************** Preloader ******************/
    
    var preloader = $('.preloader');
    $(window).load(function () {
        preloader.remove();
    });

    $("#go-encrypt").click(function(){
        $.post( "scramble_message/", { message: $('#original-message').val(), operation: 'scramble', gen_key: getGenKey('msg') } )
            .done(function( data ) {
                    $('#encrypted-message').val(data['scrambled']);
                    var extra = '';
                    var target = data['extra'];
                    for (var k in target){
                        if (target.hasOwnProperty(k)) {
                             extra +=  k + ": " + target[k] + '\n';
                        }
                    }
                    $('#text-extra-data').text(extra);
            });
    });

    $("#go-decrypt").click(function(){
        $.post( "scramble_message/", { message: $('#encrypted-message').val(), operation: 'un_scramble', gen_key: getGenKey('msg') } )
            .done(function( data ) {
                    $('#decrypted-message').val(data['scrambled']);
                    var extra = '';
                    var target = data['extra'];
                    for (var k in target){
                        if (target.hasOwnProperty(k)) {
                             extra +=  k + ": " + target[k] + '\n';
                        }
                    }
                    $('#text-extra-data').text(extra);
            });
    });

    var getGenKey = function(prefix){
        var gen = $('#' + prefix + '-prng').find(":selected").val();
        var seed = $('#' + prefix + '-seed').val();
        var seqno = $('#' + prefix + '-seqno').val();

        return [gen, seed, seqno].join(':');
    };

    $("#img-encrypt").click(function(){
        $('#encrypted-image').attr('src', 'img/loading.gif');
        $.post( "scramble_image/", { image: $('#original-image').attr('data-url'), operation: 'scramble', gen_key: getGenKey('img') } )
            .done(function( data ) {
                    $('#encrypted-image').attr('src', data['scrambled']);
                    $('#encrypted-image').attr('data-url', data['scrambled']);
                    var extra = '';
                    var target = data['extra'];
                    for (var k in target){
                        if (target.hasOwnProperty(k)) {
                             extra +=  k + ": " + target[k] + '\n';
                        }
                    }
                    $('#img-extra-data').text(extra);
            });
    });

    $("#img-decrypt").click(function(){
        $('#decrypted-image').attr('src', 'img/loading.gif');
        $.post( "scramble_image/", { image: $('#encrypted-image').attr('data-url'), operation: 'un_scramble', gen_key: getGenKey('img') } )
            .done(function( data ) {
                    $('#decrypted-image').attr('src', data['scrambled']);
                    $('#decrypted-image').attr('data-url', data['scrambled']);
                    var extra = '';
                    var target = data['extra'];
                    for (var k in target){
                        if (target.hasOwnProperty(k)) {
                             extra +=  k + ": " + target[k] + '\n';
                        }
                    }
                    $('#img-extra-data').text(extra);
            });
    });

    $("#gen-action").click(function(){
        var gen = $('#gen-prng').find(":selected").val();
        var seed = $('#gen-seed').val();
        var seqlen = $('#gen-seqno').val();
        var url = '/random/?generator=' + gen + '&seed=' + (seed || 12345) + '&count=' + (seqlen || 10000);
        console.log(url);
        window.open(url, '_blank');
    });

    $(function () {
        'use strict';
        // Change this to the location of your server-side upload handler:
        var url = '/file_upload/',
            uploadButton = $('<button/>')
                .addClass('btn btn-primary')
                .prop('disabled', true)
                .text('Processing...')
                .on('click', function () {
                    var $this = $(this),
                        data = $this.data();
                    $this
                        .off('click')
                        .text('Abort')
                        .on('click', function () {
                            $this.remove();
                            data.abort();
                        });
                    data.submit().always(function () {
                        $this.remove();
                    });
                });
            $('#fileupload').fileupload({
                url: url,
                dataType: 'json',
                // autoUpload: false,
                acceptFileTypes: /(\.|\/)(gif|jpe?g|png)$/i,
                maxFileSize: 999000,
                limitMultiFileUploads: 1,
                // Enable image resizing, except for Android and Opera,
                // which actually support image resizing, but fail to
                // send Blob objects via XHR requests:
                disableImageResize: /Android(?!.*Chrome)|Opera/
                    .test(window.navigator.userAgent),
                previewMaxWidth: 100,
                previewMaxHeight: 100,
                previewCrop: true
            }).on('fileuploadadd', function (e, data) {
                data.context = $('<div/>').appendTo('#files');
                $.each(data.files, function (index, file) {
                    var node = $('<p/>')
                            // .append($('<span/>').text(file.name));
                            .append($('<span/>').text(''));
                    // if (!index) {
                    //     node
                    //         .append('<br>');
                    // }
                    node.appendTo(data.context);
                });
            }).on('fileuploadprocessalways', function (e, data) {
                var index = data.index,
                    file = data.files[index],
                    node = $(data.context.children()[index]);
                // if (file.preview) {
                //     node
                //         .prepend('<br>')
                //         .prepend(file.preview);
                // }
                if (file.error) {
                    node
                        .append('<br>')
                        .append($('<span class="text-danger"/>').text(file.error));
                }
                if (index + 1 === data.files.length) {
                    data.context.find('button')
                        .text('Upload')
                        .prop('disabled', !!data.files.error);
                }
            }).on('fileuploadprogressall', function (e, data) {
                var progress = parseInt(data.loaded / data.total * 100, 10);
                $('#progress .progress-bar').css(
                    'width',
                    progress/2 + '%'
                );
            }).on('fileuploaddone', function (e, data) {
                data.context.find('button').remove();
                $.each(data.result.files, function (index, file) {
                    if (file.url) {
                        $('#original-image').attr('data-url', file.url);
                        loadImage(file.url);
                    } else if (file.error) {
                        var error = $('<span class="text-danger"/>').text(file.error);
                        $(data.context.children()[index])
                            .append('<br>')
                            .append(error);
                    }
                });
            }).on('fileuploadfail', function (e, data) {
                $.each(data.files, function (index) {
                    var error = $('<span class="text-danger"/>').text('File upload failed.');
                    $(data.context.children()[index])
                        .append('<br>')
                        .append(error);
                });
            }).prop('disabled', !$.support.fileInput)
                .parent().addClass($.support.fileInput ? undefined : 'disabled');
    });

            var img_request;

            function loadImage(imageURI)
            {
                img_request = new XMLHttpRequest();
                // request.onloadstart = showProgressBar;
                img_request.onprogress = updateProgressBar;
                img_request.onload = showImage;
                // request.onloadend = hideProgressBar;
                img_request.open("GET", imageURI, true);
                img_request.overrideMimeType('text/plain; charset=x-user-defined');
                img_request.send(null);
            }

            function updateProgressBar(e)
            {
                if (e.lengthComputable) {
                    progress = 50 + (e.loaded / e.total * 100)/2;
                    $('#progress .progress-bar').css('width', progress + '%');
                }
            }

            function showImage()
            {

                $('#original-image').attr('src', "data:image/jpeg;base64," + base64Encode(img_request.responseText));

            }

            // This encoding function is from Philippe Tenenhaus's example at http://www.philten.com/us-xmlhttprequest-image/
            function base64Encode(inputStr)
            {
               var b64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";
               var outputStr = "";
               var i = 0;

               while (i < inputStr.length)
               {
                   //all three "& 0xff" added below are there to fix a known bug
                   //with bytes returned by xhr.responseText
                   var byte1 = inputStr.charCodeAt(i++) & 0xff;
                   var byte2 = inputStr.charCodeAt(i++) & 0xff;
                   var byte3 = inputStr.charCodeAt(i++) & 0xff;

                   var enc1 = byte1 >> 2;
                   var enc2 = ((byte1 & 3) << 4) | (byte2 >> 4);

                   var enc3, enc4;
                   if (isNaN(byte2))
                   {
                       enc3 = enc4 = 64;
                   }
                   else
                   {
                       enc3 = ((byte2 & 15) << 2) | (byte3 >> 6);
                       if (isNaN(byte3))
                       {
                           enc4 = 64;
                       }
                       else
                       {
                           enc4 = byte3 & 63;
                       }
                   }

                   outputStr += b64.charAt(enc1) + b64.charAt(enc2) + b64.charAt(enc3) + b64.charAt(enc4);
                }

                return outputStr;
            }
});