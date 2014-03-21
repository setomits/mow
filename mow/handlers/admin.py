# -*- coding: utf-8 -*-

from flask import render_template

from mow import app
from mow.models import User
from mow.handlers import login_required

@app.route('/admin')
@login_required
def admin_top_page():
    return render_template('admin/top.html')
