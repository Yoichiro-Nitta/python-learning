let editor = ace.edit("editor");
editor.$blockScrolling = Infinity;
editor.setTheme("ace/theme/monokai");
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

    let elem = document.getElementById('editor');
    let elem_Y = elem.getBoundingClientRect().top + window.pageYOffset;
window.addEventListener("load", function() {
        if (document.getElementById( 'backup' ).value != '') {
            scrollTo({top: elem_Y, left: 0, behavior: "instant",});
        }
    });