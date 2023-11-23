const openButton = document.getElementById('openButton');
const closeButton = document.getElementById('closeButton');
const overlay = document.getElementById('overlay');
const div_edit = document.getElementById('div_edit');


function creata_label(value, container) {
  if (value == "external_id" || value == "id" || value == "service"){
    console.log("")
  }else{
    var novoLabel = document.createElement("label");
    novoLabel.setAttribute("for", "userName"); // Define o atributo "for" para associar com um campo de entrada específico
    novoLabel.setAttribute("class", "col-sm-3 control-label col-form-label");
    novoLabel.textContent = value+":"; // Define o texto do label
    container.appendChild(novoLabel)
  }
}

function create_imput_text(value, id_inputs, container) {
  var quebraDeLinha = document.createElement("br");
  var novoInput = document.createElement("input");

  if (id_inputs == "external_id" || id_inputs == "id" || id_inputs == "service"){
    novoInput.setAttribute("type", "hidden");
    novoInput.setAttribute("id", id_inputs);
    novoInput.setAttribute("value", value);
    novoInput.setAttribute("name", id_inputs);
    novoInput.setAttribute("class", "col-sm-8  control-label col-form-label")
    container.appendChild(novoInput);
  }else{
    novoInput.setAttribute("type", "text");
    novoInput.setAttribute("id", id_inputs);
    novoInput.setAttribute("value", value);
    novoInput.setAttribute("name", id_inputs);
    novoInput.setAttribute("class", "col-sm-8  control-label col-form-label")
    container.appendChild(novoInput);
    container.appendChild(quebraDeLinha);
    container.appendChild(quebraDeLinha);
  }
}

function create_new_section(){
  div_edit.removeChild(div_edit.firstChild)
  var section = document.createElement("section");
  section.setAttribute("id", "values_edit");
  div_edit.appendChild(section);
  return section
}

function close_window(){
  closeButton.addEventListener('click', () => {
    overlay.style.display = 'none';
  });
}


function editConfig(tab){
  var container = create_new_section()
  var table = $('#' + tab)[0];
  var external_id = document.getElementsByClassName("external_id")[0].innerHTML
  console.log(external_id)
  var name_edit = document.getElementById("name_edit");
  creata_label("service", container)
  create_imput_text(tab, "service", container)
  $(table).delegate('.tr_clone_edit', 'click', function () {
    var thisRow = $(this).closest("tr")[0];
    var elements = thisRow.querySelectorAll('td');
    elements.forEach(td => {
      const classList = td.classList;
      const className = Array.from(classList);
      if (className[0] != undefined){
        var value = thisRow.getElementsByClassName(className[0])[0].innerHTML
        creata_label(className[0], container)
        create_imput_text(value, className[0], container)
        if (className[0] == "name"){
          name_edit.textContent = tab + " - " + value
        }
      }
    });
    overlay.style.display = 'flex';
  });
}

var url_socket = document.currentScript.getAttribute("url");
console.log(url_socket)
var socket = io.connect(url_socket);

function add_config_by_filter(service){
    const table = document.getElementById('zero_config');
    var linhas = table.getElementsByTagName("tr");

    var dados = [];
    for (var i = 1; i < linhas.length; i++) {
          var linha = linhas[i];
          var celulas = linha.getElementsByTagName("td"); // Obtém todas as células da linha

          var dado = {};
          dado.id = celulas[0].innerText;
          dado.external_id = celulas[1].innerText;

          dados.push(dado);
      }
    console.log(socket)
    socket.emit('event_add_config_by_filter', { "dados": dados, "service": service });
  }