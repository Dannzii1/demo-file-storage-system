from humanfriendly import format_timespan
import datetime
from os.path import isfile

from flask_sqlalchemy import Pagination
from werkzeug.exceptions import abort

from app import allowed_uploads, app, login_manager, mail
import os
from .forms import *
from .models import *

from flask import render_template, request, redirect, url_for, flash, jsonify, safe_join, send_file
from flask_login import logout_user, login_user, login_required, current_user
from werkzeug.utils import secure_filename
from flask_mail import Message
from werkzeug.security import check_password_hash, generate_password_hash
from .utils import has_document_access, generate_institution_document_paths


@app.route('/')
def home():
    return render_template('home.html', landing_page=True, homepage=True)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data

        user = Users.query.filter_by(username=username).first()

        if user is None:
            flash("login failed, This user does not exist in our database", 'info')
            app.logger.warning(
                "{} has attempted to log into the system but they do don't exist on the database".format(username))
            return redirect(url_for('login'))

        try:
            if user is not None and check_password_hash(user.password, app.config.get("DEFAULT_PASSWORD")):
                token = user.generate_token(int(app.config['PW_RESET_TIMEOUT']))
                user.last_reset_token = token
                db.session.add(user)
                db.session.commit()
                flash("Welcome to the Institutional Registration System", 'success')
                app.logger.info(
                    "{} has logged into the system for the first time".format(username))
                return redirect(url_for('reset_password', token=token))

            if user is not None and check_password_hash(user.password, password):
                login_user(user)
                flash("Login Successful, You may begin uploading your documents for registration", "success")
                app.logger.info("{} has logged into the system".format(username))
                return redirect(url_for('dashboard'))
            else:
                flash("login failed, Check Username and Password", 'info')
                app.logger.info(
                    "{} has tried to log into the system but their credentials were wrong".format(username))
                return redirect(url_for('login'))

        except Exception as e:
            app.logger.error(e)
            flash("login failed", 'danger')
            return redirect(url_for('login'))

    return render_template('login.html', form=form, form_action=url_for('login'), on_login=True, login_header="Login")


@app.route('/reset/password/<token>', methods=['POST', 'GET'])
def reset_password(token):
    user = Users.validate_token(token)

    if user is None:
        abort(404, "Token invalid or user does not exist")

    form = ResetPasswordForm()

    if request.method == 'POST' and form.validate():

        try:
            user.password = generate_password_hash(form.confirm_password.data, method='pbkdf2:sha512', salt_length=10)
            user.token_used = True

            db.session.add(user)
            db.session.commit()
            flash("Your password has been reset", 'success')
            redirect_url = url_for('login')
            return redirect(redirect_url)
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            flash("An error occurred", 'danger')
            return redirect(url_for('reset_password', token=token))

    return render_template('reset_password.html', login_header="Reset Password", form_action=url_for('reset_password',
                                                                                                     token=token),
                           reset=True, form=form)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    page = int(request.args.get('page')) if request.args.get('page') is not None else 1
    current_user_id = current_user.id
    current = Users.query.filter_by(id=current_user_id).first()

    page = Documents.get_institution_files(current_user_id, page=page)

    return render_template('dashboard.html', on_dashboard=True, User=current_user.username,
                           files=page.items, page=page)


@login_manager.user_loader
def load_user(id):
    return Users.query.get(int(id))


@app.route('/forget/password', methods=['POST', 'GET'])
def forget_password():
    form = RequestResetForm()

    if request.method and form.validate_on_submit():
        email = form.email.data

        user = Users.query.filter_by(email_address=email).first()

        if user.email_address is not None:
            token = user.generate_token(int(app.config['PW_RESET_TIMEOUT']))
            try:
                user.last_reset_token = token
                db.session.add(user)
                db.session.commit()
                message = Message("Reset Password Request", sender=app.config.get("MAIL_SENDER"),
                                  recipients=[user.email_address])
                message.html = render_template("forget_password.html", username=user.username,
                                               token=token,
                                               expiration_time=format_timespan(int(app.config['PW_RESET_TIMEOUT'])))
                mail.send(message)
                app.logger.info(
                    "{} has requested to reset their email address on the system on"
                        .format(user.username))
                flash("An email has been sent to {}".format(email), 'info')
                redirect(url_for('forget_password'))
            except Exception as e:
                app.logger.error(e)
                flash("An Error Occurred, Sorry Please Try Again", 'danger')
                return redirect(url_for('forget_password'))
        else:
            flash("This username currently does not exist on our system, contact your admin to get registered", 'info')
            app.logger.info(
                "{} has requested to reset their email address on the system"
                ", however they do not exist on our system".format(user.username, datetime.now()))
            return redirect(url_for('forget_password'))

    return render_template('reset_password.html', on_login=True, forget_password=True,
                           form_action=url_for('forget_password'), login_header="Reset Password Request", form=form)


