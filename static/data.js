function getParameterByName(name) {
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.search);
    return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}

var vid = getParameterByName('vi');
var chart_viewers;

function requestData() {
    $.ajax({
        contentType: 'application/json',
        url: '/summary/' + vid,
        dataType: "json",
        success: function(result) {
            console.log(result)
            jQuery("#numchat").html(String(result[0]) + " 개");
            jQuery("#runtime").html(result[1]);
            jQuery("#viewers").html("현재 " + String(result[2]) + " 명");
            jQuery("#viewers_accumulate").html("누적 " + String(result[3]) + " 명");
            jQuery("#streaming_title").html(result[4]);
            jQuery("#subscriber").html("구독자: " + String(result[5]) + "명");
            jQuery("#like").html("좋아요: " + String(result[6]) + "개");
            jQuery("#thumbnail_img").attr("src", result[7]);

            // viewers charts
            var series = chart_viewers.series[0],
            shift = series.data.length > 20; // shift if the series is
            console.log(result[8]);
            // add the point
            chart_viewers.series[0].addPoint(result[8], true, shift);

            setTimeout(requestData, 10000);
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
        },
        yAxis: {
            title: "ds",
        },
        series: [{
            name: 'Random data',
            data: [],
        }],
        exporting: {
            enabled: false
        },

        legend:{
            enabled: false,
        },
    });
});

