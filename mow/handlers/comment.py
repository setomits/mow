# -*- coding: utf-8 -*-

from flask import abort, g, redirect, render_template, request, url_for

from mow import app
from mow.models import Entry, Tag, User, Comment
from mow.handlers import login_required

@app.route('/comment/post', methods = ['POST'])
def post_comment():
    entry_id = request.form.get('entry_id', '').strip()
    author_name = request.form.get('author_name', '').strip()
    title = request.form.get('comment_title', '').strip()
    body = request.form.get('comment_body', '').strip()

    if entry_id and entry_id.isdigit():
        entry = Entry.get_by_id(int(entry_id))
        if entry:
            pass
        else:
            return abort(400)
    else:
        return abort(400)

    if author_name and title and body:
        Comment(entry_id = entry.id,
                author_name = author_name,
                title = title,
                body = body).save(clear_cache = False)

        return redirect(url_for('entry_page', entry_id = entry.id))
    else:
        return abort(400)


@app.route('/admin/comment/edit', methods = ['GET', 'POST'])
@login_required
def comment_editing_page():
    g.active = {'comment': True}

    if request.method == 'GET':
        comment_id = request.args.get('comment_id', '').strip()
    else:
        comment_id = request.form.get('comment_id', '').strip()

    comment = Comment.get_by_id(int(comment_id)) if comment_id.isdigit() else None

    if request.method == 'POST':
        if comment is None:
            return abort(400)

        author_name = request.form.get('author_name', '').strip()
        title = request.form.get('title', '').strip()
        body = request.form.get('body', '').strip()

        to_save = False

        if author_name != comment.author_name:
            comment.author_name = author_name
            to_save = True

        if title != comment.title:
            comment.title = title
            to_save = True

        if body != comment.body:
            comment.body = body
            to_save = True

        if to_save:
            comment.save()

    g.comment = comment

    return render_template('admin/edit_comment_page.html')

@app.route('/admin/comment/delete', methods = ['POST'])
@login_required
def delete_comment():
    comment_id = request.form.get('comment_id', '').strip()

    if comment_id and comment_id.isdigit():
        comment = Comment.get_by_id(int(comment_id))
        if comment:
            comment.delete()
            return redirect(url_for('admin_top_page'))
        else:
            return abort(404)
    else:
        return abort(400)
