"use strict;"
$('document').ready(function(){
    $('#submit_upload').click(function(event){
        event.preventDefault();
        $('#document').trigger('click');
    });

    $('#submit').click(function(){
        $('#file_upload_form').submit();
    });

});


const fileTempl = document.getElementById("file-template"),
  imageTempl = document.getElementById("image-template"),
  empty = document.getElementById("empty");

// use to store pre selected files
let FILES = {};

function get_content_size_str(content_size){
    var unit_limit = 1024
    unit_labels = {0: 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    var converted_size = content_size

    for (let i = 0; i < Object.keys(unit_labels).length; i++) {
      if( converted_size < unit_limit){
         return parseFloat(converted_size).toFixed(1)+unit_labels[i]
      }

      converted_size /= unit_limit
    }
    $.each(unit_labels, (unit_index, unit) => {

    })

}
// check if file is of type image and prepend the initialied
// template to the target element
function addFile(target, file) {
    if (file.size > parseFloat($('#content_size').val())) {
        $('#errors').removeClass("hidden");
        $('#errors').append("<div class=\"alert alert-info alert-dismissible fade show rounded-full shadow-md sm:w-2/3 lg:w-11/12\" role=\"alert\">"+
            "<span class=\"text-blue-500 float-left mr-2\">"+
                  "<svg fill=\"currentColor\""+
                       "viewBox=\"0 0 20 20\""+
                       "class=\"h-6 w-6\">"+
                      "<path fill-rule=\"evenodd\""+
                            "d=\"M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z\""+
                            "clip-rule=\"evenodd\"></path>"+
                  "</svg>"+
              "</span>"+
                "<span class=\"text-gray-700 font-bold\">"+
                    file.name+" is too large. Limit the file size to "+get_content_size_str(parseFloat($('#content_size').val()))
                +"</span>"+
              "<button type=\"button\" class=\"close hover:no-outline no-outline focus:outline-none focus:shadow-outline\" data-dismiss=\"alert\" aria-label=\"Close\">"+
              "<span aria-hidden=\"true\">&times;</span>"+
              "</button>"+
            "</div>")
        return;
    }
  const isImage = file.type.match("image.*"),
    objectURL = URL.createObjectURL(file);

  const clone = isImage
    ? imageTempl.content.cloneNode(true)
    : fileTempl.content.cloneNode(true);

  clone.querySelector("h1").textContent = file.name;
  clone.querySelector("li").id = objectURL;
  clone.querySelector(".delete").dataset.target = objectURL;
  clone.querySelector(".size").textContent =
    file.size > 1024
      ? file.size > 1048576
        ? Math.round(file.size / 1048576) + "mb"
        : Math.round(file.size / 1024) + "kb"
      : file.size + "b";

  isImage &&
    Object.assign(clone.querySelector("img"), {
      src: objectURL,
      alt: file.name
    });

  empty.classList.add("hidden");
  target.prepend(clone);

  FILES[objectURL] = file;
}

const gallery = document.getElementById("gallery"),
  overlay = document.getElementById("overlay");

// click the hidden input of type file if the visible button is clicked
// and capture the selected files
const hidden = document.getElementById("document");
document.getElementById("button").onclick = () => hidden.click();
hidden.onchange = (e) => {
  for (const file of e.target.files) {
    addFile(gallery, file);
  }
};

// use to check if a file is being dragged
const hasFiles = ({ dataTransfer: { types = [] } }) =>
  types.indexOf("Files") > -1;

// use to drag dragenter and dragleave events.
// this is to know if the outermost parent is dragged over
// without issues due to drag events on its children
let counter = 0;

// reset counter and append file to gallery when file is dropped
function dropHandler(ev) {
  ev.preventDefault();
  for (const file of ev.dataTransfer.files) {
    addFile(gallery, file);
    overlay.classList.remove("draggedover");
    counter = 0;
  }
}

// only react to actual files being dragged
function dragEnterHandler(e) {
  e.preventDefault();
  if (!hasFiles(e)) {
    return;
  }
  ++counter && overlay.classList.add("draggedover");
}

function dragLeaveHandler(e) {
  1 > --counter && overlay.classList.remove("draggedover");
}

function dragOverHandler(e) {
  if (hasFiles(e)) {
    e.preventDefault();
  }
}

// event delegation to caputre delete events
// fron the waste buckets in the file preview cards
gallery.onclick = ({ target }) => {
  if (target.classList.contains("delete")) {
    const ou = target.dataset.target;
    document.getElementById(ou).remove(ou);
    gallery.children.length === 1 && empty.classList.remove("hidden");
    delete FILES[ou];
  }
};

// clear entire selection
document.getElementById("cancel").onclick = () => {
  while (gallery.children.length > 0) {
    gallery.lastChild.remove();
  }
  FILES = {};
  empty.classList.remove("hidden");
  gallery.append(empty);
};

document.getElementById("cancel").onclick = () => {
    if (gallery.children.length == 0){

    }
};