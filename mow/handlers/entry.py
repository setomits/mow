# -*- coding: utf-8 -*-

from flask import abort, g, redirect, render_template, request, url_for

from mow import app
from mow.models import Entry, Tag, User
from mow.handlers import login_required

@app.route('/<int:entry_id>')
def entry_page(entry_id):
    mc_key = 'Entry_%d' % entry_id

    html = g.mc.get(mc_key)
    if html is None:
        entry = Entry.get_by_id(entry_id)
        if entry:
            g.entry = entry
            html = render_template('entry_page.html')
            g.mc.set(mc_key, html)
        else:
            return abort(404)
    return html


@app.route('/admin/entry/post', methods = ['POST'])
@login_required
def post_entry():
    user_name = request.form.get('user_name', '').strip()
    title = request.form.get('title', '').strip()
    subtitle = request.form.get('subtitle', '').strip()
    body = request.form.get('body', '').strip()
    extend = request.form.get('extend', '').strip()
    s_tags = request.form.get('tags', '').strip()

    if body:
        user = User.get_by_name(user_name)


        entry = Entry(author_id = user.id if user else g.login_user.id,
                      body = body,
                      title = title,
                      subtitle = subtitle,
                      extend = extend).save()
        labels = set([tag.strip() for tag in s_tags.split(',')])
        for label in labels:
            Tag(entry.id, label).save()

        return redirect(url_for('entry_editing_page', entry_id = entry.id))
    else:
        return abort(400)


@app.route('/admin/entry/edit', methods = ['GET', 'POST'])
@login_required
def entry_editing_page():
    if request.method == 'GET':
        entry_id = request.args.get('entry_id', '').strip()
    else:
        entry_id = request.form.get('entry_id', '').strip()

    entry = Entry.get_by_id(int(entry_id)) if entry_id.isdigit() else None

    if request.method == 'POST':
        if entry is None:
            return abort(400)

        title = request.form.get('title', '').strip()
        subtitle = request.form.get('subtitle', '').strip()
        body = request.form.get('body', '').strip()
        extend = request.form.get('extend', '').strip()
        s_tags = request.form.get('tags', '').strip()

        to_save = False

        if title != entry.title:
            entry.title = title
            to_save = True

        if subtitle != entry.subtitle:
            entry.subtitle = subtitle
            to_save = True

        if body != entry.body:
            entry.body = body
            to_save = True

        if extend != entry.extend:
            entry.extend = extend
            to_save = True

        if to_save:
            entry.save(clear_cache = True)

        labels = list(set([t.strip() for t in s_tags.split(',')]))
        tags = [tag for tag in entry.tags]

        if labels != [tag.label for tag in tags]:
            for tag in tags:
                tag.delete()

            for label in labels:
                Tag(entry.id, label).save()

    g.entry = entry

    return render_template('admin/edit_entry_page.html')


@app.route('/admin/entry/delete', methods = ['POST'])
@login_required
def delete_entry():
    entry_id = request.form.get('entry_id', '').strip()

    if entry_id and entry_id.isdigit():
        entry = Entry.get_by_id(int(entry_id))
        if entry:
            entry.delete()
            return redirect(url_for('admin_top_page'))
        else:
            return abort(404)
    else:
        return abort(400)
