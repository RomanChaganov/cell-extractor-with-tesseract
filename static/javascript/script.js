var canvas;
var ctx;
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
  
  modes.forEach(function(element) {
    if (element.checked) mode = element.value;
  });
  
  var request = new XMLHttpRequest();
  request.overrideMimeType('application/zip');
  var fd = new FormData();
  fd.append('mode', mode);
  fd.append('file', blob);

  request.onload = function() {
    if(request.status == 200) {
      // Получаем ответ сервера в виде Blob (файла)
      var fileBlob = request.response;

      // Создаем ссылку для скачивания файла
      var url = URL.createObjectURL(fileBlob);
      var a = document.createElement('a');
      a.href = url;
      a.download = 'excel_tables.zip'; // Указываем имя файла для скачивания
      a.textContent = 'Скачать файл с распознанными таблицами';
      var downloadLinkContainer = document.getElementById('download-link');
      downloadLinkContainer.innerHTML = 'Таблицы: '; // Очищаем предыдущие ссылки, если они были
      downloadLinkContainer.appendChild(a);

      // Отображаем фотографии таблиц
      getTables();
    }
  };

  request.onerror = function() {
      alert('Ошибка соединения');
  }
  
  request.responseType = 'blob';
  request.open('POST', '/upload');
  request.send(fd);
}

function get_size(func) {
  let request = new XMLHttpRequest();
  request.overrideMimeType('application/json');
  request.onload = function() {
    if(request.status == 200) {
      let data = JSON.parse(request.responseText);
      func(data['size']);
    }
  }
  
  request.onerror = function() {
    alert('Не получил размер');
  }
  
  request.open('GET', '/get_size');
  request.send();
}

function displayTables(size) {
  let tablesContainer = document.getElementById('tables-container');
  tablesContainer.innerHTML = '';
  
  for (let i = 0; i < size; i++) {
    let filename = 'bin/rotated_tables/table' + i + '.jpg'
    let tableImg = document.createElement('img');
    tableImg.classList.add('expnd');
    tableImg.addEventListener('click', function() {
      this.classList.toggle('expanded');
    });
    tableImg.src = filename;
    tableImg.alt = 'Table ' + i;
    
    tablesContainer.appendChild(tableImg);
  }
}

function getTables() {
  get_size(displayTables);
}

function start()
{
  canvas = document.getElementById('img_main');
  
  canvas.addEventListener('click', function() {
      this.classList.toggle('expanded');
  });
  
  canvas.addEventListener('dragover', function(e) {
    e.preventDefault();
  });
  
  canvas.addEventListener('drop', canvas_drop);
  send_btn = document.getElementById('send');
  send_btn.addEventListener('click', send_btn_click);
}