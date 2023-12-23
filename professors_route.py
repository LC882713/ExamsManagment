from flask import Blueprint, render_template, redirect, url_for, request, session,flash
from flask_login import login_required, current_user
from sqlalchemy.orm import aliased
from collections import defaultdict
from datetime import datetime 
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError
from psycopg2 import errors
from init import *
from forms import *

professor_bp = Blueprint('professor_bp', __name__)

Session = sessionmaker(bind=engine)
session = Session()

#routes for the professors

@professor_bp.route('/exams', methods=['GET','POST'])
@login_required
def exams():
    form = ExamForm()
    if request.method == 'GET':
        return render_template("exams.html", form=form)

    if request.method == 'POST':
        if form.validate_on_submit():
            name = form.examName.data
            credits = form.credits.data
            num_tests = form.num_tests.data
            new_exam = Exams(name=name, credits=credits, num_tests=num_tests, id_professors=current_user.id)
            session.add(new_exam)
            session.commit()
            num_tests = int(num_tests)
            return redirect(url_for('professor_bp.examsTests', num_tests=num_tests))
    return render_template('professorMenu.html')

@professor_bp.route('/exams/examsTests<num_tests>', methods=['GET','POST'])
@login_required
def examsTests(num_tests):
    form =TestForm()
    if request.method == 'GET':
        if int(num_tests) == 0:
            flash('Tests registered successfully!', 'success')
            return redirect(url_for('professor_bp.exams'))
        exams=session.query(Exams).order_by(desc(Exams.id_exam)).limit(1)
        return render_template('examsTests.html',exams=exams,num_tests=int(num_tests),form=form)
    if  request.method == 'POST':
        if form.validate_on_submit():
            id_exams = form.id_exams.data
            for i in range(int(num_tests)):
                namet = form.name.data
                bonus = form.bonus.data
                type = form.type.data
                grade_weight = form.grade_weight.data

                new_test = Tests(type=type, bonus=bonus, name=namet, grade_weight=grade_weight, id_exams=id_exams)
                session.add(new_test)
                session.commit()

                new_professor_tests = Professors_tests(id_professors=current_user.id, id_tests=new_test.id_test)
                session.add(new_professor_tests)
                session.commit()          
                return redirect(url_for('professor_bp.examsTests', num_tests=int(num_tests)-1))
        flash('Tests registered successfully!', 'success')
        return redirect(url_for('professor_bp.exams'))
    return render_template('examsTests.html', num_tests=int(num_tests))


@professor_bp.route('/justtest', methods=['GET','POST'])
@login_required
def justtest():
    form = justTestForm()
    if request.method == 'GET':
        lists = ( session.query(Exams).filter(Exams.id_professors == current_user.id).all())
        for list in lists:
            print(list)
        return render_template("justtest.html",lists=lists, form=form)
    
    if request.method == 'POST':
        
        if form.validate_on_submit():
            id_exam = form.id_exam.data
            namet = form.name.data
            bonus = form.bonus.data
            type = form.type.data
            grade_weight = form.grade_weight.data
            
            new_test = Tests(type=type, bonus=bonus, name=namet, grade_weight=grade_weight, id_exams=int(id_exam))
            session.add(new_test)
            session.commit()
            new_professor_tests = Professors_tests(id_professors=current_user.id, id_tests=new_test.id_test)
            session.add(new_professor_tests)
            session.commit()

            return redirect(url_for('professor_bp.exams'))
        
    return render_template('justtest.html')

@professor_bp.route('/dateExams', methods=['GET','POST']) 
@login_required
def dateExams():
    form = DateExamForm()
    if request.method == 'GET':        
        pt = aliased(Professors_tests)
        st = aliased(Sessions_tests)
        tests = session.query(Tests).\
        join(pt, Tests.id_test == pt.id_tests).\
        filter(pt.id_professors == current_user.id).\
        outerjoin(st, Tests.id_test == st.id_tests).\
        filter(st.id_tests == None).all()

        return render_template('dateExams.html',tests=tests,form=form)

    if  request.method == 'POST':
        if form.validate_on_submit():
            selected_date = form.selected_date.data 
            id_tests = form.id_tests.data

            try:
                new_sessions=Sessions()
                session.add(new_sessions)
                session.commit()

                new_sessions_tests = Sessions_tests(id_sessions=new_sessions.id_session,id_tests=id_tests,date=selected_date)
                session.add(new_sessions_tests)
                session.commit()
                return redirect(url_for('professor_bp.dateExams'))
            
            except IntegrityError as e:
                session.rollback()
                if 'Il test non può essere fatto nei weekend' in str(e):
                    flash('Test cannot be done on weekends. Please select a different date.', 'error')
                    
                else:
                    flash('An error occurred while processing your request.', 'error')

            return redirect(url_for('professor_bp.dateExams'))
    return render_template('professorMenu.html')


