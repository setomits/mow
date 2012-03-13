MOW.previewEntry = function() {
    $('#preview').show().css('clear', 'both');
    $('#preview_body').html($('#body').val());
    $('#preview_extend').html($('#extend').val());
    $('#posting').removeAttr('disabled');
};

MOW.preventMultiPost = function() {
    $('#posting').attr('disabled', 'disabled');
};


MOW.loadEntry = function() {
    location.search = '?eid=' + $('#eid').val();
};

MOW.updateEntry = function(col) {
    var inp = $('#' + col);
    var btn = inp.next('input:button');

    btn.attr('disabled', 'disabled');

    $.post('./update_entry',
           {eid: $('#eid').val(), col: col, val: inp.val()},
           function(res) {
               $.trim(res) === 'ok' ? alert('succeeded!') : alert('error!');
               btn.removeAttr('disabled');
           });
};

MOW.updateTags = function() {
    var btn = $('#tags').next('input:button');

    btn.attr('disabled', 'disabled');

    $.post('./update_tags', 
           {eid: $('#eid').val(), tags: $('#tags').val(),
            ymdhm: $('#ymdhm').val()},
           function(res) {
               $.trim(res) === 'ok' ? alert('succeeded!') : alert('error!');
               btn.removeAttr('disabled');
           });
};

MOW.confirmToDelete = function(x) {
    var _msg = 'Are you really sure to delete this ' + x + ' entry?';
    return window.confirm(_msg) ? true : false;
};

MOW.loadComment = function() {
    location.search = '?cid=' + $('#cid').val();
};

MOW.updateComment = function(col) {
    var inp = $('#' + col);
    var btn = inp.next('input:button');
    var val = null;

    if (col === 'visible') {
        val = inp.is(':checked') ? 1 : 0;
    } else {
        val = inp.val();
    }

    btn.attr('disabled', 'disabled');

    $.post('./update_comment',
           {cid: $('#cid').val(), col: col, val: val},
           function() {
               btn.removeAttr('disabled');
           });
};
