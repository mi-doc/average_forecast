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
      var status = ''
      var html = ''

      switch (res.task_status) {
        case 'SUCCESS':
          const data = res.task_result
          html = `
            <td>${data.temp}</td>
            <td>${data.condition}</td>
            <td data-winddir="${data.wind_direction}">${degToCompass(data.wind_direction)}</td>
            <td>${Math.round(data.wind_speed * 0.27778)}</td>
            <td>${Math.round(data.humidity)}</td>
            <td>${Math.round(data.pressure)}</td>
            <td>${Math.round(data.precip * 10) / 10}</td>
          ` 
          html = html.replace(/undefined|nan|null/gi, '-')
          status = '✅ '
          break;
        case 'PENDING':
          pending.push(res.task_id)
          status = '⏳ '
          break;
        case 'FAILURE':
          status = '❌ '
          html = `
            <td colspan='7'>${res.task_result}</td>
          `
          break;
      }
      updateTableAndStatus(res.task_id, status, html)
    }
    updateAverage();

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
    $("#forecasts_table > tbody > tr").each(function () {
      var name = $(this).data('readablename')
      $(this).find('td').remove()
      $(this).find('th').text(status + name)
    })
    return true
  }

  var el = $(' [data-taskid="' + taskid + '"]')
  el.find('td').remove()
  el.find('th').text(status + el.data('readablename'))
  if (html) {
    el.append(html)
  }
}

function degToCompass(num) {
  // This function converts wind direction in degrees
  // to letter "compass" representation
  var val = Math.floor((num / 22.5) + 0.5);
  var arr = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"];
  return arr[(val % 16)];
}

function updateAverage() {
  // This func calculates average numbers for table columns listed below
  // This is the so called "average forecast"
  const params = [
    // The name of a column and its order number
    ['av_temp', 1],
    ['av_wspd', 4],      // Average wind direction is calculated separately
    ['av_humidity', 5],
    ['av_press', 6],
    ['av_precip', 7]
  ]

  var table = $('#forecasts_table')[0]

  for (let param of params) {
    var values = Array()
    var col_num = param[1]
    for (let r of table.tBodies[0].rows){
      var cell = r.cells[col_num]
      if (typeof(cell) == 'undefined') {continue;}
      var val = cell.textContent
      if (!isNaN(val) && !isNaN(parseFloat(val))) {   // Checking if the value is a number
        values.push(parseFloat(val))
      }
    }
    // Next we calculate the average value of a list
    const sum = values.reduce((a, b) => a + b, 0); 
    const avg = (sum / values.length) || 0;

    $("#" + param[0])[0].textContent = Math.round(avg)
  }

  // Finally calculating average wind direction.
  // It is a "circular" data, so it needs some math to find average direction
  var wind_dir_list = Array()
  $('[data-winddir]').each(function() {
    var d = $(this).data('winddir')
    if (!isNaN(d)) {
      wind_dir_list.push(d);
    }
  })
  average_dir = getAverageDegrees(wind_dir_list)
  average_dir_compass = degToCompass(average_dir)
  $('#av_wdir')[0].textContent = average_dir_compass
}

getAverageDegrees = (array) => {
  // WARNING BEWARE OF MATH
  // I found this solution on stackoverflow
  let arrayLength = array.length;
  let sinTotal = 0;
  let cosTotal = 0;

  for (let i = 0; i < arrayLength; i++) {
      sinTotal += Math.sin(array[i] * (Math.PI / 180));
      cosTotal += Math.cos(array[i] * (Math.PI / 180));
  }

  let averageDirection = Math.atan(sinTotal / cosTotal) * (180 / Math.PI);

  if (cosTotal < 0) {
      averageDirection += 180;
  } else if (sinTotal < 0) {
      averageDirection += 360;
  }

  return averageDirection;
}