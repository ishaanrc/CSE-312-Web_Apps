function update() {
    $.ajax({
        url: 'home.html',
        success:  function(data) {
            update();
        },
        timeout: 500000 //Long poll to repeat itself
    });
}
function load() {
    $.ajax({
        url: 'home.html',
        success: function(data) {
            update();
        }
    });
}
$(document).ready(function() {
    load();
});
