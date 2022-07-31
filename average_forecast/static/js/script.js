$('#request_forecast_button').on('click', function() {
  $.ajax({
    url: '/get_forecasts/',
    data: { city: $("#city_name")[0].value },
    method: 'POST',
  })
  .done((res) => {
    var task_ids = Array()
    for (const n in res.tasks) {
      var task = res.tasks[n]
      $("#"+task.forecaster_id).attr('data-taskid', task.task_id)
      task_ids.push(task.task_id)
    }
    $("#address").text(res.address); 
    getStatus(task_ids);
  })
  .fail((err) => {
    console.log(err);
  });
});


function getStatus(task_ids) {
  $.ajax({
    url: `/get_forecast_statuses/`,
    data: {task_ids: task_ids.toString()},
    method: 'POST'
  })
  .done((response) => {
    var pending = Array()
    for (var n in response.results) {
      res = response.results[n]
      if (res.task_status === 'SUCCESS') {
        const data = res.task_result

        // Adding weather data to the row
        const html = `
          <td>${data.temp}</td>
          <td>${data.condition}</td>
          <td>${data.wind_direction}</td>
          <td>${data.wind_speed}</td>
          <td>${data.humidity}</td>
          <td>${data.pressure}</td>
          <td>${data.precip}</td>
        ` 
        $('#' + data.source + ' > td').remove() // Removing previous forecasts 
        $('#' + data.source).append(html)
      } else if (res.task_status === 'PENDING') {
        pending.push(res.task_id)
        $(' [data-taskid="' + res.task_id + '"] > td').remove()
        $(' [data-taskid="' + res.task_id + '"]').append('<td>PENDING</td>')
      } else {
        $(' [data-taskid="' + res.task_id + '"] > td').remove()
        $(' [data-taskid="' + res.task_id + '"]').append('<td>Service hasn\'t responded</td>')
        // ToDo: add failed tasks handling
      }
    }

    if (pending.length === 0) return true;
    setTimeout(function() {
      getStatus(pending);
    }, 300);
  })
  .fail((err) => {
    console.log(err)
  });
}


// function change_forecaster_header(forecaster_id, status) {
//   // This function changes the header of the forecaster row in the table 
//   // accordingly to the task status
//   var status_text = ''
//   switch (status.toLowerCase()) {
//     case 'success':
//       status_text = '✅'
//     case 'pending':
//       status_text = "⌛️"
//     case 'failed': 
//       status_text = "❌"
//   } 
//   const header_text = $("#" + forecaster_id + " > th").text()
//   const new_header_text = header_text + ' ' + status_text
//   $("#" + forecaster_id + " > th").text(new_header_text)
// }
