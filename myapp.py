from pymongo import MongoClient
from bson.json_util import dumps
from bson.json_util import loads
from flask import Flask, jsonify, request
import requests
import certifi
from datetime import datetime

client = MongoClient("mongodb+srv://aakashdb:Aakash10@cluster0.ygxgrgj.mongodb.net/?retryWrites=true&w=majority",tlsCAFile = certifi.where())
db = client["sensor"]

now = datetime.now()
current_time = now.time()
timestamp = datetime.timestamp(now)


myheader = {"Authorization" : "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyMzhRNVIiLCJzdWIiOiJCNEYzNVEiLCJpc3MiOiJGaXRiaXQiLCJ0eXAiOiJhY2Nlc3NfdG9rZW4iLCJzY29wZXMiOiJyc29jIHJzZXQgcm94eSBycHJvIHJudXQgcnNsZSByYWN0IHJyZXMgcmxvYyByd2VpIHJociBydGVtIiwiZXhwIjoxNjkyMzIxOTk2LCJpYXQiOjE2NjA3ODU5OTZ9.Rw2SpXEMA3YVx1-O1W0ZamKq2BwRnUpOw_fQCMRn0z8"}

app = Flask(__name__)
@app.route("/heartrate/last", methods=["GET"])
def mymethod ():
    myurl = "https://api.fitbit.com/1/user/-/activities/heart/date/today/today/1min.json"
    resp = requests.get(myurl, headers=myheader).json()
    hr = resp["activities-heart-intraday"]["dataset"][-1]["value"]
    record = str(resp["activities-heart-intraday"]["dataset"][-1]["time"])
    time = current_time.strftime("%H:%M:%S")
    record2 = record.split(":")
    time2 = time.split(":")

    time_list = []
    i = 0
    while i < len(time2) :
        time_list.append(int(time2[i]) - int(record2[i]))
        i = i+1

    j = 1

    while j < len(time_list):
        if time_list[j] < 0:
            time_list[j] = time_list[j] + 60
            if time_list[j-1] != 0:
                time_list[j-1] = time_list[j-1] - 1
        j = j + 1

    res = ""

    for ele in time_list:
        res = res + str(ele) + ":"
    

    ret = {'heart-rate': hr, 'time offset': res}
    return jsonify(ret)

@app.route("/steps/last", methods=["GET"])
def stepmethod ():
    myurl = "https://api.fitbit.com/1/user/-/activities/date/2022-09-14.json"
    resp = requests.get(myurl, headers=myheader).json()
    url2 = "https://api.fitbit.com/1/user/-/activities/steps/date/today/1d/1min.json"
    time_resp = requests.get(url2, headers=myheader).json()

    g = -1
    while g > -len(time_resp["activities-steps-intraday"]["dataset"]):
        if time_resp["activities-steps-intraday"]["dataset"][g]["value"] > 0 :
            record = time_resp["activities-steps-intraday"]["dataset"][g]["time"]
            break
        g = g-1
    step = str(resp["summary"]["steps"])
    distance = str(resp["summary"]["distances"][0]['distance'])
    time = current_time.strftime("%H:%M:%S")
    record2 = record.split(":")
    time2 = time.split(":")

    time_list = []
    i = 0
    while i < len(time2) :
        time_list.append(int(time2[i]) - int(record2[i]))
        i = i+1

    j = 1

    while j < len(time_list):
        if time_list[j] < 0:
            time_list[j] = time_list[j] + 60
            if time_list[j-1] != 0:
                time_list[j-1] = time_list[j-1] - 1
        j = j + 1

    res = ""

    for ele in time_list:
        res = res + str(ele) + ":"
    

    ret = {'steps': step, 'distance': distance, 'time offset': res}
    return jsonify(ret)

@app.route("/sleep/<date>", methods=["GET"])
def sleepmethod (date):
    myurl = "https://api.fitbit.com/1.2/user/-/sleep/date/%s.json" % date
    resp = requests.get(myurl, headers=myheader).json()
    deep = resp["summary"]["stages"]["deep"]
    rem = resp["summary"]["stages"]["rem"]
    light = resp["summary"]["stages"]["light"]
    wake = resp["summary"]["stages"]["wake"]
    ret = {'deep': deep, 'light': light, 'rem': rem, 'wake': wake}
    return jsonify(ret)

@app.route("/activity/<date>", methods=["GET"])
def activemethod (date):
    myurl = "https://api.fitbit.com//1/user/-/activities/date/%s.json" % date
    resp = requests.get(myurl, headers=myheader).json()
    sed = resp["summary"]["sedentaryMinutes"]
    light = resp["summary"]["fairlyActiveMinutes"]
    very = resp["summary"]["veryActiveMinutes"]
    ret = {'very-active': very, 'lightly-active': light, 'sedentary': sed}
    return jsonify(ret)

@app.route("/sensors/env", methods=["GET"])
def envmethod ():
    x = []
    ret = db.env.find().limit(1)
    for i in ret:
        x.append(i)
    print(x)
    return(dumps(x))

@app.route("/sensors/pose", methods=["GET"])
def posemethod ():
    x = []
    ret = db.pose.find().limit(1)
    for i in ret:
        x.append(i)
    print(x)
    return(dumps(x))

@app.route("/post/env", methods= ["POST"])
def envpost():

    data = request.get_json() 
    temp = data["temp"]
    humidity = data["humidity"]
    ret = {"temp": temp, "humidity": humidity, "timestamp": timestamp}
    db.env.insert_one(ret)
    return (dumps(ret))

@app.route("/post/pose", methods= ["POST"])
def posepost():

    data = request.get_json() 
    presence = data["presence"]
    pose = data["pose"]
    ret = {"presence": presence, "pose": pose, "timestamp": timestamp}
    db.env.insert_one(ret)
    return (dumps(ret))


if __name__ == '__main__':
    app.run(debug=True)