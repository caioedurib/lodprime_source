var result = null

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
        formattedTable.push({removeCol: row[0], compound: row[1], str_ids: row[2], gene_names:row[3]});
   }
   return JSON.stringify(formattedTable);
}

// Remove a single row from the table
function InputTable_RemoveRow(delRow) {
  //https://examples.bootstrap-table.com/#methods/remove.html#view-source
  let table = $('#table_input').DataTable();
  table.row(delRow).remove().draw();
  saveTable();
}

// Clear the whole table and local data
function InputTable_ClearTable() {
  let table = $('#table_input').DataTable();
  table.clear().draw();
  localStorage.removeItem("DataTables_tableData");
  InputTable_AddRow('', '', '');
}

// Add a row to the table.
function InputTable_AddRow(compound, str_ids, gene_names) {
    let table = $('#table_input').DataTable();
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
    let hue=((1-value)*120).toString(10);
    return ["hsl(",hue,",100%,50%)"].join("");
}


// Automatically fill the targets column based on the compound names column
function InputTable_AutofillTargets(){
   let table = $('#table_input').DataTable();
   let tableJSON = convertTableJSON(table);
   $.post("../autocomplete/", { empty_targets_list: tableJSON}, function(data) {
        let result = JSON.parse(data);
        for(let i=0; i<result.length;i++){
            /*
            eq() is a css selector to find the row(s) we want to edit.
            Means we ref by "render" instead of internal "array" that may get shifted by delete.
             */
            let row = table.row(`:eq(${i})`).data();
            row[2] = result[i]["str_ids"];
            row[3] = result[i]["gene_names"];
            table.row(`:eq(${i})`).data(row);
        }
        table.draw();
   })
}

// Scan for "empty" compound rows (no STRING target ID/Gene Name) -> Trigger autofill for that row.
function InputTable_AutofillEmpty(){
    let table = $('#table_input').DataTable();
    let tableJSON = convertTableJSON(table);

    // Must be async, or we might make a prediction before the autocomplete is done!
    $.ajax({
        type: "POST",
        url: "../autocomplete/",
        async: false,
        data: {empty_targets_list: tableJSON}
    })
       .done(function(data) {
           console.log(data);
            let result = JSON.parse(data);
            for(let i=0; i<result.length;i++){
                console.log("Row: " + i);
                let row = table.row(`:eq(${i})`).data();
                // If both string ID/gene name are empty...
                if(row[2].trim() === "" && row[3].trim() === "") {
                    row[2] = result[i]["str_ids"];
                    row[3] = result[i]["gene_names"];
                    table.row(`:eq(${i})`).data(row);
                }
            }
            table.draw();
       })
}


// Send data to python to get predictions.
function InputTable_MakePredictions(){

    // Autofill any "empty" lines.
    InputTable_AutofillEmpty();

   // Select table as DataTable instance, convert data to array (deep copy)
   let table = $('#table_input').DataTable();
   let tableJSON = convertTableJSON(table);
    // TODO: Reveal spinner here
   // Send AJAX request, append returned html to the page.
   $.post(window.location, { targets_list: tableJSON}, function(data) {
        result = JSON.parse(data);
        let resultTable = "<table class='display dataTable'>";
        let printdetailedResults = "<b>"
        //resultTable += "<tr><th>Compound</th><th>STRING Target IDs</th><th>Gene names</th><th>Valid Targets</th><th>Male Pos-class likelihood %</th><th>Female Pos-class likelihood %</th></tr>";
        resultTable += "<tr><th>Compound</th><th>Valid Targets</th><th>Male Pos-class likelihood</th><th>Female Pos-class likelihood</th></tr>";

        for(let i=0; i<result.length;i++){
            resultTable += '<tr><td>' + result[i]["compound"] + '</td>';
            //resultTable += '<td>' + result[i]["str_ids"] + '</td>';
            //resultTable += '<td>' + result[i]["gene_names"] + '</td>';
            resultTable += '<td>' + result[i]["target_number"] + '</td>';
            predictionColor = getColor(result[i]["m_prediction"]/100)
            resultTable += `<td style="background-color: ${predictionColor}">` + result[i]["m_prediction"] + '%</td>';
            predictionColor = getColor(result[i]["f_prediction"]/100)
            resultTable += `<td style="background-color: ${predictionColor}">` + result[i]["f_prediction"] + '%</td></tr>';
            if(result[i]["detailed_results"] != ""){
                printdetailedResults += result[i]["detailed_results"] +'<br>';
            }
        }
        // TODO: Hide spinner here
        printdetailedResults += "</b>"
        resultTable += "</table>";
        $("#result").html(resultTable);
        $("#detailed_results").html(printdetailedResults);
       $('#Btn_DetailedPredictionsFile').prop("hidden", false)
   })
}

