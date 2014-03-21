# -*- coding: utf-8 -*-

from flask import abort, g, render_template, redirect, request, session, url_for

from mow import app
from mow.models import User
from mow.handlers import login_required

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    error = None

    if request.method == 'POST':
        _user_name = request.form.get('user_name', '').strip()
        _password = request.form.get('password', '').strip()
        _next_url = request.form.get('next_url', url_for('top_page'))

        if _user_name and _password:
            user = User.get_by_name(_user_name)
            if user:
                if User.make_hash(_password) == user.password_hash:
                    session['user_name'] = user.name
                    return redirect(_next_url)
        return abort(403)
    else:
        _next_url = request.args.get('next_url', url_for('top_page'))
        return render_template('login.html', next_url = _next_url)


@app.route('/logout')
def logout():
    session.pop('user_name', None)
    return redirect(url_for('top_page'))
