import json
from flask import Flask, request, jsonify,render_template,request,redirect,url_for,make_response
from flask_sqlalchemy import SQLAlchemy
import razorpay
import pandas as pd

key = pd.read_csv('rzp.csv')
key_id = key['key_id'][0]
key_secret = key['key_secret'][0]

app = Flask(__name__)
app.config['SECREt_KEY'] = 'PAYMENT_APP'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///payment.db'
db = SQLAlchemy(app)
app.app_context().push()

class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(120),nullable=False)
    email = db.Column(db.String(120),nullable=False)
    address = db.Column(db.String(120),nullable=False)
    amount = db.Column(db.String('120'),nullable=False)


@app.route('/',methods=['GET','POST'])
def index():
    if request.method == 'POST':
        # request_data = request.form.get['name'
        name = request.form['name']
        email = request.form['email']
        address = request.form['address']
        amount = request.form['amount']
        user = User(name=name,email=email,address=address,amount=amount)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('pay',id=user.id))
    else:
        return render_template('index.html')

@app.route('/pay/<id>',methods=['GET','POST'])
def pay(id):
    user = User.query.filter_by(id=id).first()
    # print(name,email,address,amount)
    client = razorpay.Client(auth=(key_id,key_secret))
    DATA = {
        "amount": int(user.amount*100),
        "currency": "INR",
        "receipt": "order_rcptid_11",
        "notes": {
            "address": user.address,
            "email": user.email,
            "name": user.name
        }
    }
    order = client.order.create(data=DATA)
    print(order)
    try:
        # redirect to success.html
        return render_template('pay.html',payment=order)
    except:
        return 'Payment Failed'
    
@app.route('/success',methods=['GET','POST'])
def success():
    return render_template('success.html')


if __name__ == '__main__':
    from waitress import serve
    # app.debug = True
    db.create_all()
    # app.run(debug=True)
    serve(app, host="0.0.0.0", port=8080)
