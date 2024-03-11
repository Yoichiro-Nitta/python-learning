let eColor = document.getElementById( 'default_color' ).value
let editor1 = ace.edit("editor1");
editor1.$blockScrolling = Infinity;
editor1.setTheme(eColor);
editor1.getSession().setMode("ace/mode/python");
editor1.setOptions({
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
      
let switchBtn = document.getElementById('show');
let edit = document.getElementById('editor2');
switchBtn.addEventListener('click', ()=> {
    edit.style.display ='';
    show.style.display ='none';
}, false);

window.addEventListener('pageshow', () => {
  if(performance.getEntriesByType("navigation")[0].type == 'back_forward'){
    const judgment = document.querySelectorAll("[data-abc]");
    judgment.forEach((element) => {
      element.className = '';
      });
      }
});