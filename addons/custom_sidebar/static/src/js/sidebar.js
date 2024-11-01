document.addEventListener('DOMContentLoaded', function() {
    var sidebarItems = document.querySelectorAll('.o_sidebar .nav-item a');
    sidebarItems.forEach(function(item) {
        item.addEventListener('click', function() {
            // Lógica interativa pode ser adicionada aqui
            console.log('Menu clicado: ' + item.textContent);
        });
    });
});
