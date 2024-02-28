let editor = ace.edit("editor");
editor.$blockScrolling = Infinity;
editor.setTheme("ace/theme/monokai");
editor.getSession().setMode("ace/mode/python");
editor.setOptions({
    enableBasicAutocompletion: true,
    enableSnippets: true,
    enableLiveAutocompletion: false
  });
  let editor2 = ace.edit("editor2");
editor2.$blockScrolling = Infinity;
editor2.setTheme("ace/theme/monokai");
editor2.getSession().setMode("ace/mode/python");
editor2.setOptions({
    enableBasicAutocompletion: true,
    enableSnippets: true,
    enableLiveAutocompletion: false
  });