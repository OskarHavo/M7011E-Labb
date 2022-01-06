from flask_table.html import element
from flask_table import Table, Col, ButtonCol


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
    online = Col('Online')
    goto = ScriptButtonCol("Go to")
    block = ScriptButtonCol("Block")
    update = ScriptButtonCol("Update")
    delete = ScriptButtonCol("Delete")
    ip = Col('IP')
    port = Col('Port')


class Row(object):
    def __init__(self,user,online,goto,block,update,delete,ip,port):
        self.user = user
        self.online = online
        self.goto = goto
        self.block = block
        self.update = update
        self.delete = delete
        self.ip = ip
        self.port = port