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

engine = create_engine('oracle://system:sqlplus@localhost/orcl')


bcrypt = Bcrypt(app)
checkindate = "18-NOV-19"
checkoutdate = "19-NOV-19"
current_email = "None"
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

isLoggedin=0
bookingp=0
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
            global isLoggedin,bookingp
            isLoggedin=1
            if bookingp==1:
                return redirect(url_for('book')) 
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
            engine.execute("insert into userdata(firstname, lastname, emailid, password, phone, dob) values (:firstname,:lastname,:email,:hashed_pw,:phone,:dob)",{'firstname':firstname,'lastname':lastname,
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
    print(checkindate)
    from_entered = datetime.strptime(checkindate, '%Y-%m-%d').date()
    to_entered = datetime.strptime(checkoutdate, '%Y-%m-%d').date()
    print(from_entered)
    engine.execute("create table tmp(id int, floor int, category varchar(50),price int, capacity int)")
    engine.execute("insert into tmp (select r.id,r.floor,r.category,r.price,r.capacity from booking b join room r on r.id = b.roomid where :from_entered > checkout or :to_entered < checkin)",{'from_entered':from_entered,'to_entered':to_entered})
    engine.execute("insert into tmp (select * from room where id not in (select roomid from booking))")
    engine.execute("delete from tmp where id in (select roomid from booking where :from_entered > checkout or :to_entered < checkin)",{'from_entered':from_entered,'to_entered':to_entered})
    cnt = engine.execute("select count(*) from tmp")
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
    return render_template('available.html',rooms=rooms,indate=from_entered,outdate=to_entered)


    return render_template('login.html')
@app.route("/books", methods=['GET','POST'])
def books():
    return render_template('first.html')

@app.route("/showRooms", methods=['GET','POST'])
def showRooms():
    rooms=engine.execute("select * from room")
    r=[]
    for room in rooms:
        roomid = room[0] 
        floor = room[1]
        category = room[2]
        price = room[3]
        capacity = room[4]
        item = {'roomid':roomid, 'floor': floor, 'category':category,'price':price,'capacity':capacity}
        r.append(item)
    return render_template('showRooms.html',rooms=r)

@app.route("/addRoom", methods=['GET','POST'])
def addRoom():
    return render_template('addRoom.html')

@app.route("/updateRoom", methods=['GET','POST'])
def updateRoom():
    roomid=request.form.get('roomid')
    floor= request.form.get('floor')
    price= request.form.get('price')
    capacity= request.form.get('capacity')
    category= request.form.get('category')
    engine.execute("update room set floor=:floor,category=:category,price=:price,capacity=:capacity where id=:roomid",{'floor':floor,
        'category':category,'price':price,'capacity':capacity,'roomid':roomid})
    return redirect(url_for('showRooms'))

@app.route("/deleteRoom", methods=['GET','POST'])
def deleteRoom():
    roomid=request.form.get('delId')
    engine.execute("delete from room where id=:roomid",{'roomid':roomid})
    return redirect(url_for('showRooms'))

@app.route("/currentRoom", methods=['GET','POST'])
def currentRoom():
    books=engine.execute("select * from booking where checkin<=(select current_date from dual) and checkout>=(select current_date from dual)")
    bookings=[]
    for b in books:
        bookingid=b[0]
        roomid = b[1]
        email=b[4]
        fdate=b[2]
        todate=b[3]
        x={'bookingid':bookingid,'roomid':roomid,'email':email,'from':fdate,'to':todate}
        bookings.append(x)
    return render_template('currentRooms.html',bookings=bookings)

@app.route("/insertRoom", methods=['GET','POST'])
def insertRoom():
    floor= request.form.get('floor')
    price= request.form.get('price')
    capacity= request.form.get('capacity')
    types= request.form.get('type')
    engine.execute("insert into room(id,floor,category,price,capacity) values (103,:floor,:type,:price,:capacity)",{'floor':floor,
        'type':types,'price':price,'capacity':capacity})
    return render_template('first.html')

@app.route("/showBookings", methods=['GET','POST'])
def showBookings():
    books=engine.execute("select * from booking")


    bookings=[]
    for b in books:
        bookingid=b[0]
        roomid = b[1]
        email=b[4]
        fdate=b[2]
        todate=b[3]
        x={'bookingid':bookingid,'roomid':roomid,'email':email,'from':fdate,'to':todate}
        bookings.append(x)
    return render_template('showBookings.html',bookings=bookings)

@app.route("/checkoutRoom", methods=['GET','POST'])
def checkoutRoom():
    bookingid=request.form.get('delId')
    engine.execute("delete from booking where bookingid=:bookingid",{'bookingid':bookingid})
    return redirect(url_for('currentRoom'))

@app.route("/book/<roomid>", methods=['POST', 'GET']) 
def book(roomid):
    global checkin
    global checkout
    global current_email
    from_entered = datetime.strptime(checkindate, '%Y-%m-%d').date()
    to_entered = datetime.strptime(checkoutdate, '%Y-%m-%d').date()

    if current_email == "None":
        return redirect(url_for('login'))
    engine.execute("insert into booking(roomid,checkin,checkout,email) values(:roomid,:from_entered,:to_entered,:current_email)",{'roomid':roomid,'from_entered':from_entered,'to_entered':to_entered,'current_email':current_email})
    return render_template('book.html')

@app.route("/profile", methods=['POST', 'GET']) 
def profile():
    global current_email
    if current_email == "None":
        return redirect(url_for('login'))

    name = engine.execute("select firstname,lastname from userdata where emailid=:current_email",{'current_email':current_email})
    for x in name:
        firstname = x[0]
        lastname = x[1]

    pastbookings = engine.execute("select * from booking where email=:current_email and checkout<(select current_date from dual)",{'current_email':current_email})
    presentbookings=engine.execute("select * from booking where email=:current_email and checkout>=(select current_date from dual) and checkin<=(select current_date from dual)",{'current_email':current_email})
    futurebookings=engine.execute("select * from booking where email=:current_email and checkin>(select current_date from dual)",{'current_email':current_email})
    pastbookedRooms = []
    for book in pastbookings:
        roomid = book[1]    
        checkin = book[2]
        checkout = book[3]

        pastbookedRooms.append({'roomid':roomid,'checkin':checkin,'checkout':checkout})
    presentbookedRooms = []
    for book in presentbookings:
        roomid = book[1]    
        checkin = book[2]
        checkout = book[3]

        presentbookedRooms.append({'roomid':roomid,'checkin':checkin,'checkout':checkout})
    futurebookedRooms = []
    for book in futurebookings:
        roomid = book[1]    
        checkin = book[2]
        checkout = book[3]

        futurebookedRooms.append({'roomid':roomid,'checkin':checkin,'checkout':checkout})

    return render_template('profile.html',fn = firstname,ln = lastname,pastbookedRooms=pastbookedRooms,presentbookedRooms=pastbookedRooms,futurebookedRooms=pastbookedRooms)

@app.route("/cancel/<roomid>", methods=['POST', 'GET']) 
def cancel(roomid):
    engine.execute("delete from booking where roomid=:roomid",{'roomid':roomid})
    return redirect(url_for('profile'))

@app.route("/adminlogin", methods=['POST', 'GET']) 
def adminlogin():
    return render_template('adminlogin.html')

@app.route("/correctadminlogin", methods=['POST', 'GET']) 
def correctadminlogin():
    name= request.form.get('fullname')
    password= request.form.get('pass')
    if(password=='sqlplus'):
        return redirect(url_for('books'))

if __name__ == '__main__':
    app.run(debug=True) 