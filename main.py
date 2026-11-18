
from flask import Flask,render_template,request,redirect,session, url_for 
from dotenv import load_dotenv

import mysql.connector

app = Flask(__name__)
app.secret_key = "brother"

import os

load_dotenv()

db = mysql.connector.connect(
    host = os.getenv("DB_HOST", "localhost"),
    user = os.getenv("DB_USER", "root"),
    password = os.getenv("DB_PASSWORD", ""),
    database = os.getenv("DB_NAME", "college_manage")
)
# dictionary=True
mycursor = db.cursor(dictionary=True , buffered=True)

# MAIN_DASHBOARD PAGE ALL ROUTES HOME , ACADEMIC , ABOUT , ADMISSION , CONTACT AND LOGIN

@app.route('/')
def home():
    return render_template('main_dashboard.html')

@app.route('/academic')
def academic():
    return render_template('academic.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/admission',methods=['GET','POST'])
def admission():
    course_query = "SELECT * FROM COURSES ;"
    mycursor.execute(course_query)
    course = mycursor.fetchall()
    if request.method == 'POST':
        name = request.form['name']
        dob = request.form['dob']
        email = request.form['email']
        mobil_no = request.form['mobil_no']
        course = request.form['course']
        address = request.form['address']

        query = "INSERT INTO ADMISSION (FULL_NAME , DATE_OF_BIRTH , EMAIL , PHONE_NO ,COURSE , ADDRESS) VALUES (%s,%s,%s,%s,%s,%s);"
        val = (name,dob,email,mobil_no,course,address)

        mycursor.execute(query,val)
        db.commit()

    return render_template('admission.html',course=course)

@app.route('/view_admission')
def view_admission():

    if session.get("role") != "admin":
        return "Access Denied"

    mycursor.execute("SELECT * FROM ADMISSION")
    data = mycursor.fetchall()

    return render_template(
        'admin/view_admissions.html',
        admissions=data
)

@app.route('/admin/delete_admission/<int:id>')
def delete_admission(id):

    if session.get("role") != "admin":
        return "access denied"

    mycursor.execute(
        "DELETE FROM ADMISSION WHERE ID=%s",
        (id,)
    )
    db.commit()

    return redirect(url_for('view_admission'))


@app.route('/contact',methods=['GET','POST'])
def contact():
    if request.method == 'POST' :
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        mobil_no = request.form['mobil_no']
        message = request.form['message']
        
        sql_query = "INSERT INTO CONTACTS (FULL_NAME , EMAIL , SUBJECT , PHONE_NO , MESSAGE ) VALUES (%s,%s,%s,%s,%s);"
        val = (name,email,subject,mobil_no,message)

        mycursor.execute(sql_query,val)
        db.commit()
        return render_template('contact.html')
    
    return render_template('contact.html')

@app.route('/view_contact')
def contact_details():

    if session.get("role") != "admin":
        return "Access Denied"

    mycursor.execute("SELECT * FROM CONTACTS")
    contacts = mycursor.fetchall()

    return render_template(
        'admin/view_contact.html',
        contacts=contacts
    )

@app.route('/admin/delete_record/<int:id>')
def delete_record(id):
    if session.get("role") != "admin":
        return "access denied"
    mycursor.execute("DELETE FROM CONTACTS WHERE ID=%s",(id,))
    db.commit()
    return redirect(url_for('contact_details'))


@app.route('/login',methods=['GET','POST'])
def login():

    if request.method == 'POST' :
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        

        if role == 'admin':

            login_query = "SELECT * FROM ADMIN WHERE USERNAME = %s and PASSWORD = %s AND ROLE = %s;"
            val = (username,password,role)
            mycursor.execute(login_query,val)
            user = mycursor.fetchone()
            if user :
                session['username'] = user['USERNAME']
                session["role"] = role
                return redirect('/admin/admin_dashboard')
        
        elif role == 'student' :
            
            std = "SELECT * FROM students WHERE ID = %s AND phone_number = %s;"
            val_std = (username,password)
            mycursor.execute(std,val_std)

            user = mycursor.fetchone()         

            if user :
                session['student_id'] = user['id']
                session['firstname'] = user['Firstname']
                session['course'] = user['course']
                session["role"] = role
           
                return redirect('/student')
        
        elif role == 'teacher' :

            teacher = "SELECT * FROM teachers WHERE ID = %s AND MOBIL_NO = %s;"
            val_teacher = (username,password)
            mycursor.execute(teacher,val_teacher)
            
            user = mycursor.fetchone()
            if user :
                session['teacher_id'] = user['ID']
                session['firstname'] = user['FIRSTNAME']
                session["role"] = role
                return redirect('/teacher')
        else :
            return redirect('/login')

    return render_template('login.html')
            

