    function changelist() {

        var keyword = document.getElementById("speciality").value;
        var select = document.getElementById("doctors");
        

        for (var i = 0; i < select.options.length; i++) {
            var txt = select.options[i].text;
            console.log(txt);
            if (!txt.match(keyword)) {
                console.log(txt);
            $(select.options[i]).attr('disabled', 'disabled').hide();
            } else {
            $(select.options[i]).removeAttr('disabled').show();
                }
            }
            
    }
/*
     function changelist() {

    var keyword = document.getElementById("testinput").value;

    var select = document.getElementById("doctors_list");
    for (var i = 1; i < select.length; i++) {
            var txt = select.options[i].getElementByClassName("spec")[0].text;
        if (!txt.match(keyword)) {
        $(select.options[i]).attr('disabled', 'disabled').hide();
            } else {
        $(select.options[i]).removeAttr('disabled').show();
            }
        }
        select.value = select.options[0].text;
    }
*/