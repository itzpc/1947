import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from application.config.config import DriveConfig

class Drive_Config():
    def __init__(self):
        self.creds =os.path.join(os.getcwd()+ DriveConfig.CRED_JSON_LOC)
        self.sheet_name = DriveConfig.SHEET_NAME
        self.scope = DriveConfig.SCOPE

    def create_client(self):
        creds = ServiceAccountCredentials.from_json_keyfile_name(self.creds, self.scope)
        return gspread.authorize(creds)

    def open_sheet(self,client,sheet_num,sheet_name=None):
        if sheet_name == None:
            sheet_name = self.sheet_name
        if sheet_num == 1:
            return client.open(sheet_name).sheet1
        elif sheet_num == 2:
            return client.open(sheet_name).sheet2
        elif sheet_num == 3:
            return client.open(sheet_name).sheet3
        else:
            return None