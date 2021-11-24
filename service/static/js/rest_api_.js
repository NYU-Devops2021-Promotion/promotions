$(function () {
    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************
    document.getElementById("promotion_category").selectedIndex = -1;

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#promotion_id").val(res.product_id);
        $("#promotion_name").val(res.product_name);
        //$("#promotion_category").val(res.category);
        $("#promotion_amount").val(res.amount);
        $("#promotion_from_date").val(res.from_date);
        $("#promotion_to_date").val(res.to_date);

    }

    /// Clears all form fields
    function clear_form_data() {
        $("#promotion_id").val("");
        $("#promotion_name").val("");
        $("#promotion_category").val("");
        $("#promotion_amount").val("");
        $("#promotion_from_date").val("");
        $("#promotion_to_date").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a promotion
    // ****************************************

    $("#create-btn").click(function () {
        var id = parseInt($("#promotion_id").val());
        var name = $("#promotion_name").val();
        var category = $("#promotion_category").val();
        var amount = parseInt($("#promotion_amount").val());
        var description = $("#promotion_description").val();
        var from_date = ($("#promotion_from_date").val());
        var to_date = ($("#promotion_to_date").val());

        console.log(id, name, from_date, to_date);
        var data = {
            'product_id': id,
            "product_name": name,
            "category": category,
            "amount": amount,
            "description": description,
            "from_date": from_date,
            "to_date": to_date,
        };

        var ajax = $.ajax({
            type: "POST",
            url: "/promotions",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a promotion
    // ****************************************

    $("#update-btn").click(function () {

        var id = $("#promotion_id").val();
        var name = $("#promotion_name").val();
        var category = $("#promotion_category").val();
        var from_date = new Date($("#promotion_from_date").val());
        var to_date = new Date($("#promotion_to_date").val());
        alert(from_date, to_date);

        var data = {
            'product_id': id,
            "product_name": name,
            "category": category,
            "from_date": from_date,
            "to_date": to_date,
        };
        var ajax = $.ajax({
                type: "PUT",
                url: "/promotions/" + id,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a promotion
    // ****************************************

    $("#retrieve-btn").click(function () {
        var id = $("#promotion_id").val();

        var ajax = $.ajax({
            type: "GET",
            url: "/promotions/" + id,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a promotion
    // ****************************************

    $("#delete-btn").click(function () {

        var id = $("#promotion_id").val();
         
        var ajax = $.ajax({
            type: "DELETE",
            url: "/promotions/" + id,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("promotion has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#promotion_id").val("");
        clear_form_data()
    });

    // ****************************************
    // Search for a promotion
    // ****************************************

    $("#search-btn").click(function () {
        var id = $("#promotion_id").val();
        var name = $("#promotion_name").val();
        var category = $("#promotion_category").val();
        var from_date = $("#promotion_from_date").val();
        var to_date = $("#promotion_to_date").val();

        var queryString = ""
        if (id) {
            queryString += 'product_id=' + id
        }
        if (name) {
            queryString += '&product_name=' + name
        }
        if (category) {
            queryString += '&category=' + category
        }
        if (from_date) {
            queryString += '&from_date=' + from_date
        }
        if (to_date) {
            queryString += '&to_date=' + to_date
        }
        

        var ajax = $.ajax({
            type: "GET",
            url: "/promotions?" + queryString,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            $("#search_results").append('<table class="table-striped" cellpadding="10">');
            var header = '<tr>'
            header += '<th style="width:20%">ID</th>'
            header += '<th style="width:20%">Name</th>'
            header += '<th style="width:20%">Category</th>'
            header += '<th style="width:30%">From</th>'
            header += '<th style="width:30%">To</th></tr>'
            $("#search_results").append(header);
            var firstpromotion = "";
            for(var i = 0; i < res.length; i++) {
                var promotion = res[i];
                var row = "<tr><td>"+promotion.product_id+"</td><td>"+promotion.product_name+"</td><td>"+promotion.category+"</td><td>"+promotion.from_date+"</td><td>"+promotion.to_date+"</td></tr>";
                $("#search_results").append(row);
                if (i == 0) {
                    firstpromotion = promotion;
                }
            }

            $("#search_results").append('</table>');

            // copy the first result to the form
            if (firstpromotion != "") {
                update_form_data(firstpromotion)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

})