@app.route('/logout')
def logout():
    session.clear()
    
    return redirect('/login')

# ADMIN  ALL PAGES  

@app.route('/admin/admin_dashboard')
def admin():
    if session.get("role") != "admin" :
        return "access denied"
    
    user_id  = session.get("username")

    query = "SELECT * FROM admin WHERE USERNAME = %s;"

    count_student = "SELECT COUNT(*) FROM students;"
    count_teacher = "SELECT COUNT(*) FROM teachers;" 
    count_class = "SELECT COUNT(*) FROM COURSES"
    mycursor.execute(count_student)
    s_count = mycursor.fetchone()
    
    
    mycursor.execute(count_teacher)
    t_count = mycursor.fetchone()
    
    mycursor.execute(count_class)
    c_count = mycursor.fetchone()

    mycursor.execute("SELECT * FROM NOTICE ORDER BY created_at DESC")
    notice = mycursor.fetchall()

    val = (user_id,)
    mycursor.execute(query, val)
    admin = mycursor.fetchone()


        # return redirect('/login')
        
    return render_template('admin/admin_dashboard.html',admin=admin,s_count = s_count,t_count=t_count,c_count=c_count,notice=notice,user_id=user_id)


@app.route('/admin/admin_students',methods=['GET','POST'])
def admin_students():

    if session.get("role") != "admin" :
        return "access denied"

    user_id  = session.get("username")
    
    # Get admin info
    mycursor.execute("SELECT * FROM admin WHERE USERNAME = %s;", (user_id,))
    admin = mycursor.fetchone()

    course_query = "SELECT * FROM COURSES ;"
    mycursor.execute(course_query)
    course = mycursor.fetchall()
    # print(course)

    if request.method == 'POST' :

        student_id = request.form.get('id') 

        firstname = request.form['firstname']
        middlename = request.form['middlename']
        surname = request.form['surname']
        dob = request.form['dob']
        gender = request.form['gender']
        admission_no = request.form['admission-no']
        roll_no = request.form['roll-no']
        aadhar_no = request.form['aadhar-no']
        mobil_no = request.form['mobil_no']
        email = request.form['email']
        category = request.form['category']
        religion = request.form['religion']
        nationality = request.form['nationality']
        course = request.form['course'] 
        address = request.form['address']
        city = request.form['city']
        state = request.form['state']
        pincode = request.form['pincode']
        parent_name = request.form['parent_name']
        parent_contact_no = request.form['parent_contact_no']
        parent_email = request.form['parent_email']

        if student_id :
            query_update = "UPDATE students SET FIRSTNAME=%s, MIDDLENAME=%s, SURNAME=%s, DOB=%s, GENDER=%s, ADMISSION_NO=%s, ROLL_NUMBER=%s, AADHAR_NUMBER=%s, PHONE_NUMBER=%s, EMAIL=%s, CATEGORY=%s, RELIGION=%s, NATIONALITY=%s, COURSE=%s , ADDRESS=%s, CITY=%s, STATE=%s, PINCODE=%s, PARENT_NAME=%s, PARENT_PHONE=%s, PARENT_EMAIL=%s WHERE id=%s"
            val = (firstname, middlename, surname, dob, gender, admission_no, roll_no, aadhar_no, mobil_no, email, category, religion, nationality, course, address, city, state, pincode, parent_name, parent_contact_no, parent_email,student_id)

            mycursor.execute(query_update,val)
            db.commit()


        else :
            query_insert = "INSERT INTO students (FIRSTNAME , MIDDLENAME , SURNAME ,DOB , GENDER , ADMISSION_NO, ROLL_NUMBER, AADHAR_NUMBER , PHONE_NUMBER , EMAIL , CATEGORY, RELIGION, NATIONALITY, COURSE  , ADDRESS , CITY , STATE , PINCODE , PARENT_NAME , PARENT_PHONE , PARENT_EMAIL) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
            val = (firstname,middlename,surname,dob,gender,admission_no,roll_no,aadhar_no,mobil_no,email,category,religion,nationality,course,address,city,state,pincode,parent_name,parent_contact_no,parent_email)

            mycursor.execute(query_insert,val)


        db.commit()
        
    show_query = "SELECT * FROM students "
    mycursor.execute(show_query)
    result = mycursor.fetchall()
    return render_template('admin/admin_students.html',result=result,courses=course,admin=admin,user_id=user_id)

