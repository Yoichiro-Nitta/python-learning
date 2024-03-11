let eColor = document.getElementById( 'default_color' ).value
let editor = ace.edit("editor");
editor.$blockScrolling = Infinity;
editor.setTheme(eColor);
editor.getSession().setMode("ace/mode/python");
editor.setFontSize(14);
editor.setOptions({
        enableBasicAutocompletion: true,
        enableSnippets: true,
        enableLiveAutocompletion: false
      });
editor.getSession().on('change', function(){
        let textcode = editor.getSession().getValue();
        document.getElementById( 'text' ).value = textcode;});

function color() {
    let changedColor = document.getElementById("editor_color").value.split("//");
    editor.setTheme(changedColor[0]);
    document.getElementById( 'default_color' ).value = changedColor[0];
    let numColor = document.querySelectorAll('[data-color="num"]');
    let strColor = document.querySelectorAll('[data-color="str"]');
    let printColor = document.querySelectorAll('[data-color="print"]');
    let funcColor = document.querySelectorAll('[data-color="func"]');
    let defColor = document.querySelectorAll('[data-color="def"]');
    let bgColor = document.querySelectorAll('[data-color="bg"]');
    let mainColor = document.querySelectorAll('[data-color="main"]');
    let sideColor = document.querySelectorAll('[data-color="side"]');
    numColor.forEach(element => element.className = changedColor[1] + "num");
    strColor.forEach(element => element.className = changedColor[1] + "str");
    printColor.forEach(element => element.className = changedColor[1] + "print");
    funcColor.forEach(element => element.className = changedColor[1] + "func");
    defColor.forEach(element => element.className = changedColor[1] + "def");
    bgColor.forEach(element => element.className = changedColor[1] + "bg");
    mainColor.forEach(element => element.className = changedColor[1] + "main");
    sideColor.forEach(element => element.className = changedColor[1] + "side");
      };

let elem = document.getElementById('editor');
let elem_Y = elem.getBoundingClientRect().top + window.pageYOffset;
window.addEventListener("load", function() {
        if (document.getElementById( 'backup' ).value != '') {
            scrollTo({top: elem_Y, left: 0, behavior: "instant",});
        }
    });