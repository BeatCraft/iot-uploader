const params = new URL(document.location).searchParams;
const imageId = parseInt(params.get("image_id"));

const app = new PIXI.Application({
  view: document.getElementById('preview'),
  width: 640,
  height: 480,
});

class SelectionRect {
  static selected = null;

  constructor(app, _parent, name) {
    this.app = app;
    this._parent = _parent;
    this.name = name;
    this.x = 0;
    this.y = 0;
    this.w = 0;
    this.h = 0;
    this.grabOffset = { x: 0, y: 0 };
    this.handleSize = 5;
    this.resizeTag = "";
    this.resizeHandlers = {};

    this.app.renderer.events.cursorStyles["move"] = "move";
    this.app.renderer.events.cursorStyles["ew-resize"] = "ew-resize";
    this.app.renderer.events.cursorStyles["ns-resize"] = "ns-resize";
    this.app.renderer.events.cursorStyles["nesw-resize"] = "nesw-resize";
    this.app.renderer.events.cursorStyles["nwse-resize"] = "nwse-resize";

    this.graphics = new PIXI.Graphics();
    this.graphics.eventMode = 'static';
    this.graphics.cursor = 'move';
    this.graphics.setParent(this._parent);

    const text = new PIXI.Text(name, { fill: 0x00ff00, fontSize: 14 });
    text.x =  8;
    text.y =  8;
    this.graphics.addChild(text);

    this.graphics
      .on('pointerdown', (ev) => {
        this.onPointerDown(ev);
      })
      .on('pointerup', (ev) => {
        this.onPointerUp(ev);
      });

  }

  onPointerDown(ev) {
    //console.log("down " + i);
    if (SelectionRect.selected) {
      return;
    }

    SelectionRect.selected = this;
    this.grabOffset.x = this.graphics.x - (ev.client.x / scale);
    this.grabOffset.y = this.graphics.y - (ev.client.y / scale);
  }

  onPointerUp(ev) {
    //console.log("up " + i);
    SelectionRect.selected = null;
    this.resizeTag = "";
  }

  onPointerMove(ev) {
      if (this.resizeTag === "") {
        this.x = Math.round(ev.client.x / scale + this.grabOffset.x);
        this.y = Math.round(ev.client.y / scale + this.grabOffset.y);
      }
      if (this.resizeTag.includes("l")) {
        this.x = Math.round(ev.client.x / scale + this.grabOffset.x) - 2;
        this.w = this.graphics.x - this.x + this.w;
      }
      if (this.resizeTag.includes("r")) {
        this.w = Math.round(ev.global.x / scale - this.graphics.x) + 2;
      }
      if (this.resizeTag.includes("t")) {
        this.y = Math.round(ev.client.y / scale + this.grabOffset.y) -2;
        this.h = this.graphics.y - this.y + this.h;
      }
      if (this.resizeTag.includes("b")) {
        this.h = Math.round(ev.global.y / scale - this.graphics.y) + 2;
      }

      this.draw(this.x, this.y, this.w, this.h);
  }

  hide() {
    this.graphics.removeFromParent(this._parent);
  }

  draw(x, y, w, h) {
    this.x = x;
    this.y = y;
    this.w = w;
    this.h = h;

    this.graphics.setParent(this._parent);
    this.graphics.clear();
    this.graphics.x = x;
    this.graphics.y = y;
    this.graphics.hitArea = new PIXI.Rectangle(
        -this.handleSize, -this.handleSize,
        w + (2 * this.handleSize), h + (2 * this.handleSize)
    );

    this.graphics.lineStyle(1 / scale, 0x00ff00, 1, 1);
    this.graphics.drawRect(0, 0, w, h);

    this.makeResizeHandles(this.graphics, w, h);
  }

