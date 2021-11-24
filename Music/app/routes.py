from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user
from flask_login import logout_user
from flask_login import login_required
import uuid

from datetime import datetime, timedelta

from app import myapp_obj
from app import db


from app.forms import LoginForm, RegisForm, ProjectForm, TaskForm, ChangePasswordForm, DeleteAccountForm, ReassignedTask, AddnoteForm, ReadmeForm



from app.models import User, Tasks, Project, Schedule, Notification, Addnote, Readme



@myapp_obj.route("/login", methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect("/home") 
	form = LoginForm()
	if form.validate_on_submit():
        # User.query.filter_by() returns a list from the User table
        # first() returns first element of the list
        # the form.username.data is getting the info the user submitted in the form
		user = User.query.filter_by(username=form.username.data).first()
		print(form.username.data)
        # if no user found or password for user incorrect
        # user.check_password() is a method in the User class
		if user is None or not user.check_password(form.password.data):
			flash('Invalid username or password')
			return redirect('/login')
        # let flask_login library know what user logged int
        # it also means that their password was correct
		login_user(user, remember=form.remember_me.data)
		current_t = datetime.utcnow()
		current_user.last_login = current_t - timedelta(microseconds=current_t.microsecond)
		db.session.add(current_user)
		db.session.commit()
		print(current_user.last_login)
		next_page = url_for('home')

		return redirect(next_page)

	return render_template('login.html', title='Sign In', form=form)


@myapp_obj.route("/regis", methods=['GET','POST'])
def regis():
	if current_user.is_authenticated:
		return "<h1>you already logged in</h1>"
	form = RegisForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user is None:
			u = User(username=form.username.data, email=form.email.data)
			#u.last_login = datetime.utcnow()
			u.set_password(password=form.password.data)
			db.session.add(u)
			db.session.commit()
			flash('user added')
			#return redirect(url_for('login'))
		else:
			flash('user exist')
			#return redirect(url_for('login'))

	return render_template('regis.html', title='Sign Up', form=form)


@myapp_obj.route('/logout')
@login_required
def logout():
	current_t = datetime.utcnow()
	current_user.last_logout = current_t - timedelta(microseconds=current_t.microsecond)
	print("logout at: ", current_user.last_logout)
	print("login at: ", current_user.last_login)
	print("session time: ", current_user.last_logout- current_user.last_login)
	schedule = Schedule(user_id=current_user.id, total_time=(current_user.last_logout - current_user.last_login),login=current_user.last_login,logout=current_user.last_logout)
	db.session.add(schedule)
	db.session.commit()

	logout_user()
	return redirect(url_for('login'))











# user setting
@myapp_obj.route("/userSetting")
@login_required
def user_setting():
	return render_template('userSetting.html')


# change password
@myapp_obj.route('/changePassword',methods=['GET','POST'])
@login_required
def change_password():
	user = User.query.filter_by(id = current_user.id).first()
	form = ChangePasswordForm()
	print(user)
	if form.validate_on_submit():
		if user.check_password(form.old_password.data) and (form.old_password.data != form.new_password.data)  and (form.new_password.data == form.new_password_confirm.data):
			user.set_password(form.new_password.data)
			db.session.commit()
			return redirect(url_for('user_setting'))

	return render_template('changePassword.html', form = form)



# delete account
@myapp_obj.route('/deleteAccount', methods=['GET','POST'])
@login_required
def delete_account():
	user = User.query.filter_by(id = current_user.id).first()
	form = DeleteAccountForm()
	if form.validate_on_submit():
		if user.check_password(form.password.data) and (form.password.data == form.password_confirm.data):
			logout_user()
			db.session.delete(user)
			db.session.commit()
			flash('Account Deleted Successfully!')
			return redirect(url_for('login'))
		else:
			flash('Wrong password')
	return render_template('deleteAccount.html', form = form)




