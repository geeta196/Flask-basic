from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

# -------------------- FLASK APP -------------------- #
app = Flask(__name__)

# -------------------- DATABASE CONFIG -------------------- #
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:root@localhost:5432/internship_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -------------------- MODELS -------------------- #
class Student(db.Model):
    __tablename__ = "students"
    student_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    course = db.Column(db.String(100))

    internships = db.relationship("Internship", backref="student", lazy=True)


class Internship(db.Model):
    __tablename__ = "internships"
    internship_id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100))
    duration_months = db.Column(db.Integer)
    stipend = db.Column(db.Float)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'))

# -------------------- CREATE TABLES -------------------- #
with app.app_context():
    db.create_all()

# -------------------- MAIN ROUTE -------------------- #
@app.route('/')
def home():
    return "Welcome to Flask Internship App"

# -------------------- ADD STUDENT -------------------- #
@app.route('/student', methods=['POST'])
def add_student():
    name = request.form.get('name')
    email = request.form.get('email')
    course = request.form.get('course')

    student = Student(name=name, email=email, course=course)
    db.session.add(student)
    db.session.commit()
    return jsonify({"message": "Student added successfully"}), 201

# -------------------- ADD INTERNSHIP -------------------- #
@app.route('/internship', methods=['POST'])
def add_internship():
    student_id = request.form.get('student_id')
    company_name = request.form.get('company_name')
    duration_months = request.form.get('duration_months')
    stipend = request.form.get('stipend')

    internship = Internship(
        student_id=int(student_id) if student_id else None,
        company_name=company_name,
        duration_months=int(duration_months),
        stipend=float(stipend)
    )
    db.session.add(internship)
    db.session.commit()
    return jsonify({"message": "Internship added successfully!"}), 201

# -------------------- INNER JOIN -------------------- #
@app.route('/join/inner', methods=['GET'])
def inner_join():
    data = db.session.query(Student, Internship).join(Internship).all()
    result = [
        {
            'student_name': s.name,
            'course': s.course,
            'company': i.company_name,
            'duration': i.duration_months,
            'stipend': i.stipend
        } for s, i in data
    ]
    return jsonify(result)

# -------------------- LEFT JOIN -------------------- #
@app.route('/join/left', methods=['GET'])
def left_join():
    data = db.session.query(Student, Internship).outerjoin(Internship).all()
    result = [
        {
            'student_name': s.name,
            'course': s.course,
            'company': i.company_name if i else None,
            'duration': i.duration_months if i else None,
            'stipend': i.stipend if i else None
        } for s, i in data
    ]
    return jsonify(result)

# -------------------- RIGHT JOIN -------------------- #
@app.route('/join/right', methods=['GET'])
def right_join():
    sql = """
    SELECT s.student_id, s.name, s.course,
           i.company_name, i.duration_months, i.stipend
    FROM students s
    RIGHT JOIN internships i
    ON s.student_id = i.student_id;
    """
    result = db.session.execute(text(sql))
    data = []
    for row in result:
        data.append({
            'student_name': row[1],
            'course': row[2],
            'company': row[3],
            'duration': row[4],
            'stipend': row[5]
        })
    return jsonify(data)

# -------------------- FULL OUTER JOIN -------------------- #
@app.route('/join/full', methods=['GET'])
def full_join():
    sql = """
    SELECT s.student_id, s.name, s.course,
           i.company_name, i.duration_months, i.stipend
    FROM students s
    FULL OUTER JOIN internships i
    ON s.student_id = i.student_id;
    """
    result = db.session.execute(text(sql))
    data = []
    for row in result:
        data.append({
            'student_name': row[1],
            'course': row[2],
            'company': row[3],
            'duration': row[4],
            'stipend': row[5]
        })
    return jsonify(data)

# -------------------- RUN APP -------------------- #
if __name__ == '__main__':
    app.run(debug=True)