  makeResizeHandles(p, w, h) {
    const sz = this.handleSize / scale;

    const handleDefs = [
      {
        tag: "lt", cursor: "nwse-resize",
        x: -sz, y: -sz, w: sz*2, h: sz*2,
      },
      {
        tag: "rt", cursor: "nesw-resize",
        x: w-sz, y: -sz, w: sz*2, h: sz*2,
      },
      {
        tag: "lb", cursor: "nesw-resize",
        x: -sz, y: h-sz, w: sz*2, h: sz*2,
      },
      {
        tag: "rb", cursor: "nwse-resize",
        x: w-sz, y: h-sz, w: sz*2, h: sz*2,
      },
      {
        tag: "l", cursor: "ew-resize",
        x: -sz, y: sz, w: sz*2, h: h-sz,
      },
      {
        tag: "r", cursor: "ew-resize",
        x: w-sz, y: sz, w: sz*2, h: h-sz,
      },
      {
        tag: "t", cursor: "ns-resize",
        x: sz, y: -sz, w: w-sz, h: sz*2,
      },
      {
        tag: "b", cursor: "ns-resize",
        x: sz, y: h-sz, w: w-sz, h: sz*2,
      },
    ]

    handleDefs.forEach((def) => {
      let h = this.resizeHandlers[def.tag];
      if (h === undefined) {
        h = this.resizeHandlers[def.tag] = new PIXI.Graphics();
        h.eventMode = 'static';
        h.cursor = def.cursor;
        h.on('pointerdown', (ev) => {
          this.resizeTag = def.tag;
        });
        p.addChild(h);
      }

      h.clear();
      h.lineStyle(1, 0x00ff00, 1, 1);
      h.hitArea = new PIXI.Rectangle(def.x, def.y, def.w, def.h);
    });
  }

}

let previewSprite = initSprite(app);
let fullTexture;
let scale = 1;
let rangeRect = new SelectionRect(app, previewSprite, "range");
let offsetX = 0;
let offsetY = 0;

let selectionRects = [];
for (let i=0; i<setting.max_rects; i++) {
  selectionRects.push(new SelectionRect(app, previewSprite, `r${i}`));
}


function onChangeBasic() {
  const num = $("#num_rects").val();
  const angle = $("#rotation_angle").val();

  $("#num_rects_ro").val(num);
  $("#rotation_angle_ro").val(angle);

  for (let i=0; i<setting.max_rects; i++) {
    if (i < num) {
      $(`#r${i}`).removeClass("d-none");
      $(`#labeled_r${i}_label`).removeClass("d-none");
      $(`#labeled_r${i}`).removeClass("d-none");
    } else {
      $(`#r${i}`).addClass("d-none");
      $(`#labeled_r${i}_label`).addClass("d-none");
      $(`#labeled_r${i}`).addClass("d-none");
    }
  }

  drawPreview();

  $("#change-basic-modal").modal("hide");
  onChangeRect();
}


function onSubmit() {
  let data = { };
  let rect = "";
  let labeled_values = [];

  data.num_rects = $("#num_rects_ro").val();
  data.rotation_angle = $("#rotation_angle_ro").val();

  for (let i=0; i<data.num_rects; i++) {
    rect += $(`#r${i}_x`).val() + ","
         +  $(`#r${i}_y`).val() + ","
         +  $(`#r${i}_w`).val() + ","
         +  $(`#r${i}_h`).val() + ","
         +  $(`#r${i}_th`).val() + "\n";

    labeled_values.push($(`#labeled_r${i}`).val());
  }
  data.rect = rect;
  data.labeled_values = labeled_values;

  data.not_read = $("#not_read").prop("checked");
  data.labeled = $("#labeled").prop("checked");

  data.range_x = parseInt($("#range_x").val());
  data.range_y = parseInt($("#range_y").val());
  data.range_w = parseInt($("#range_w").val());
  data.range_h = parseInt($("#range_h").val());

  console.log(data);

  const wifc = $("#wifc").prop("files")[0];
  if (wifc) {
    console.log(wifc);
    const reader = new FileReader();
    reader.onload = () => {
      data.wifc = reader.result;
      postMeterSetting(data)
    };
    reader.readAsText(wifc);
  } else {
    postMeterSetting(data)
  }
}

function postMeterSetting(data) {
  $.ajax({
    type: "POST",
    url: `/tools/readingsetting?image_id=${imageId}`,
    cache: false,
    data: JSON.stringify(data),
    dataType: "json",
  })
  .done(function() {
    $("#result").text("Done");
    $("#save").prop('disabled', true);
  })
  .fail(function(jqxhr) {
    $("#result").text("Error");
    console.log(jqxhr);
  });
}

