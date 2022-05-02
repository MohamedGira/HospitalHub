












function EnableThis(mycheckbox, idname) {
    
    var day1 = document.getElementById(idname + "1");
    var day2 = document.getElementById(idname + "2");
    day1.disabled = mycheckbox.checked ? false : true;
    day2.disabled = mycheckbox.checked ? false : true;
    if (!day1.disabled) {
        day1.focus();
    }
}





function EnableSaturday(saturday) {
          var saturday1 = document.getElementById("saturday1");
    saturday1.disabled = saturday.checked ? false : true;
    saturday2.disabled = saturday.checked ? false : true;
    if (!saturday1.disabled) {
        saturday1.focus();
          }
    }

    function EnableSunday(sunday) {
          var sunday1 = document.getElementById("sunday1");
    sunday1.disabled = sunday.checked ? false : true;
    sunday2.disabled = sunday.checked ? false : true;
    if (!sunday1.disabled) {
        sunday1.focus();
          }
      }
    function EnableMonday(monday) {
          var monday1 = document.getElementById("monday1");
    monday1.disabled = monday.checked ? false : true;
    monday2.disabled = monday.checked ? false : true;
    if (!monday1.disabled) {
        monday1.focus();
          }
      }
    function EnableTuesday(tuesday) {
          var tuesday1 = document.getElementById("tuesday1");
    tuesday1.disabled = tuesday.checked ? false : true;
    tuesday2.disabled = tuesday.checked ? false : true;
    if (!tuesday1.disabled) {
        tuesday1.focus();
          }
      }
    function EnableWednesday(wednesday) {
          var wednesday1 = document.getElementById("wednesday1");
    wednesday1.disabled = wednesday.checked ? false : true;
    wednesday2.disabled = wednesday.checked ? false : true;
    if (!wednesday1.disabled) {
        wednesday1.focus();
          }
      }
    function EnableThursday(thursday) {
          var thursday1 = document.getElementById("thursday1");
    thursday1.disabled = thursday.checked ? false : true;
    thursday2.disabled = thursday.checked ? false : true;
    if (!thursday1.disabled) {
        thursday1.focus();
          }
      }
    function EnableFriday(friday) {
          var friday1 = document.getElementById("friday1");
    friday1.disabled = friday.checked ? false : true;
    friday2.disabled = friday.checked ? false : true;
    if (!friday1.disabled) {
        friday1.focus();
          }
      }
