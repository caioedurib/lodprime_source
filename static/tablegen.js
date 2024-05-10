function CreateTable(table_id, info_bool, paging_bool, searching_bool) {
    let gen_table = new DataTable(table_id, {
        info: info_bool,
        paging: paging_bool,
        searching: searching_bool
    });
    return gen_table;
}

function InputTable_AddRow() {
    var table = document.getElementById("table_input"),
    tbody = table.getElementsByTagName("tbody")[0];
    var row = document.createElement("tr");
    var cell1 = document.createElement("td");
    var cell2 = document.createElement("td");
    var cell3 = document.createElement("td");
    cell1.innerHTML = "1";
    cell2.innerHTML = "2";
    cell3.innerHTML = "3";
    row.appendChild(cell1);
    row.appendChild(cell2);
    row.appendChild(cell3);
    tbody.appendChild(row);
}

function InputTable_RemoveRow(index) {
  document.getElementById("table_input").deleteRow(index);
}