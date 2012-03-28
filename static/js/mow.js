var MOW = {
    _setCalendar: function() {
        if ($.cookie('last_calendar')) {
            var ym = $.cookie('last_calendar').split('-');
            var y = parseInt(ym[0]);
            var m = parseInt(ym[1]);
            this.cal_table(y, m, false);
        }
    },

    init: function() {
        this._setCalendar();

        if ($('#comm_field').length > 0) {
            this.setCommentForm();

            if (location.hash) {
                $('#c' + location.hash.substr(1)).animate(
                    {backgroundColor: 'white'}, 1500,
                    function() {
                        $(this).animate(
                            {backgroundColor: $('body').css('backgroundColor')},
                            3000);
                    });
            }
        }
    },

    calTable: function(y, m, dir) {
        var hdir = false;
        var sdir = false;
        if (dir == 'prev') {
            if (m == 1) {
                y = y - 1;
                m = 12;
            } else {
                m = m - 1;
            }
            hdir = 'right';
            sdir = 'left';
        } else if (dir == 'next') {
            if (m == 12) {
                y = y + 1;
                m = 1;
            } else {
                m = m + 1;
            }
            hdir = 'left';
            sdir = 'right';
        }

        var url = MOW.vars.blog_path + '/cal_table?year=' + y + '&month=' + m;
        var ym = y + '-' + m;
        if (ym in cal_cache) {
            $('#calendar').hide(
                'slide', {direction: hdir}, 'fast',
                function() {
                    $(this).html(cal_cache[ym])
                        .show('slide', {direction: sdir}, 'fast');
                });
        } else {
            $.get(url, function(table) {
                $('#calendar').hide(
                    'slide', {direction: hdir}, 'fast',
                    function() {
                        $(this).html(table)
                            .show('slide', {direction: sdir}, 'fast');
                        cal_cache[ym] = table;
                    });
            });
        }
        $.cookie('last_calendar', ym);
    },

    expandAllTags: function() {
        var url = MOW.vars.blog_path + '/all_tags';
        console.log(url);
        $.get(url, function(ul) {
            $('#allTags').hide(
                'slide', {direction: 'up'}, 'slow',
                function() {
                    $(this).html(ul)
                        .show('slide', {direction: 'up'}, 'slow');
                });
        });
    },

    previewComment: function() {
        if (! MOW.vars.previewd) {
            $('<input type="hidden" name="eid" />')
                .val(location.pathname.split('/').pop())
                .appendTo($('#comm_field'));
            $('<input type="hidden" name="comm_time" />')
                .val(new Date().getTime() / 1000)
                .appendTo($('#comm_field'));
            $('<input type="hidden" name="pbody" />')
                .val($('#comm_body').val())
                .appendTo($('#comm_field'));
            MOW.vars.previewed = true;
        }

        if ($('#comm_author').val()) {
            $.cookie('comm_author', $('#comm_author').val(),
                     {expires: 30, path: MOW.vars.blog_path + '/'});
        } else {
            alert('Please input your name.');
            $('#comm_author').focus();
            return;
        }

        if (! $('#comm_body').val()) {
            alert('Please input comment.');
            $('#comm_body').focus();
            return;
        }
        
        $('#preview').empty();
        $('#preview').html($('#comm_body').val().replace('\n', '<br />'));
        $('#posting').removeAttr('disabled').addClass('btn-success');
        $('#comm_form').attr('action', MOW.vars.blog_path + '/post_comment');
    },

    search: function() {
        $('#search').val($('#search').val() +
                         ' site:' + location.host + MOW.vars.blog_path + '/');
    },

    setCommentForm: function() {
        if ($.cookie('comm_author')) {
            $('#comm_author').val($.cookie('comm_author'));
        } else {
            $('#comm_author').attr('placeholder', 'required');
        }

        $('#comm_title').val('Re: ' + $('h2 > a').text());

        $('<input type="button" class="btn-info" />')
            .val('Preview').click(MOW.previewComment).appendTo('#comm_actions');

        $('<input type="submit" id="posting" />')
            .val('Post').attr('disabled', 'disabled').appendTo('#comm_actions');
        $('<div id="preview" />').insertBefore($('#comm_actions'));

        this.vars.previewed = false;
    },
    
    vars: {}
};

var cal_cache = new Array();


$(document).ready(function() {
    MOW.init();
});
