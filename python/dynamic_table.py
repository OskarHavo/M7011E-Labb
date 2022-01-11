from flask_table.html import element
from flask_table import Table, Col

class ScriptItem():
    """! An item that holds a name and, presumably, a javascript in string format."""
    def __init__(self, name, func):
        """Init
        @param name Name of the item.
        @param func Function to call.
        """
        self.name = name
        self.func = func

class ScriptButtonCol(Col):
    """! A custom class for enabling the addition of buttons in our table"""
    def td_contents(self, i, attr_list):
        """! Adds the functionality of the button.
        @param i Item
        @param attr_list Attribute list
        """
        return element(
            element="input",
            attrs={
                'value': self.name, "type": "button", "onClick": self.from_attr_list(i, attr_list)
            },
            escape_attrs=False
        )

class UserTable(Table):
    """! Class for creating a usertable which is displayed in the admin dashboard"""

    user = Col('User')
    online = Col('Status')
    goto = ScriptButtonCol("Go to User")
    block = ScriptButtonCol("Block User")
    ip = Col('IP Address')
    port = Col('Port')

class Row(object):
    """! The structure of a row in the table."""
    def __init__(self, user, online, goto, block, ip, port):
        """! Init.
        @param user User name.
        @param online Online status.
        @param goto ScriptItem.
        @param block ScriptItem.
        @param ip User IP.
        @param port User port.
        """
        self.user = user
        self.online = online
        self.goto = goto
        self.block = block
        self.ip = ip
        self.port = port
