var testRowIdx = 0;

$('#addBtn').on('click', function () {
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

$(document).on('change','#type',function() {
    if($("#type option:selected").text() == 'Coding'){
        $('#coding').show();
        $('#mcq').hide();
    }
    else {
        $('#coding').hide();
        $('#mcq').show();
    }
});
