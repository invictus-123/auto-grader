$('#run-code').click(function() {
	$('#sample-run').html('Accepted');
	$('#sample-run').show();
    console.log($('html, body').get(0));
    $("html, body").animate({
        scrollTop: $('html, body').get(0).scrollHeight
    }, 5000);
});


const codeEditor = document.querySelector("#code");
if(codeEditor) {
    codeEditor.addEventListener('keydown', (e) => {
        if(e.keyCode === 9) {
            e.preventDefault();
            codeEditor.setRangeText(
                "  ",
                codeEditor.selectionStart,
                codeEditor.selectionStart,
                "end"
            );
        }
    });
}
