var chart;

/**
 * Request data from the server, add it to the graph and set a timeout
 * to request again
 */
function requestData_words() {
    $.ajax({
        url: '/live-words',
        success: function(point) {
            var series = chart.series[0],
                shift = series.data.length > 20;

            for(var i = 0; i < 5; i++){
                chart.series[i].name = point[i][0];
                chart.series[i].legendItem = chart.series[i].legendItem.destroy();
                chart.series[i].legendGroup = chart.series[i].legendGroup.destroy();
                chart.series[i].setData([point[i][1]]);
            }


            chart.isDirtyLegend = true;
            chart.redraw(false);
            // call it again after one second
            setTimeout(requestData_words, 1000);
        },
        cache: false
    });
}

$(document).ready(function() {
    chart = new Highcharts.Chart({
        chart: {
            backgroundColor: '#DAD9FB',
            width: 550,
            height: 275,
            renderTo: 'words-container',
            defaultSeriesType: 'bar',
            events: {
                load: requestData_words
            }

        },
        credits: {
            enabled : false
        },
        legend:{
          align: 'right',
          x: -80,
          verticalAlign: 'top',
          y: 0,
          floating: true,
          backgroundColor: (Highcharts.theme && Highcharts.theme.background2) || 'white',
          borderColor: '#CCC',
          borderWidth: 1,
          shadow: false
        },
        title: {
            text: '',
            verticalAlign: 'vertical',
        },
        tooltip:{
            enabled:false
        },
        xAxis: {
            title : "단어",
            labels: {
                enabled: false
            },

        },
        yAxis: {
            title: "단어 수",
        },
        series: [{
            name: 'Random data',
            data: []
        },{
            name: 'Random data',
            data: []
        },{
            name: 'Random data',
            data: []
        },{
            name: 'Random data',
            data: []
        },{
            name: 'Random data',
            data: []
        }],
        exporting: {
            enabled: false
        },

    });

});

var chart_viewers;

/**
 * Request data from the server, add it to the graph and set a timeout
 * to request again
 */
function requestData_viewers() {
    $.ajax({
        url: '/live-viewers',
        success: function(point) {
            var series = chart_viewers.series[0],

                shift = series.data.length > 20; // shift if the series is
                                                 // longer than 20

            // add the point
            chart_viewers.series[0].addPoint(point, true, shift);

            // call it again after one second
            setTimeout(requestData_viewers, 1000);
        },
        cache: false
    });
}

$(document).ready(function() {
    chart_viewers = new Highcharts.Chart({
        chart: {
            backgroundColor: '#DAD9FB',
            width: 530,
            height: 275,
            renderTo: 'viewers-container',
            defaultSeriesType: 'spline',
            events: {
                load: requestData_viewers
            }
        },
        credits: {
            enabled : false
        },
        title: {
            text: ''
        },
        xAxis: {
            type: 'datetime',
            tickPixelInterval: 150,
            maxZoom: 20 * 1000
        },
        yAxis: {
            title: "시청자수",
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


var chart_segment;

/**
 * Request data from the server, add it to the graph and set a timeout
 * to request again
 */
function requestData_segment() {
    $.ajax({
        url: '/live-segment',
        success: function(point) {
            var series = chart_segment.series[0],
                shift = series.data.length > 20;
            var dataSet = [{name: '긍정', y: 0}, {name: '부정', y: 0}];
            dataSet[0].y = point[0];
            dataSet[1].y = point[1];
            console.log("hello");
            //chart_segment.series[0].legendItem = chart_segment.series[0].legendItem.destroy();
            //chart_segment.series[0].legendGroup = chart_segment.series[0].legendGroup.destroy();
            chart_segment.series[0].setData(dataSet);

            chart_segment.redraw(false);
            // call it again after one second
            setTimeout(requestData_segment, 1000);
        },
        cache: false
    });
}

$(document).ready(function() {
    chart_segment = new Highcharts.Chart({
  chart: {
      events: {
            load: requestData_segment
        },
      renderTo: 'segment-container',
      type: 'pie',
      spacingRight:0,//차트 우측 여백 지정(default 10)
      style: {
      color: '#444',
      fontWeight: '400',
      width: 300,
      height: 300,

    },

  	backgroundColor:'rgba(255, 255, 255, 0)'
  },
  	credits: {enabled: false}, //highchart 워터마크 숨김처리
    title: {
    	text: '',
    },
    legend: {
      layout: 'vertical',//범례 세로 정렬 시 vertical로 지정.(default horizontal)
      align:'center',
      verticalAlign: 'middle',
      x: -4,
      y: -2,
      itemMarginTop: 5,//범례 margin top 지정(bottom도 존재.)
      symbolHeight: 10,
      symbolWidth: 10,
      symbolPadding: 5,
      symbolRadius: 0,
      itemStyle: {
        color: '#444',
        fontSize: '16px',
        fontWeight:'normal'
      }
     },
     plotOptions: {
       pie: {//도넛(파이)차트 전체 옵션 지정.
       dataLabels: {
       enabled: false,
       distance: -20,
       },
       }
     },
     series: [{
       type: 'pie',
       name:'',
       innerSize: '50%',//도넛 차트 지정시 내부 구멍 너비를 설정.(도넛 차트 필수 지정 옵션)
       data:[
       	{
       	  name: "긍정",
          y: 47,
        },
        {
          name: "부정",
          y: 34,
        }
        ],

	}],
	exporting: {
            enabled: false
    },
});
});