function InputTable_ExportTable() {
    let textToSave = "Compound\tMale Pos-class likelihood\tFemale Pos-class likelihood\n";
    for(let i=0; i<result.length;i++){
        textToSave += result[i]["compound"] + '\t' + result[i]["m_prediction"] +  '%\t' + result[i]["f_prediction"] + '%\n';
       //if(result[i]["detailed_results"] != ""){
       //     textToSave += result[i]["detailed_results"] + '\n';
       // }
    }
    let hiddenElement = document.createElement('a');
    hiddenElement.href = 'data:attachment/text,' + encodeURI(textToSave);
    hiddenElement.target = '_blank';
    hiddenElement.download = 'Model Predictions - Detailed Results.tsv';
    hiddenElement.click();
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

function InputTable_LoadFromFile(fileInput) {
    InputTable_ClearTable();
    // Identify the file path
    let file = fileInput.files[0];

    // Set up a reader to read the file, and set up a function to run when it is finished reading
    const reader = new FileReader();
    reader.addEventListener('load', (event) => {
        let filecontent = event.target.result.toString();

        console.log(filecontent);
        let lines = filecontent.split('\n');
        for (let i = 0; i < lines.length; i++) {
            let tabs = lines[i].split('\t');
            console.log("Drugs: " + tabs[0]);
            console.log("String IDs: " + tabs[1]);
            console.log("Gene Names: " + tabs[2]);
            console.log("----");
            tabs[1] = tabs[1].replaceAll("\"",""); //if loading from .tsv file, Excel may have added quotations
            tabs[2] = tabs[2].replaceAll("\"",""); //if loading from .tsv file, Excel may have added quotations
            InputTable_AddRow(tabs[0], tabs[1], tabs[2]);
        }
        saveTable();
    });

    // Read the file, trigger the "load" listener.
    reader.readAsText(file);
}

// ------------------------------------------------------------------------------------------------------------------
function ChemCreateTable(table_id, info_bool, paging_bool, searching_bool) {
    let gen_table = new DataTable(table_id, {
        info: info_bool,
        paging: paging_bool,
        searching: searching_bool,
        columnDefs: [{orderable: false, width: '20px', targets: 0}, {type: "text", targets: [1,2]}],
        order: []
    });
    return gen_table;
}

function ChemCreateTable_data(table_id, info_bool, paging_bool, searching_bool) {
    let gen_table = new DataTable(table_id, {
        info: info_bool,
        paging: paging_bool,
        searching: searching_bool,
        columnDefs: [{width: '200px', targets: 0}, {width: '20px', targets: [1]}, {width: '200px', targets: 2},
        {orderable: true, type: "text", targets: [0,1,2]}],
        order: []
    });
    return gen_table;
}

// Convert table data into JSON
function ChemconvertTableJSON(table) {
   let tableArray = structuredClone(table.rows().data().toArray());
   // Convert table into a formatted JSON object
   formattedTable = []
   for (let i = 0; i < tableArray.length; i++) {
        let row = tableArray[i];
        formattedTable.push({removeCol: row[0], compound: row[1], cid: row[2]});
   }
   return JSON.stringify(formattedTable);
}


// Remove a single row from the table
function ChemInputTable_RemoveRow(delRow) {
  let table = $('#table_cheminput').DataTable();
  table.row(delRow).remove().draw();
  saveTable();
}

// Clear the whole table and local data
function ChemInputTable_ClearTable() {
  let table = $('#table_cheminput').DataTable();
  table.clear().draw();
  localStorage.removeItem("DataTables_chemtableData");
  ChemInputTable_AddRow('', '');
}

// Add a row to the table.
function ChemInputTable_AddRow(compound, cid) {
    let table = $('#table_cheminput').DataTable();
    removeIcon = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="darkRed"\
        class="bi bi-x-circle-fill" viewBox="0 0 16 16" onclick="ChemInputTable_RemoveRow($(this).closest(\'tr\'))">\
        <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0M5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0\
        .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293z"/>\
        </svg>'
    table.row.add([removeIcon, compound.toString(), cid.toString()]).draw();
}


// Save table contents to localstorage
function ChemsaveTable() {
    let table = $('#table_cheminput').DataTable();
    let tableJSON = ChemconvertTableJSON(table);
    localStorage.setItem('DataTables_chemtableData', tableJSON);
}

// Load table from localstorage
function ChemloadTable() {
    let loadData = localStorage.getItem('DataTables_chemtableData');
    // Check if it's valid JSON, return empty if not.
    if(!loadData){
        return;
    }
    let parseData = JSON.parse(loadData);
    for ( i = 0; i < parseData.length; i++) {
        row = parseData[i];
        ChemInputTable_AddRow(row.compound, row.cid)
    }
}

function ChemInputTable_LoadFromFile(fileInput) {
    ChemInputTable_ClearTable();
    // Identify the file path
    let file = fileInput.files[0];

    // Set up a reader to read the file, and set up a function to run when it is finished reading
    const reader = new FileReader();
    reader.addEventListener('load', (event) => {
        let filecontent = event.target.result.toString();

        console.log(filecontent);
        let lines = filecontent.split('\n');
        for (let i = 0; i < lines.length; i++) {
            let tabs = lines[i].split('\t');
            console.log("Compound: " + tabs[0]);
            console.log("CID: " + tabs[1]);
            console.log("----");
            tabs[1] = tabs[1].replaceAll("\"",""); //if loading from .tsv file, Excel may have added quotations
            tabs[2] = tabs[2].replaceAll("\"",""); //if loading from .tsv file, Excel may have added quotations
            ChemInputTable_AddRow(tabs[0], tabs[1]);
        }
        ChemsaveTable();
    });

    // Read the file, trigger the "load" listener.
    reader.readAsText(file);
}


// Send data to python to get predictions.
function ChemInputTable_MakePredictions(){
   // Select table as DataTable instance, convert data to array (deep copy)
   let table = $('#table_cheminput').DataTable();
   let tableJSON = ChemconvertTableJSON(table);
    // TODO: Reveal spinner here
   // Send AJAX request, append returned html to the page.
   $.post(window.location, { targets_list: tableJSON}, function(data) {
        result = JSON.parse(data);
        let resultTable = "<table class='display dataTable'>";
        let printdetailedResults = "<b>"
        //resultTable += "<tr><th>Compound</th><th>STRING Target IDs</th><th>Gene names</th><th>Valid Targets</th><th>Male Pos-class likelihood %</th><th>Female Pos-class likelihood %</th></tr>";
        resultTable += "<tr><th>Compound</th><th>CID</th><th>Male Pos-class likelihood</th><th>Female Pos-class likelihood</th></tr>";

        for(let i=0; i<result.length;i++){
            resultTable += '<tr><td>' + result[i]["compound"] + '</td>';
            resultTable += '<td>' + result[i]["cid"] + '</td>';
            predictionColor = getColor(result[i]["m_prediction"]/100)
            resultTable += `<td style="background-color: ${predictionColor}">` + result[i]["m_prediction"] + '%</td>';
            predictionColor = getColor(result[i]["f_prediction"]/100)
            resultTable += `<td style="background-color: ${predictionColor}">` + result[i]["f_prediction"] + '%</td></tr>';
            if(result[i]["detailed_results"] != ""){
                printdetailedResults += result[i]["detailed_results"] +'<br>';
            }
        }
        // TODO: Hide spinner here
        printdetailedResults += "</b>"
        resultTable += "</table>";
        $("#result").html(resultTable);
        $("#detailed_results").html(printdetailedResults);
        $('#Btn_DetailedPredictionsFile').prop("hidden", false)
   })
}

function ChemInputTable_ExportTable() {
    let textToSave = "Compound\tMale Pos-class likelihood\tFemale Pos-class likelihood\n";
    for(let i=0; i<result.length;i++){
        textToSave += result[i]["compound"] + '\t' + result[i]["m_prediction"] +  '%\t' + result[i]["f_prediction"] + '%\n';
       //if(result[i]["detailed_results"] != ""){
       //     textToSave += result[i]["detailed_results"] + '\n';
       // }
    }
    let hiddenElement = document.createElement('a');
    hiddenElement.href = 'data:attachment/text,' + encodeURI(textToSave);
    hiddenElement.target = '_blank';
    hiddenElement.download = 'Chem_Model Predictions - Detailed Results.tsv';
    hiddenElement.click();
}