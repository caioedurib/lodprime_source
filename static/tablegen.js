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

function getColor(value){
    //value from 0 to 1
    value = 1 - value // Flip
    var hue=((1-value)*120).toString(10);
    return ["hsl(",hue,",100%,50%)"].join("");
}

function InputTable_MakePredictions(){
   // Select table as DataTable instance, convert data to array (deep copy)
   let table = $('#table_input').DataTable();
   let tableArray = structuredClone(table.rows().data().toArray());

   // Convert table into a formatted JSON object
   formattedTable = []
   for (let i = 0; i < tableArray.length; i++) {
        row = tableArray[i];
        row[2] = row[2].replaceAll(' ','').split(",") // Convert targets to array, removing spaces
        formattedTable.push({compound: row[0], pubchem: row[1], targets:row[2]});
   }
   let tableJSON = JSON.stringify(formattedTable);

   // Send AJAX request, append returned html to the page.
   $.post(window.location, { targets_list: tableJSON}, function(data) {
        result = JSON.parse(data);
        var resultTable = "<table class='display dataTable'>";
        resultTable += "<tr><th>Compound</th><th>Pubchem ID</th><th>Targets</th><th>No. Targets</th><th>Prediction</th></tr>";
        for(i=0; i<result.length;i++){
            resultTable += '<tr><td>' + result[i]["compound"] + '</td>';
            resultTable += '<td>' + result[i]["pubchem"] + '</td>';
            resultTable += '<td>' + result[i]["targets"] + '</td>';
            resultTable += '<td>' + result[i]["target_number"] + '</td>';

            predictionColor = getColor(result[i]["prediction"]/100)
            resultTable += `<td style="background-color: ${predictionColor}">` + result[i]["prediction"] + '</td></tr>';
        }
        resultTable += "</table>";
        $("#result").html(resultTable);
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