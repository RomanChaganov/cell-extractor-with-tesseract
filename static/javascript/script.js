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
      // displayTables();
    }
  };

  request.onerror = function() {
      alert('Ошибка соединения');
  }
  
  request.responseType = 'blob';
  request.open('POST', '/upload');
  request.send(fd);
}

function displayTables() {
    var tablesContainer = document.getElementById('tables-container');
    tablesContainer.innerHTML = ''; // Очищаем предыдущие фотографии таблиц

    // Создаем и добавляем элементы <img> для каждой фотографии таблицы
    var tableIndex = 0;
    var tableFound = true;
    while (tableFound) {
      var tableImg = document.createElement('img');
      tableImg.src = '../../bin/rotated_tables/table' + tableIndex + '.jpg';
      tableImg.alt = 'Table ' + tableIndex;

      tableImg.onerror = function () {
        tableFound = false;
      };

      tablesContainer.appendChild(tableImg);
      tableIndex++;
    }
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