const publicVapidKey = 'BCFxaPZEymM57yWrlIPuFkMdSsQjkClmmAnVfHqKVaDtGnQ_t5uA8Yq2B0mm7GxpsNRLmqKSQIr-vdxFkSRCVQc';

// Copied from the web-push documentation
const urlBase64ToUint8Array = (base64String) => {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding)
    .replace(/\-/g, '+')
    .replace(/_/g, '/');

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
};

function askPermission() {
    return new Promise(function (resolve, reject) {
        const permissionResult = Notification.requestPermission(function (result) {
            resolve(result);
        });

        if (permissionResult) {
            permissionResult.then(resolve, reject);
        }
    });
}

window.subscribe = async (machine=4,unsubscribe=false) => {
    console.log("subscribing?")
    if (!('serviceWorker' in navigator)) {
        alert("Your browser does not seem to support Service Workers. " +
        "This means you'll be unable to recieve push messages.")

        $('.notify-button').each(function() {
            setButtonEnabled($( this ), false)
            setButtonSubscribed($( this), false)
        });

        return;
    }
    console.log("waiting for service worker to be ready")
    const registration = await navigator.serviceWorker.ready;

    console.log("ready")

    navigator.serviceWorker.addEventListener("message", (message) => {
        console.log("got message! updating subscriptions")
        updateSubscriptions()
    })

    const perm = await askPermission()
    if (perm !== 'granted') {
        alert("Aww, you rejected permissions. " +
        "This means you'll be unable to recieve push messages.");
        
        console.log("we didn't get permission!");
    }

    if (!('pushManager' in registration)) {
        alert("Unable to subscribe to push messages. " +
            "On iOS, check that Push API is enabled, " +
            "and add this site as a bookmark to your home screen.")
    }

    var subscription = await registration.pushManager.getSubscription()
    console.log(subscription);
    if(subscription === null){
        // Subscribe to push notifications
        subscription = await registration.pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: urlBase64ToUint8Array(publicVapidKey),
        });

        console.log("subscription: " + subscription)

    }

    console.log("unsubscribe="+unsubscribe)

    var csrftoken = '{{ csrf_token }}';

    if (!unsubscribe) {
        var url = "{% url 'subscribe' %}"
        await fetch(url, {
            method: 'POST',
            body: JSON.stringify({'subscription': subscription, 'machine': machine}),
            headers: {
                'X-CSRFToken': csrftoken,
                'content-type': 'application/json',
            },
        });
    }
    else {
        var url = "{% url 'unsubscribe' %}"
        await fetch(url, {
            method: 'POST',
            body: JSON.stringify({'endpoint': subscription.endpoint, 'machine': machine}),
            headers: {
                'X-CSRFToken': csrftoken,
                'content-type': 'application/json',
            },
        });
    }

    updateSubscriptions()
};