@app.route('/user/registration', methods=['GET', 'POST'])
def registration():
    form = RegistrationForm()

    if request.method == 'POST' and form.validate():
        try:
            first_name = form.first_name.data
            last_name = form.last_name.data
            email = form.email.data
            username = form.username.data
            password = form.password.data
            confirm_password = form.confirm_password.data

            if password == confirm_password:
                store_password = generate_password_hash(password, method='pbkdf2:sha512', salt_length=10)
                user = Users(username=username, password=store_password, first_name=first_name,
                             last_name=last_name, email_address=email)
                db.session.add(user)
                db.session.commit()

                flash("Registration Successful", 'success')
                app.logger.info(
                    "{} has registered successfully".format(username))
                return redirect(url_for('login'))
            else:
                flash('Please check your your passwords, ensure they match', 'info')
                app.logger.info("{} attempted to register".format(current_user.username))
                return redirect(url_for('registration'))

        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            flash("Internal Error Occurred, Try Again", 'info')
            return redirect(url_for('registration'))

    return render_template('registration.html', form=form, form_action=url_for('registration'), on_login=True,
                           form_title="Register aHere")


def save_file(document, base_path):
    filename = secure_filename(document.filename)
    document.save(os.path.join(base_path, filename))
    msg = 'The Document was Uploaded successfully'
    msg_type = 'success'
    return msg, msg_type


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also tell the browser not to cache the rendered page. If we wanted
    to we could change max-age to 600 seconds which would be 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


def generate_document_paths(current_users):
    relative_path = os.path.normpath(os.path.join(current_users, datetime.now().strftime('%Y')))
    absolute_path = os.path.normpath(os.path.join(app.config['DOCUMENTS_UPLOAD_FOLDER'], relative_path))
    return absolute_path, relative_path


@app.route("/user/upload", methods=['POST', 'GET'])
@login_required
def upload():
    files_form = UploadForm()

    if request.method == 'POST' and files_form.validate():
        try:
            file_uploaded = False
            current_users = current_user.id
            absolute_path, relative_path = generate_document_paths(str(current_users))

            if not os.path.exists(absolute_path):
                os.makedirs(absolute_path)

            for uploads in files_form.document.raw_data:
                filename = secure_filename(uploads.filename)

                new_upload = Documents(user_id=current_users, file_name=filename,
                                       relative_location=relative_path)

                db.session.add(new_upload)
                db.session.commit()
                save_file(uploads, absolute_path)
                file_uploaded = True

            if file_uploaded:
                flash('Upload successful', 'success')
                app.logger.info("{} has uploaded {} to the system".format(current_user.username, filename))
                return redirect(url_for('dashboard'))
            else:
                flash('No Documents were uploaded', 'warning')
                return redirect(url_for('upload'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            flash("Internal Error Occurred Please Check With Your Administrator", 'danger')
            return redirect(url_for('upload'))

    return render_template("upload.html", upload_form=True, files_form=files_form)


@app.route("/logout")
@login_required
def logout():
    logout_user()

    flash('Logged out successful', 'info')
    return redirect(url_for('home'))


@app.route('/document/<int:file_id>', methods=['GET'])
@has_document_access
@login_required
def get_file(file_id):
    file = Documents.query.filter_by(id=file_id).first()

    if file:
        is_pdf = file.file_name.split('.')[-1].lower() == 'pdf'

        file_path = os.path.normpath(os.path.join(app.config['DOCUMENTS_UPLOAD_FOLDER'], file.
                                                  relative_location, file.file_name))

        if not isfile(file_path):
            app.logger.error('Unable to locate file %s' % file_path)
            abort(500)

        response = send_file(file_path, as_attachment=(not is_pdf), attachment_filename=file.file_name)

        if is_pdf:
            response.headers['Content-Disposition'] = 'inline; filename=%s' % file.file_name

        return response

    abort(404)


@app.route('/del_file/<file_id>', methods=['GET'])
@has_document_access
@login_required
def del_file(file_id):
    file = Documents.query.filter_by(id=file_id).first()

    location = generate_institution_document_paths(str(file.user_id))
    file_path = os.path.normpath(os.path.join(location[0], file.file_name))

    redirect_url = url_for('dashboard')
    try:
        if os.path.exists(file_path):
            db.session.delete(file)
            db.session.commit()
            os.remove(file_path)

            msg = 'Document %s Deleted' % file.file_name
            msg_type = 'success'

            flash(msg, msg_type)
            app.logger.info("{} has {} successfully from the system".format(current_user.username, msg))
            return redirect(redirect_url)
        else:
            msg = 'Document %s not found' % file.file_name
            app.logger.info(msg)
            flash(msg, 'info')
            return redirect(redirect_url)

    except Exception as e:
        app.logger.error(e)
        msg = 'Document Deletion Failed'
        msg_type = 'danger'
        db.session.rollback()
        flash(msg, msg_type)
        return redirect(redirect_url)
