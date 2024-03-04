let eColor = document.getElementById( 'defalt_color' ).value
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
    let changedColor = document.getElementById("editor_color").value;
    editor.setTheme(changedColor);
    document.getElementById( 'defalt_color' ).value = changedColor;
      };

function select() {
    let in_out = document.getElementById("testcase").value.split("//");
    
        document.getElementById("input_ex").innerHTML = in_out[0];
        document.getElementById("output_ex").innerHTML = in_out[1];
        document.getElementById("selected_n").innerHTML = in_out[2];
      };


let elem = document.getElementById('editor');
let elem_Y = elem.getBoundingClientRect().top + window.scrollY;
window.addEventListener("load", function() {
        if (document.getElementById( 'backup' ).value != '') {
            scrollTo({top: elem_Y, left: 0, behavior: "instant",});
        }
    });