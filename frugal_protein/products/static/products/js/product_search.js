window.onload = function() {
    this.document.getElementById('btn-reset').addEventListener('click', btn_reset);
}

function btn_reset() {
    // Reset dropdown selections to default value
    var brand_dropdown = document.getElementById('id_brand');
    var store_dropdown = document.getElementById('id_store');

    brand_dropdown.selectedIndex = 0;
    store_dropdown.selectedIndex = 0;

    var form = document.getElementById('form')
}