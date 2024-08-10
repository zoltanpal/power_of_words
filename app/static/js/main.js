function init_datapicker(start_date, end_date) {
    var newStartDate = null;
    var newEndDate = null;

    var configObject = {
        applyButtonClasses: 'ui blue button',
        cancelButtonClasses: 'ui gray button',
        locale: {
            firstDay: 1,
            separator: " - ",
            format: 'YYYY-MM-DD',
        },
        ranges: {
            'Yesterday': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
            'Today': [moment(), moment()],
            'Last 7 days': [moment().subtract(6, 'days'), moment()],
            'This week': [moment().startOf('isoWeek'), moment().endOf('isoWeek')],
            'This month': [moment().startOf('month'), moment().endOf('month')],
            'Last month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')],
        },
        startDate: start_date,
        endDate: end_date,
    };

    if ($(".datepicker").length) {
        var dateRangePicker = $(".datepicker");

        dateRangePicker.daterangepicker(configObject, function(start, end) {
            newStartDate = start;
            newEndDate = end;
        });

        dateRangePicker.on('apply.daterangepicker', function(e, picker) {
            newStartDate = picker.startDate.format('YYYY-MM-DD');
            newEndDate = picker.endDate.format('YYYY-MM-DD');
            $("#startDateInput").val(newStartDate);
            $("#endDateInput").val(newEndDate);
        });
    }
}

function displaySentimentChart(divID, data) {
    console.log(data)
    Highcharts.chart(divID, {
      chart: {
          type: 'bar'
      },
          title: {
          text: null // Remove the title
      },
          credits: {
          enabled: false // Disable the Highcharts credits
      },
      xAxis: {
          categories: [],
          visible: false
      },
      yAxis: {
          visible: false
      },
      plotOptions: {
          series: {
              stacking: 'stacked',
              dataLabels: {
                  enabled: false,
                  format: '{point.y:.2f}' // Display data labels with two decimal places
              }
          },
          bar: {
              pointWidth: 100, // Adjust the width of the bar
              borderWidth: 0,
              dataLabels: {
                  inside: true
              }
          }
      },
      tooltip: {
          formatter: function(e) {
              var key = this.series.name;
              var value = data[key.toLowerCase()];
              return '<span>' + key + ': <b>' + value + '</b></span><br/>';
          }
      },
      legend: {
          enabled: false // Disable legend
      },
      series: [{
          name: 'Positive',
          data: [0, data.positive],
          color: '#AFD198'
      }, {
          name: 'Neutral',
          data: [0, data.neutral],
          color: '#E8EFCF'
      }, {
          name: 'Negative',
          data: [0, data.negative],
          color: '#ECCA9C'
      }]
  });
}

$(document).ready(function() {

    var url = new URL(document.URL);
    var urlParams = new URLSearchParams(window.location.search);

    $('.dropdown.feed_sources').dropdown(
        {placeholder:'feed sources'}
    );

    $('.ui.sticky').sticky({
        context: '.stick_to_this'
    });

    var startDate = moment().subtract(7, 'days').format('YYYY-MM-DD');
    var endDate = moment().format('YYYY-MM-DD');

    if (urlParams.has('start_date') == true) {
        startDate = urlParams.get('start_date');
    }

    if (urlParams.has('end_date') == true) {
        endDate = urlParams.get('end_date');
    }

    if ($("#startDateInput").length) {
        $("#startDateInput").val(startDate);
    }

    if ($("#endDateInput").length) {
        $("#endDateInput").val(endDate);
    }

    init_datapicker(startDate, endDate);

    $('.feed .label').popup();

    $("form#FeedSearchForm").on("submit", function(event) {
        var queryParams = [];

        // Iterate over form fields
        $(this).find(":input").each(function() {
            // Get the field name and value
            var fieldName = $(this).attr("name");
            var fieldValue = $(this).val();

            // Check if the field has a non-empty value
            if (fieldName !== undefined && fieldValue.length > 0) {
                // Add the key-value pair to the array
                queryParams.push(fieldName + "=" + encodeURIComponent(fieldValue));
            }
        });

        // Construct the query string
        var queryString = queryParams.join("&");

        // Construct the new URL with the query string
        var newUrl = window.location.origin + window.location.pathname + "?" + queryString;

        // Redirect to the new URL
        window.location.href = newUrl;

        event.preventDefault();
    });


    $('#SearchWordsSelectize').selectize({
        searchField: 'title',
        persist: false,
        openOnFocus: false,
        closeAfterSelect: true,
        valueField: 'title',
        items: urlParams.get('words'),
        options: [],
        maxOptions: 20,
        createFilter: function(input) { return input.length >= 3; },
        load: function (query, callback) {
            if (!query || query.length < 3) return callback();
        },
        render: {
            option: function (data, escape) {
                return '<option>' + escape(data.title) + '</option>';
            },
            item: function (data, escape) {
                return '<a class="ui label visible" style="margin-bottom: 3px;">' + escape(data.title)
                    + '<i class="delete icon SearchWordsLabel" data-value="' + escape(data.title) + '"></i></a>';
            }
        },
        create: true,
        onItemAdd(value, $item) {
        },
        onItemRemove(value) {

        },
        onOptionRemove(value) {
            console.log(value)
        }
    });

    var initialWords = urlParams.get('words');
    if (initialWords) {
        var selectize = $('#SearchWordsSelectize')[0].selectize;
        var wordsArray = initialWords.split(',');
        wordsArray.forEach(function(word) {
            selectize.addOption({ title: word });
            selectize.addItem(word);
        });
    }

    // Event delegation to handle clicks on the delete icon
    $(document).on('click', '.SearchWordsLabel', function() {
        var valueToRemove = $(this).data('value');
        $('#SearchWordsSelectize')[0].selectize.removeItem(valueToRemove);
    });


});