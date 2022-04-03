import json
from flask import Flask, request, jsonify, render_template
import pymysql
import cv2
import numpy as np
from database import Database

db = Database(dbname='booksite')
# db.createdb()
#db.createTable("CREATE  TABLE booksite.stocks (ISBN int primary key, BookName TEXT, BookAuther TEXT, BookDate TEXT, BookDescription TEXT, BoookCover TEXT, BookTradePrice TEXT, BookRetailPrice TEXT, BookQuantity TEXT);")
# db.createTable("CREATE  TABLE booksite.users (ID int primary key, Username TEXT,Password TEXT, FullName Text, Address TEXT);")
# db.createTable("CREATE TABLE booksite.cart (ID int primary key, username TEXT, isbn TEXT, quantity TEXT);")
# db.createTable("CREATE TABLE booksite.admin (ID int primary key AUTO_INCREMENT, username TEXT, password TEXT, name TEXT);")
'''
1. The name of the book.
2. The author of the book.
3. A data picker allowing the publication date to be set.
4. The ISBN-13 number.
5. The multiline book description.
6. A picture of the front cover.
7. A slider allowing the trade price to be set (max £100).
8. A slider allowing the retail price to be set (max £100).
9. A slider allowing the quantity of books to be set (max 20).
'''
app  = Flask(__name__)


@app.route('/')
def homepage():
    return render_template("login.html")


@app.route('/adminlogin',methods = ['post'])
def AdminLogin():
    username = request.form.get('username')
    password = request.form.get('password')
    print("-"*10)
    print(username,password)
    data = db.SelectQuery('SELECT *  FROM booksite.admin WHERE Username = %s AND Password = %s;',param = (username,password))
    if data is None:
        return render_template("adminlogin.html",data = "Check your username or password OR something went wrong")
    elif data is not None:
        return render_template("adminpanel.html",name = username)
        #return AdminLogin()


@app.route('/loadadmin',methods=['GET'])
def loadadmin():
    return render_template('adminlogin.html')


#admin panel
@app.route('/userslogin',methods = ['POST'])
def userslogin():
    username = request.form.get('username')
    password = request.form.get('password')
    print("-"*10)
    print(username,password)
    data = db.SelectQuery('SELECT *  FROM booksite.users WHERE Username = %s AND Password = %s;',param = (username,password))
    if data is None:
        return render_template("login.html",data = "Check your username or password OR something went wrong")
    elif data is not None:
        #return render_template("booksite.html",name = username)
        return display(username)



@app.route('/users-signup',methods=['POST'])
def userssignup():
    
    username = request.form.get('username')
    password = request.form.get('password')
    
    id = request.form.get('id')
    fullname = request.form.get('fullname')
    address = request.form.get('address')
    db.InsertQuery("Insert into booksite.users(id,Username, Password, Fullname, Address) values (%s, %s, %s, %s, %s)",param = (id,username, password, fullname, address))
    return jsonify({"msg":"Signup Successfull"})
#add and update stocks:: Feature 1
@app.route("/addstocks",methods= ['GET', 'POST'])
def AddBook():
    print(request.method)
    if request.method == 'POST':
        isbn = request.form.get('isbn')
        check_isbn = db.SelectQuery('SELECT * FROM booksite.stocks WHERE ISBN = %s;',param = (isbn),mode = 'fetchone')
        print('---'*10)
        print(isbn)
        bookname = request.form.get('bookname')
        author = request.form.get('author')
        bookdate = request.form.get('date')
        bookdescription = request.form.get('desc')
        #----------------
        dir = 'covers/'
        f = request.files.get('cover').read()
        img = np.fromstring(f, np.uint8)
        img = cv2.imdecode(img, cv2.IMREAD_COLOR)
        cv2.imwrite(dir+f"{isbn}_COVER.jpg",img)
        #---------------
        booktradeprice = request.form.get('tradeprice')
        bookretailprice = request.form.get('retailprice')
        bookquantity = int(request.form.get('quantity'))

        if check_isbn is not None:

            db.UpdateQuery('''Update booksite.stocks SET BookName = %s, BookAuther = %s,
                                                                    BookDate = %s, BookDescription = %s, BoookCover = %s,
                                                                    BookTradePrice = %s, BookRetailPrice = %s, BookQuantity = %s 
                                                                    WHERE ISBN = %s;
                                                                    ''' ,param = (bookname, author, bookdate, bookdescription, 
                                                                    dir+f'{isbn}_COVER.jpg', booktradeprice, bookretailprice, bookquantity,isbn))
        elif check_isbn is None:
            db.InsertQuery('''INSERT INTO booksite.stocks (ISBN, BookName, BookAuther,
                                                                    BookDate, BookDescription, BoookCover,
                                                                    BookTradePrice, BookRetailPrice, BookQuantity) 
                                                                    values (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                                                                    
                                                                    ''' ,param = (isbn, bookname, author, bookdate, bookdescription, 
                                                                    dir+f'{isbn}_COVER.jpg', booktradeprice, bookretailprice, bookquantity))
        return render_template('adminpanel.html',data = 'Stocks added')
    elif request.method == 'GET':
        return render_template('adminpanel.html',data = 'Stocks added')




