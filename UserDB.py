import csv
import sys

class UserDB(object):
    def __init__(self) -> None:
        self.users = {}
        file = open('users.csv', 'r')
        reader = csv.reader(file)
        for row in reader:
            self.addUser(row[0], row[1])
        file.close()

    def addUser(self, username, password):
        self.users[username] = password
            
    def newUser(self, username, password):
        self.addUser(username, password)
        file = open('users.csv', 'a', newline='')
        writer = csv.writer(file)
        writer.writerow([username, password])
        file.close()

    def search(self, username , password):
        try:
            p = self.users[username]
            if p == password: return True
            else: return False
        except:
            return False
    
