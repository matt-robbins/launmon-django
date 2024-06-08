function update() {
  fetch(`${$SCRIPT_ROOT}/json`)
    .then((resp) => resp.json())
    .then((status) => {
      status.forEach((location) => {
        const locdiv = $(`#location-${location.location}`);
        const lastUpdated = new Date(`${location.lastseen}`);

        locdiv
          .find("[data-js-attr='location-updated-at']")
          .text(`Last updated: ${lastUpdated.toLocaleTimeString()}`);
        locdiv
          .find("svg.washer")
          .attr("class", "machine washer " + location.status);
        locdiv
          .find("path.washer-center")
          .attr("class", "washer-center " + location.status);
        locdiv
          .find("svg.dryer")
          .attr("class", "machine dryer " + location.status);
        
      });
    });

  updateSubscriptions();
}

function startWebsocket(url) {
  var ws = new WebSocket(url);

  ws.onmessage = function(event) {
      e = JSON.parse(event.data)
      if (e.status) {
        console.log("got websocket status message. Reloading")
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

$(function () {
  window.subscriptions = [];

  update();

  startWebsocket("wss://" + location.host + "/websocket")

  console.log(window.subscriptionEndpoint);

  // app regaining focus on mobile
  window.addEventListener("visibilitychange", function () {
    if (document.visibilityState == "visible") {
      window.location.reload();
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
