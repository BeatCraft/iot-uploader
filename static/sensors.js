function postSensorsCsv() {
  const sensors_csv = $("#sensors_csv").prop("files")[0];
  if (!sensors_csv) {
    return;
  }

  const reader = new FileReader();
  reader.onload = () => {
    const data = {
      sensors_csv: reader.result,
    };

    fetch("./sensors", {
      method: "POST",
      body: JSON.stringify(data),
      headers: {
        'Content-Type': 'application/json'
      },
    })
    .then(function() {
      location.reload();
    })
    .catch(function(reason) {
      console.log(reason);
    });
  };

  reader.readAsText(sensors_csv);
}

