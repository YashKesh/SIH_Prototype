window.onload=function(){//from  w ww  .  j a v  a  2  s.com
    var data = {
      labels: [
        "Red",
        "Blue",
        "Yellow"
      ],
      datasets: [
        {
          data: [300, 50, 100],
          backgroundColor: [
            "#FF6283",
            "#36A2EB",
            "#FFCC54"
          ],
          hoverBackgroundColor: [
            "#FF6283",
            "#36A2EB",
            "#FFCC54"
          ]
        }]
    };
    var promisedDeliveryChart = new Chart(document.getElementById('myChart2'), {
      type: 'doughnut',
      data: data,
      options: {
         responsive: true,
        legend: {
          display: false
        },
        cutoutPercentage: 70 
      }
    });
    Chart.pluginService.register({
      beforeDraw: function(chart) {
        var width = chart.chart.width,
            height = chart.chart.height,
            ctx = chart.chart.ctx;
        ctx.restore();
        var fontSize = (height / 114).toFixed(2);
        ctx.font = fontSize + "em sans-serif";
        ctx.textBaseline = "middle";
        var text = "75%",
            textX = Math.round((width - ctx.measureText(text).width) / 2),
            textY = height / 2;
        ctx.fillText(text, textX, textY);
        ctx.save();
      }
    });
        }

 