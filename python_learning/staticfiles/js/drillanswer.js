let eColor = document.getElementById( 'default_color' ).value
let editor = ace.edit("editor");
editor.$blockScrolling = Infinity;
editor.setTheme(eColor);
editor.getSession().setMode("ace/mode/python");
editor.setOptions({
    enableBasicAutocompletion: true,
    enableSnippets: true,
    enableLiveAutocompletion: false
  });
  let editor2 = ace.edit("editor2");
editor2.$blockScrolling = Infinity;
editor2.setTheme(eColor);
editor2.getSession().setMode("ace/mode/python");
editor2.setOptions({
    enableBasicAutocompletion: true,
    enableSnippets: true,
    enableLiveAutocompletion: false
  });