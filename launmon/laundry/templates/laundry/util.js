
function setButtonSubscribed(checkbox, subscribed) {
    checkbox[0].checked = subscribed
}

function isButtonSubscribed(button) {
    return button.hasClass("btn-primary")
}

function setButtonEnabled(checkbox, enabled) {
    checkbox[0].disabled = !enabled
}

function checkServiceWorkers() {
    return ('serviceWorker' in navigator)
}

function updateSubscriptions() {

    if (!checkServiceWorkers()) {
        return
    }

    var ids = [];

    navigator.serviceWorker.getRegistration("/laundry").then((registration) => {
        if (registration) {
            registration.pushManager.getSubscription().then((subscription) => {
                if (subscription === null) {
                    return;
                }

                var url = "{% url 'check-subscription' %}"+"?url="+encodeURIComponent(subscription.endpoint)
                fetch(url)
                .then((resp) => resp.json())
                .then((list) => { 
                    list.forEach(element => {
                        ids.push(Number(element.location));
                    });
                    Array.from(document.querySelectorAll('[id^="subcheck-"]')).forEach((btn,ix) => {
                        loc_id = Number(btn.id.split("-")[1]);
                        setButtonSubscribed($('#'+btn.id),ids.includes(loc_id))
                    })
                })
            })
        }
    });
}
