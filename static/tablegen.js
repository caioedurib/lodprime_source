function CreateTable(table_id, info_bool, paging_bool, searching_bool) {
    let gen_table = new DataTable(table_id, {
        info: info_bool,
        paging: paging_bool,
        searching: searching_bool
    });
    return gen_table;
}

function InputTable_AddRow() {
    var table = new DataTable('#table_input');
    table.row.add(['','','','TBD','']).draw();
}

function InputTable_RemoveRow() {
  document.getElementById("table_input").deleteRow(1);
}

function InputTable_ClearTable() {
  table = document.getElementById("table_input");
  var rows = table.rows;
  var i = rows.length;
  while (--i) {
    rows[i].parentNode.removeChild(rows[i]);
    // or
    // table.deleteRow(i);
  }
}