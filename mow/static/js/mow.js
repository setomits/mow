if (! mow ) {
    var mow = {};
}

mow.init = function() {
    $('#preview_comment').click(function(){
        if ($.trim($('#author_name').val()) &&
            $.trim($('#comment_title').val()) &&         
            $.trim($('#comment_body').val())) {
            $('#entry_id').val(mow.vars.entry_id);
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
