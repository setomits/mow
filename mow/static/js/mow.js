if (! mow ) {
    var mow = {};
}

mow.init = function() {
    $('#preview_comment').click(function(){
        if ($.trim($('#author_name').val()) &&
            $.trim($('#comment_title').val()) &&         
            $.trim($('#comment_body').val())) {

            var preview_body = $.trim($('#comment_body').val())
                    .replace(/(\r\n|\n\r|\r|\n)/g, "<br>");

            $('#entry_id').val(mow.vars.entry_id);
            $('#preview > .comment-title')
                .text($.trim($('#comment_title').val()));
            $('#preview > .body').html(preview_body).autolink();
//            $('#preview > .body').autolink();
            $('#preview').removeClass('hidden');

            $('#post_comment_button')
                .removeClass('btn-default')
                .addClass('btn-primary')
                .removeAttr('disabled');
        }
    });

    $('#search').submit(function() {
        $('#keyword').val($('#keyword').val() +
                          ' site:' + mow.vars.top);

    });

};

$(document).ready(function() {
    mow.init();
});
