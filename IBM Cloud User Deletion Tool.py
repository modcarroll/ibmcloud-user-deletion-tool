import json
import requests
import tkinter
from tkinter.filedialog import askopenfile
import tkinter.messagebox
from tkinter.ttk import *
import re
import shutil
import threading
import time
from datetime import datetime
import math

###
# Read users from csv file
###
def read_users():
    try:
        account_id = entryID.get()
        apikey = entryAPI.get()
        progressbar['value'] = 1
        userList = entryInput.get("1.0", tkinter.END)
        if(type(userList) != 'str'):
            userList = userList.encode('utf-8')
        userString = ""
        array_of_users = {}

        userList = re.split(',|\n| |\r|\t', userList)
        userList = filter(None, userList)

        if(len(userList) > 20):
            MsgBox = tkinter.messagebox.showerror('Error','Too many users entered',icon = 'warning')
            userList = ""
            return 0

        if(len(apikey) < 1):
            MsgBox = tkinter.messagebox.showerror('Error','No API key entered',icon = 'warning')
            apikey = ""
            return 0
        if(len(account_id) < 1):
            MsgBox = tkinter.messagebox.showerror('Error','No account ID entered',icon = 'warning')
            account_id = ""
            return 0
        if(len(userList) < 1):
            MsgBox = tkinter.messagebox.showerror('Error','No users entered',icon = 'warning')
            userList = ""
            return 0

        for item in userList:
            array_of_users[item] = ""
            userString += item + "\n"

        MsgBox = tkinter.messagebox.askquestion ('Confirmation',"Are you sure you want to delete " + str(len(userList)) + " users? \n\n",icon = 'warning')

        if MsgBox == 'yes':
            get_token(apikey, account_id, array_of_users)
        else:
            print("Do nothing")
    except:
        output.insert(tkinter.END, "Something went wrong. Please restart and try again.")

###
# Threading
###
def start_submit_thread(event):
    global submit_thread
    submit_thread = threading.Thread(target=read_users)
    # submit_thread.daemon = True
    submit_thread.start()
    submit_thread.join(1)
    root.after(50, check_submit_thread)

###
# Check status of thread
###
def check_submit_thread():
    if submit_thread.is_alive():
        root.after(50, check_submit_thread)
    else:
        progressbar.stop()

###
# Get IBM Cloud IAM token
###
def get_token(apikey, account_id, array_of_users):
    try:
        url = "https://iam.cloud.ibm.com/identity/token"
        data = {"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": apikey}
        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "application/json"}

        auth_response = requests.post(url, data=data, headers=headers)
        token = json.loads(auth_response.content)
        token = token['access_token']
    except:
        output.insert(tkinter.END, "Something went wrong. Please restart and try again.")
    get_iam_ids(token, account_id, array_of_users)

###
# Get each users's IAM ID
###
def get_iam_ids(token, account_id, array_of_users):
    try:
        headers = {"Authorization": "Bearer " + token}
        url = "https://user-management.cloud.ibm.com/v2/accounts/" + account_id + "/users/"
        id_response = requests.get(url, headers=headers)
    except:
        output.insert(tkinter.END, "Something went wrong. Please restart and try again.")
    set_iam_ids(array_of_users, json.loads(id_response.content), token, account_id)

###
# Match users with their IAM IDs
###
def set_iam_ids(userDict, iamResponse, token, account_id):
    try:
        for userdic in userDict:
            currentUser = userdic
            for user in iamResponse['resources']:
                if user["user_id"].lower() == currentUser.lower() or user["email"].lower() == currentUser.lower():
                    userDict[currentUser] = user["iam_id"]
    except:
        output.insert(tkinter.END, "Something went wrong. Please restart and try again.")
    delete_users(token, userDict, account_id)

