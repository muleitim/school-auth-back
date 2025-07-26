from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
from models import db, Student, AuthorizedUser
from config import Config
import os
import cloudinary
import cloudinary.uploader
from werkzeug.utils import secure_filename

from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)


app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
CORS(app, origins=[app.config["CORS_ORIGIN"]], supports_credentials=True)
jwt = JWTManager(app)

cloudinary.config(
    cloud_name=app.config["CLOUDINARY_CLOUD_NAME"],
    api_key=app.config["CLOUDINARY_API_KEY"],
    api_secret=app.config["CLOUDINARY_API_SECRET"],
    secure=True
)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


# user profile
@app.route("/api/me", methods=["POST"])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = AuthorizedUser.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        # Add other fields if needed
    }), 200



#Protected route 
@app.route("/api/protected", methods=["GET"])
@jwt_required()
def protected():
    user_id = get_jwt_identity()
    return jsonify({"message": f"Welcome User {user_id}!"}), 200



#Logout api endpoint
@app.route("/api/logout", methods=["POST"])
def logout():
    response = jsonify({"message": "Logged out successfully"})
    response.set_cookie("access_token_cookie", "", expires=0)
    response.set_cookie("refresh_token_cookie", "", expires=0)
    return response, 200



#Login route
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    identifier = data.get("username")  # can be username or email
    password = data.get("password")

    if not identifier or not password:
        return jsonify({"error": "Username/email and password required"}), 400

    user = AuthorizedUser.query.filter(
        (AuthorizedUser.username == identifier) | (AuthorizedUser.email == identifier)
    ).first()

    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    response = jsonify({"message": "Login successful"})
    response.set_cookie("access_token_cookie", access_token, httponly=True, samesite="Lax")
    response.set_cookie("refresh_token_cookie", refresh_token, httponly=True, samesite="Lax")
    return response, 200




@app.route("/api/register-student", methods=["POST"])
def register_student():
    data = request.form
    file = request.files.get("student-photo")

    registration_number = data.get("registration_number")
    if not registration_number:
        return jsonify({"error": "Missing registration number"}), 400

    if not file or not allowed_file(file.filename):
        return jsonify({"error": "Invalid or missing file"}), 400

    # Generate filename from registration number (slashes replaced)
    sanitized_reg_no = registration_number.replace("/", "_")
    file_ext = os.path.splitext(file.filename)[1]  # keep file extension
    filename = f"{sanitized_reg_no}{file_ext}"

    # Upload to Cloudinary
    upload_result = cloudinary.uploader.upload(
        file,
        public_id=f"students/{sanitized_reg_no}",  # no extension
        overwrite=True,
        resource_type="image"
    )

    cloudinary_url = upload_result["secure_url"]
    print("\nCloudinary url:", cloudinary_url, "\n")

    # Save student record
    student = Student(
        registration_number=registration_number,
        firstname=data.get("firstname"),
        middlename=data.get("middlename"),
        lastname=data.get("lastname"),
        date_of_birth=data.get("date-picker"),
        gender=data.get("gender"),
        nationality=data.get("nationality"),
        previous_school=data.get("previous-school"),
        admission_number=data.get("admission-number"),
        photo_filename=cloudinary_url  # store the URL
    )

    db.session.add(student)
    db.session.commit()

    return jsonify({"message": "Student registered successfully"}), 201


@app.route("/api/students", methods=["GET"])
def get_students():
    students = Student.query.all()
    return jsonify([
        {
            "id": s.id,
            "registrationNumber": s.registration_number,
            "firstName": s.firstname,
            "middleName": s.middlename,
            "lastName": s.lastname,
            "admissionNumber": s.admission_number,
            "photo": s.photo_filename  # Full Cloudinary URL
        }
        for s in students
    ])



# Register authorized user
@app.route("/api/register-user", methods=["POST"])
def register_user():
    data = request.get_json()

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not all([username, email, password]):
        return jsonify({"error": "All fields are required"}), 400

    if AuthorizedUser.query.filter((AuthorizedUser.username == username) | (AuthorizedUser.email == email)).first():
        return jsonify({"error": "Username or email already exists"}), 409

    new_user = AuthorizedUser(username=username, email=email)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201




if __name__ == "__main__":
    app.run()
