$(document).ready(function() {
    $("#TopicForm").validate({
        rules: {},
        messages: {},
        submitHandler: function(form, event) {
            event.preventDefault();
            var formData = $("#TopicForm").serializeArray();
            var url = $("#form_url").val()
            $.ajax({
                url: url,
                headers: {
                    "X-CSRFToken": $("[name=csrfmiddlewaretoken]").val()
                },
                method: "POST",
                data: formData,
                beforeSend: function() {
                    $("#topic-submit").attr("disabled", "disabled");
                    $("#topic-submit").val("Saving...");
                },
                success: function(response) {
                    if (response.status) {                        
                        $(".carousel__button").click()
                        FilterTopic('')
                        $(".msg_desc").text(response.message)
                        $("#flash_message_success").attr("style", "display:block;")
                        setTimeout(function() {
                            $("#flash_message_success").attr("style", "display:none;")
                        }, 3500)
                    } else {                       
                        if ('message' in response ){
                            $(".carousel__button").click()
                            $(".msg_desc").text(response.message)
                            $("#flash_message_error").attr("style", "display:block;")
                            setTimeout(function() {
                                $("#flash_message_error").attr("style", "display:none;")
                            }, 3500)                                                       
                        } else {                      
                            $('#topic-form-div').html(response.template)     
                        } 
                    }                
                },
                complete: function() {
                    $("#topic-submit").attr("disabled", false);
                    $("#topic-submit").val("Save");
                },
            });
        },
    });
});



function FilterTopic(page) {
    if (page == '') {
        page = $('#current_page').val()
    }
    var url = $('#load_topic').val()
    var filter = $('#search-id').val()
    var subject = $('#subject-select').val()
    var course = $('#course').val()


    $.ajax({
        url: url,
        headers: { "X-CSRFToken": $("[name=csrfmiddlewaretoken]").val() },
        method: "GET",
        data: { 'page': page ,
                'filter':filter,
                'subject':subject,
                'course':course,
              
              },
        beforeSend: function() {},
        success: function(response) {
            $('#topic-tbody').html(response.template)
            $('#topic-pagination').html(response.pagination)
        },
    });
}

function SubjectDropdown(courseId) {
    $.ajax({
        url: '/SubjectDropdown/',
        type: 'GET',
        data: {
            'course_id': courseId
        },
        success: function (response) {
            var subjectSelect = $('#subject-select');
            subjectSelect.empty();
            subjectSelect.append($('<option>', {
                value: '',
                text: '- select subject -'
            }));
            $.each(response.subjects, function(key, value) {
                subjectSelect.append(
                    $("<option>").text(value).val(key)
                );
            });
            
        }
    });
}

   

// live search
$('#form').on('keyup', function () {
    var filter = $(this).val();
    FilterTopic(filter);
});

// dropdown subject

$('#course').change(function () {
    var courseId = $(this).val();
    SubjectDropdown(courseId);
    FilterTopic('');
});

// dropdown course

$('#subject-select').change(function () {
   
    var subject = $('#subject-select').val()
    FilterTopic('');
});

// //res
$('#reset-button').click(function() {
    $('#search-id').val('');  // Clear the search input
    $('#course').val(''); 
    $('#subject-select').val(''); 

    FilterTopic();  
});





$(document).on('click', '#create_topic', function(event) {
    event.preventDefault();
    var url = $(this).attr('data-url');
    $.ajax({
        url: url,
        headers: { "X-CSRFToken": $("[name=csrfmiddlewaretoken]").val() },
        method: "GET",
        data: {},
        beforeSend: function() {
            $('#topic-form-div').html('Loading...');
        },
        success: function(response) {
            $('#topic-form-div').html(response.template);
            $('#popup_head').html(response.title);

            $('#course-form').change(function() {
                var courseId = $(this).val();
               
                var subjectSelect = $('#subject-form');

                // Clear previous options
                subjectSelect.empty();

                // Make AJAX request to fetch subjects based on the selected course
                $.ajax({
                    url: "/get_subjects/",
                    data: {
                        course_id: courseId
                    },
                    success: function(data) {
                        // Populate the subject options with the received data
                        $.each(data.subjects, function(key, value) {
                            subjectSelect.append(
                                $("<option>").text(value).val(key)
                            );
                        });
                    }
                });
            });
        },
    });
});



$(document).on('click', '.topic-edit', function(event) {
    event.preventDefault();
    var url = $(this).attr('data-url')
    $.ajax({
        url: url,
        headers: { "X-CSRFToken": $("[name=csrfmiddlewaretoken]").val() },
        method: "GET",
        data: {},
        beforeSend: function() {
            $('#topic-form-div').html('Loading...')
        },
        success: function(response) {
            $('#topic-form-div').html(response.template)
            $('#popup_head').html(response.title)
            var courseSelect = $('#course-form');
            courseSelect.val(response.course_id);
            $('#course-form').change(function() {
                
                var courseId = $(this).val();
                
                var subjectSelect = $('#subject-form');
                

                // Clear previous options
                subjectSelect.empty();

                // Make AJAX request to fetch subjects based on the selected course
                $.ajax({
                    url: "/get_subjects/",
                    data: {
                        course_id: courseId
                    },
                    success: function(data) {
                        // Populate the subject options with the received data
                        $.each(data.subjects, function(key, value) {
                            subjectSelect.append(
                                $("<option>").text(value).val(key)
                            );
                        });
                    }
                });
            });
        },
    });
});


// // Function to delete subject
function DeleteTopic(id) {
    var url = '/topic/' + String(id) + '/delete/'
    swal({
        icon: "warning",
        title: "Verify Details",
        text: "Are you sure you want to delete this record?",
        buttons: true,
        dangerMode: true,
    }).then(function(okey) {
        if (okey) {
            $.ajax({
                url: url,
                headers: { "X-CSRFToken": $("[name=csrfmiddlewaretoken]").val() },
                method: "POST",
                data: {},
                beforeSend: function() {},
                success: function(response) {
                    if (response.status) {
                        $(".msg_desc").text(response.message);
                        $("#flash_message_success").attr("style", "display:block;");
                        setTimeout(function() {
                            $("#flash_message_success").attr("style", "display:none;");
                        }, 3500);
                        FilterTopic('')
                    }
                },
            });
        }
    });
}



