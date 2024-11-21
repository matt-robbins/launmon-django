const status_table = {'none': 'Available','wash': "Washing", 'dry': 'Drying', 'both': 'Running'}

function timeAgo(input) {
  const date = (input instanceof Date) ? input : new Date(input);
  const formatter = new Intl.RelativeTimeFormat('en');
  const ranges = {
    years: 3600 * 24 * 365,
    months: 3600 * 24 * 30,
    weeks: 3600 * 24 * 7,
    days: 3600 * 24,
    hours: 3600,
    minutes: 60,
    seconds: 1
  };
  const secondsElapsed = (date.getTime() - Date.now()) / 1000;
  for (let key in ranges) {
    if (ranges[key] < Math.abs(secondsElapsed)) {
      const delta = secondsElapsed / ranges[key];
      return formatter.format(Math.round(delta), key);
    }
  }
}

function update_location(locdiv, status, time) {

  locdiv
    .querySelector("[data-js-attr='status-display']")
    .className = "status " + status;

  locdiv
    .querySelector("[data-js-attr='location-updated-at']")
    .innerHTML = timeAgo(time);
    
  locdiv
    .querySelector("svg.washer")
    .className = "machine washer " + status;
  locdiv
    .querySelector("path.washer-center")
    .className = "washer-center " + status;
  locdiv
    .querySelector("svg.dryer")
    .className = "machine dryer " + status;
}

function update() {
  fetch(`/v1/locations/?format=json`)
    .then((resp) => resp.json())
    .then((status) => {
      status.forEach((location) => {
        time = new Date(location.lastseen)
        const locdiv = document.querySelector(`[data-loc="${location}"]`)
        update_location(locdiv, location.latest_status, new Date(location.latest_time))
      });
    });
}

function updateTimestamps() {
  const locdiv = document.querySelectorAll("[data-js-attr='location-updated-at']");

  Array.from(locdiv).forEach((tstamp) => {
    tstamp.innerHTML = timeAgo(tstamp.dateTime);
  })
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
document.addEventListener("DOMContentLoaded", function() {
  window.subscriptions = [];

  // const locdiv = document.querySelectorAll("[data-js-attr='location-updated-at']");

  // Array.from(locdiv).forEach((tstamp) => {
  //   tstamp.innerHTML = timeAgo(tstamp.dateTime);
  // })

  updateTimestamps();

  var timer = setInterval(updateTimestamps, 1000);

  Array.from(document.getElementsByClassName('clickable list-group-item')).forEach((el) => {
    var location = el.querySelector("div.location-cell").dataset.loc;
    el.addEventListener('click', (e) => {
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
  });

  

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
