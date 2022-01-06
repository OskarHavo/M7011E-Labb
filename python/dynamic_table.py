from flask_table.html import element
"""
from python.index import tableDir


# https://stackoverflow.com/questions/60603303/flask-table-send-entire-row-data-on-buttoncol-form

class ProsumerTable (Table):
    userID = Col('User')
    userStatus = Col('Status')
    gotoButton = ButtonCol('Go To', tableDir, url_kwargs=dict(userID='userID'))
    blockButton = ButtonCol('Block', tableDir, url_kwargs=dict(userID='userID'))
    updateButton = ButtonCol('Update', tableDir, url_kwargs=dict(userID='userID'))
    deleteButton = ButtonCol('Delete', tableDir, url_kwargs=dict(userID='userID'))
    userIP = Col('IP')
    userPort = Col('Port')

class Item(object):
    def __init__(self, userID, userStatus, userIP, userPort):
        self.userID = userID
        self.userStatus = userStatus
        self.userIP = userIP
        self.userPort = userPort

items = [Item('User1', 'Online', '192.168.1.1', '6000'),
         Item('User2', 'Online', '192.168.1.2', '9886'),
         Item('User3', 'Offline', '192.168.1.3', '2540')]


# Or, more likely, load items from your database with something like
#items = ItemModel.query.all()

# Populate the table
prosumerTable = ProsumerTable(items)

# Print the html
print(prosumerTable.__html__())
"""
from flask_table import Table, Col, ButtonCol, LinkCol

class ScriptItem():
    def __init__(self,name, func):
        self.name = name
        self.func = func

from flask import Markup
class ScriptButtonCol(Col):
    def td_contents(self, i, attr_list):
        # by default this does
        return element(
            element="input",
            attrs={
                'value':self.name,"type":"button","onClick":self.from_attr_list(i, attr_list)
            },
            escape_attrs=False
        )

class UserTable(Table):
    user = Col('User')
    online = Col('Status')
    goto = ScriptButtonCol("Go to User")
    block = ScriptButtonCol("Block User")
    #update = ScriptButtonCol("Update Credentials")
    #delete = ScriptButtonCol("Delete")
    ip = Col('IP Address')
    port = Col('Port')


class Row(object):
    def __init__(self,user,online,goto,block,ip,port):
        self.user = user
        self.online = online
        self.goto = goto
        self.block = block
        self.ip = ip
        self.port = port