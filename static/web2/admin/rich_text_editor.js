(function () {
  function ready(fn) {
    if (document.readyState !== "loading") {
      fn();
    } else {
      document.addEventListener("DOMContentLoaded", fn);
    }
  }

  function button(label, title, command, value) {
    var btn = document.createElement("button");
    btn.type = "button";
    btn.textContent = label;
    btn.title = title;
    btn.dataset.command = command;
    if (value) {
      btn.dataset.value = value;
    }
    return btn;
  }

  function select(title, options) {
    var field = document.createElement("select");
    field.title = title;
    options.forEach(function (item) {
      var option = document.createElement("option");
      option.value = item[0];
      option.textContent = item[1];
      field.appendChild(option);
    });
    return field;
  }

  function separator() {
    var item = document.createElement("span");
    item.className = "rich-text-separator";
    return item;
  }

  function sync(textarea, editor) {
    textarea.value = editor.innerHTML;
  }

  function createEditor(textarea) {
    if (textarea.dataset.richTextReady === "1") {
      return;
    }
    textarea.dataset.richTextReady = "1";

    var wrapper = document.createElement("div");
    wrapper.className = "rich-text-editor";

    var toolbar = document.createElement("div");
    toolbar.className = "rich-text-toolbar";

    var format = select("Text format", [
      ["<p>", "Paragraph"],
      ["<h1>", "Heading 1"],
      ["<h2>", "Heading 2"],
      ["<h3>", "Heading 3"],
      ["<h4>", "Heading 4"],
      ["<blockquote>", "Quote"],
      ["<pre>", "Code block"]
    ]);

    var fontSize = select("Font size", [
      ["", "Size"],
      ["2", "Small"],
      ["3", "Normal"],
      ["4", "Medium"],
      ["5", "Large"],
      ["6", "Extra Large"]
    ]);

    toolbar.appendChild(format);
    toolbar.appendChild(fontSize);
    toolbar.appendChild(separator());
    toolbar.appendChild(button("B", "Bold", "bold"));
    toolbar.appendChild(button("I", "Italic", "italic"));
    toolbar.appendChild(button("U", "Underline", "underline"));
    toolbar.appendChild(button("S", "Strike", "strikeThrough"));
    toolbar.appendChild(button("X2", "Subscript", "subscript"));
    toolbar.appendChild(button("X^2", "Superscript", "superscript"));
    toolbar.appendChild(separator());
    toolbar.appendChild(button("UL", "Bullet list", "insertUnorderedList"));
    toolbar.appendChild(button("OL", "Numbered list", "insertOrderedList"));
    toolbar.appendChild(button("<", "Outdent", "outdent"));
    toolbar.appendChild(button(">", "Indent", "indent"));
    toolbar.appendChild(separator());
    toolbar.appendChild(button("Left", "Align left", "justifyLeft"));
    toolbar.appendChild(button("Center", "Align center", "justifyCenter"));
    toolbar.appendChild(button("Right", "Align right", "justifyRight"));
    toolbar.appendChild(button("Justify", "Justify text", "justifyFull"));
    toolbar.appendChild(separator());
    toolbar.appendChild(button("Link", "Insert link", "createLink"));
    toolbar.appendChild(button("Unlink", "Remove link", "unlink"));
    toolbar.appendChild(button("Line", "Horizontal line", "insertHorizontalRule"));
    toolbar.appendChild(separator());
    toolbar.appendChild(button("Undo", "Undo", "undo"));
    toolbar.appendChild(button("Redo", "Redo", "redo"));
    toolbar.appendChild(button("Clear", "Remove formatting", "removeFormat"));

    var textColor = document.createElement("input");
    textColor.type = "color";
    textColor.title = "Text color";
    textColor.value = "#111111";
    toolbar.appendChild(textColor);

    var highlightColor = document.createElement("input");
    highlightColor.type = "color";
    highlightColor.title = "Highlight color";
    highlightColor.value = "#fff3a3";
    toolbar.appendChild(highlightColor);

    var editor = document.createElement("div");
    editor.className = "rich-text-canvas";
    editor.contentEditable = "true";
    editor.innerHTML = textarea.value || "";

    textarea.style.display = "none";
    textarea.parentNode.insertBefore(wrapper, textarea);
    wrapper.appendChild(toolbar);
    wrapper.appendChild(editor);

    format.addEventListener("change", function () {
      editor.focus();
      document.execCommand("formatBlock", false, format.value);
      sync(textarea, editor);
    });

    fontSize.addEventListener("change", function () {
      if (!fontSize.value) {
        return;
      }
      editor.focus();
      document.execCommand("fontSize", false, fontSize.value);
      sync(textarea, editor);
      fontSize.value = "";
    });

    toolbar.addEventListener("click", function (event) {
      var target = event.target;
      if (!target.dataset.command) {
        return;
      }
      editor.focus();
      var value = target.dataset.value || null;
      if (target.dataset.command === "createLink") {
        value = window.prompt("Enter URL", "https://");
        if (!value) {
          return;
        }
      }
      document.execCommand(target.dataset.command, false, value);
      sync(textarea, editor);
    });

    textColor.addEventListener("input", function () {
      editor.focus();
      document.execCommand("foreColor", false, textColor.value);
      sync(textarea, editor);
    });

    highlightColor.addEventListener("input", function () {
      editor.focus();
      document.execCommand("hiliteColor", false, highlightColor.value);
      sync(textarea, editor);
    });

    ["input", "keyup", "paste", "blur"].forEach(function (eventName) {
      editor.addEventListener(eventName, function () {
        window.setTimeout(function () {
          sync(textarea, editor);
        }, 0);
      });
    });

    if (textarea.form) {
      textarea.form.addEventListener("submit", function () {
        sync(textarea, editor);
      });
    }
  }

  ready(function () {
    document.querySelectorAll("textarea.rich-text-source").forEach(createEditor);
  });
})();
