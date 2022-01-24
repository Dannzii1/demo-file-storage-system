$('document').ready(()=>{

    $('.form-link').click((event) => {
        event.preventDefault();
        var el = event.target || event.srcElement;
        if (el instanceof HTMLAnchorElement) {
            var link_arr = el.getAttribute('href').split('=')
            $('#page').val(link_arr[link_arr.length - 1])
            $('#submit').click();
        }

    });
});