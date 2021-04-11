from flask import Flask, request
import pyrebase
import requests

choice_dict = {1:"Sad", 2: "Happy", 3: "Angry", 4: "Excited"}

config = {"apiKey": "AIzaSyBrey3ZZ5X74WrAQuj7HISWLl70PqP8dnA",
  "authDomain": "trialproject-55deb.firebaseapp.com",
  "databaseURL": "https://trialproject-55deb-default-rtdb.firebaseio.com",
  "projectId": "trialproject-55deb",
  "storageBucket": "trialproject-55deb.appspot.com",
  "messagingSenderId": "930590452475",
  "appId": "1:930590452475:web:d8857d9906874468fd5e5e"
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()

app = Flask(__name__)

# @app.route('/signup', methods =['GET'])
# def signup():
#     register = request.get_json()
#     email = register['email']
#     password = register['password']
#     auth.create_user_with_email_and_password(email, password)
#     return {"status": " success", "email": email, "password": password}

@app.route('/signin/<string:email>/<string:password>', methods = ['GET'])
def signin(email, password):
  try:
    result = auth.sign_in_with_email_and_password(email, password)
    global userId
    userId = result['localId']
    get_token = db.child("Users").child(userId).get()
    global token 
    token = get_token.val()['token']
    name = get_token.val()['name']
    return{"token": token, "status": 1, "name": name}
    
  except: 
    return {"status": 0}

@app.route('/speaker/<int:choice>', methods = ["GET"])
def speaker(choice):

  try:
    users = db.child("Online").child("Listener").child(choice_dict[choice]).get()

    uid = ""
    flag = True

    for key in users.val():
      if flag == True:
        uid = key
        flag = False

    
    db.child("Online").child("Listener").child(choice_dict[choice]).child(uid).child("status").set(userId)
    db.child("Users").child(userId).child("token").set(token-1)
    
    url = "https://fcm.googleapis.com/fcm/send"

    payload="{\r\n  \"to\":\"/topics/"+userId+",\r\n  \"data\": {\r\n    \"title\": \"Alert\",\r\n    \"body\": \"You have an incoming call...\"\r\n  }\r\n}"
    headers = {'Authorization': 'key=AAAA2KuDavs:APA91bGCwqzJYQntRNVZU4WfjDh71D2kLvI4ei3iXr9BIlrz-lzp3HdzZWKAWghUwZK0i1rvC0RKFl2rdk1uyAf3RozvlPO1snRvwYpxJVz5qAH5keFgzygj8h16D0g-YDHrz6SoqJfh',
  'Content-Type': 'application/json'}

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response)
    return {"channel_name": uid, "status":1}

  except:
    return {"message": "No Listner available. Try reconnecting later.", "status":0}

@app.route('/listner/<int:choice>', methods = ["GET"])
def push_listner(choice):
  db.child("Online").child("Listener").child(choice_dict[choice]).child(userId).child("status").set("0")
  db.child("Online").child("Listener").child(choice_dict[choice]).child(userId).child("uid").set(userId)
  db.child("Users").child(userId).child("token").set(token+1)
  return {"status" : 1, "message": "You will be connected to a speaker shortly."}


if __name__ == '__main__':
    app.run(debug = True)