@professor_bp.route('/tests_created', methods=['GET','POST'])
@login_required
def tests_created():
    form =TestCreatedForm()
    if request.method == 'GET':
        t= aliased(Tests)
        pt=aliased(Professors_tests)
        st=aliased(Sessions_tests)
        tests=(session.query(t.id_test, t.name, t.type, st.date,pt.id_professors)
            .join(pt, t.id_test== pt.id_tests)
            .join(st,st.id_tests==t.id_test ).all())
        return render_template("tests_created.html", tests=tests,form=form)
    
    if request.method == 'POST':
        if form.validate_on_submit():
            test_id = form.id_test.data
            new_name = form.name.data
            new_grade_weight = form.grade_weight.data
            new_type = form.type.data
            new_date = form.date.data

            test = session.query(Tests).filter_by(id_test=test_id).first()
            sessions_tests = session.query(Sessions_tests).filter_by(id_tests=test_id).first()

            if test and sessions_tests:
                test.name = new_name
                test.type = new_type
                sessions_tests.date = new_date
                test.grade_weight = new_grade_weight
                session.commit()

                flash('Test aggiornato con successo', 'success')
                return redirect(url_for('professor_bp.tests_created'))
            else:
                flash('Test non trovato o sessione non trovata', 'error')

            return redirect(url_for('professor_bp.tests_created'))

    return render_template('professorMenu.html')


@professor_bp.route('/grades', methods=['GET','POST'])
@login_required
def grades():
    form = GradeForm()
    if request.method == 'GET':

        tests = (
            session.query(
                Tests.name.label('Test_Name'),
                Users.name.label('User_Name'),
                Tests.id_test,
                Tests.type,
                Tests.bonus,
                Registrations.verb_date,
                Registrations.id_registrations
            )
            .join(Registrations, Registrations.id_tests == Tests.id_test)
            .join(Users, Registrations.id_students == Users.id)
            .join(Professors_tests,Tests.id_test == Professors_tests.id_tests)
            .filter(Professors_tests.id_professors == current_user.id) 
            .filter(Registrations.grade==None ).all()) 
        
        return render_template('grades.html',tests=tests,form=form)
    
    if  request.method == 'POST':
        if form.validate_on_submit():
            id_registrations = form.id_subscribes.data
            score = form.score.data
            subscribe = session.query(Registrations).filter(Registrations.id_registrations == id_registrations).first()
            subscribe.grade = score
            session.commit()
            flash('subscribed successfully!', 'success')
            
            return redirect(url_for('professor_bp.grades'))
        return render_template('professorMenu.html', tests=tests, form=form) 
    return render_template('professorMenu.html')


@professor_bp.route('/studentStatus')
@login_required
def studentStatus():
    t = aliased(Tests)
    e = aliased(Exams)
    se = aliased(Students_exams)
    lists = (
            session.query(
                Users.id, Users.name,
                t.id_test, t.name.label('test_name'), t.type,t.bonus,t.grade_weight,
                Registrations.verb_date, Registrations.grade,
                e.num_tests, e.id_exam, e.name.label('exam_name')
            )
            .join(Registrations, Users.id == Registrations.id_students)
            .join(t, Registrations.id_tests == t.id_test)
            .join(Professors_tests, t.id_test == Professors_tests.id_tests)
            .join(e, t.id_exams == e.id_exam)         
            .join(se, and_(Users.id == se.id_students,e.id_exam == se.id_exams), isouter=True)
            .filter( 
                Professors_tests.id_professors == current_user.id,
                t.id_test == Professors_tests.id_tests,
                Registrations.expiration_date > func.current_date()
            )
            .group_by(
                Users.id, Users.name,
                t.id_test, t.name, t.type,
                Registrations.verb_date, Registrations.grade,
                e.num_tests, e.id_exam, e.name
            ).all())
    
    return render_template('studentStatus.html',lists=lists) 