function onTest() {
  $.ajax({
    type: "GET",
    url: `/tools/readingsetting/test?image_id=${imageId}`,
    cache: false,
  })
  .done(function(data) {
    $("#result").text(data);
  })
  .fail(function(jqxhr) {
    $("#result").text("Error");
    console.log(jqxhr);
  });
}

function onClickTab(event) {
  drawPreview(event.target.id);
  drawRects(event.target.id);
}

function onChangeRect() {
  if ($("#range-tab").hasClass("active")) {
    drawRects("range-tab");
  } else {
    drawRects("rects-tab");
  }

  $("#save").prop('disabled', false);
}

function onChangeUploadRect() {
  const path = $("#upload-rect").prop("files")[0];
  const reader = new FileReader();
  reader.onload = () => {
    const lines = reader.result.split(/\r\n|\n/);
    for (let i=0; i<lines.length; i++) {
      const values = lines[i].split(",");

      $(`#r${i}_x`).val(values[0]);
      $(`#r${i}_y`).val(values[1]);
      $(`#r${i}_w`).val(values[2]);
      $(`#r${i}_h`).val(values[3]);
      $(`#r${i}_th`).val(values[4]);
    }

    drawRects("rects-tag");
    $("#save").prop('disabled', false);
  };

  reader.readAsText(path);
}

function onChangeWifc() {
  $("#save").prop('disabled', false);
}

function onChangeLabeled() {
  if ($("#labeled").prop("checked")) {
    for (let i=0; i<setting.max_rects; i++) {
      $(`#labeled_r${i}`).prop("disabled", false);
    }
  } else {
    for (let i=0; i<setting.max_rects; i++) {
      $(`#labeled_r${i}`).prop("disabled", true);
    }
  }
  $("#save").prop('disabled', false);
}

function initParams() {
  $("#num_rects_ro").val(setting.num_rects);
  $("#num_rects").val(setting.num_rects);
  $("#rotation_angle_ro").val(setting.rotation_angle);
  $("#rotation_angle").val(setting.rotation_angle);

  for (let i=0; i<setting.max_rects; i++) {
    if (i < setting.num_rects) {
      $(`#r${i}_x`).val(setting.rects[i][0]);
      $(`#r${i}_y`).val(setting.rects[i][1]);
      $(`#r${i}_w`).val(setting.rects[i][2]);
      $(`#r${i}_h`).val(setting.rects[i][3]);
      $(`#r${i}_th`).val(setting.rects[i][4]);
      $(`#labeled_r${i}`).val(setting.labeled_values[i]);

    } else {
      $(`#r${i}_x`).val(i * 10);
      $(`#r${i}_y`).val(480);
      $(`#r${i}_w`).val(50);
      $(`#r${i}_h`).val(50);
      $(`#r${i}_th`).val(200);
      $(`#labeled_r${i}`).val(0);
    }

    if (setting.labeled) {
      $(`#labeled_r${i}`).prop("disabled", false);
    } else {
      $(`#labeled_r${i}`).prop("disabled", true);
    }
  }

  $("#range_x").val(setting.range_x);
  $("#range_y").val(setting.range_y);
  $("#range_w").val(setting.range_w);
  $("#range_h").val(setting.range_h);

  $("#not_read").prop("checked", setting.not_read);
  $("#labeled").prop("checked", setting.labeled);
}

function initSprite(app) {
  const sprite = new PIXI.Sprite();
  sprite.eventMode = 'static';
  sprite
    .on('globalpointermove', (ev) => {
      const selected = SelectionRect.selected;
      if (!selected) {
        return;
      }

      selected.onPointerMove(ev);

      if (selected.name === "range") {
        $(`#${selected.name}_x`).val(selected.x);
        $(`#${selected.name}_y`).val(selected.y);
        $(`#${selected.name}_w`).val(selected.w);
        $(`#${selected.name}_h`).val(selected.h);
      } else {
        $(`#${selected.name}_x`).val(selected.x + offsetX);
        $(`#${selected.name}_y`).val(selected.y + offsetY);
        $(`#${selected.name}_w`).val(selected.w);
        $(`#${selected.name}_h`).val(selected.h);
      }

      $("#save").prop('disabled', false);
    })

  app.stage.addChild(sprite);
  return sprite
}

