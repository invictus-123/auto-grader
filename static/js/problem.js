const codeEditor = document.querySelector("#code");
if(codeEditor) {
    codeEditor.addEventListener('keydown', (e) => {
        if(e.keyCode === 9) {
            e.preventDefault();
            codeEditor.setRangeText(
                "\t",
                codeEditor.selectionStart,
                codeEditor.selectionStart,
                "end"
            );
        }
        else if(e.key == '(') {
            e.preventDefault();
            codeEditor.setRangeText(
                "()",
                codeEditor.selectionStart,
                codeEditor.selectionStart,
                "end"
            );
            codeEditor.selectionEnd = codeEditor.selectionStart - 1;
        }
        else if(e.key == '{') {
            e.preventDefault();
            codeEditor.setRangeText(
                "{}",
                codeEditor.selectionStart,
                codeEditor.selectionStart,
                "end"
            );
            codeEditor.selectionEnd = codeEditor.selectionStart - 1;
        }
        else if(e.key == '[') {
            e.preventDefault();
            codeEditor.setRangeText(
                "[]",
                codeEditor.selectionStart,
                codeEditor.selectionStart,
                "end"
            );
            codeEditor.selectionEnd = codeEditor.selectionStart - 1;
        }
        else if(e.key == '"') {
            e.preventDefault();
            codeEditor.setRangeText(
                '""',
                codeEditor.selectionStart,
                codeEditor.selectionStart,
                "end"
            );
            codeEditor.selectionEnd = codeEditor.selectionStart - 1;
        }
        else if(e.key == "'") {
            e.preventDefault();
            codeEditor.setRangeText(
                "''",
                codeEditor.selectionStart,
                codeEditor.selectionStart,
                "end"
            );
            codeEditor.selectionEnd = codeEditor.selectionStart - 1;
        }
    });
}
$("#code").keydown(function(e){
    if(e.keyCode == 13){
        var cursorPos = this.selectionStart;
        var curentLine = this.value.substr(0, this.selectionStart).split("\n").pop();
        var indent = curentLine.match(/^\s*/)[0];
        var value = this.value;
        var textBefore = value.substring(0,  cursorPos );
        var textAfter  = value.substring( cursorPos, value.length );
        e.preventDefault();
        this.value = textBefore + "\n" + indent + textAfter;
        setCaretPosition(this, cursorPos + indent.length + 1);
    }
});

function setCaretPosition(ctrl, pos) {
    if(ctrl.setSelectionRange){
        ctrl.focus();
        ctrl.setSelectionRange(pos,pos);
    }
    else if (ctrl.createTextRange) {
        var range = ctrl.createTextRange();
        range.collapse(true);
        range.moveEnd('character', pos);
        range.moveStart('character', pos);
        range.select();
    }
}
