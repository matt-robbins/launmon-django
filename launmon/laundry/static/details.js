
var hours = 96

hist = new HourlyHistogram(document.getElementById("histogram"));
dry_tl = new Timeline(document.getElementById("timeline"), 
    "drywash",duration=96*3600*1000,tracks=2);

dry_tl.setZoom=16.0
dry_tl.zoomInButton = document.getElementById("timeline-zin");
dry_tl.zoomOutButton = document.getElementById("timeline-zout");

chart = new Chart(document.getElementById("graph-canvas"), {});
chart.realtime = false;

async function updatePlot(loc,e) {
    var url = '';
    var realtime = false;
    if (e) {
        url = '/rawcurrent-range-json?location='+loc+'&start='+e.start+'&end='+e.end;
    }
    else {
        realtime=true;
        url = '/rawcurrent-json?location='+loc+'&minutes='+30;
    }

    const response = await fetch(url);
    const data = await response.json();

    t = document.getElementById("rtdata-text");
    t.innerText = data.current.join("\n");

    chart.destroy();

    chart = new Chart(document.getElementById("graph-canvas"), {
        type: 'line',
        data: {
            labels: data.time.map((x) => new Date(x+"Z").getTime()),
            datasets: [{
                label: 'Current (units)',
                data: data.current,
                borderWidth: 1
            }]
        },
        options: {
            scales: {
            y: {
                beginAtZero: true
            },
            x: {
                type: "time"
            }
            },
            animation: false
        }
    });
    chart.realtime = realtime;
}

function addData(chart,time,current) {

    if (!chart.realtime){
        return;
    }
    chart.data.labels.shift();
    chart.data.labels.push(time);
    chart.data.datasets[0].data.shift();
    chart.data.datasets[0].data.push(current);

    var t = document.getElementById("rtdata-text");
    t.innerText = chart.data.datasets[0].data.join("\n");

    var term = document.getElementById("realtime");
    term.scrollTo(0,term.scrollHeight);
    chart.update();
}

async function reloadHistogram() {
    tz = new Date().getTimezoneOffset()/60
    loc = document.getElementById("loc_select").value
    day = document.getElementById("day_select").value

    const url = '/histogram-json?weekday='+day+'&location='+loc+'&tzoff='+tz;
    const response = await fetch(url);
    const data = await response.json();

    hist.draw(data);
}

function reloadTimeline() {
    dry_tl.reset();
    reloadTimelineTrack('dry',0);
    reloadTimelineTrack('wash',1);
}

async function reloadTimelineTrack(name='dry',number=0) {
    loc = document.getElementById("loc_select").value;

    var url = '/cycles-json?type='+name+'&hours='+hours+'&location='+loc;
    var response = await fetch(url);
    var data = await response.json();

    dry_tl.draw(data,track=number, function (e) {
        updatePlot(loc,e);
    });
}

function startWebsocket(url) {
    var ws = new WebSocket(url);
  
    ws.onmessage = function(event) {
        e = JSON.parse(event.data)
        if (e.current && e.location == loc) {
            
            d = new Date().getTime();
            addData(chart,d,e.current);
            dry_tl.update(d);
        }
        if (e.status) {
            reloadTimeline();
        }
    };
  
    ws.onclose = function() {
        // connection closed, discard old websocket and create a new one in 5s
        ws = null
        setTimeout(function(){ 
            startWebsocket(url);
            reloadTimeline();
            updatePlot();
        }, 5000);
    };
}

window.addEventListener("load", (event) => {
    tz = new Date().getTimezoneOffset()/60;
    dow = new Date().getDay();
    loc = document.getElementById("loc_select").value
    document.getElementById("day_select").value = dow;
    
    day = document.getElementById("day_select").value;

    document.getElementById("loc_select").addEventListener("change", (event) => {
        reloadHistogram();
        reloadTimeline();
        updatePlot(loc);
    });
    document.getElementById("day_select").addEventListener("change", (event) => {
        reloadHistogram();
    });

    for (var tk of document.getElementsByClassName("timeline-track")) {
        tk.addEventListener("click", (ev) => {
            if (ev.target.classList.contains("timeline-event")) {
                return;
            }
            updatePlot(loc);
        });
    }

    reloadHistogram();
    reloadTimeline();

    updatePlot(loc);

    startWebsocket("wss://laundry.375lincoln.nyc/websocket");

});