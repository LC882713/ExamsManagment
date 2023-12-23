from flask import Blueprint, render_template, redirect, url_for, request, session,flash
from flask_login import login_required, current_user
from sqlalchemy.orm import aliased
from sqlalchemy.orm.exc import NoResultFound
from datetime import timedelta, datetime as dt
from init import *
from forms import *


student_bp = Blueprint('student_bp', __name__)

Session = sessionmaker(bind=engine)
session = Session()

#routes for the students

@student_bp.route('/subscribeRounds',methods=['GET','POST'])  
@login_required
def subscribeRounds():
    form = SubscribeForm()
    if request.method == 'GET': 
        subs = (
            session.query(
                Exams.name.label('exam_name'),  
                Tests.name.label('test_name'),
                Sessions_tests.date,Sessions_tests.id_sessions,
                Tests.type,
                Tests.id_test
            )
            .join(Sessions_tests, Tests.id_test == Sessions_tests.id_tests)
            .join(Exams, Exams.id_exam == Tests.id_exams)
            .join(Students_exams, and_(Students_exams.id_students == current_user.id, Students_exams.id_exams == Exams.id_exam), isouter=True) 
            .filter(
                Sessions_tests.date.isnot(None),
                ~exists().where(and_(
                    Registrations.id_students == current_user.id,
                    Registrations.id_tests == Tests.id_test,
                    Registrations.verb_date == Sessions_tests.date
                ))
            )
            .all()
        )
        

        return render_template('subscribeRound.html', subs=subs,form=form)

    if  request.method == 'POST':
        print("POST Request")
        if form.validate_on_submit():
            print("Form is valid")
            id_students = form.id.data
            id_tests = form.id_tests.data
            id_sessions=form.id_sessions.data
            verb_date = form.verb_date.data 
            expiration_date=verb_date + timedelta(days=365)
            print(f"Data received: id_students={id_students}, id_tests={id_tests}, verb_date={verb_date}")
            new_registrations=Registrations(verb_date=verb_date,expiration_date=expiration_date,id_students=id_students,id_tests=id_tests,id_sessions=id_sessions)
            session.add(new_registrations)
            session.commit()
            print("Data saved successfully")
            return redirect(url_for('student_bp.subscribeRounds'))
        else:
            print("Form is not valid")
            print(form.errors)
            print(form.id.data)
            print(form.id_tests.data)
            print(form.verb_date.data)
    return render_template('studentMenu.html') 


@student_bp.route('/listSubscribe',methods=['GET','POST'])
@login_required
def listSubscribe():
    form =listsubscribe()
    if request.method == 'GET': 
        subs = (
        session.query(
            Tests.name.label('test_name'),
            Users.name.label('student_name'),
            Tests.id_test,
            Tests.type,
            Registrations.verb_date,
            Registrations.id_registrations
        )
        .join(Registrations, Registrations.id_tests == Tests.id_test)
        .join(Users, Registrations.id_students == Users.id)
        .filter(Users.id == current_user.id).distinct().all()) 
    
        return render_template('listSubscribe.html', subs=subs,form=form)
    if  request.method == 'POST':
        if form.validate_on_submit():
            id_registration = form.id_registrations.data 
            try:
                registration_to_delete = session.query(Registrations).filter_by(id_registrations=id_registration).one()

                current_date = dt.today()
                if registration_to_delete.verb_date >= current_date.date() + timedelta(days=3):
                    session.delete(registration_to_delete)
                    session.commit()
                    flash('Registration deleted successfully', 'success')
                else:
                    flash('Cannot delete registration with verb_date less than 3 days from the current date', 'error')

            except NoResultFound:
                flash('Registration not found', 'error')
                
        return redirect(url_for('student_bp.listSubscribe'))
    return render_template('studentMenu.html') 


@student_bp.route('/resultsBoard')
@login_required
def resultsBoard():

    lists = (
        session.query(
            Registrations.id_tests,
            Tests.name.label('test_name'),
            Tests.type,
            Tests.bonus,
            Registrations.verb_date,
            Registrations.grade,
            Users.id.label('professor_id'),
            Users.name.label('professor_name'),
        )
        .join(Tests, Registrations.id_tests == Tests.id_test)
        .join(Exams, Tests.id_exams == Exams.id_exam)
        .join(Users, Exams.id_professors == Users.id)
        .filter(Registrations.grade > 17, Registrations.id_students == current_user.id)
        .all()
    )
    
    return render_template('resultsBoard.html', lists=lists)
   

@student_bp.route('/career')
@login_required
def career():
  
    lists = (
        session.query(
            Exams.id_exam,
            Exams.name.label('exam_name'),
            Exams.credits.label('exam_credits'),
            Users.id.label('professor_id'),
            Users.name.label('professor_name'),
            Students_exams.total_grade
        )
        .join(Tests, Tests.id_exams == Exams.id_exam)
        .join(Users, Exams.id_professors == Users.id)
        .join(Students_exams, Exams.id_exam == Students_exams.id_exams)
        .filter(Students_exams.total_grade > 17, Students_exams.id_students == current_user.id)
        .distinct(Exams.id_exam, Exams.name)
    ).all()

    return render_template('career.html',lists=lists) 
    
