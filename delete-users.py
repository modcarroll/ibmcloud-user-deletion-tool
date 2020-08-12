import json
import requests
import csv
import tkinter
from tkinter.filedialog import askopenfilename
import tkinter.messagebox
import os

###
# Read users from csv file
###
def read_users():
    try:
        account_id = entryID.get()
        apikey = entryAPI.get()
        userString = ""
        array_of_users = {}
        csv_file_path = askopenfilename()
        with open(os.path.join(csv_file_path), 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                for item in row:
                    array_of_users[item] = ""
                    userString += item + "\n"
    except:
        output.insert(tkinter.END, "Something went wrong. Please restart and try again.")

    MsgBox = tkinter.messagebox.askquestion ('Confirmation','Are you sure you want to delete these users? \n\n' + userString,icon = 'warning')

    if MsgBox == 'yes':
       get_token(apikey, account_id, array_of_users)
    else:
        print("Do nothing")

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
                if(type(user["user_id"]) != "str"):
                    user["user_id"] = user["user_id"].encode()
                if user["user_id"] == currentUser:
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
                #TODO: use a text box that users can paste into instead? For iteration 2
                if(type(user) != "str"):
                    user = user.encode()
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
root.geometry("800x600")
frame = tkinter.Frame(root)
frame.pack(padx=50)
title = tkinter.Label(frame, text="IBM Cloud User Deletion Tool")
title.config(font=("Courier", 36))
title.pack()
label = tkinter.Label(frame, wraplength=700, text="Select a csv file with no headings that contains your list of users (e-mail addresses) to be deleted from your IBM Cloud account. Enter your IBM Cloud API key and account ID in the designatd fields. For full directions, visit: \nhttps://github.com/modlanglais/ibmcloud-user-deletion-tool\n")
label.pack()

frameAPI = tkinter.Frame(root)
frameAPI.pack(padx=50)
frameID = tkinter.Frame(root)
frameID.pack(padx=50)
frameButton = tkinter.Frame(root)
frameButton.pack(padx=50)

labelAPI = tkinter.Label(frameAPI, text="     Enter your IBM Cloud API Key:")
labelAPI.pack(side="left")
entryAPI = tkinter.Entry(frameAPI)
entryAPI.pack(side="left")
labelID = tkinter.Label(frameID, text="Enter your IBM Cloud account ID:")
labelID.pack(side="left")
entryID = tkinter.Entry(frameID)
entryID.pack(side="left")

button = tkinter.Button(frameButton, text="Click here to upload user list and begin processing", command=read_users)
button.pack(side="left")
outputFrame = tkinter.Frame(root)
outputFrame.pack(expand=True, pady=15)
output = tkinter.Text(outputFrame, bg="white smoke", height=40, width=100)
output.pack()
root.mainloop()
