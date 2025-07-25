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
  return "Just now"
}

function update_location(locdiv, status, subcount, time) {
  locdiv
    .querySelector("[data-js-attr='status-display']")
    .className = "status " + status;
  locdiv
    .querySelector("[data-js-attr='location-updated-at']")
    .setAttribute('datetime', time.toISOString());
  try {
    locdiv
      .querySelector("svg.dryer")
      .setAttribute("class", "machine dryer " + status);
  }
  catch {
    console.log("location as no dryer")
  }
  try {
    locdiv
      .querySelector("svg.washer")
      .setAttribute("class", "machine washer " + status);
    locdiv
      .querySelector("path.washer-center")
      .setAttribute("class", "washer-center " + status);
  }
  catch {
    console.log("location has no washer")
  }

  if (subcount === null) {
    return;
  }

  if (remind_button) {
    buttonEnable(remind_button, subcount > 0);
  }

  try {
    var badge = locdiv
      .querySelector("span.subcount");
    
    badge.textContent = subcount;  
    if (subcount > 0){
      badge.classList.remove('invisible')
      badge.classList.add('visible')
    }
    else {
      badge.classList.add('invisible')
      badge.classList.remove('visible')
    }
    
  }
  catch {
    console.log(`yoopsie! ${e}`)
  }
}

function update() {
  fetch(`/v1/locations/?format=json`)
    .then((resp) => resp.json())
    .then((status) => {
      status.forEach((location) => {
        time = new Date(location.lastseen)
        const locdiv = document.querySelector(`[data-loc="${location.pk}"]`)
        try {
          update_location(locdiv, location.latest_status, location.subscriber_count, new Date(location.latest_time))
        }
        catch {
          //console.log(`failed to update location ${location.pk}`)
        }
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
        console.log(`location = ${e.location}, status = ${st}`);
        const locdiv = document.querySelector(`[data-loc="${e.location}"]`)
        update_location(locdiv, st, null, new Date());
      }
      else {
        console.log(`updating for message`)
        update();
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

function checkInstalled() {
  // Detects if device is on iOS 
  const isIos = () => {
    const userAgent = window.navigator.userAgent.toLowerCase();
    return /iphone|ipad|ipod/.test( userAgent );
  }
  // Detects if device is in standalone mode
  const isInStandaloneMode = () => ('standalone' in window.navigator) && (window.navigator.standalone);

  // Checks if should display install popup notification:
  if (isIos() && !isInStandaloneMode()) {
    document.querySelector('.footermessage').classList = "footermessage";
  }
}

var remind_button = null

function buttonEnable(button,enable) {
  if (enable) {
    button.removeAttribute('disabled');
  } else {
    button.setAttribute('disabled', 'true')
  }
}
// onload function
document.addEventListener("DOMContentLoaded", function() {
  window.subscriptions = [];

  checkInstalled();

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
      machine = event.currentTarget.id.split("-")[1];

      window.subscribe(
        (machine = machine),
        (unsubscribe = !event.currentTarget.checked)
      );
    })
  })

  remind_button = document.querySelector(".remind-button")
  if (remind_button) {
    remind_button.addEventListener("click", (event) =>{
      console.log("reminder!")
      fetch(`/laundry/notify/${LOCATION}`)

      buttonEnable(remind_button,false);
      remind_button.setAttribute('disabled','true');

      var sp = document.querySelector('.remind-spinner');

      sp.classList.replace('invisible','visible');

      setTimeout(function(sp) {
        console.log(`spinner: ${sp}`)
        sp.classList.replace('visible','invisible');
        buttonEnable(remind_button,true)
      }, 5000, sp);

    })
  }
  
  updateSubscriptions();

  // Check if service workers are supported
  if ('serviceWorker' in navigator) {
    console.log("registering service worker")
    navigator.serviceWorker.register('/sw.js', {'scope': '/laundry'})
  }
});
