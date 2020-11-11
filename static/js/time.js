var start_time;         // The time the user starts the test
var cur_start_time;     // The time the user starts a question in the test

function start_timer() {
    start_time = new Date();
    cur_start_time = start_time;
    console.log("Started timer at:", start_time);
}

function record_question_and_time(user_choice) {
    var cur_time = new Date();
    delta_t = cur_time - cur_start_time;
    console.log("Elapsed time for question", question_num, "is:", delta_t);
    cur_start_time = cur_time;

    // Check if we are at the end of the test and record the total elapsed time
    if (question_num == total_num_questions) {
        var total_time = cur_start_time - start_time;
        console.log("The user completed the test in:", total_time)
    }

    // Perform an AJAX request to store the user answer and time for this question in the database
    var url = "/record_question_and_time";
    worker_id = localStorage.getItem("worker_id");
    data = {worker_id: worker_id, question_num: question_num, user_choice: user_choice, time_spent: delta_t};
    $.ajax({
        url: url,
        type: 'POST',
        dataType: 'application/json',
        data: {data: JSON.stringify(data)}
    });
}

function record_tutorial_time() {
    var cur_time = new Date();
    delta_t = cur_time - cur_start_time;
    console.log("Elapsed time for tutorial page", tutorial_page_num, "is:", delta_t);
    cur_start_time = cur_time;

    // Check if we are at the end of the test and record the total elapsed time
    if (question_num == total_num_tutorial_pages) {
        var total_time = cur_start_time - start_time;
        console.log("The user completed the tutorial in:", total_time)
    }

    // Perform an AJAX request to store the user answer and time for this question in the database
    var url = "/tutorial_record_time";
    worker_id = localStorage.getItem('worker_id');
    data = {tutorial_page_num: tutorial_page_num, time_spent: delta_t, worker_id: worker_id};
    $.ajax({
        url: url,
        type: 'POST',
        dataType: 'application/json',
        data: {data: JSON.stringify(data)}
    });
}

function new_question_start_time() {
    cur_start_time = new Date();
    console.log("User starts new question at:", cur_start_time);
}

// LEGACY
// Returns true if the time elapsed is greater or equal to the min_time_per_question required 
function elapsed_time() {
    var cur_time = new Date();
    delta_t = cur_time - cur_start_time;

    if (delta_t < min_time_per_question) {
        return false;
    }

    console.log("Elapsed time for question", question_num, "is:", delta_t);
    cur_start_time = cur_time;
    
    // Check if we are at the end of the test and record the total elapsed time
    if (question_num == total_num_questions) {
        var total_time = cur_start_time - start_time;
        console.log("The user completed the test in:", total_time)
    }
    return true;
}