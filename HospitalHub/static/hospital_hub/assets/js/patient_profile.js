var dialog, form,
  required = $(".required-fields"),
  date = $("#date"),
  diagnosis = $("#diagnosis"),
  prescription = $("#prescription"),
  tests = $("#tests"),
  allFields = $([]).add(date).add(diagnosis).add(prescription).add(tests);


function setMessage(message) {
  required
    .text(message)
    .addClass("ui-state-highlight");
  setTimeout(function() {
    required.removeClass("ui-state-highlight", 1500);
  }, 500);
}

function addBook() {
  var valid = true;
  allFields.removeClass("ui-state-error");
  valid = valid && checkLength(date, "date", 1, 80);
  valid = valid && checkLength(diagnosis, "diagnosis name", 1, 60);

  if (valid) {
    $("#books tbody").append("<tr>" +
      "<td>" + date.val() + "</td>" +
      "<td>" + diagnosis.val() + "</td>" +
      "<td>" + prescription.val() + "</td>" +
      "<td>" + tests.val() + "</td>" +
      "</tr>");
    dialog.dialog("close");
  }
  return valid;
}

function checkLength(field, name, min, max) {
  if (field.val().length > max || field.val().length < min) {
    field.addClass("ui-state-error");
    setMessage(name + " length must be between " + min + " and " + max + ".");
    return false;
  } else {
    return true;
  }
}



dialog = $("#book-modal").dialog({
  autoOpen: false,
  height: 600,
  width: 500,
  modal: true,
  buttons: {
    Cancel: function() {
      dialog.dialog("close");
    }
  },
  close: function() {
    form[0].reset();
    allFields.removeClass("ui-state-error");
  }
});

$("#add-book-modal").button().on("click", function() {
  dialog.dialog("open");
});

$("#add-book-modal2").button().on("click", function() {
  dialog.dialog("open");
});

$("#add-book-modal3").button().on("click", function() {
  dialog.dialog("open");
});

form = dialog.find("form").on("submit", function(event) {
  event.preventDefault();
  document.getElementById("myForm").submit();
});
