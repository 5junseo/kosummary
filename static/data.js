function getParameterByName(name) {
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.search);
    return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}

var vid = getParameterByName('v');
var chart_viewers;

function requestData() {
    $.ajax({
        contentType: 'application/json',
        url: '/summary/' + vid,
        dataType: "json",
        success: function(result) {
            jQuery("#numchat").html(String(result[0]) + " 개");
            jQuery("#runtime").html(result[1]);
            jQuery("#viewers").html("현재 " + String(result[2]) + " 명");
            jQuery("#viewers_accumulate").html("누적 " + String(result[3]) + " 명");
            jQuery("#streaming_title").html(result[4]);
            jQuery("#subscriber").html(String(result[5]) + "명");
            jQuery("#like").html(String(result[6]) + "개");
            jQuery("#thumbnail_img").attr("src", result[7]);

            // viewers charts
            var series = chart_viewers.series[0],
            shift = series.data.length > 20; // shift if the series is
            // add the point
            var point1 = {x : result[8][0], y: result[8][1], color :"#FF7800"};
            chart_viewers.series[0].color =  "#FF7800";
            chart_viewers.series[0].addPoint(point1, true, shift);

            setTimeout(requestData, 5000);
        }, error : function(result){
            console.log(result);
        },
        cache: false
    });
};

// viewers charts
$(document).ready(function() {
    chart_viewers = new Highcharts.Chart({
        chart: {
            backgroundColor: '#DAD9FB',
            width: 530,
            height: 300,
            renderTo: 'viewers-container',
            defaultSeriesType: 'spline',
            events: {
                load: requestData
            }
        },
        credits: {
            enabled : false
        },
        title: {
            text: ''
        },
        xAxis: {
            title: "hello",
                labels: {
                style: {
                    fontSize: 15,
            }
            }
        },
        yAxis: {
            title: "ds",
            labels: {
                style: {
                    fontSize: 15,
                }
            }
        },
        series: [{
            name: 'Random data',
            data: [

            ],
        }],
        exporting: {
            enabled: false
        },

        legend:{
            enabled: false,
        },
    });
});

