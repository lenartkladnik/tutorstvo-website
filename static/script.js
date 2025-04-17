const darkModeEnabled = document.body.dataset.darkMode === 'true';

document.addEventListener('DOMContentLoaded', function() {    
    if (darkModeEnabled) {
        toggleDarkMode();
    }
});

function toggleDarkMode() {
    var elements = document.getElementsByTagName("*");
    
    for (let i = 0; i < elements.length; i++){
        var element = elements[i]
        element.classList.toggle("dark-mode");
    }
    
    var toggle = document.getElementById('toggle-dark-mode')
    if (document.body.dataset.darkMode === 'true'){
        toggle.src = "static/light_mode.svg"
        document.body.data_dark_mode = "true"

        document.querySelectorAll('previewbox-link').forEach(el => {
            el.style.setProperty('--pb-text-color', 'white');
            el.style.setProperty('--pb-text-color-light', 'white');
            el.style.setProperty('--pb-background-color', 'rgba(0, 0, 0, 0.3)');
        });
    }
    else{
        toggle.src = "static/dark_mode.svg"
        document.body.data_dark_mode = "false"
        
        document.querySelectorAll('previewbox-link').forEach(el => {
            el.style.setProperty('--pb-text-color', 'white');
            el.style.setProperty('--pb-text-color-light', 'white');
            el.style.setProperty('--pb-background-color', 'rgba(0, 0, 0, 0.1)');
        });
    }
}

// https://stackoverflow.com/questions/10596417/is-there-a-way-to-get-element-by-xpath-using-javascript-in-selenium-webdriver
function getElementByXpath(path) {
    return document.evaluate(path, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
}

window.onload = function () {
    let sidebar = document.querySelector('.sidebar');
    sidebar.classList.toggle('collapsed');
    let sidebar_links =  document.getElementsByClassName('sidebar-link');
    let location = window.location.href.split('/');
    location = location[location.length - 1];

    for (let i = 0; i < sidebar_links.length; i++){
        if (sidebar_links[i].getAttribute('href') == location){
            sidebar_links[i].classList.add('sidebar-selected');
        }
    }
}

function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    if (sidebar){
        sidebar.classList.toggle('expanded');
        sidebar.classList.toggle('collapsed');
        if (sidebar.classList.contains('expanded')){
            document.querySelector('.main-sidebar-icon').textContent = 'arrow_back';
        }
        else{
            document.querySelector('.main-sidebar-icon').textContent = 'menu';
        }
    }
}


function applyDateSelector() {
    const currentYear = new Date().getFullYear(); 
    const input = document.getElementById("datetime");

    const isDarkMode = input.classList.contains("dark-mode");

    themeLink.href = isDarkMode
        ? "https://cdn.jsdelivr.net/npm/flatpickr/dist/themes/dark.css"
        : "https://cdn.jsdelivr.net/npm/flatpickr/dist/themes/light.css"; 

    flatpickr("#datetime", {
      enableTime: true,
      noCalendar: false, 
      dateFormat: "d/m H:i",
      time_24hr: true,
      defaultDate: "today",
      onChange: function(selectedDates, dateStr) {
        if (selectedDates.length > 0) {
          let date = selectedDates[0];
          let month = String(date.getMonth() + 1).padStart(2, "0");
          let day = String(date.getDate()).padStart(2, "0");
          let hours = String(date.getHours()).padStart(2, "0");
          let minutes = String(date.getMinutes()).padStart(2, "0");

          let fullDatetime = `${currentYear}/${day}/${month} ${hours}:${minutes}`;
          document.getElementById("fullDatetime").value = fullDatetime;

          console.log("Full Datetime:", fullDatetime);
        }
      }
    });
};

var add_subject = document.getElementsByClassName("add-subject")

for (let i = 0; i < add_subject.length; i++){
    add_subject[i].addEventListener("click", function(event) {
        event.preventDefault();

        let element = document.getElementsByClassName("add-subject-form")[0];
        element.style.display = "grid";
        element.style.visibility = "visible";
        console.log(element);
        
        buttons = document.getElementsByClassName("subject-form-button");
        for (let i = 0; i < buttons.length; i++){
            buttons[i].style.visibility = "visible";
            buttons[i].style.display = "block";
        }
        
        let main = document.getElementsByClassName("main")[0]
        main.style.filter = "blur(1.2px)";
        main.style.pointerEvents = "none";

        let top_bar = document.getElementsByClassName("topbar")[0]
        top_bar.style.filter = "blur(1.2px)";
        top_bar.style.pointerEvents = "none";
        
        let sidebar = document.getElementsByClassName("sidebar")[0]
        sidebar.style.filter = "blur(1.2px)";
        sidebar.style.pointerEvents = "none";

        document.getElementsByClassName("close-add-subject")[0].style.visibility = "visible";
        
        const currentYear = new Date().getFullYear();

        document.getElementById("fullDatetime").value = this.dataset.date;

        // flatpickr("#datetime", {
        //  enableTime: true,
        //  noCalendar: false, 
        //  dateFormat: "d/m H:i",
        //  time_24hr: true,
        //  defaultDate: "today",
        //  onChange: function(selectedDates, dateStr) {
        //    if (selectedDates.length > 0) {
        //      let date = selectedDates[0];
        //      let month = String(date.getMonth() + 1).padStart(2, "0");
        //      let day = String(date.getDate()).padStart(2, "0");
        //      let hours = String(date.getHours()).padStart(2, "0");
        //      let minutes = String(date.getMinutes()).padStart(2, "0");

        //      let fullDatetime = `${currentYear}/${day}/${month} ${hours}:${minutes}`;
        //      document.getElementById("fullDatetime").value = fullDatetime;

        //      console.log("Full Datetime:", fullDatetime);
        //    }
        //  }
        //});
    });
}

