// Check if a radio button is selected and show and hide the warning appropriately
function radio_is_checked() {
    var input_ids = ["#QA", "#QB", "#QC", "#QD"];
    for (i=0; i<input_ids.length; i++){
        if ($(input_ids[i]).is(':checked')) {
            $("#radio_selection_warning").hide()
            return true;
        }
    }
    $("#radio_selection_warning").show()
    return false
}


// Checks if the user answered correctly and visually displays the correct answer
function check_answer() {
    var input_ids = ["#QA", "#QB", "#QC", "#QD"];
    user_choice = "";
    for (i=0; i<input_ids.length; i++){
        if ($(input_ids[i]).is(':checked')) {
            user_choice = $(input_ids[i]).val();
            break;
        }
    }

    // Perform an AJAX request to check the answer for the current question number
    // The answers for other questions is not shown until the user submits their selection on that question
    var url = "/get_question_answer";
    data = {question_num: question_num};
    $.ajax({
        url: url,
        type: 'POST',
        contentType: 'application/json;charset=UTF-8',
        data: JSON.stringify(data, null, '\t'),
        success: function(data) {
            correct_answer = data
            console.log("Correct choice is:", correct_answer, ",user chose:", user_choice);

            // HTML Colors for correct and wrong answers
            var correct_color = "#6C9A33"
            var wrong_color = "#672770"

            // Change the color of the choices to suggest (in)/correctness
            if (user_choice == correct_answer) {
                console.log("Correct Answer!");
                $('#Q'+correct_answer+'_label').after("<p id='feedback_id_correct' style='display:inline;margin-left:12px';><strong>Correct</strong></p>");
                $('#feedback_id_correct').css("color", correct_color);
            }
            else {
                console.log("Wrong Answer!");
                $('#Q'+user_choice+'_label').css("color", wrong_color);
                $('#Q'+user_choice+'_label').after("<p id='feedback_id_wrong' style='display:inline;margin-left:12px';><strong>Wrong</strong></p>");
                $('#feedback_id_wrong').css("color", wrong_color);
            }
            $('#Q'+correct_answer+'_label').css("color", correct_color);

            // Disable all the radio buttons
            $('input[type=radio').attr('disabled', true);

            // Change the text on the button
            $('#submit_answer').prop('value', 'Next');

            // Perform time measurement and record it in the database
            record_question_and_time(user_choice);
        },
        error: function(xhr, testStatus, errorThrown) {
            console.log("AJAX to get_question_answer() route failed!");
        }
    });
}

// Loads the next question in the list and updates the image, schema and SQL 
function load_next_question(schema_src, sql_src) {
    // Update the schema
    // var schema_iframe = $('.sql_schema_iframe');
    // schema_src = schema_src.replace("1", question_num.toString());
    // schema_iframe[0].src = schema_src;
    // $('.sql_schema_iframe').load(document.URL +  ' .sql_schema_iframe');

    // Update the SQL
    var sql_iframe = $('.sql_query_iframe');
    sql_src = sql_src.replace("1", question_num.toString());
    sql_iframe[0].src = sql_src;
    $('.sql_query_iframe').load(document.URL +  ' .sql_query_iframe');

    // Enable all radio buttons
    $('input[type=radio').attr('disabled', false);

    // Change the color of all choices to black
    $('#Qa_label').css("color", "black");
    $('#Qb_label').css("color", "black");
    $('#Qc_label').css("color", "black");
    $('#Qd_label').css("color", "black");

    $('#feedback_id_correct').remove();
    $('#feedback_id_wrong').remove();

    // Change the text on the button
    $('#submit_answer').prop('value', 'Submit');
}