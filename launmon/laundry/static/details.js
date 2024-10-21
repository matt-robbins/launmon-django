

hist = new HourlyHistogram(document.getElementById("histogram"));

async function reloadHistogram() {
    tz = new Date().getTimezoneOffset()/60
    day = document.getElementById("day_select").value

    const url = window.location.origin+'/laundry/histogram-json?weekday='+day+'&location='+LOCATION;
    const response = await fetch(url);
    var data = await response.json();
    data = data['histogram'];
    // hack to rotate the array, concatenate 3 copies and slice it.
    const ldata = data.concat(data, data);
    data = ldata.slice(data.length+tz,2*data.length+tz)
    hist.draw(data);
}

window.addEventListener("load", (event) => {
    tz = new Date().getTimezoneOffset()/60;
    dow = new Date().getDay();
    document.getElementById("day_select").value = dow;
    day = document.getElementById("day_select").value;

    document.getElementById("day_select").addEventListener("change", (event) => {
        reloadHistogram();
    });

    reloadHistogram();
});