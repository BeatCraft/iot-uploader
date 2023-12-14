function showQuery() {
  $("#query").html(location.search.slice(1).replace("&", ", "));
}

function stateSwitch() {
  const params = new URL(location).searchParams;
  if (params.get("reload") > 0) {
    $("#reloadSwitch").prop("checked", true);
  }
}

function onChangeReloadSwitch() {
  const params = new URL(location).searchParams;

  if ($("#reloadSwitch").prop("checked")) {
    params.set("reload", 10);
  } else {
    params.delete("reload");
  }

  location.search = params.toString();
}

$(function() {
  showQuery();
  stateSwitch();

  $("#reloadSwitch").click(onChangeReloadSwitch);
});

