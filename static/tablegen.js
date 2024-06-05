function CreateTable(table_id, info_bool, paging_bool, searching_bool) {
    let gen_table = new DataTable(table_id, {
        info: info_bool,
        paging: paging_bool,
        searching: searching_bool,
        columnDefs: [{orderable: false, width: '20px', targets: 0}, {type: "text", targets: [1,2,3]}],
        order: []
    });
    return gen_table;
}

function InputTable_AddRow() {
    var table = new DataTable('#table_input');
    removeIcon = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="darkRed"\
        class="bi bi-x-circle-fill" viewBox="0 0 16 16" onclick="InputTable_RemoveRow($(this).parents(\'tr\'))">\
        <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0M5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0\
        .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293z"/>\
        </svg>'
    table.row.add([removeIcon,'','','']).draw();
}

function InputTable_RemoveRow(delRow) {
  let table = new DataTable('#table_input'); // Select table
  table.row(delRow).remove().draw();
}

function InputTable_LoadFromFile() {
  // #Todo
}

function getColor(value){
    //value from 0 to 1
    value = 1 - value // Flip, otherwise it does red for high values
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
        row[3] = row[3].replaceAll(' ','').split(",") // Convert targets to array, removing spaces
        formattedTable.push({compound: row[1], pubchem: row[2], targets:row[3]});
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
            resultTable += '<td>' + result[i]["targets"].join(", ") + '</td>';
            resultTable += '<td>' + result[i]["target_number"] + '</td>';

            predictionColor = getColor(result[i]["prediction"]/100)
            resultTable += `<td style="background-color: ${predictionColor}">` + result[i]["prediction"] + '</td></tr>';
        }
        resultTable += "</table>";
        $("#result").html(resultTable);
   })
}

function InputTable_ClearTable() {
  let table = new DataTable('#table_input'); // Select table
  table.clear().draw();
}