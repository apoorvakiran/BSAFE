from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from oauth2client.client import GoogleCredentials

import os

#Checks for file with Google authentication key, if the file is not in place, it asks to authenticate via the browser
gauth = GoogleAuth()
if os.path.isfile("mycreds.txt") is False:
    choice = input ("Do you want to: U) Upload authentication file (mycreds.txt). B) Browser authentication (only possible for owner of the connected Google drive folder). [U/B]? : ")
    if choice == "U":
          print ("Upload the mycreds.txt file")
          from google.colab import files
          files.upload()      
    elif choice == "B":
          auth.authenticate_user()
          gauth.credentials = GoogleCredentials.get_application_default()
          gauth.SaveCredentialsFile("mycreds.txt")

gauth.LoadCredentialsFile("mycreds.txt")
if gauth.access_token_expired:
    gauth.Refresh()
else: gauth.Authorize()
