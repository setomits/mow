# -*- coding: utf-8 -*-

from flask import g, redirect, render_template, request, url_for

from mow import app
from mow.models import Entry, Tag
from mow.handlers import login_required

@app.route('/tag/<label>/')
@app.route('/tag/<label>/<int:page>')
def tag_page(label, page = 1):
    if page < 1:
        return redirect(url_for('tag_page', label = label))

    g.label = label
    g.page = page
    g.entries = Entry.fetch_tagged_entries(
        label = label,
        page = page,
        limit = g.entries_per_page)

    if g.entries_per_page * (page - 1) + len(g.entries) < Tag.n_entries(label):
        g.has_older = True
    else:
        g.has_older = False
    g.has_newer = True if page > 1 else False

    return render_template('tag_page.html')


@app.route('/tag/')
def all_tags_page():
    return render_template('all_tags_page.html')


@app.route('/admin/tag/edit', methods = ['GET', 'POST'])
@login_required
def tag_editing_page():
    g.active = {'tag': True}

    if request.method == 'POST':
        current_label = request.form.get('current_label', '')
        new_label = request.form.get('new_label', '').strip()

        if Tag.n_entries(current_label):
            Tag.update_label(current_label, new_label)


    g.tag_labels = Tag.fetch_all_labels()
    return render_template('admin/edit_tag_page.html')
