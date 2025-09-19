function getState(subKey) {
    const raw = localStorage.getItem('States');
    const parsed = raw ? JSON.parse(raw) : {};
    return parsed[subKey] || null;
}

function getAllStates() {
    const raw = localStorage.getItem('States');
    return raw ? JSON.parse(raw) : {};
}

function setState(subKey, value) {
    const raw = localStorage.getItem('States');
    const parsed = raw ? JSON.parse(raw) : {};
    parsed[subKey] = value;
    localStorage.setItem('States', JSON.stringify(parsed));
}

function removeState(subKey) {
    const raw = localStorage.getItem('States');
    if (!raw) return;
    const parsed = JSON.parse(raw);
    delete parsed[subKey];
    localStorage.setItem('States', JSON.stringify(parsed));
}

function syncOpen() {
    for (const element in getAllStates()) {
        let id = getState(element);

        if (id) {
            try {
                let el = document.getElementById(id).click();
            } catch (e) {}
        }
    }
}

const darkModeEnabled = document.body.dataset.darkMode === 'true';

const userAgent = navigator.userAgent || navigator.vendor || window.opera;
const isMobile = /android|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(userAgent.toLowerCase());

const all_classrooms = ["m3", "r3", "r4", "vp", "mp", "s3", "k2", "r2", "f1", "mf", "k1", "n2", "b1", "b2", "m1", "m2", "r1", "ge", "zg", "a1", "a2", "n1", "s1", "rač", "knj"]
const always_free = ["knj"]

document.addEventListener('DOMContentLoaded', function() {
    if (darkModeEnabled) {
        toggleDarkMode();
    }
    syncOpen();

    document.addEventListener('click', function(e) {
        let sidebar = document.getElementsByClassName('sidebar')[0];

        if (!sidebar.contains(e.target) && sidebar.classList.contains('expanded')) {
            toggleSidebar();
        }
    });

});

function selectGroup(group) {
    document.getElementById('selectedGroup').value = group;

    document.querySelectorAll('.option-group button').forEach(btn => {
        btn.classList.remove('selected');
    });
    event.target.classList.add('selected');
}

function getFreeForDate(date, schedule, hour) {
  if (hour == "PRE" || hour == "O") {
    return all_classrooms;
  }

  hour = Number(hour);

  const slovenianDays = [
    "Nedelja",
    "Ponedeljek",
    "Torek",
    "Sreda",
    "Četrtek",
    "Petek",
    "Sobota"
  ];

  const schoolYearStart = new Date(date.getFullYear(), 8, 1);

  if (date < schoolYearStart) {
    schoolYearStart.setFullYear(schoolYearStart.getFullYear() - 1);
  }

  const msPerWeek = 7 * 24 * 60 * 60 * 1000;
  const weekDiff = Math.floor((date - schoolYearStart) / msPerWeek);

  const weekType = (weekDiff % 2 === 0) ? "A" : "B";

  const dayName = slovenianDays[date.getDay()];

  const indices = [];
  for (let i = 0; i < schedule.length; i++) {
    const entry = schedule[i];
    if (entry[0] === weekType && entry[1] === dayName) {
      indices.push(i);
    }
  }

  const free = schedule[indices[hour]];
  if (!free) return all_classrooms;

  free.push(always_free);
  free[3] = [...free[3], ...free[4]];
  free.pop();

  return free[3];
}

function parseDate(dateStr) {
  const [datePart, timePart] = dateStr.split(' ');
  const [yearStr, dayStr, monthStr] = datePart.split('/');
  const [hourStr, minuteStr] = timePart.split(':');

  const year = parseInt(yearStr, 10);
  const day = parseInt(dayStr, 10);
  const month = parseInt(monthStr, 10) - 1;
  const hour = parseInt(hourStr, 10);
  const minute = parseInt(minuteStr, 10);

  return new Date(year, month, day, hour, minute);
}

