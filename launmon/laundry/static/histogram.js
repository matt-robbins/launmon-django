class HourlyHistogram {
    constructor(div) {
        this.home = div
        div.textContent = '';
        div.classList.add("histogram-container")

        var hist = document.createElement('div');
        hist.textContent = '';
        hist.classList.add("histogram-histogram")
        this.hist = hist

        var axis = document.createElement('div');
        axis.classList.add("histogram-axis");
        this.axis = axis;

        var labels = document.createElement('div');
        labels.classList.add("histogram-labels");
        this.labels = labels;

        div.appendChild(hist)
        div.appendChild(axis)
        div.appendChild(labels)

        var times = ['','3a','6a','9a','12p','3p','6p','9p',''];
        for (var i in times) {
            var label = document.createElement("p");
            label.classList.add("histogram-label");
            label.textContent = times[i];
            labels.append(label)

            var tick = document.createElement("div");
            tick.classList.add("histogram-tick")
            axis.append(tick)

            if (i == 0 || i == times.length - 1){
                tick.classList.add("histogram-etick")
                label.classList.add("histogram-elabel")
            }
        }

        this.bars = [];

        for (var i = 0; i < 24; i++) {
            var nd = document.createElement("div");        
            nd.classList.add("histogram-bar")
    
            hist.appendChild(nd)
            this.bars.push(nd)
        }

    }
    draw(data) {
        for (var ix in this.bars) {
            this.bars[ix].style.maxHeight = data[ix]*95+"%";
        }
    }
}