@professor_bp.route('/helprof')
@login_required
def helprof():
    return render_template('helprof.html') 


@professor_bp.route('/examgraderecord', methods=['GET', 'POST'])
@login_required
def examgraderecord():
    form = registerExamGrade()
    if request.method == 'GET':
        t = aliased(Tests)
        e = aliased(Exams)
        se = aliased(Students_exams)
      
        lists = (
            session.query(
                Users.id, Users.name,
                t.id_test, t.name.label('test_name'), t.type,t.bonus,t.grade_weight,
                Registrations.verb_date, Registrations.grade,
                e.num_tests, e.id_exam, e.name.label('exam_name'),
                (func.sum(Registrations.grade * t.grade_weight)/ 100).label('total_grade')
            )
            .join(Registrations, Users.id == Registrations.id_students)
            .join(t, Registrations.id_tests == t.id_test)
            .join(Professors_tests, t.id_test == Professors_tests.id_tests)
            .join(e, t.id_exams == e.id_exam)         
            .join(se, and_(Users.id == se.id_students,e.id_exam == se.id_exams), isouter=True)
            .filter( 
                Registrations.grade > 17,
                se.total_grade.is_(None),
                Professors_tests.id_professors == current_user.id,
                t.id_test == Professors_tests.id_tests,
                Registrations.expiration_date > func.current_date()
            )
            .group_by(
                Users.id, Users.name,
                t.id_test, t.name, t.type,
                Registrations.verb_date, Registrations.grade,
                e.num_tests, e.id_exam, e.name
            ).all())
        for row in lists:
            print(row)
        print("-------finished lists----------")

        filtered_results = []
        counts_dict = {}
        for result in lists:
            id_exams = result.id_exam
            id_students = result.id
            num_tests = result.num_tests

            key = (id_exams, id_students)

            counts_dict[key] = counts_dict.get(key, 0) + 1

            if counts_dict[key] == num_tests:
                filtered_results.append(result)

        for row in filtered_results:
            print(row)
        print("-------filtered_results----------")
        id_exams_list = [result.id_exam for result in filtered_results]

        additional_results = (
            session.query(
                Users.id, Users.name,
                t.id_test, t.name.label('test_name'), t.type, t.bonus, t.grade_weight,
                Registrations.verb_date, Registrations.grade,
                e.num_tests, e.id_exam, e.name.label('exam_name'),
                (func.sum(Registrations.grade * t.grade_weight) / 100).label('total_grade')
            )
            .join(Registrations, Users.id == Registrations.id_students)
            .join(t, Registrations.id_tests == t.id_test)
            .join(Professors_tests, t.id_test == Professors_tests.id_tests)
            .join(e, t.id_exams == e.id_exam)
            .join(se, and_(Users.id == se.id_students, e.id_exam == se.id_exams), isouter=True)
            .filter(
                Users.id == result.id,
                e.id_exam.in_(id_exams_list)  
            )
            .group_by(
                Users.id, Users.name,
                t.id_test, t.name, t.type,
                Registrations.verb_date, Registrations.grade,
                e.num_tests, e.id_exam, e.name
            )
            .all()
        )
        for row in additional_results:
            print(row)

        total_grade_sums = defaultdict(float)

        for item in additional_results:
            key = (item.id, item.id_exam)
            total_grade_sums[key] += float(item.total_grade)+ float(item.bonus or 0)

        return render_template('examgraderecord.html',lists=additional_results,total_grade_sums=total_grade_sums, form=form)
    
    if request.method == 'POST':
        if form.validate_on_submit():
            print('Form is validated successfully!')
            id_students = form.id_students.data
            id_exams = form.id_exam.data
            total_grade = form.total_grade.data
            new_students_exam = Students_exams(id_students=id_students, id_exams=id_exams, total_grade=total_grade)
            session.add(new_students_exam)
            session.commit()
            flash('Form submitted successfully!', 'success')
            print('Record added to the database!')

            return redirect(url_for('professor_bp.examgraderecord'))
    return render_template('examgraderecord.html', form=form)
