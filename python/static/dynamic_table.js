function newTableRow() {
    // Lägg in getters
    var userID = "User"
    var status = "Online"
    var ip = "192.168.1.1"
    var port = "3459"

    var table = document.getElementById("prosumerTable");

    var rowCount = table.rows.length;
    var new_row = table.insertRow(rowCount);

    new_row.insertCell(0).innerHTML= userID.value;
    new_row.insertCell(1).innerHTML= status.value;
    new_row.insertCell(2).innerHTML= '<input type="button" value = "Go To" onClick="Javascript:deleteRow(this)">';
    new_row.insertCell(3).innerHTML= '<input type="button" value = "Block" onClick="Javascript:deleteRow(this)">';
    new_row.insertCell(4).innerHTML= '<input type="button" value = "Update" onClick="Javascript:deleteRow(this)">';
    new_row.insertCell(5).innerHTML= '<input type="button" value = "Delete" onClick="Javascript:deleteRow(this)">';
    new_row.insertCell(6).innerHTML= ip.value;
    new_row.insertCell(7).innerHTML= port.value;
}

function deleteRow(obj) {
    var index = obj.parentNode.parentNode.rowIndex;
    var table = document.getElementById("prosumerTable");
    table.deleteRow(index);
}