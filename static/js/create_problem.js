var testRowIdx = 0;

$('#addBtn').on('click', function () {
    testRowIdx = Math.max(0, testRowIdx);
    var newRow = `
        <tr id="R${++ testRowIdx}">
            <td class="row-index text-center"><p>#${testRowIdx}</p></td>
            <td class="text-center"><textarea type="text" class="test-data" name="test-case" required></textarea></td>
            <td class="text-center"><a class="btn btn-xs delete-record remove" data-id="3"><i class="far fa-trash-alt" style="font-size:24px"></i></a></td>
        </tr>
    `
    $('#tbody').append(newRow);
});

$('#tbody').on('click', '.remove', function () {
    var child = $(this).closest('tr').nextAll();
    child.each(function () {
        var id = $(this).attr('id');
        var idx = $(this).children('.row-index').children('p');
        var dig = parseInt(id.substring(1));
        idx.html(`#${dig - 1}`);
        $(this).attr('id', `R${dig - 1}`);
    });
    $(this).closest('tr').remove();
    testRowIdx--;
});

$(document).on('change','#type', function() {
    if($("#type option:selected").text() == 'Coding') {
        $('#coding').show();
        $('#mcq').hide();
        $("#sample-input").attr("required", true);
        $("#code").attr("required", true);
        $("#option1").attr("required", false);
        $("#option2").attr("required", false);
        $("#option3").attr("required", false);
        $("#option4").attr("required", false);
        $("#answer").attr("required", false);
    }
    else {
        $('#coding').hide();
        $('#mcq').show();
        $("#sample-input").attr("required", false);
        $("#code").attr("required", false);
        $("test-case").attr("required", false);
        $("#option1").attr("required", true);
        $("#option2").attr("required", true);
        $("#option3").attr("required", true);
        $("#option4").attr("required", true);
        $("#answer").attr("required", true);
    }
});

$(document).ready(function() {
    if($("#type option:selected").text() == 'Coding') {
        $('#coding').show();
        $('#mcq').hide();
        $("#sample-input").attr("required", true);
        $("#code").attr("required", true);
        $("#option1").attr("required", false);
        $("#option2").attr("required", false);
        $("#option3").attr("required", false);
        $("#option4").attr("required", false);
        $("#answer").attr("required", false);
    }
    else {
        $('#coding').hide();
        $('#mcq').show();
        $("#sample-input").attr("required", false);
        $("#code").attr("required", false);
        $("test-case").attr("required", false);
        $("#option1").attr("required", true);
        $("#option2").attr("required", true);
        $("#option3").attr("required", true);
        $("#option4").attr("required", true);
        $("#answer").attr("required", true);
    }
});
