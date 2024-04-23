var canvas;
var ctx;
var blob;


function reader_onload(e)
{
  var byteArray = new Uint8Array(e.target.result);
  blob = new Blob([byteArray], { type: 'image/jpeg' });
  
  var url = URL.createObjectURL(blob);
  var image = new Image();
  image.onload = function(e) {
    canvas.width = image.width;
    canvas.height = image.height;   
    ctx.drawImage(image, 0, 0);
  }
  image.src = url;
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
  
  modes.forEach(function(element) {
    if (element.checked) mode = element.value;
  });
  
  var request = new XMLHttpRequest();
  request.overrideMimeType('text/plain');
  var fd = new FormData();
  fd.append('mode', mode);
  fd.append('file', blob);
  
  request.onerror = function() {
      alert('Ошибка соединения');
  }
  
  request.responseType = 'blob';
  request.open('POST', '/upload');
  request.send(fd);
}


function start()
{
  canvas = document.getElementById('canvas');
  ctx = canvas.getContext('2d');
  
  canvas.addEventListener('dragover', function(e) {
    e.preventDefault();
  });
  
  canvas.addEventListener('drop', canvas_drop);
  send_btn = document.getElementById('send');
  send_btn.addEventListener('click', send_btn_click);
}