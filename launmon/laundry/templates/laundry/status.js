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

$(function () {
  window.subscriptions = [];

  update();
  setInterval(function () {
    update();
  }, 5000);

  ws = new WebSocket("wss://" + location.host + "/websocket");
  ws.addEventListener("message", (event) => {
    console.log("got websocket message. Reloading")
    e = JSON.parse(event.data);
    if (e.status) {
      update();
    }
  });

  console.log(window.subscriptionEndpoint);

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
