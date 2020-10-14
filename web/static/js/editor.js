
  function loadTab( config, schema, tab, boton, esarray)
  {
      $.getJSON(config, function(data)
      {
         editor = loadEditor( schema,tab,data, esarray , boton, config);
      }).fail(function() { editor = loadEditorDefault( schema, tab,esarray ,boton, config); });

      //return editor;
  }

  function CreateEvent(editorform,file,boton)
  {

    document.getElementById(boton).addEventListener('click',function()
        {
            var datos = editorform.getValue()
            $.ajax
            (
              {
                type: "POST",
                url: "/save",
                data: { filename: file , contenido: JSON.stringify(datos)},
                dataType: "text"
              }
            ).done(function( o ) { alert("OK PROGRAMACION GRABADA"); });
            // Get the value from the editor
            console.log(datos);
        });
  }

  function loadEditor( fichero, tab, jsondata, esarray , boton, config )
  {
    JSONEditor.defaults.options.theme = 'bootstrap4';
    JSONEditor.defaults.options.iconlib = "fontawesome5";
    // Initialize the editor
    editor = new JSONEditor(document.getElementById(tab),
    {

        // Enable fetching schemas via ajax
        ajax: true,

        // The schema for the editor
        schema:
        {

            $ref: fichero
        },

        // Seed the form with a starting value
        //startval: starting_value,

        // Disable additional properties
        no_additional_properties: true,
        disable_edit_json : !esarray,
        disable_collapse : true,
        disable_array_add : !esarray,
        disable_array_delete : !esarray,
        disable_properties : true,

        // Require all properties by default
        required_by_default: true,

        // Seed the form with a starting value
        startval: jsondata
    });

    // Listen for changes
    editor.on("change",  function()
    {
        // Do something...
    });

    CreateEvent(editor,config,boton)

    return editor;
  }

  function loadEditorDefault( fichero, tab, esarray, boton, config )
  {
    JSONEditor.defaults.options.theme = 'bootstrap4';
    JSONEditor.defaults.options.iconlib = "fontawesome5";
    // Initialize the editor
    editor = new JSONEditor(document.getElementById(tab),
    {

        // Enable fetching schemas via ajax
        ajax: true,

        // The schema for the editor
        schema:
        {
            $ref: fichero
        },

        // Seed the form with a starting value
        //startval: starting_value,

        // Disable additional properties
        no_additional_properties: true,
        disable_edit_json : !esarray,
        disable_collapse : true,
        disable_array_add : !esarray,
        disable_array_delete : !esarray,
        disable_properties : true,

        // Require all properties by default
        required_by_default: true,
    });

    // Listen for changes
    editor.on("change",  function()
    {
        // Do something...
    });

    CreateEvent(editor,config,boton)

    return editor;
  }