@app.route('/admin/show_student/<int:id>')
def show_student(id):

    if session.get("role") != "admin" :
        return "access denied"

    user_id  = session.get("username")

    mycursor.execute("SELECT * FROM students WHERE id = %s", (id,))
    student = mycursor.fetchone()
    return render_template('admin/show_student.html', student=student, admin=admin,user_id=user_id)

@app.route('/admin/edit_student/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    
    if session.get("role") != "admin" :
        return "access denied"

    user_id  = session.get("username")
    
    # Get admin info
    mycursor.execute("SELECT * FROM admin WHERE USERNAME = %s;", (user_id,))
    admin = mycursor.fetchone()

    course_query = "SELECT * FROM COURSES ;"
    mycursor.execute(course_query)
    course = mycursor.fetchall()
    
    mycursor.execute("SELECT * FROM students WHERE id=%s", (id,))
    students = mycursor.fetchone()

    mycursor.execute("SELECT * FROM students")
    result = mycursor.fetchall()

    
    return render_template('admin/admin_students.html',courses=course,result=result,admin=admin,student=students,user_id=user_id)

@app.route('/admin/delete_student/<int:id>')
def delete_student(id):

    if session.get("role") != "admin" :
        return "access denied"

    user_id  = session.get("username")

    mycursor.execute("DELETE FROM students WHERE id=%s", (id,))
    db.commit()
    return redirect(url_for('admin_students'))

@app.route('/admin/admin_teachers', methods=['GET', 'POST'])
def admin_teachers():

    if session.get("role") != "admin" :
        return "access denied"
    
    user_id  = session.get("username")
    
    # Get admin info
    mycursor.execute("SELECT * FROM admin WHERE USERNAME = %s;", (user_id,))
    admin = mycursor.fetchone()

    course_query = "SELECT * FROM COURSES ;"
    mycursor.execute(course_query)
    course = mycursor.fetchall()
    
    if request.method == 'POST':

        teacher_id = request.form.get('id')                      

        firstname = request.form['firstname']       
        middlename = request.form['middlename']
        surname = request.form['surname']
        gender = request.form['gender']
        dob = request.form['dob']
        join_date = request.form['join_date']
        subject = request.form['subject']
        mobil_no = request.form['mobil_no']
        email = request.form['email']
        address = request.form['address']


        if teacher_id: 

            query = "UPDATE teachers SET FIRSTNAME=%s,MIDDLENAME=%s,SURNAME=%s,GENDER=%s,DOB=%s,JOIN_DATE=%s,SUBJECT=%s,MOBIL_NO=%s,EMAIL=%s,ADDRESS=%s WHERE id=%s;"

            val = (firstname,middlename,surname , gender, dob, join_date,subject,mobil_no, email, address,teacher_id)

        else: 

            query = "INSERT INTO teachers (FIRSTNAME,MIDDLENAME,SURNAME,GENDER,DOB,JOIN_DATE,SUBJECT,MOBIL_NO,EMAIL,ADDRESS) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"

            val = (firstname,middlename,surname, gender, dob, join_date,subject,mobil_no, email, address)

        mycursor.execute(query, val)
        db.commit()

        return redirect(url_for('admin_teachers'))
        
    show_query = "SELECT * FROM teachers "
    mycursor.execute(show_query)
    result = mycursor.fetchall()
    
    return render_template('admin/admin_teachers.html',course=course,admin=admin,result=result,user_id=user_id)

@app.route('/admin/edit_teacher/<int:id>',methods=['GET','POST'])
def edit_teachers(id):
    if session.get("role") != "admin" :
        return "access denied"
    
    user_id  = session.get("username")
    
    # Get admin info
    mycursor.execute("SELECT * FROM admin WHERE USERNAME = %s;", (user_id,))
    admin = mycursor.fetchone()

    course_query = "SELECT * FROM COURSES ;"
    mycursor.execute(course_query)
    course = mycursor.fetchall()
 
    mycursor.execute("SELECT * FROM teachers WHERE id=%s", (id,))
    teacher = mycursor.fetchone()
    # print(teacher)

    mycursor.execute("SELECT * FROM teachers")
    result = mycursor.fetchall()
    # return redirect(url_for('admin_teachers'))


    return render_template('admin/admin_teachers.html',course=course,user_id=user_id,teacher=teacher,result=result,admin=admin)

@app.route('/admin/delete_teachers/<int:id>')
def delete_teacher(id):
    if session.get("role") != "admin" :
        return "access denied"

    user_id  = session.get("username")

    mycursor.execute("DELETE FROM teachers WHERE id=%s", (id,))
    db.commit()
    return redirect(url_for('admin_teachers'))


@app.route('/admin/admin_courses', methods=['GET', 'POST'])
def admin_courses():
    
    if session.get("role") != "admin" :
        return "access denied"

    user_id  = session.get("username")
    
    # Get admin info
    mycursor.execute("SELECT * FROM admin WHERE USERNAME = %s;", (user_id,))
    admin = mycursor.fetchone()

    if request.method == 'POST' :
        course_name = request.form['c_name']
        course_code = request.form['c_code']
        department = request.form['department']
        credits = request.form['credits']

        query = "INSERT INTO COURSES (COURSE_NAME,COURSE_CODE,DEPARTMENT,CREDITS) VALUES(%s,%s,%s,%s)"
        val = (course_name,course_code,department,credits)
        mycursor.execute(query,val)
        db.commit()
        return redirect(url_for('admin_courses'))
    
    show_query = "SELECT * FROM courses "
    
    mycursor.execute(show_query)
    courses = mycursor.fetchall()
    

    return render_template('admin/admin_courses.html', courses=courses,admin=admin,user_id=user_id)


@app.route('/admin/exam', methods=['GET', 'POST'])
def admin_exam():

    if session.get("role") != "admin" : 
        return "access denied"

    user_id  = session.get("username")
    
    # Get admin info
    mycursor.execute("SELECT * FROM admin WHERE USERNAME = %s;", (user_id,))
    admin = mycursor.fetchone()

    course_query = "SELECT * FROM COURSES ;"
    mycursor.execute(course_query)
    course = mycursor.fetchall()

    if request.method == 'POST':
        if 'addexam' in request.form:
            exam_name = request.form['exam-name']
            course = request.form['course']
            academic_year = request.form['academic-year']
            exam_type = request.form['exam-type']

            
            query_insert = "INSERT INTO exam (exam_name ,course , academic_year , EXAM_TYPE) VALUES (%s,%s,%s,%s);"
            val = (exam_name,course,academic_year,exam_type)
            mycursor.execute(query_insert,val)

            db.commit()
            return redirect(url_for('admin_exam'))
            
        if 'addtimetable' in request.form:
            eid = request.form['exam_id']
            course = request.form['course']
            edate = request.form['exam_date']
            eday = request.form['exam-day']
            subject = request.form['subject']
            time = request.form['start-time'] + '-' + request.form['end-time']
            duration = request.form['duration']
            etype = request.form['exam-type']

            q1 = "INSERT INTO exam_timetable(EXAM_ID,COURSE,EXAM_DATE,EXAM_DAY,SUBJECT_NAME,EXAM_TIME,DURATION,EXAM_TYPE) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)"
            val1 = (eid,course,edate,eday,subject,time,duration,etype)

            mycursor.execute(q1,val1)
            db.commit()
            return redirect(url_for('admin_exam'))
    
    query = "SELECT * FROM exam ;"

    mycursor.execute(query)
    exams = mycursor.fetchall()
    # print(exams)

    for exam in exams:

        q2 = "SELECT * FROM exam_timetable WHERE EXAM_ID = %s ORDER BY exam_date ASC"

        mycursor.execute(q2,(exam['ID'],))
        exam['tt'] = mycursor.fetchall()
        # print(exam['tt'])


    # print(tt)
    return render_template('admin/admin_exam.html',courses=course , exams=exams , admin=admin,user_id=user_id)

@app.route('/admin/delete_exam/<int:id>',methods = ['GET','POST'])
def delete_exam(id):
    if session.get("role") != "admin" :
        return "access denied"

    user_id  = session.get("username")

    mycursor.execute("DELETE FROM exam WHERE ID=%s", (id,))
    db.commit()
    return redirect(url_for('admin_exam'))

@app.route('/admin/delete_examtimetable/<int:id>',methods = ['GET','POST'])
def delete_examtimetable(id):
    if session.get("role") != "admin" :
        return "access denied"

    user_id  = session.get("username")

    mycursor.execute("DELETE FROM exam_timetable WHERE id=%s", (id,))
    db.commit()
    return redirect(url_for('admin_exam'))


@app.route('/admin/delete_timetable/<int:id>')
def delete_timetable(id):
    if session.get("role") != "admin":
        return redirect('/login')
    
    try:
        mycursor.execute("DELETE FROM lecture_timetable WHERE id=%s", (id,))
        db.commit()
    except Exception as e:
        db.rollback()
        return f"Error deleting timetable: {str(e)}"
    
    return redirect(url_for('admin_time_table'))

@app.route('/admin/time_table', methods=['GET', 'POST'])
def admin_time_table():

    if session.get("role") != "admin" :
        return "access denied"

    user_id  = session.get("username")
    
    # Get admin info
    mycursor.execute("SELECT * FROM admin WHERE USERNAME = %s;", (user_id,))
    admin = mycursor.fetchone()

    course_query = "SELECT * FROM COURSES ;"
    mycursor.execute(course_query)
    course = mycursor.fetchall()
    
    mycursor.execute("SELECT * FROM teachers ;") 
    teachers = mycursor.fetchall()

    timetable = []
    if request.method == 'POST':
        if 'generate' in request.form:
            course_val = request.form['course']
            day = request.form['day']
            lecture = request.form['lecture_name']
            start_time = request.form['start_time']
            end_time = request.form['end_time']
            subject_name = request.form['subject_name']
            teacher_name = request.form['teacher_name']

            query_insert = "INSERT INTO lecture_timetable (course, lecture_day, period_name, start_time, end_time, subject_name, teacher_id) VALUES (%s,%s,%s,%s,%s,%s,%s);"
            val = (course_val,day,lecture,start_time,end_time,subject_name,teacher_name)

            mycursor.execute(query_insert,val)
            db.commit()
            return redirect(url_for('admin_time_table'))
            
        elif 'update' in request.form:
            tt_id = request.form['tt_id']
            course_val = request.form['course']
            day = request.form['day']
            lecture = request.form['lecture_name']
            start_time = request.form['start_time']
            end_time = request.form['end_time']
            subject_name = request.form['subject_name']
            teacher_name = request.form['teacher_name']
            
            query_update = "UPDATE lecture_timetable SET course=%s, lecture_day=%s, period_name=%s, start_time=%s, end_time=%s, subject_name=%s, teacher_id=%s WHERE id=%s"
            val = (course_val, day, lecture, start_time, end_time, subject_name, teacher_name, tt_id)
            
            mycursor.execute(query_update, val)
            db.commit()
            return redirect(url_for('admin_time_table'))
    
    show_query = "SELECT id, course, lecture_day, period_name, start_time, end_time, subject_name, teacher_id FROM lecture_timetable ORDER BY course, FIELD(lecture_day,'MONDAY','TUESDAY','WEDNESDAY','THURSDAY','FRIDAY','SATURDAY'), start_time;"
    mycursor.execute(show_query)
    timetable = mycursor.fetchall()
    return render_template('admin/admin_timetable.html',courses=course,teachers=teachers,admin=admin, timetable=timetable,user_id=user_id)

@app.route('/admin/notice',methods=['GET','POST'])
def admin_notice():

    if session.get("role") != "admin" :
        return "access denied"

    user_id  = session.get("username")
    
    # Get admin info
    mycursor.execute("SELECT * FROM admin WHERE USERNAME = %s;", (user_id,))
    admin = mycursor.fetchone()
    
    mycursor.execute("SELECT * FROM COURSES")
    courses = mycursor.fetchall()

    if request.method == "POST" :
        topic = request.form['topic']
        referance = "ADMIN"
        notice = request.form['notice']
        course = request.form['course']

        query = "INSERT INTO NOTICE (TOPIC,REFERANCE,NOTICE,COURSE) VALUES(%s,%s,%s,%s)"
        val = (topic,referance,notice,course)

        mycursor.execute(query,val)
        db.commit()
        return redirect(url_for('admin_notice'))
    mycursor.execute("SELECT * FROM NOTICE ORDER BY created_at DESC")
    notice = mycursor.fetchall()
    return render_template('admin/admin_notice.html',courses=courses,notice=notice,admin=admin,user_id=user_id)

@app.route('/admin/notice_delete/<int:id>')
def notice_delete(id):
    if session.get("role") != "admin" :
        return "access denied"

    user_id  = session.get("username")

    mycursor.execute("DELETE FROM notice WHERE id=%s", (id,))
    db.commit()
    return redirect(url_for('admin_notice'))

#TEACHER ALL PAGES 

@app.route('/teacher')
def teacher():

    if session.get("role") != "teacher" :
        return "access denied"
    
    user_id  = session.get("teacher_id")
    firstname = session['firstname']

    query = "SELECT * FROM TEACHERS WHERE ID = %s;"
    val = (user_id,)
    mycursor.execute(query, val)
    teacher = mycursor.fetchone()
    return render_template('teacher/teacher_dashboard.html',teacher=teacher,firstname=firstname)
    

@app.route('/teacher/teacher_student', methods=['GET', 'POST'])
def teacher_student():

    if session.get("role") != "teacher":
        return "access denied"

    firstname = session.get('firstname')

    mycursor.execute("SELECT * FROM COURSES")
    courses = mycursor.fetchall()

    result = []
    selected_course = ""

    if request.method == 'POST':

        selected_course = request.form.get('course')

        if selected_course:

            show_query = "SELECT * FROM students WHERE COURSE = %s"

            mycursor.execute(show_query, (selected_course,))
            result = mycursor.fetchall()

    return render_template('teacher/students.html',courses=courses,result=result,firstname=firstname,selected_course=selected_course)

@app.route('/teacher/teacher_show_student/<int:id>')
def teacher_show_student(id):

    if session.get("role") != "teacher" :
        return "access denied"
    

    firstname = session.get('firstname')

    mycursor.execute("SELECT * FROM students WHERE id = %s", (id,))
    student = mycursor.fetchone()
    return render_template('teacher/teacher_show_student.html', student=student,firstname=firstname)


@app.route('/teacher/teacher_exam')
def teacher_exam():
    if session.get("role") != "teacher" :
        return "access denied"

    firstname = session.get('firstname')

    query = "SELECT * FROM exam ORDER BY id DESC"

    mycursor.execute(query)
    exams = mycursor.fetchall()

    for exam in exams:

        q2 = "SELECT * FROM exam_timetable WHERE exam_id = %s ORDER BY exam_date ASC"

        mycursor.execute(q2, (exam['ID'],))
        exam['tt'] = mycursor.fetchall()

    return render_template('teacher/exam.html', exams=exams, firstname=firstname)

@app.route('/teacher/teacher_time_table')
def teacher_timetable():

    if session.get("role") != "teacher" :
        return "access denied"
    
    firstname = session.get('firstname')
    teacher_id = session.get('teacher_id')
    
    # Get teacher's subject
    mycursor.execute("SELECT SUBJECT FROM teachers WHERE ID=%s", (teacher_id,))
    teacher_data = mycursor.fetchone()
    teacher_subject = teacher_data.get('SUBJECT') if teacher_data else None
    
    # Get all courses for filter
    mycursor.execute("SELECT * FROM COURSES")
    courses = mycursor.fetchall()
    
    # Get timetable for this teacher's subject only
    if teacher_subject:
        mycursor.execute("SELECT * FROM lecture_timetable WHERE teacher_id=%s AND subject_name=%s ORDER BY FIELD(lecture_day,'MONDAY','TUESDAY','WEDNESDAY','THURSDAY','FRIDAY','SATURDAY'), start_time", (teacher_id, teacher_subject))
        timetable = mycursor.fetchall()
    else:
        timetable = []
    
    # Get all courses' timetables as fallback
    if not timetable:
        mycursor.execute("SELECT * FROM lecture_timetable WHERE teacher_id=%s ORDER BY FIELD(lecture_day,'MONDAY','TUESDAY','WEDNESDAY','THURSDAY','FRIDAY','SATURDAY'), start_time", (teacher_id,))
        timetable = mycursor.fetchall()
    
    return render_template('teacher/timetable.html', timetable=timetable, courses=courses, firstname=firstname, teacher_subject=teacher_subject)



@app.route('/teacher/notice',methods=['GET','POST'])
def teacher_notice():

    if session.get("role") != "teacher" :
        return "access denied"

    firstname = session.get('firstname')

    
    mycursor.execute("SELECT * FROM COURSES")
    courses = mycursor.fetchall()

    if request.method == "POST" :
        topic = request.form['topic']
        referance = "TEACHER"
        notice = request.form['notice']
        course = request.form['course']

        query = "INSERT INTO NOTICE (TOPIC,REFERANCE,NOTICE,COURSE) VALUES(%s,%s,%s,%s)"
        val = (topic,referance,notice,course)

        mycursor.execute(query,val)
        db.commit()
        return redirect(url_for('teacher_notice'))
    mycursor.execute("SELECT * FROM NOTICE ORDER BY created_at DESC")
    notice = mycursor.fetchall()
    return render_template('teacher/notice.html',courses=courses,notice=notice,admin=admin,firstname=firstname)

@app.route('/teacher/notice_delete/<int:id>')
def teachernotice_delete(id):
    if session.get("role") != "teacher" :
        return "access denied"

    user_id  = session.get("teacher_id")

    mycursor.execute("DELETE FROM notice WHERE id=%s", (id,))
    db.commit()
    return redirect(url_for('teacher_notice'))


# STUDENT ALL PAGES 

@app.route('/student')
def student():

    if session.get("role") != "student" :
        return "access denied"

    firstname = session.get('firstname')

    user_id  = session.get("student_id")
    query = "SELECT * FROM STUDENTS WHERE ID = %s;"
    val = (user_id,)
    mycursor.execute(query, val)
    student = mycursor.fetchone()

    return render_template('student/student_dashboard.html',student=student,firstname=firstname)

@app.route('/student/exam')
def student_exam():
    if session.get("role") != "student" :
        return "access denied"
    
    firstname = session.get('firstname')
    course = session.get('course')

    query = "SELECT * FROM exam ;"

    mycursor.execute(query)
    exams = mycursor.fetchall()

    for exam in exams:

        q2 = "SELECT * FROM exam_timetable WHERE exam_id = %s AND COURSE=%s ORDER BY exam_date ASC"

        mycursor.execute(q2, (exam['ID'], course))
        exam['tt'] = mycursor.fetchall()

    return render_template('student/exam_student.html' , exams=exams, firstname=firstname)
   

@app.route('/student/timetable')
def student_timetable():
    if session.get("role") != "student" :
        return "access denied"

    firstname = session.get('firstname')
    
    student_id = session.get("student_id")

    # Get student's course
    mycursor.execute("SELECT COURSE FROM students WHERE ID=%s",(student_id,))
    student = mycursor.fetchone()

    if not student:
        return render_template('student/timetable_student.html', timetable_by_day={}, firstname=firstname)

    course = student.get('course') or student.get('COURSE')

    # Get all timetable entries for the course, sorted by day and time
    mycursor.execute("SELECT * FROM lecture_timetable WHERE course=%s ORDER BY FIELD(lecture_day,'MONDAY','TUESDAY','WEDNESDAY','THURSDAY','FRIDAY','SATURDAY'), start_time", (course,))

    timetable_list = mycursor.fetchall()
    
    # Organize by day for better display
    days = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY']
    timetable_by_day = {day: [] for day in days}
    
    for entry in timetable_list:
        day = entry.get('lecture_day', '').upper()
        if day in timetable_by_day:
            timetable_by_day[day].append(entry)

    return render_template('student/timetable_student.html', timetable_by_day=timetable_by_day, firstname=firstname, course=course)

@app.route('/student/notice')
def student_notice():

    if session.get("role") != "student" :
        return "access denied"
    
    firstname = session.get('firstname')
    course = session.get('course')

    query = "SELECT * FROM NOTICE WHERE COURSE=%s"
    val = (course,)
    mycursor.execute(query, val)
    notice = mycursor.fetchall()
    return render_template('student/notice.html', notice=notice, firstname=firstname)


@app.route('/error')
def error():
    return render_template('error.html')


if __name__ == '__main__':
    app.run(debug=True)