###
# Delete section
###
def delete_users(token, deleteList, account_id):
    addedString = ""
    notAdded = ""
    notPresent = ""

    try:
        delete_url = "https://user-management.cloud.ibm.com/v2/accounts/" + account_id + "/users/"
        headers = {"Authorization": "Bearer " + token, "Content-Type": "application/json"}

        counter = 1
        for person in deleteList:
            counter += 1
            percent = 100 * (float(counter)/float(len(deleteList) + 1))
            print(percent)
            progressbar['value'] = percent
            user = str(deleteList[person])
            print(user)
            if(len(user) > 1):
                delete_response = requests.delete(delete_url + user, headers=headers, timeout=50)
                print(delete_response)
                if(delete_response.status_code == 204 or delete_response.status_code == 200):
                    output.insert("1.0", person + " removed.\n")
                    addedString += person + "\n"
                else:
                    output.insert("1.0", person + " not removed.\n")
                    notAdded += person + " " + user + " " + str(delete_response.content) + "\n"
            else:
                output.insert("1.0", person + " does not exist.\n")
                notPresent += person + "\n"
    except:
        output.delete("1.0", tkinter.END)
        output.insert(tkinter.END, "Something went wrong. Please restart and try again.\n")

    output.delete("1.0", tkinter.END)
    if len(addedString) > 1:
        output.insert(tkinter.END, "---------------------------------\n")
        output.insert(tkinter.END, "Users removed: \n")
        output.insert(tkinter.END, addedString)
        output.insert(tkinter.END, "---------------------------------\n")
    if len(notAdded) > 1:
        output.insert(tkinter.END, "---------------------------------\n")
        output.insert(tkinter.END, "Users not removed: \n")
        output.insert(tkinter.END, notAdded)
        output.insert(tkinter.END, "---------------------------------\n")
    if len(notPresent) > 1:
        output.insert(tkinter.END, "---------------------------------\n")
        output.insert(tkinter.END, "Users do not exist in account: \n")
        output.insert(tkinter.END, notPresent)
        output.insert(tkinter.END, "---------------------------------\n")

root = tkinter.Tk()
root.title("IBM Cloud - User Deletion")
root.geometry("800x800")
frame = tkinter.Frame(root)
frame.pack(padx=50)
title = tkinter.Label(frame, text="IBM Cloud User Deletion Tool")
title.config(font=("Courier", 36))
title.pack()
label = tkinter.Label(frame, wraplength=700, text="For full directions, visit: https://github.com/modlanglais/ibmcloud-user-deletion-tool\n")
label.pack()

frameAPI = tkinter.Frame(root)
frameAPI.pack(padx=50)
frameID = tkinter.Frame(root)
frameID.pack(padx=50)
frameInput = tkinter.Frame(root)
frameInput.pack(padx=50)
frameUsers = tkinter.Frame(root, width="500", height="400")
frameUsers.pack(padx=50)
frameButton = tkinter.Frame(root)
frameButton.pack(padx=50)

labelAPI = tkinter.Label(frameAPI, text="     Enter your IBM Cloud API Key:", font='Helvetica 16 bold')
labelAPI.pack(side="left")
entryAPI = tkinter.Entry(frameAPI)
entryAPI.pack(side="left")

labelID = tkinter.Label(frameID, text="Enter your IBM Cloud account ID:", font='Helvetica 16 bold')
labelID.pack(side="left")
entryID = tkinter.Entry(frameID)
entryID.pack(side="left")

labelInput = tkinter.Label(frameInput, text="Enter email address (max of 20) separated by commas, spaces, or line breaks:", font='Helvetica 16 bold')
labelInput.pack(side="left")
entryInput = tkinter.Text(frameUsers, bg="white smoke", height=20, width=100)
entryInput.pack()

button = tkinter.Button(frameButton, text="Click here to begin processing", command=lambda:start_submit_thread(None))
button.pack(side="left")

outputFrame = tkinter.Frame(root, width="500", height="150")
outputFrame.pack(pady=15)
labelOutput = tkinter.Label(outputFrame, text="Output:")
labelOutput.pack()
output = tkinter.Text(outputFrame, bg="white smoke", height=20, width=100)
output.pack()

progressFrame = tkinter.Frame(root, width="500", height="40")
progressFrame.pack(expand=True)
labelProgress = tkinter.Label(progressFrame, text="Progress")
labelProgress.pack(side="left")
progressbar = tkinter.ttk.Progressbar(progressFrame, length="400", mode='determinate') #TODO: Switch to determinate
progressbar.pack()

root.mainloop()
