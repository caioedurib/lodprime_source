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
    table.row.add(['','','','']).draw();
}

function InputTable_RemoveRow() {
  document.getElementById("table_input").deleteRow(1);
}

function InputTable_LoadFromFile() {
  //
}

function InputTable_MakePredictions(){
   // Select table as DataTable instance, convert data to array
   let table = $('#table_input').DataTable();
   let tableArray = table.rows().data().toArray();

   // Remove the last column from each row (the "remove row" button column)
   for (let i = 0; i < tableArray.length; i++) {
        tableArray[i].pop();
   }

   // Convert array to JSON string
   let tableJSON = JSON.stringify(tableArray);

   // Send AJAX request, append returned html to the page.
   $.post(window.location, { targets_list: tableJSON}, function(data) {
        $("#result").html(data);
   })
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