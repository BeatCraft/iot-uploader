let reloadTimer;

function isoDate(orig) {
  return orig.getFullYear() + "-"
      + (orig.getMonth()+1).toString().padStart(2, "0") + "-"
      + orig.getDate().toString().padStart(2, "0");
}

const params = new URL(location).searchParams;
let date = params.get("date");
if (!date) {
  const now = new Date();
  date = isoDate(now);
}

function resizeWindow() {
  const tc = document.getElementById("table-container");
  tc.style.height = window.innerHeight - 100 + 'px';
}

function resetCounts(counts) {
  const now = new Date();
  document.getElementById("query").innerHTML = "loaded: " + now.toLocaleString();

  // reset header color
  for (let i=0; i<24; i++) {
    document.getElementById(`header_${i}`).style.backgroundColor = null;
  }

  // header color
  if (isoDate(now) == date) {
    const hour = now.getHours();
    document.getElementById(`header_${hour}`).style.backgroundColor = "#AAFFAA";
  }

  sensors.forEach((s) => {
    const e_name = document.getElementById(`${s.sensor_name}_name`);
    const e_icon = document.getElementById(`${s.sensor_name}_icon`);
    const e_ts = document.getElementById(`${s.sensor_name}_ts`);

    if ((s.sensor_name in counts) && (counts[s.sensor_name].timestamp)) {
      const ts = counts[s.sensor_name].timestamp.substr(11);
      e_ts.innerHTML = ts;
      const diff = (now.getTime() - new Date(counts[s.sensor_name].timestamp).getTime()) / (60000);
      if (diff < 5) {
        e_icon.style.color = "#22DD22";
      } else {
        e_icon.style.color = "#FF7777";
      }
    } else {
      e_icon.style.color = "#FF7777";
    }

    for (let h=0; h<24; h++) {
      if ((s.sensor_name in counts) && (counts[s.sensor_name][h])) {
        document.getElementById(`${s.sensor_name}_${h}`).innerHTML = counts[s.sensor_name][h];
      } else {
        document.getElementById(`${s.sensor_name}_${h}`).innerHTML = "0";
      }
    }
  });
}

function loadCounts() {
  const url = `./uploadcounts/data/${date}`;
  fetch(url)
    .then((res) => {
      return res.json();
    })
    .then((data) => {
      console.log(data);
      resetCounts(data);
    });
}

function onChangeReloadSwitch() {
  if ($("#reloadSwitch").prop("checked")) {
    loadCounts();
    reloadTimer = setInterval(loadCounts, 60000);
  } else {
    clearInterval(reloadTimer);
  }
}

window.onload = function() {
  window.onresize = resizeWindow;

  let d0 = new Date(date);
  d0.setDate(d0.getDate() - 1);
  const bday = isoDate(d0);
  d0.setDate(d0.getDate() + 2);
  const nday = isoDate(d0);

  let backButton = $(`<a href="?date=${bday}" class="mr-2"><i class="bi-caret-left-square-fill" style="font-size: 1.5rem;"></i></a>`);
  backButton.insertBefore($("#auto-reload-ui"));

  $(`<span class="mr-2 text-primary font-weight-bold">${date}</span>`).insertBefore($("#auto-reload-ui"));

  let nextButton = $(`<a href="?date=${nday}" class="mr-3"><i class="bi-caret-right-square-fill" style="font-size: 1.5rem;"></i></a>`);
  nextButton.insertBefore($("#auto-reload-ui"));

  loadCounts();
  resizeWindow();
}

