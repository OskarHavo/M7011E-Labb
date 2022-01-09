from flask_table.html import element
from flask_table import Table, Col


class ScriptItem():
    def __init__(self, name, func):
        self.name = name
        self.func = func


class ScriptButtonCol(Col):
    def td_contents(self, i, attr_list):
        return element(
            element="input",
            attrs={
                'value': self.name, "type": "button", "onClick": self.from_attr_list(i, attr_list)
            },
            escape_attrs=False
        )


class UserTable(Table):
    user = Col('User')
    online = Col('Status')
    goto = ScriptButtonCol("Go to User")
    block = ScriptButtonCol("Block User")

    ip = Col('IP Address')
    port = Col('Port')


class Row(object):
    def __init__(self, user, online, goto, block, ip, port):
        self.user = user
        self.online = online
        self.goto = goto
        self.block = block
        self.ip = ip
        self.port = port
