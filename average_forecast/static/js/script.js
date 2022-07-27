$('#request_forecast_button').on('click', function() {
  $.ajax({
    url: '/get_forecasts/',
    data: { type: 'moscow' },
    method: 'POST',
  })
  .done((res) => {
    getStatus(res.task_ids);
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
  .done((results) => {
    var pending = Array()
    // ToDo figure out how to read data
    // from the response.
    for (var n in results.results) {
      res = results.results[n]
      if (res.task_status === 'SUCCESS') {
        var data = res.task_result
        const html = `
          <th>${data.temp}</th>
          <th>${data.condition}</th>
          <th>${data.wind_direction}</th>
          <th>${data.wind_speed}</th>
          <th>${data.humidity}</th>
          <th>${data.pressure}</th>
        ` 
        $('#' + data.source).append(html)
      } else if (res.task_status === 'PENDING') {
        pending.push(res.task_id)
      } else {
        // ToDo: add failed tasks handling
      }
    }

    if (pending.length === 0) return true;
    setTimeout(function() {
      getStatus(pending);
    }, 1000);
  })
  .fail((err) => {
    console.log(err)
  });
}











// $('.button').on('click', function() {
//     $.ajax({
//       url: '/tasks/',
//       data: { type: $(this).data('type') },
//       method: 'POST',
//     })
//     .done((res) => {
//       getStatus(res.task_id);
//     })
//     .fail((err) => {
//       console.log(err);
//     });
//   });


//   function getStatus(taskID) {
//     $.ajax({
//       url: `/tasks/${taskID}/`,
//       method: 'GET'
//     })
//     .done((res) => {
//       const html = `
//         <tr>
//           <td>${res.task_id}</td>
//           <td>${res.task_status}</td>
//           <td>${res.task_result}</td>
//         </tr>`
//       $('#tasks').prepend(html);
  
//       const taskStatus = res.task_status;
  
//       if (taskStatus === 'SUCCESS' || taskStatus === 'FAILURE') return false;
//       setTimeout(function() {
//         getStatus(res.task_id);
//       }, 1000);
//     })
//     .fail((err) => {
//       console.log(err)
//     });
//   }