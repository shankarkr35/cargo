
    //  ----------------------- END Document type option ----------------------
    $(document).on("click", ".add_item_btn", function (e) {
        var index = parseInt(
            $(this)
                .parents("#mainItem")
                .find(".item_option")
                .last()
                .attr("data-id")
        );
        index++;
        console.log(index);
        //$(".add_item_btn").click(function(e){
        e.preventDefault();

        var html = "";
        html +=
            '<div id="show_item" class="item_option" data-id="' + index + '">';
        html += '<div class="row">';
        
        
        html += '<div class="col-md-6 mb-6">';
        html += '<input id="options' + index + '" Type="text" name="options[]" class="form-control txt_Search" placeholder="Options">';
        html += '<span class="text-danger font-weight-bold options-err" id="options-err"></span>';
        html += "</div>";
        
        html += '<div class="col-md-3 mb-3 d-grid">';
        html +=
            '<button class="btn btn-danger remove_item_btn">Remove</button>';
        html += "</div>";
        html += "</div>";
        html += "</div>";

        $("#mainItem").append(html);
    });

    $(document).on("click", ".remove_item_btn", function (e) {
        e.preventDefault();

        let row_item = $(this).parent().parent();
        $(row_item).remove();
    });
