const editor = new DataTable.Editor({
    fields: [
        {
            label: 'Compound:',
            name: 'compound'
        },
        {
            label: 'DrugBank ID:',
            name: 'drugbankid'
        },
        {
            label: 'Targets List:',
            name: 'targetslist'
        },
        {
            label: 'Prediction:',
            name: 'prediction'
        },
    ],
    table: '#table_input'
});

const table = new DataTable('#table_input', {
    columns: [
        {
            data: null,
            orderable: false,
            render: DataTable.render.select()
        },
        { data: 'compound' },
        { data: 'drugbankid' },
        { data: 'targetslist' },
        { data: 'prediction' },
    ],
    layout: {
        topStart: {
            buttons: [
                { extend: 'create', editor: editor },
                { extend: 'edit', editor: editor },
                { extend: 'remove', editor: editor }
            ]
        }
    },
    order: [[1, 'asc']],
    select: {
        style: 'os',
        selector: 'td:first-child'
    }
});

// Activate an inline edit on click of a table cell
table.on('click', 'tbody td:not(:first-child)', function (e) {
    editor.inline(this);
});