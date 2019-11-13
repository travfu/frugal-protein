window.onload = function() {
    document.getElementById('btn-reset').addEventListener('click', reset_form);
}

function reset_form() {
    var input_ids = [
        'id_price_value',
        'id_qty_value',
        'id_protein_value',
        'id_protein_per_value'
    ]

    for (i = 0; i < input_ids.length; i++) {
        document.getElementById(input_ids[i]).removeAttribute('value')
    }
}