from flask_blog.models import Users, Post
from flask import render_template, url_for, redirect, flash, request, abort
from flask_bcrypt import Bcrypt
from flask_blog.forms import (Registration_form, Log_in_form, Update_acc_form,
                              Post_form, RequestResetForm, ResetPasswordForm)
from flask_blog import app, db, mail
from flask_login import login_user, current_user, logout_user
import os
import secrets
from flask_mail import Message

title = 'ABOUT'
bcrypt = Bcrypt(app) #For encryption of password...


@app.route("/")
@app.route("/home", endpoint='home')
def home():
    return render_template('home.html')


@app.route("/about", endpoint='about')
def about():
    if current_user.is_authenticated:
        posts = Post.query.all()
        return render_template('about.html', posts=posts, title= title)
    else:
        flash(f'Not logged in!', 'info')
        return redirect(url_for('Register'))

@app.route("/login", methods=['GET', 'POST'])
def Login():
    if current_user.is_authenticated:
        return redirect(url_for('about'))
    form = Log_in_form()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Welcome back', 'success')
            return redirect(url_for('about'))
        else:
            flash(f'Login incorrect check email, password!', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/register", methods=['GET', 'POST'])
def Register():
    if current_user.is_authenticated:
        return redirect(url_for('about'))
    form = Registration_form()
    if form.validate_on_submit():
        #hashing the password...
        hashed_pass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        #Adding to database...
        user = Users(username= form.username.data, email=form.email.data, password=hashed_pass)
        db.session.add(user)
        db.session.commit()

        flash(f'Account created for {form.username.data}! Login Now!!', 'success')
        return redirect(url_for('Login'))
    else:
        return render_template('register.html', title='Register', form=form)



@app.route("/logout")
def Logout():
    logout_user()
    return redirect(url_for('Register'))


def save_pic(image_file):
    hex = secrets.token_hex(10)
    _, f_ext = os.path.splitext(image_file.filename)
    pic_path = os.path.join(app.root_path, 'static/profile_pics', hex + f_ext)
    image_file.save(pic_path)
    return (hex + f_ext)

@app.route("/account", methods=["GET", "POST"])
def Account():
    if current_user.is_authenticated:
        form = Update_acc_form()

        if form.validate_on_submit():
            if form.pic.data:
                current_user.image = save_pic(form.pic.data)

            current_user.username = form.username.data
            current_user.email = form.email.data
            db.session.commit()
            flash(f"Account is updated!", 'success')
            return redirect(url_for("Account"))
        elif request.method == "GET":
            form.username.data = current_user.username
            form.email.data = current_user.email
        img_file = url_for('static', filename='profile_pics/' + current_user.image)
        return render_template('account.html', title='Account', img = img_file, form =form)
    else:
        flash(f'Not logged in!', 'info')
        return redirect(url_for('Register'))

@app.route("/post/new", methods=["GET", "POST"])
def new_post():
    if current_user.is_authenticated:
        form = Post_form()
        if form.validate_on_submit():
            post = Post(title=form.title.data, content=form.content.data, user_id= current_user.id)
            db.session.add(post)
            db.session.commit()
            flash(f"Post is created!",'success')
            return redirect(url_for('about'))
        return render_template('create_post.html', title="New Post", form = form, legend="Create Post")
    else:
        return redirect(url_for('Register'))

@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def post(post_id):
    if current_user.is_authenticated:
        post = Post.query.get_or_404(post_id)
        return render_template('post.html', title=post_id, post= post)
    else:
        return redirect(url_for('Register'))

@app.route("/post/<int:post_id>/update", methods=["GET", "POST"])
def update_post(post_id):
    if current_user.is_authenticated:
        form = Post_form()
        post = Post.query.get_or_404(post_id)
        if post.author.username != current_user.username:
            abort(403)
        if form.validate_on_submit():
            post.title = form.title.data
            post.content = form.content.data
            db.session.commit()
            flash(f"Post for {post.author.username} updated!", "success")
            return redirect(url_for('about'))
        elif request.method == "GET":
            form.title.data = post.title
            form.content.data = post.content
        return render_template('create_post.html', title="Update post", post= post, form = form, legend="Update post")
    else:
        return redirect(url_for('Register'))


@app.route("/post/<int:post_id>/delete", methods=["POST"])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user.username != post.author.username:
        abort(403)
    else:
        db.session.delete(post)
        db.session.commit()
        flash(f"Post deleted successfully for {post.author.username}", "info")
    return redirect(url_for("about"))













def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender= 'abhijeet2101999@gmail.com', recipients=[user.email])
    msg.body = f"""To reset your password visit the link:
{url_for('reset_token', token=token, _external=True)}
If you did not request then ignore."""
    mail.send(msg)


@app.route("/reset_request", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:  # User needs to be logged out to change password...
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash(f"An email is sent to your mail for resetting password", 'info')
        return redirect((url_for('Login')))
    return render_template('reset_request.html', title="Reset request", form =form)


@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated: #User needs to be logged out to change password...
        return redirect(url_for('home'))
    user = Users.verify_reset_token(token)

    if user is None:
        flash(F"Invalid or expired token", "warning")
        return redirect(url_for("reset_request"))
    else:
        form = ResetPasswordForm()
        if form.validate_on_submit():
            # hashing the password...
            hashed_pass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

            # Adding to database...
            user.password = hashed_pass
            db.session.commit()

            flash(f'Password is updated ! Login Now!!', 'success')
            return redirect(url_for('Login'))
        return render_template('reset_token.html', title="Reset Password", form =form)