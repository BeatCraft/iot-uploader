let reloadTimer;

function resizeWindow() {
  const tc = document.getElementById("table-container");
  tc.style.height = window.innerHeight - 100 + 'px';
}

function resetCounts(counts) {
  document.getElementById("loaded").innerHTML = (new Date()).toLocaleString();

  sensors.forEach((s) => {
    if ((s.sensor_name in counts) && (counts[s.sensor_name].timestamp)) {
      const ts = counts[s.sensor_name].timestamp.substr(11);
      document.getElementById(`${s.sensor_name}_ts`).innerHTML = ts;
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

