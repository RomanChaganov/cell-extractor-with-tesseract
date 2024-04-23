var canvas;
var canvas1;
var blob;


function reader_onload(e)
{
  var byteArray = new Uint8Array(e.target.result);
  blob = new Blob([byteArray], { type: 'image/jpeg' });
  
  var url = URL.createObjectURL(blob);
  canvas.src = url;
}


function canvas_drop(e)
{
  e.preventDefault();
  var file = e.dataTransfer.files[0];
  var reader = new FileReader();
  
  if (!file.type.startsWith('image/')) {
    alert('Выбранный файл не является изображением!');
    return;
  }
  
  reader.onload = reader_onload;
  reader.readAsArrayBuffer(file);
}


function send_btn_click()
{
  if (!blob) {
    alert('Сначала загрузите изображение!');
    return;
  }
  
  var modes = document.getElementsByName('mode');
  var mode;
  
  for (var i = 0; i < modes.length; i++) {
    if (modes[i].checked) mode = modes[i].value;
  }
  
  var request = new XMLHttpRequest();
  request.overrideMimeType('image/jpeg');
  var fd = new FormData();
  fd.append('mode', mode);
  fd.append('file', blob);
  
  request.onload = function() {
    if (request.status == 200) {
      var file_blob = request.response;
      var url = URL.createObjectURL(file_blob);
      //if (!file_blob.type.startsWith('image/')) {
      //  console.log('Ответ не корректен!');
      //  console.log(file_blob.type);
      //  return;
      //}
      canvas1.src = url;
    }
  };
  
  request.onerror = function() {
      alert('Ошибка соединения');
  }
  
  request.responseType = 'blob';
  request.open('POST', '/upload');
  request.send(fd);
}


function start()
{
  var images = document.getElementsByClassName('scale_img');
  for (var i = 0; i < images.length; i++) {
    images[i].addEventListener('click', function() {
       this.classList.toggle('expanded');
    });
  }
  
  canvas = document.getElementById('canvas');
  canvas.addEventListener('dragover', function(e) {
    e.preventDefault();
  });
  
  canvas.addEventListener('drop', canvas_drop);
  send_btn = document.getElementById('send');
  send_btn.addEventListener('click', send_btn_click);
  
  canvas1 = document.getElementById('canvas1');
}