function parseHour(dateStr) {
  const periods = [
    { label: 'PRE', start: '7:10', end: '7:55' },
    { label: 'O',   start: '10:25', end: '10:55' },
    { label: '6',   start: '12:40', end: '13:25' },
    { label: '7',   start: '13:30', end: '14:15' },
    { label: '8',   start: '14:20', end: '15:05' },
  ];

  date = parseDate(dateStr);

  function createDateWithTime(timeStr) {
    const [h, m] = timeStr.split(':').map(Number);
    const d = new Date(date);
    d.setHours(h, m, 0, 0);
    return d;
  }

  for (const period of periods) {
    const start = createDateWithTime(period.start);
    const end = createDateWithTime(period.end);

    if (date >= start && date <= end) {
      return period.label;
    }
  }

  return null;
}

function toggleDarkMode() {
    document.documentElement.classList.toggle('dark-mode');

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

            setState("sidebar", "sidebar-button");
        }
        else{
            document.querySelector('.main-sidebar-icon').textContent = 'menu';

            setState("sidebar", "");
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

var add_subject = document.getElementsByClassName("add-subject");

for (let i = 0; i < add_subject.length; i++){
    add_subject[i].addEventListener("click", function(event) {
        event.preventDefault();

        let element = document.getElementsByClassName("add-subject-form")[0];
        element.style.display = "grid";
        element.style.visibility = "visible";

        const free_cls = JSON.parse(element.dataset.frcls);

        const cls_opts = getFreeForDate(parseDate(this.dataset.date), free_cls, parseHour(this.dataset.date));

        // https://stackoverflow.com/questions/3364493/how-do-i-clear-all-options-in-a-dropdown-box
        function removeOptions(selectElement) {
            var i, L = selectElement.options.length - 1;
            for(i = L; i >= 0; i--) {
                selectElement.remove(i);
            }
        }

        const cls_sel = document.getElementById("classroom-selector");
        removeOptions(cls_sel);

        for (var i = 0; i < cls_opts.length; i++) {
            cls_sel.options[cls_sel.options.length] = new Option(cls_opts[i].toUpperCase(), cls_opts[i]);
        }

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

var people_amount = document.getElementsByClassName("people-amount");
if (people_amount) {
    for (var i = 0; i < people_amount.length; i++) {
        people_amount[i].addEventListener("click", function(event) {
            var nextSibling = event.target.nextSibling;
            while(nextSibling && nextSibling.nodeType != 1 && nextSibling.nodeName.toLowerCase() != "input") {
                nextSibling = nextSibling.nextSibling
            }

            nextSibling.focus();
        });
    }
}

var search = document.getElementsByClassName("tutorstvo-search")[0];

if (search) {
search.addEventListener("click", function(event) {
    event.preventDefault();

    let element = document.getElementsByClassName("search-results")[0];
    element.style.display = "grid";
    element.style.visibility = "visible";

    let main = document.getElementsByClassName("main")[0]
    main.style.filter = "blur(1.2px)";
    main.style.pointerEvents = "none";

    let top_bar = document.getElementsByClassName("topbar")[0]
    top_bar.style.filter = "blur(1.2px)";
    top_bar.style.pointerEvents = "none";

    let sidebar = document.getElementsByClassName("sidebar")[0]
    sidebar.style.filter = "blur(1.2px)";
    sidebar.style.pointerEvents = "none";

    document.getElementsByClassName("close-search-results")[0].style.visibility = "visible";

    setState("tutorstvo_search", "tutorstvo-search-button");
});

var closeSearch = document.getElementsByClassName("close-search-results")[0];

closeSearch.addEventListener("click", function(event) {
    let element = document.getElementsByClassName("search-results")[0];
    element.style.display = "none";
    element.style.visibility = "hidden";

    let main = document.getElementsByClassName("main")[0]
    main.style.filter = "none";
    main.style.pointerEvents = "auto";

    let top_bar = document.getElementsByClassName("topbar")[0]
    top_bar.style.filter = "none";
    top_bar.style.pointerEvents = "auto";

    let sidebar = document.getElementsByClassName("sidebar")[0]
    sidebar.style.filter = "none";
    sidebar.style.pointerEvents = "auto";

    document.getElementsByClassName("close-search-results")[0].style.visibility = "hidden";

    setState("tutorstvo_search", "");
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

    const firstOption = document.createElement('option');
    firstOption.setAttribute('value', '');
    firstOption.textContent = 'IZBERITE';
    newSelect.appendChild(firstOption);

    groups.forEach(function(group) {
        const option = document.createElement('option');
        option.setAttribute('value', group);
        option.textContent = group;
        newSelect.appendChild(option);
    });
    
    groupsContainer.appendChild(newSelect);

    newSelect.addEventListener('change', function() {
        if (this.value) {
            document.getElementById(`users-form-${id}`).submit();
        }
    });

}

function removeGroupBtn(id) {
    const groupsContainer = document.getElementById(`groups-container-${id}`);

    const selects = groupsContainer.getElementsByTagName('select');

    if (selects.length > 1) {
        groupsContainer.removeChild(selects[selects.length - 1]);
    }

    document.getElementById(`users-form-${id}`).submit();
}

var coll = document.getElementsByClassName("expand");

for (let i = 0; i < coll.length; i++) {
    coll[i].addEventListener("click", function() {
        this.classList.toggle("active");

        var icon = this.getElementsByClassName("expand-icon")[0];
        var content = this.nextElementSibling;

        icon.textContent = icon.textContent == 'v' ? '^': 'v';
        content.style.display = content.style.display == "none" ? "flex": "none";

        if (this.classList.contains('active')) {
            setState(coll[i].id.split('-button')[0], coll[i].id);
        }
        else {
            setState(coll[i].id.split('-button')[0], "");
        }
  });
}

function updateScale() {
    const vw = window.innerWidth;

    if (vw < 1700 && !isMobile) {
        const scale = vw / 1900;
        week = document.getElementsByClassName("week")[0]
        arrows = document.getElementsByClassName("tutorstvo-arrows")[0]

        if (week) {
        week.style.transform = `scale(${scale})`;
        arrows.style.right = "0";
        }
    }
}

window.addEventListener("resize", updateScale);
window.addEventListener("DOMContentLoaded", updateScale);

function linkSelectRedirect(element, argName) {
    value = element.value;

    if (value) {
        currentLocation = window.location.href;
        const param = `${argName}=${encodeURIComponent(value)}`;

        window.location.href = `${currentLocation}?${param}`;
    }
}

function hideElement(element) {
    try {
        element.style.visibility = 'hidden';
    } catch (e) {
        console.warn(`[hideElement] Couldn't hide element '${element}': ${e}`);
    }
}

function showElement(element) {
    try {
        element.style.visibility = 'visible';
    } catch (e) {
        console.warn(`[hideElement] Couldn't show element '${element}': ${e}`);
    }
}

function toggleVisibilityById(id) {
    const element = document.getElementById(id);
    if (element.style.visibility == 'hidden') {
        showElement(element);
    }
    else {
        hideElement(element);
    }
}

function showElementById(id) {
    const element = document.getElementById(id);
    showElement(element);
}

function hideElementById(id) {
    const element = document.getElementById(id);
    hideElement(element);
}

function showElementsByClassName(class_name) {
    const elements = document.getElementsByClassName(class_name);
    for (var i = 0; i < elements.length; i++) {
        showElement(elements[i]);
    }
}

function hideElementsByClassName(class_name) {
    const elements = document.getElementsByClassName(class_name);
    for (var i = 0; i < elements.length; i++) {
        hideElement(elements[i]);
    }
}

function applyBlurToBody() {
    document.body.classList.add('blur');
    document.body.classList.add('blur-move-fix');
}

function removeBlurFromBody() {
    document.body.classList.remove('blur');
    document.body.classList.remove('blur-move-fix');
}
