/*
Attribution
Original code snippet by Andrew Whitaker http://stackoverflow.com/users/497356/andrew-whitaker
from http://stackoverflow.com/questions/5972958/implementing-jquery-ui-autocomplete-to-show-suggestions-when-you-type

Remixed by Kabir Kukreti http://stackoverflow.com/users/1099639/kabirkukreti also using jQuery autocomplete UI code http://jqueryui.com/autocomplete/

*/


$(function () {
    var PlayerNames = [
        "Romario",
        "Ronaldo",
        "Zico",
        "Cafu",
        "Pele",
        "Maradona",
        "Luis Figo",
        "Zinedine Zidane",
        "Bebeto",
        "Gerd Müller"];

    function split(val) {
        return val.split(/@\s*/);
    }

    function extractLast(term) {
        return split(term).pop();
    }

    $("#comment_form_input")
    // don't navigate away from the field on tab when selecting an item
    .bind("keydown", function (event) {
        if (event.keyCode === $.ui.keyCode.TAB && $(this).data("autocomplete").menu.active) {
            event.preventDefault();
        }
    }).autocomplete({
        minLength: 0,
        source: function (request, response) {
            var term = request.term,
                results = [];
            if (term.indexOf("@") >= 0) {
                term = extractLast(request.term);
                if (term.length > 0) {
                    results = $.ui.autocomplete.filter(
                    PlayerNames, term);
                } else {
                    results = ['Type the name of the player'];
                }
            }
            response(results);
        },
        focus: function () {
            // prevent value inserted on focus
            return false;
        },
        select: function (event, ui) {
            var terms = split(this.value);
            // remove the current input
            terms.pop();
            // add the selected item
            terms.push(ui.item.value);
            // add placeholder to get the comma-and-space at the end
            terms.push("");
            this.value = terms.join("");
            return false;
        }
    });

});
