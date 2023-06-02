$(document).ready(function() {
    $("#SubtopicForm").validate({
        rules: {},
        messages: {},
        submitHandler: function(form, event) {
            event.preventDefault();
            var formData = $("#SubtopicForm").serializeArray();
            var url = $("#form_url").val()
            $.ajax({
                url: url,
                headers: {
                    "X-CSRFToken": $("[name=csrfmiddlewaretoken]").val()
                },
                method: "POST",
                data: formData,
                beforeSend: function() {
                    $("#subtopic-submit").attr("disabled", "disabled");
                    $("#subtopic-submit").val("Saving...");
                },
                success: function(response) {
                    if (response.status) {                        
                        $(".carousel__button").click()
                        FilterSubtopic('')
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
                            $('#subtopic-form-div').html(response.template)     
                        } 
                    }                
                },
                complete: function() {
                    $("#subtopic-submit").attr("disabled", false);
                    $("#subtopic-submit").val("Save");
                },
            });
        },
    });
});



function FilterSubtopic(page) {
    if (page == '') {
        page = $('#current_page').val()
    }
    var url = $('#load_subtopic').val()
    var filter = $('#search-id').val()
    var subject = $('#subject-select').val()
    var course = $('#course-select').val()
    var topic = $('#topic-select').val()


    $.ajax({
        url: url,
        headers: { "X-CSRFToken": $("[name=csrfmiddlewaretoken]").val() },
        method: "GET",
        data: { 'page': page ,
                'filter':filter,
                'subject':subject,
                'course':course,
                'topic':topic,
              
              },
        beforeSend: function() {},
        success: function(response) {
            $('#subtopic-tbody').html(response.template)
            $('#subtopic-pagination').html(response.pagination)
        },
    });
}
// filter subject dropdown
function SearchDropdown1(courseId) {
    $.ajax({
        url: '/SearchDropdown/',
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

// filter dropdowntopic
function SearchDropdown2(subjectId) {
    $.ajax({
        url: '/SearchDropdown_topic/',
        type: 'GET',
        data: {
            'subject_id': subjectId
        },
        success: function (response) {
            var topicSelect = $('#topic-select');
            topicSelect.empty();
            topicSelect.append($('<option>', {
                value: '',
                text: '- select topic -'
            }));
            $.each(response.topics, function(key, value) {
                topicSelect.append(
                    $("<option>").text(value).val(key)
                );
            });
            
        }
    });
}
 

// live search
$('#form').on('keyup', function () {
    var filter = $(this).val();
    FilterSubtopic(filter);
});

// dropdown subject

$('#course-select').change(function () {
    var courseId = $(this).val();
    SearchDropdown1(courseId);
    FilterSubtopic('');
});

// dropdown topic

$('#subject-select').change(function () {
    var subjectId = $(this).val();
    SearchDropdown2(subjectId);
    FilterSubtopic('');
});

// topic select

$('#topic-select').change(function () {
  
    FilterSubtopic('');
});



// //res
$('#reset-button').click(function() {
    $('#search-id').val('');  // Clear the search input
    $('#course-select').val(''); 
    $('#subject-select').val(''); 
    $('#topic-select').val(''); 

    FilterSubtopic('');  
});


$(document).on('click', '#create_subtopic', function(event) {
    event.preventDefault();
    var url = $(this).attr('data-url');

    $.ajax({
        url: url,
        headers: { "X-CSRFToken": $("[name=csrfmiddlewaretoken]").val() },
        method: "GET",
        data: {},
        beforeSend: function() {
            $('#subtopic-form-div').html('Loading...');
        },
        success: function(response) {
            $('#subtopic-form-div').html(response.template);
            $('#popup_head').html(response.title);

            // Attach change event listener to the course dropdown
            $('#course-form').change(function() {
                var courseId = $(this).val();

                // Send an AJAX request to retrieve the related subject options
                $.ajax({
                    url: '/get_related_data/',
                    data: {
                        'course_id': courseId
                    },
                    dataType: 'json',
                    success: function(data) {
                        var subjectSelect = $('#subject-form');
                        var topicSelect = $('#topic-form');

                        // Clear the existing options
                        subjectSelect.empty();
                        topicSelect.empty();

                        // Populate the subject dropdown with options
                        $.each(data.subjects, function(index, subject) {
                            subjectSelect.append($('<option></option>')
                                .attr('value', subject.id)
                                .text(subject.name));
                        });

                        // Trigger the change event on the subject dropdown to load related topics
                        subjectSelect.trigger('change');
                    },
                    error: function(xhr, status, error) {
                        // Handle the error
                        console.error(error);
                    }
                });
            });

            // Attach change event listener to the subject dropdown
            $('#subject-form').change(function() {
                var subjectId = $(this).val();

                // Send an AJAX request to retrieve the related topic options
                $.ajax({
                    url: '/get_related_topic/',
                    data: {
                        'subject_id': subjectId
                    },
                    dataType: 'json',
                    success: function(data) {
                        var topicSelect = $('#topic-form');

                        // Clear the existing options
                        topicSelect.empty();

                        // Populate the topic dropdown with options
                        $.each(data.topics, function(index, topic) {
                            topicSelect.append($('<option></option>')
                                .attr('value', topic.id)
                                .text(topic.name));
                        });
                    },
                    error: function(xhr, status, error) {
                        // Handle the error
                        console.error(error);
                    }
                });
            });
        },
        error: function(xhr, status, error) {
            // Handle the error
            console.error(error);
        }
    });
});



$(document).on('click', '.subtopic-edit', function(event) {
    event.preventDefault();
    var url = $(this).attr('data-url')
    $.ajax({
        url: url,
        headers: { "X-CSRFToken": $("[name=csrfmiddlewaretoken]").val() },
        method: "GET",
        data: {},
        beforeSend: function() {
            $('#subtopic-form-div').html('Loading...')
            
        },
        
        success: function(response) {
            $('#subtopic-form-div').html(response.template)
            $('#popup_head').html(response.title)
            var courseSelect = $('#course-form');
            courseSelect.val(response.course_id);
            console.log(courseSelect.val());
            var subjectSelect = $('#subject-form');
            subjectSelect.val(response.subject);
            console.log(subjectSelect.val());
            var topicSelect = $('#topic-form');
            topicSelect.val(response.topic_id);
            console.log(topicSelect.val());

            
          
          
            // Attach change event listener to the course dropdown
            // $('#course-form').change(function(){
            $(document).off('change', '#course-form').on('change', '#course-form', function ()  {
                var courseId = $(this).val();

                // Send an AJAX request to retrieve the related subject options
                $.ajax({
                    url: '/get_related_data/',
                    data: {
                        'course_id': courseId
                    },
                    dataType: 'json',
                    success: function(data) {
                      
                        var subjectSelect = $('#subject-form');
                        // var topicSelect = $('#topic-form');

                        // Clear the existing options
                        subjectSelect.empty();
                        topicSelect.empty();

                        // Populate the subject dropdown with options
                        $.each(data.subjects, function(index, subject) {
                            subjectSelect.append($('<option></option>')
                                .attr('value', subject.id)
                                .text(subject.name));
                        });

                        // Trigger the change event on the subject dropdown to load related topics
                        subjectSelect.trigger('change');
                    },
                    error: function(xhr, status, error) {
                        // Handle the error
                        console.error(error);
                    }
                });
            });
            
            // Attach change event listener to the subject dropdown
            $('#subject-form').change(function() {
                var subjectId = $(this).val();

                // Send an AJAX request to retrieve the related topic options
                $.ajax({
                    url: '/get_related_topic/',
                    data: {
                        'subject_id': subjectId
                    },
                    dataType: 'json',
                    success: function(data) {
                        var topicSelect = $('#topic-form');

                        // Clear the existing options
                        topicSelect.empty();

                        // Populate the topic dropdown with options
                        $.each(data.topics, function(index, topic) {
                            topicSelect.append($('<option></option>')
                                .attr('value', topic.id)
                                .text(topic.name));
                        });
                    },
                    error: function(xhr, status, error) {
                        // Handle the error
                        console.error(error);
                    }
                });
            });
        },
        error: function(xhr, status, error) {
            // Handle the error
            console.error(error);
        }
    });
});


// Function to delete subject
function DeleteSubtopic(id) {
    var url = '/subtopic/' + String(id) + '/delete/'
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
                        FilterSubtopic('')
                    }
                },
            });
        }
    });
}



