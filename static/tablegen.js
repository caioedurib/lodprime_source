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

function CreateTable_data(table_id, info_bool, paging_bool, searching_bool) {
    let gen_table = new DataTable(table_id, {
        info: info_bool,
        paging: paging_bool,
        searching: searching_bool,
        columnDefs: [{width: '200px', targets: 0}, {width: '20px', targets: [1,2]}, {width: '200px', targets: 3},
        {orderable: true, type: "text", targets: [0,1,2,3]}],
        order: []
    });
    return gen_table;
}

// Convert table data into JSON
function convertTableJSON(table) {
   let tableArray = structuredClone(table.rows().data().toArray());

   // Convert table into a formatted JSON object
   formattedTable = []
   for (let i = 0; i < tableArray.length; i++) {
        let row = tableArray[i];
        if(Array.isArray(row[3])) {
            row[3] = row[3].toString();
        }
        row[3] = row[3].replaceAll(' ','').split(",") // Convert targets to array, removing spaces
        formattedTable.push({removeCol: row[0], compound: row[1], str_ids: row[2], gene_names:row[3]});
   }
   return JSON.stringify(formattedTable);
}

// Remove a single row from the table
function InputTable_RemoveRow(delRow) {
  let table = new DataTable('#table_input');
  table.row(delRow).remove().draw();
  saveTable();
}

// Clear the whole table and local data
function InputTable_ClearTable() {
  let table = new DataTable('#table_input');
  table.clear().draw();
  localStorage.removeItem("DataTables_tableData");
}

// Add a row to the table.
function InputTable_AddRow(compound, str_ids, gene_names) {
    var table = new DataTable('#table_input');
    removeIcon = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="darkRed"\
        class="bi bi-x-circle-fill" viewBox="0 0 16 16" onclick="InputTable_RemoveRow($(this).parents(\'tr\'))">\
        <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0M5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0\
        .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293z"/>\
        </svg>'
    table.row.add([removeIcon, compound.toString(), str_ids.toString(), gene_names.toString()]).draw();
}

// Gen colour based on prediction result 0-100
function getColor(value){
    //value from 0 to 1
    value = 1 - value // Flip, otherwise it does red for high values
    var hue=((1-value)*120).toString(10);
    return ["hsl(",hue,",100%,50%)"].join("");
}

// Send data to python to get predictions.
function InputTable_MakePredictions(){
   // Select table as DataTable instance, convert data to array (deep copy)
   let table = $('#table_input').DataTable();
   let tableJSON = convertTableJSON(table);

   // Send AJAX request, append returned html to the page.
   $.post(window.location, { targets_list: tableJSON}, function(data) {
        result = JSON.parse(data);
        var resultTable = "<table class='display dataTable'>";
        var printdetailedResults = "<b>"
        resultTable += "<tr><th>Compound</th><th>STRING Target IDs</th><th>Gene names</th><th>No. Targets</th><th>Prediction</th></tr>";

        for(let i=0; i<result.length;i++){
            resultTable += '<tr><td>' + result[i]["compound"] + '</td>';
            resultTable += '<td>' + result[i]["str_ids"] + '</td>';
            resultTable += '<td>' + result[i]["gene_names"].join(", ") + '</td>';
            resultTable += '<td>' + result[i]["target_number"] + '</td>';
            predictionColor = getColor(result[i]["prediction"]/100)
            resultTable += `<td style="background-color: ${predictionColor}">` + result[i]["prediction"] + '</td></tr>';
            printdetailedResults += result[i]["detailed_results"] +'<br>'
        }

        printdetailedResults += "</b>"
        resultTable += "</table>";
        $("#result").html(resultTable);
        $("#detailed_results").html(printdetailedResults);
   })
}

// Save table contents to localstorage
function saveTable() {
    let table = $('#table_input').DataTable();
    let tableJSON = convertTableJSON(table);
    localStorage.setItem('DataTables_tableData', tableJSON);
}

// Load table from localstorage
function loadTable() {
    let loadData = localStorage.getItem('DataTables_tableData');
    // Check if it's valid JSON, return empty if not.
    if(!loadData){
        return;
    }
    let parseData = JSON.parse(loadData);
    for ( i = 0; i < parseData.length; i++) {
        row = parseData[i];
        InputTable_AddRow(row.compound, row.str_ids, row.gene_names)
    }
}

function InputTable_LoadFromFile() {
  // #Todo
}