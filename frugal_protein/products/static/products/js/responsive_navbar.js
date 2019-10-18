
window.onload = function() {
    document.getElementById('navbar-left-dropdown-btn').addEventListener('click', navbar_add_dropdown);
    // document.getElementById('navbar-search-btn').addEventListener('click', navbar_add_search_show);
}

// func to add 'dropdown' to class attributes to sepcific elements in HTML DOM
function navbar_add_dropdown() {
    var nav_left = document.getElementsByClassName('navbar-left')[0]
    var nav_right = document.getElementsByClassName('navbar-right')[0]

    if (nav_left.className === 'navbar-left') {
        nav_left.classList.add('dropdown')
    } else {
        nav_left.classList.remove('dropdown')
    }

    if (!nav_right.className.includes('dropdown')) {
        nav_right.classList.add('dropdown')
    } else {
        nav_right.classList.remove('dropdown')
    }

}