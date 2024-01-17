let reloadTimer;

function resizeWindow() {
  const tc = document.getElementById("table-container");
  tc.style.height = window.innerHeight - 100 + 'px';
}

function resetCounts(counts) {
  const now = new Date();
  document.getElementById("loaded").innerHTML = now.toLocaleString();

  const hour = now.getHours();
  document.getElementById(`header_${hour}`).style.backgroundColor = "#AAFFAA";

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
  const url = "./uploadcounts/data/2024-01-17";
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

  const query = document.getElementById("query");
  query.innerHTML = '<span id="loaded"></span><span id="auto-reload"></span>';

  loadCounts();
  resizeWindow();
}

