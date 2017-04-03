from flask import *
import mlab
from models.CarItems import CarItems
from models.user import User
import os
from werkzeug.utils import *
from flask_login import *
from sessionuser import SessionUser

app = Flask(__name__)


#connect to mlab database
mlab.connect()


app.config['UPLOAD_PATH'] = os.path.join(app.root_path, 'uploads')
if not os.path.exists(app.config['UPLOAD_PATH']):
    os.makedirs(app.config['UPLOAD_PATH'])

app.secret_key = 'secretkey'

login_manager = LoginManager()
login_manager.init_app(app)

# admin_user = User()
# admin_user.username = 'admin'
# admin_user.password = 'admin'
# admin_user.save()


#create a new CarItems and save it to database
# new_car = CarItems()
# new_car.src = "http://st.motortrend.com/uploads/sites/5/2012/12/2014-BMW-M6-Gran-Coupe-rear-three-quarters.jpg"
# new_car.title = "Item 2"
# new_car.description = "Description for Item 2"
# new_car.save()

@login_manager.user_loader
def user_loader(user_token):
    found_user = User.objects(token=user_token).first()
    if found_user:
        session_user = SessionUser(found_user.id)
        return session_user


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        user = User.objects(username=request.form["username"]).first()
        if user and user.password == request.form["password"]:
            session_user = SessionUser(user.id)
            user.update(set__token=str(user.id))
            login_user(session_user)

            return redirect(url_for('add_cars'))
        else:
            return render_template("login.html")

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/')
def hello_world():
    return redirect(url_for("foodblog"))


@app.route('/addcars', methods=["GET", "POST"])
@login_required
def add_cars():
    if request.method == "GET":
        return render_template("addcars.html")
    if request.method == "POST":
        file = request.files['source']
        if file:
            filename = secure_filename(file.filename)
            if os.path.exists(os.path.join(app.config['UPLOAD_PATH'], filename)):
                name_index = 0
                original_name = filename.rsplit('.', 1)[0]
                original_extension = filename.rsplit('.', 1)[1]
                while os.path.exists(os.path.join(app.config['UPLOAD_PATH'], filename)):
                    name_index += 1
                    filename = "{0} ({1}).{2}".format(original_name, name_index, original_extension)

            file.save(os.path.join(app.config['UPLOAD_PATH'], filename))

            new_car = CarItems()
            new_car.src = url_for('uploaded_file', filename=filename)
            new_car.title = request.form["title"]
            new_car.description = request.form["description"]
            new_car.save()
            return render_template("addcars.html")


@app.route('/deletecars', methods=["GET", "POST"])
def delete_cars():
    if request.method == "GET":
        return render_template("deletecars.html")
    if request.method == "POST":
        new_car = CarItems.objects(title=request.form["title"]).first()
        if new_car is not None:
            new_car.delete()
        return render_template("deletecars.html")

@app.route('/updatecars', methods=["GET", "POST"])
def update():
    if (request.method == "GET"):
        return render_template("updatecars.html")
    if (request.method == "POST"):
        new_car = CarItems.objects(title=request.form["title"]).first()
        if new_car is not None:
            new_car.src = request.form["new_source"]
            new_car.description = request.form["new_description"]
            new_car.save()
        return render_template("updatecars.html")


@app.route('/foodblog')
def foodblog():
    return render_template("foodblog.html", car_items=CarItems.objects())


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)

if __name__ == '__main__':
    app.run()
