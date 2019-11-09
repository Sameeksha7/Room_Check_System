from flask import Flask,render_template,url_for,flash,redirect,request
# from forms import RegistrationForm, LoginForm, RegisterAlbum,RegisterArtist,AddSongs,UpdateForm
from datetime import datetime
from sqlalchemy import create_engine
from flask_bcrypt import Bcrypt
import cx_Oracle
from wtforms.validators import ValidationError

app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
app.config.from_object(__name__)

app.config['SECRET_KEY'] = '2e3d9442882549964af284ca7d59f157'

engine = create_engine('oracle://dhairya:db99pb05@localhost/orcl')

bcrypt = Bcrypt(app)

@app.route("/")
def home():
    rooms = []
    for i in range(4):
        roomSet = engine.execute("select * from room where floor= :i",{'i':i})
        subroom = []
        flag=0
        for room in roomSet:
            roomid = room[0] 
            floor = room[1]
            category = room[2]
            price = room[3]
            capacity = room[4]
            flag=1
            item = {'roomid':roomid, 'floor': floor, 'category':category,'price':price,'capacity':capacity}
            subroom.append(item)
        if(flag==0):
            subroom.append({})
        rooms.append(subroom)

    return render_template('home.html',rooms=rooms)

@app.route("/login", methods=['GET','POST'])
def login():
    password_entered = request.form.get('psw')
    email_entered = request.form.get('email')
    print(email_entered)
    count = engine.execute("select count(*) from UserData where emailid = :email_entered",{'email_entered':email_entered})
    for cnt in count:
        noofemails = cnt

    password_reg = engine.execute("select password from UserData where emailid = :email_entered",{'email_entered':email_entered})
    username = engine.execute("select FirstName from UserData where emailid = :email_entered",{'email_entered':email_entered})
        
    for row in password_reg:
        reg = row

    if noofemails[0] == 1:
        if bcrypt.check_password_hash(reg[0] , password_entered) :
            flash('You have been logged in!', 'success')
            if email_entered == 'iit2017080@iiita.ac.in':
                return redirect(url_for('home'))
            else:
                return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check password', 'danger')
    else:
        flash('Incorrect email!', 'danger')

    return render_template('login.html')

@app.route("/signup", methods=['GET','POST'])
def signup():
    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')
    email = request.form.get('email')
    password = request.form.get('psw')
    phone = request.form.get('phone')
    dob = request.form.get('dob')
    print(email)
    if password==None:
        password = "abcd"
    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    count = engine.execute("select count(*) from UserData where EmailId = :email",{'email':email})
    for cnt in count:
        noofemails = cnt[0]
    if noofemails == 1:
        flash('This email is already taken! Please choose another one.','danger')
    else:
        if email!=None:
            date_object = datetime.strptime(dob, '%Y-%m-%d').date()
            print(date_object)
            engine.execute("insert into UserData(FirstName, LastName, EmailId,Password,Phone,DOB) values (:firstname,:lastname,:email,:hashed_pw,:phone,:dob)",{'firstname':firstname,'lastname':lastname,
                                'email':email,'hashed_pw':hashed_pw, 'phone':phone, 'dob':date_object})
            flash(f'Account created for {firstname}!', 'success')
            return redirect(url_for('login'))
        else:
            print("Not inserted")
    return render_template('signup.html')

@app.route("/admin", methods=['GET','POST'])
def admin():
    floor = request.form.get('floor')
    category = request.form.get('type')
    price = request.form.get('price')
    capacity = request.form.get('capacity')
    if floor!=None and category!=None and price!=None and capacity!=None:
        engine.execute("insert into room(floor,category,price,capacity) values(:floor,:category,:price,:capacity)",{'floor':floor,
        'category':category,'price':price,'capacity':capacity})
    return render_template('admin.html')

@app.route("/available", methods=['GET','POST'])
def available():
    checkindate = request.form.get('checkin')
    checkoutdate = request.form.get('checkout')
    from_entered = datetime.strptime(checkindate, '%Y-%m-%d').date()
    to_entered = datetime.strptime(checkoutdate, '%Y-%m-%d').date()
    engine.execute("create table tmp(id int, floor int, category varchar(50),price int, capacity int)")
    engine.execute("insert into tmp (select r.id,r.floor,r.category,r.price,r.capacity from booking b join room r on r.id = b.roomid where :from_entered > checkout or :to_entered < checkin)",{'from_entered':from_entered,'to_entered':to_entered})
    engine.execute("insert into tmp (select * from room where id not in (select roomid from booking))")
    cnt = engine.execute("select count(*) from tmp")
    for x in cnt:
        print(x[0])
    rooms = []
    for i in range(4):
        roomSet = engine.execute("select * from tmp where floor= :i",{'i':i})
        subroom = []
        flag=0
        for room in roomSet:
            roomid = room[0] 
            floor = room[1]
            category = room[2]
            price = room[3]
            capacity = room[4]
            flag=1
            item = {'roomid':roomid, 'floor': floor, 'category':category,'price':price,'capacity':capacity}
            subroom.append(item)
        if(flag==0):
            subroom.append({})
        rooms.append(subroom)
    engine.execute("drop table tmp")
    return render_template('available.html',rooms=rooms)


if __name__ == '__main__':
    app.run(debug=True) 