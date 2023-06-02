$(document).ready(function () {
    $("#CourseForm").validate({
        rules: {},
        messages: {},
        submitHandler: function (form, event) {
            event.preventDefault();
            var formData = $("#CourseForm").serializeArray();
            var url = $("#form_url").val()
            $.ajax({
                url: url,
                headers: {
                    "X-CSRFToken": $("[name=csrfmiddlewaretoken]").val()
                },
                method: "POST",
                data: formData,
                beforeSend: function () {
                    $("#course-submit").attr("disabled", "disabled");
                    $("#course-submit").val("Saving...");
                },
                success: function (response) {
                    if (response.status) {
                        $(".carousel__button").click()
                        FilterCourse('')
                        $(".msg_desc").text(response.message)
                        $("#flash_message_success").attr("style", "display:block;")
                        setTimeout(function () {
                            $("#flash_message_success").attr("style", "display:none;")
                        }, 3500)
                    } else {
                        if ('message' in response) {
                            $(".carousel__button").click()
                            $(".msg_desc").text(response.message)
                            $("#flash_message_error").attr("style", "display:block;")
                            setTimeout(function () {
                                $("#flash_message_error").attr("style", "display:none;")
                            }, 3500)
                        } else {
                            $('#course-form-div').html(response.template)
                        }
                    }
                },
                complete: function () {
                    $("#course-submit").attr("disabled", false);
                    $("#course-submit").val("Save");
                },
            });
        },
    });
});

function FilterCourse(page) {
    if (page == '') {
        page = $('#current_page').val()
    }
    var url = $('#load_course').val()
    var filter = $('#search-id').val()
    var curriculum = $('#curriculum-select').val()
    $.ajax({
        url: url,
        headers: { "X-CSRFToken": $("[name=csrfmiddlewaretoken]").val() },
        method: "GET",
        data: { 'page': page,'filter':filter,'curriculum':curriculum},
        beforeSend: function () { },
        success: function (response) {
            $('#course-tbody').html(response.template)
            $('#course-pagination').html(response.pagination)
        },
    });
}
$(document).ready(function () {
//search
// $('#form').submit(function (e) {
//     e.preventDefault();

//     FilterCourse('');
// });

$('#form').on('keyup', function () {
    var filter = $(this).val();
    FilterCourse(filter);
});


// dropdown
$('#curriculum-select').change(function () {
    // var curriculum = $(this).val(); 
    FilterCourse('');
});


// reset
$('#reset-button').click (function() {
    $('#search-id').val('');
    $('#curriculum-select').val('');
    
    FilterCourse()
});
});


$(document).on('click', '#create_course', function (event) {
    event.preventDefault();
    var url = $(this).attr('data-url')
    $.ajax({
        url: url,
        headers: { "X-CSRFToken": $("[name=csrfmiddlewaretoken]").val() },
        method: "GET",
        data: {},
        beforeSend: function () {
            $('#course-form-div').html('Loading...')
        },
        success: function (response) {
            $('#course-form-div').html(response.template)
            $('#popup_head').html(response.title)
        },
    });
})
$(document).on('click', '.course-edit', function (event) {
    event.preventDefault();
    var url = $(this).attr('data-url')
    $.ajax({
        url: url,
        headers: { "X-CSRFToken": $("[name=csrfmiddlewaretoken]").val() },
        method: "GET",
        data: {},
        beforeSend: function () {
            $('#course-form-div').html('Loading...')
        },
        success: function (response) {
            $('#course-form-div').html(response.template)
            $('#popup_head').html(response.title)
        },
    });
})

// Function to delete course
function DeleteCourse(id) {
    var url = '/course/' + String(id) + '/delete/'
    swal({
        icon: "warning",
        title: "Verify Details",
        text: "Are you sure you want to delete this record?",
        buttons: true,
        dangerMode: true,
    }).then(function (okey) {
        if (okey) {
            $.ajax({
                url: url,
                headers: { "X-CSRFToken": $("[name=csrfmiddlewaretoken]").val() },
                method: "POST",
                data: {},
                beforeSend: function () { },
                success: function (response) {
                    if (response.status) {
                        $(".msg_desc").text(response.message);
                        $("#flash_message_success").attr("style", "display:block;");
                        setTimeout(function () {
                            $("#flash_message_success").attr("style", "display:none;");
                        }, 3500);
                        FilterCourse('')
                    }
                },
            });
        }
    });
}


// $(document).ready(function () {
//     $('#search-input').on('input', function () {
//         var query = $(this).val();
//         $.ajax({
//             url: '/search/',  // Replace with your URL endpoint
//             data: {'query': query},
//             success: function (response) {
//                 var results = response.items;
//                 var select = $('#search-results');
//                 select.empty();  // Clear previous results
//                 for (var i = 0; i < results.length; i++) {
//                     var option = $('<option>').val(results[i].id).text(results[i].name);
//                     select.append(option);
//                 }
//             }
//         });
//     });
// });

// $(document).ready(function() {
//     $('#multiselect').select2(); // Apply Select2 to the multiselect dropdown
    
//     $('#form').on('submit', function(event) {
//       event.preventDefault(); // Prevent the form from submitting normally
      
//       var query = $('#search-id').val(); // Get the search query
      
//       $.ajax({
//         url: '/course/', // URL to your Django view
//         data: {
//           filter: query // Pass the search query as a parameter
//         },
//         dataType: 'json',
//         success: function(data) {
//           var dropdown = $('#multiselect');
//           dropdown.empty(); // Clear the existing options
          
//           $.each(data, function(index, item) {
//             dropdown.append($('<option>', {
//               value: item.id,
//               text: item.name
//             }));
//           });
          
//           dropdown.trigger('change'); // Notify Select2 about the updated options
//         }
//       });
//     });
//   });




// src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"
// src="https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.13/js/select2.min.js"