function loadImage() {
  PIXI.Texture.fromURL(imageUrl).then((texture) => {
    fullTexture = texture;
    drawPreview("rects-tab");
    drawRects("rects-tab");
  });

}

function drawPreview(tabName=undefined) {
  if (!tabName) {
    if ($("#range-tab").hasClass("active")) {
      tabName = "range-tab";
    } else {
      tabName = "rects-tab";
    }
  }

  const origW = fullTexture.width;
  const origH = fullTexture.height;
  let trimW = fullTexture.width;
  let trimH = fullTexture.height;
  let rotate = 0;

  const angle = $("#rotation_angle_ro").val();
  if (angle === "90") {
    rotate = 2;
    trimW = fullTexture.height;
    trimH = fullTexture.width;
  } else if (angle === "180") {
    rotate = 4;
  } else if (angle === "270") {
    rotate = 6;
    trimW = fullTexture.height;
    trimH = fullTexture.width;
  }

  if (tabName === "range-tab") {
    scale = Math.min(640 / trimW, 480 / trimH);
    previewSprite.scale.x = scale;
    previewSprite.scale.y = scale;
    previewSprite.texture = new PIXI.Texture(
      fullTexture.baseTexture,
      new PIXI.Rectangle(0, 0, origW, origH),
      new PIXI.Rectangle(0, 0, origW, origH),
      new PIXI.Rectangle(0, 0, trimW, trimH),
      rotate
    );

  } else {
    scale = 1;
    previewSprite.scale.x = scale;
    previewSprite.scale.y = scale;

    const centerX = parseInt($("#range_x").val()) + Math.floor(parseInt($("#range_w").val()) / 2);
    const centerY = parseInt($("#range_y").val()) + Math.floor(parseInt($("#range_h").val()) / 2);

    offsetX = centerX - app.screen.width / 2;
    offsetX = Math.max(offsetX, 0);
    offsetX = Math.min(offsetX, origW - app.screen.width);
    offsetY = centerY - app.screen.height / 2;
    offsetY = Math.max(offsetY, 0);
    offsetY = Math.min(offsetY, origH - app.screen.height);

    previewSprite.texture = new PIXI.Texture(
      fullTexture.baseTexture,
      new PIXI.Rectangle(0, 0, origW, origH),
      new PIXI.Rectangle(0, 0, origW, origH),
      new PIXI.Rectangle(-offsetX, -offsetY, trimW, trimH),
      rotate
    );
  }
}

function drawRects(tabName) {
  if (tabName === "range-tab") {
    const x = parseInt($("#range_x").val());
    const y = parseInt($("#range_y").val());
    const w = parseInt($("#range_w").val());
    const h = parseInt($("#range_h").val());
    rangeRect.draw(x, y, w, h);

    for (let i=0; i<selectionRects.length; i++) {
      selectionRects[i].hide();
    }

  } else {
    for (let i=0; i<selectionRects.length; i++) {
      if (i >= $("#num_rects_ro").val()) {
        selectionRects[i].hide();
        continue;
      }
      const x = parseInt($(`#r${i}_x`).val()) - offsetX;
      const y = parseInt($(`#r${i}_y`).val()) - offsetY;
      const w = parseInt($(`#r${i}_w`).val());
      const h = parseInt($(`#r${i}_h`).val());
      selectionRects[i].draw(x, y, w, h);
    }

    rangeRect.hide();
  }
}

function initPreview() {
  loadImage();
}

$(function () {
  $("#auto-reload-ui").addClass("d-none");

  $("#change-basic-ok").click(onChangeBasic);
  $("#save").click(onSubmit);
  $("#test").click(onTest);

  $("#rects-tab").click(onClickTab);
  $("#range-tab").click(onClickTab);

  $(".dmrect").each(() => {
    $(this).on('input', onChangeRect);
  });

  $("#upload-rect").change(onChangeUploadRect);
  $("#wifc").change(onChangeWifc);

  $("#labeled").change(onChangeLabeled);

  initParams();
  initPreview();
});

