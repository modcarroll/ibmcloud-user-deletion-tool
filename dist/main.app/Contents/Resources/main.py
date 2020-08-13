import json
import requests
import csv
import tkinter
from tkinter.filedialog import askopenfile
import tkinter.messagebox
import os
from tkinter.font import BOLD
import re

###
# Read users from csv file
###
def read_users():
    output.delete("1.0", tkinter.END)
    try:
        account_id = entryID.get()
        apikey = entryAPI.get()
        userList = entryInput.get("1.0", tkinter.END)
        if(type(userList) != 'str'):
            userList = userList.encode('utf-8')
        userString = ""
        array_of_users = {}

        userList = re.split(',|\n| |\r', userList)
        userList = filter(None, userList)

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

        MsgBox = tkinter.messagebox.askquestion ('Confirmation','Are you sure you want to delete these users? \n\n' + userString,icon = 'warning')

        if MsgBox == 'yes':
            get_token(apikey, account_id, array_of_users)
        else:
            print("Do nothing")
    except:
        output.insert(tkinter.END, "Something went wrong. Please restart and try again.")

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
                if user["user_id"] == currentUser or user["email"] == currentUser:
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

        for person in deleteList:
            user = deleteList[person]
            if(len(user) > 1):
                delete_response = requests.delete(delete_url + user, headers=headers)
                if(delete_response.status_code == 204 or delete_response.status_code == 200):
                    addedString += person + "\n"
                else:
                    notAdded += person + " " + user + " " + str(delete_response.content) + "\n"
            else:
                notPresent += person + "\n"
    except:
        output.insert(tkinter.END, "Something went wrong. Please restart and try again.\n")

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
frameUsers = tkinter.Frame(root, width="500", height="500")
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
labelInput = tkinter.Label(frameInput, text="Enter email address separated by commas, spaces, or line breaks:", font='Helvetica 16 bold')
labelInput.pack(side="left")
entryInput = tkinter.Text(frameUsers, bg="white smoke", height=20, width=100)
entryInput.pack()

button = tkinter.Button(frameButton, text="Click here to begin processing", command=read_users)
button.pack(side="left")
outputFrame = tkinter.Frame(root)
outputFrame.pack(expand=True, pady=15)
labelOutput = tkinter.Label(outputFrame, text="Output:")
labelOutput.pack()
output = tkinter.Text(outputFrame, bg="white smoke", height=40, width=100)
output.pack()
root.mainloop()
