from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime
from app import app, db
from app.forms import EditProfileForm, LoginForm, RegistrationForm, PostForm
from app.models import Post, User

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live')

        # https://en.wikipedia.org/wiki/Post/Redirect/Get
        return redirect(url_for('index'))

    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]

    return render_template('index.html', title='Home', form=form, posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is not None and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            
            next_page = request.args.get('next')

            # For security only redirect if path is relative. So redirect stays within the same site than application.
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
            
            return redirect(next_page)
        else:
            flash('Invalid username or password')
            return redirect(url_for('login'))

    return render_template('login.html', title='Sign in', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')

        return redirect(url_for('login'))
    
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()

    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]

    empty_form = EmptyForm()

    return render_template('user.html', user=user, posts=posts, form=empty_form)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit() # user adds to session automatically when we invoke current_user so we don't need to db.session.add()


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    return render_template('edit_profile.html', title='Edit Profile', form=form)


@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()

        if user is not None:
            if user is not current_user:
                current_user.follow(user)
                db.session.commit()
                flash('You are following {}!'.format(username))
                return redirect(url_for('user', username=username))
            else:
                flash('You cannot follow yourself!')
                return redirect(url_for('user', username=username))
        else:
            flash('User {} not found.'.format(username))
            return redirect(url_for('index'))
    else:
        # the only reason why the validate_on_submit() call can fail is if the CSRF token is missing or invalid, 
        # so in that case we just redirect the application back to the home page.
        return redirect(url_for('index'))


@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()

        if user is not None:
            if user is not current_user:
                current_user.unfollow(user)
                db.session.commit()
                flash('You are not following {}.'.format(username))
                return redirect(url_for('user', username=username))
            else:
                flash('You cannot unfollow yourself!')
                return redirect(url_for('user', username=username))
        else:
            flash('User {} not found.'.format(username))
            return redirect(url_for('index'))
    else:
        # the only reason why the validate_on_submit() call can fail is if the CSRF token is missing or invalid, 
        # so in that case we just redirect the application back to the home page.
        return redirect(url_for('index'))