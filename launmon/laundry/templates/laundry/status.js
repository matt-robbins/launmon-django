const status_table = {'none': 'Available','wash': "Washing", 'dry': 'Drying', 'both': 'Running'}


function update_location(location, status, time) {
  const locdiv = $(`#location-${location}`);
  // if (location.lastseen === null) {
  //   time_text = "unknown time";
  // }
  // else {
  //   time_text = jQuery.timeago(time);
  // }
  //const lastUpdated = new Date(`${location.lastseen}`);
  locdiv
    .find("[data-js-attr='status-display']")
    .attr("class", "status " + status);
  locdiv
    .find("[data-js-attr='location-updated-at']")
    .timeago("update", time)
  locdiv
    .find("svg.washer")
    .attr("class", "machine washer " + status);
  locdiv
    .find("path.washer-center")
    .attr("class", "washer-center " + status);
  locdiv
    .find("svg.dryer")
    .attr("class", "machine dryer " + status);

  const li = document.getElementById("li-"+location)

  if (li != null) {
    li.addEventListener('click', (e) => {
      e.stopPropagation();
  
      if (e.target.classList.contains('no-nav')) {
        console.log("not navigating");
        console.log(e.target);
        
      }
      else {
        console.log("navigating!")
        window.location.href = "details/" + location;
      }
    })
  }
}

function update() {
  fetch(`${$SCRIPT_ROOT}/json`)
    .then((resp) => resp.json())
    .then((status) => {
      status.forEach((location) => {
        time = new Date(location.lastseen)
        update_location(location.location, location.status, new Date(location.lastseen))
      });
    });
}

function startWebsocket(url) {
  var ws = new WebSocket(url);

  ws.onmessage = function(event) {
      e = JSON.parse(event.data)
      if (e.status) {
        st = e.status.split(":");
        st = st[st.length - 1];
        update_location(e.location,st, new Date());
      }
  };

  ws.onclose = function() {
      // connection closed, discard old websocket and create a new one in 5s
      console.log("websocket closed. Restarting...")
      ws = null
      setTimeout(function(){ 
          startWebsocket(url);
      }, 5000);
  };
}

// onload function
$(function () {
  window.subscriptions = [];
  jQuery("time.timeago").timeago();

  update();

  //var timer = setInterval(update, 5000);

  if (location.hostname == "localhost") {
    startWebsocket("ws://" + location.hostname + ":5678")
  }
  else {
    startWebsocket("wss://" + location.host + "/websocket")
  }

  // app regaining focus on mobile
  window.addEventListener("visibilitychange", function () {
    if (document.visibilityState == "visible") {
      update();
    }
  })

  // set up callbacks for subscribe buttons
  Array.from(document.querySelectorAll('[id^="subcheck-"]')).forEach((btn,ix) => {
    btn.addEventListener("click", (event) => {
      console.log(event.currentTarget.id);
      machine = event.currentTarget.id.split("-")[1];
      console.log(window.subscriptions)

      console.log(event.currentTarget.checked)

      window.subscribe(
        (machine = machine),
        (unsubscribe = !event.currentTarget.checked)
      );
    })
  })

  updateSubscriptions();

  // Check if service workers are supported
  if ('serviceWorker' in navigator) {
    console.log("registering service worker")
    navigator.serviceWorker.register('/sw.js', {'scope': '/laundry'})
  }
});
