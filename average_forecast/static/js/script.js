$('#request_forecast_button').on('click', function() {
  $('#request_forecast_button').text('⏳')

  // Making a reguest to receive forecasters names and task ids 
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
    if ((err.status == 404) || (err.status == 503)) {
      $("#address").text("❌ " + err.responseJSON.error); 
      updateTableAndStatus('all', '')
    } else {
      console.log(err);
    }
  })
  .always(() => {
    $('#request_forecast_button').text('Request')
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
        
        updateTableAndStatus(res.task_id, '✅ ', html)
      } else if (res.task_status === 'PENDING') {
        pending.push(res.task_id)
        updateTableAndStatus(res.task_id, '⏳ ')
      } else {
        updateTableAndStatus(res.task_id, '❌ ')
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

function updateTableAndStatus(taskid, status, html = '') {
  if (taskid == 'all') {
    $("#forecasts_table > tbody > tr > th").each(function () {
      var name = $(this).parent().data('readablename')
      $(this)
        .text(status + name)
        .parent().find(' > td').remove()
    })
    return true
  }

  var el = $(' [data-taskid="' + taskid + '"]')
  el.find(' > td').remove()
  el.find(' > th').text(status + el.data('readablename'))
  if (html) {
    el.append(html)
  }
}