var close_add_subject = document.getElementsByClassName("close-add-subject")[0]

if (close_add_subject){
    close_add_subject.addEventListener("click", function(event) {
        event.preventDefault();

        let form = document.getElementById("subject-form");
        form.reset();

        let element = document.getElementsByClassName("add-subject-form")[0];
        element.style.display = "none";
        element.style.visibility = "hidden";
        
        buttons = document.getElementsByClassName("subject-form-button");
        for (let i = 0; i < buttons.length; i++){
            buttons[i].style.visibility = "hidden";
            buttons[i].style.display = "none";
        }

        let main = document.getElementsByClassName("main")[0];
        main.style.filter = "none";
        main.style.pointerEvents = "auto";

        let top_bar = document.getElementsByClassName("topbar")[0];
        top_bar.style.filter = "none";
        top_bar.style.pointerEvents = "auto";
        
        let sidebar = document.getElementsByClassName("sidebar")[0];
        sidebar.style.filter = "none";
        sidebar.style.pointerEvents = "auto";

        document.getElementsByClassName("close-add-subject")[0].style.visibility = "hidden";
    });
}

function registerInput(input){
    input.addEventListener('input', function () {
        const tempSpan = document.createElement('span');
        
        tempSpan.style.fontFamily = getComputedStyle(input).fontFamily;
        tempSpan.style.fontSize = getComputedStyle(input).fontSize;
        tempSpan.style.fontWeight = getComputedStyle(input).fontWeight;
        tempSpan.style.whiteSpace = 'nowrap';
        tempSpan.style.visibility = 'hidden';
        
        tempSpan.textContent = input.value || ' ';
    
        document.body.appendChild(tempSpan);
        
        input.style.width = `${tempSpan.offsetWidth || 5}px`;
        
        document.body.removeChild(tempSpan);
    });
}

inputs = document.getElementsByClassName("dynamicInput");

for (let i = 0; i < inputs.length; i++){
    input = inputs[i];
    
    registerInput(input);
}


const description = getElementByXpath("//textarea[contains(@class, 'description')]");
const charCount = document.getElementById("description-char-count");
if (description){
    description.addEventListener("input", () => {
        charCount.textContent = description.value.length;
    });
}

const addSubjectBtn = document.getElementById('addSubjectBtn');
const removeSubjectBtn = document.getElementById('removeSubjectBtn');
const subjectsContainer = document.getElementById('subjects-container');
const hold_subjects = document.getElementById('hold_subjects');

if (addSubjectBtn && removeSubjectBtn && subjectsContainer && hold_subjects){
    const subjects = eval(hold_subjects.value);

    addSubjectBtn.addEventListener('click', function() {
        const newSelect = document.createElement('select');
        newSelect.setAttribute('name', 'subjects[]');
        newSelect.setAttribute('class', darkModeEnabled ? 'element dark-mode': 'element');
        newSelect.setAttribute('required', '');
    
        subjects.forEach(function(subject) {
            const option = document.createElement('option');
            option.setAttribute('value', subject);
            option.textContent = subject;
            newSelect.appendChild(option);
        });
    
        subjectsContainer.appendChild(newSelect);
    });
    
    removeSubjectBtn.addEventListener('click', function() {
        const selects = subjectsContainer.getElementsByTagName('select');
        
        if (selects.length > 1) {
            subjectsContainer.removeChild(selects[selects.length - 1]);
        }
    });
}

function addGroupBtn(id) {
    const hold_groups = document.getElementById(`hold_groups-${id}`);
    const groups = eval(hold_groups.value);
    const groupsContainer = document.getElementById(`groups-container-${id}`);

    const newSelect = document.createElement('select');
    newSelect.setAttribute('name', 'groups[]');
    newSelect.setAttribute('class', darkModeEnabled ? 'element dark-mode': 'element');
    newSelect.setAttribute('style', 'width: 15ch; text-transform: none;');
    newSelect.setAttribute('required', '');
    
    groups.forEach(function(group) {
        const option = document.createElement('option');
        option.setAttribute('value', group);
        option.textContent = group;
        newSelect.appendChild(option);
    });
    
    groupsContainer.appendChild(newSelect);
  
}

function removeGroupBtn(id) {
    const groupsContainer = document.getElementById(`groups-container-${id}`);

    const selects = groupsContainer.getElementsByTagName('select');
        
    if (selects.length > 1) {
        groupsContainer.removeChild(selects[selects.length - 1]);
    }

}

var coll = document.getElementsByClassName("expand");

for (let i = 0; i < coll.length; i++) {
    coll[i].addEventListener("click", function() {
        this.classList.toggle("active");

        var icon = this.getElementsByClassName("expand-icon")[0];
        var content = this.nextElementSibling;

        icon.textContent = icon.textContent == 'v' ? '^': 'v';
        content.style.display = content.style.display == "none" ? "flex": "none";

  });
}

function updateScale() {
    const vw = window.innerWidth;

    if (vw < 1700) {
        const scale = vw / 1900;
        week = document.getElementsByClassName("week")[0]
        arrows = document.getElementsByClassName("tutorstvo-arrows")[0]

        week.style.transform = `scale(${scale})`;
        arrows.style.right = "0";
    }
}

window.addEventListener("resize", updateScale);
window.addEventListener("DOMContentLoaded", updateScale);