#display stocks:: Feature 2
@app.route('/display-stocks-all/',methods = ['GET'])
def display(username):
    print(username)
    check_isbn = db.SelectQuery('SELECT * FROM booksite.stocks',mode = 'fetchall',param=None)
    return render_template('booksite.html',data = check_isbn,username = username)


#add to card :: Feature 3
@app.route('/add-to-cart',methods = ['POST'])
def AddToCart():
    #username, isbn, quantity

    
    username = request.form.get('username')
    isbn = request.form.get('isbn')
    quantity = '1'

    db.InsertQuery('INSERT INTO booksite.cart(username,isbn,quantity) values(%s, %s, %s);',param = (username, isbn,quantity))

    return display(username)

@app.route('/display-cart/<username>',methods = ['GET'])
def DisplayCart(username):
    isbns = []
    cover = []
    price = []
    title = []
    quantity = []
    data = db.SelectQuery('SELECT * FROM booksite.cart where username = %s',(username),mode='fetchall')
    for i in data:
        isbns.append(i[2])
        quantity.append(i[-1])
    
    for isbn in isbns:
        xdata = db.SelectQuery("SELECT * from booksite.stocks where ISBN = %s",param = (isbn),mode = 'fetchone')
        cover.append(xdata[5])
        price.append(xdata[-2])
        title.append(xdata[1])
        


    
  
    #data = (cover,price,title)
    data = []
    for c,p,t,q,i in zip(cover,price,title,quantity,isbns):
        data.append([c,p,t,i,q])
    return render_template("displaycart.html",data = data,username = username)

@app.route("/delete-cart/",methods=['GET'])
def DeleteCart():
    isbn = request.args.get("isbn")
    db.DeleteFromRow('DELETE FROM booksite.cart where isbn = %s',param = (isbn))
    return jsonify({"msg":"Removed Successfully"})


@app.route("/checkout",methods = ['GET'])
def Checkout():
    username = request.args.get('username')
 
    isbn = []
    quantities = []
    cart_qty = []
    data = db.SelectQuery('SELECT * FROM booksite.cart where username = %s',param = (username),mode = 'fetchall')
    print(data)
    for i in data:
        cart_qty.append(i[-1])
        isbn.append(i[2])
        quantities.append(db.SelectQuery('SELECT BookQuantity FROM booksite.stocks where ISBN = %s',param = (i[2]), mode = 'fetchone')[0])
    print(isbn)
    print(quantities)
    print('-'*10)
    for q_c, q_r,isbn in zip(cart_qty,quantities,isbn):
        print(q_c,q_r,isbn)
        if int(q_c) > int(q_r):
            return jsonify({"msg":f"quantity limit exceeds for {isbn} {q_c} and {q_r}"})
        elif int(q_c) < int(q_r) or int(q_c) == int(q_r):
            i = int(int(q_r) - int(q_c))
            db.UpdateQuery("UPDATE booksite.stocks SET BookQuantity = %s where ISBN = %s",param = (i,isbn))
            db.DeleteFromRow("DELETE FROM booksite.cart where isbn = %s",param=(isbn))
            return render_template('paymentmethod.html')
    #update quantity
    #db.UpdateQuery('UPDATE')
    return display(username)


if __name__ == '__main__':
    app.run()