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
