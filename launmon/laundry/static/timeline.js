
class Timeline {
    //tape_end = 0;
    //tape_start = 0;
    scale = 0;
    head = 0;
    tape_start = 0;
    tape_end = 0;
    
    constructor(div,name,duration=3600000,tracks=1) {
        this.root = div;
        this.name = name;
        this.tracks = [];

        console.log("creating timeline with name: "+name)
        console.log("tracks="+tracks)
        div.textContent = '';
        div.classList.add("timeline-container");

        this.tape = document.createElement('div');
        this.tape.classList.add("timeline-tape");
        this.tape.id = name+"-timeline";
        div.appendChild(this.tape);

        var ruler = document.createElement('div');
        ruler.classList.add("timeline-ruler");
        ruler.id = "timeline-ruler";
        this.tape.append(ruler);
        
        this.ruler = ruler;

        for (var i = 0; i < tracks; i++){
            var tk = document.createElement('div');
            tk.classList.add("timeline-track");
            tk.id = name+"-track-"+i;
            this.tape.append(tk);
            this.tracks[i] = tk;
            console.log(this.tracks)
        }

        this.tape_end = new Date().getTime();
        this.tape_start = this.tape_end - duration;
        this.scale = this.tape_end - this.tape_start;
        this.head = this.tape_end;
        this.zoom_center = 1;
        this.zoom = 1;

        this.zoom_update();
        this.drawRuler();
        //this.pd = new PinchDetector(div);
    }

    setEventPosition(ev) {
        var start = new Date(ev.timelineEvent.start+"Z").getTime();
        var end = new Date(ev.timelineEvent.end+"Z").getTime();
        
        if (ev.timelineEvent.end === null) {
            end = new Date().getTime();
        }
        
        var left = (1-((this.tape_end-start)/this.scale))*100;
        var width = ((end-start)/this.scale)*100;

        if (left+width < 0) {
            ev.remove();
        }

        ev.style.left = left+'%';
        ev.style.width = width+'%';
    }

    draw(events, track, cb) {

        for (const ix in events) {
            var e = events[ix];
            var ev = document.createElement('div');
            ev.classList.add("timeline-event");

            ev.id = "timeline-"+this.name+"-"+track+"-"+ix;
            ev.timelineEvent = e

            this.setEventPosition(ev);

            ev.addEventListener('click', function(ev,e) {
                cb(ev.currentTarget.timelineEvent)
            }, e);

            this.tracks[track].appendChild(ev);
        }
    }

    drawRuler(time) {
        var now = new Date().getTime();
        var hour = 3600000;
        var minute = hour / 60;
        var day = hour * 24;

        var nearest = Math.floor(now/hour)*hour;
        var count = Math.floor(this.scale/hour)/this.zoom;
        console.log("count = "+count);
        var desired_count = 4;

        var divs = [1,3,4,6,12,24]
        var divz = 1;
        for (var ix in divs) {
            var c = count / divs[ix];
            if (c >= desired_count) {
                divz = divs[ix];
            }
        }

        this.ruler.innerText = '';
        var first = nearest;
        this.ruler.latest = first;
        this.ruler.update_after = hour;

        while (nearest > this.tape_start) {

            var date = new Date(nearest);
            var hr = date.getHours();

            var label = document.createElement("div");
            label.classList.add("timeline-label");
            var text = document.createElement("p");
            text.classList.add("timeline-text");
            var tick = document.createElement("div");
            tick.classList.add("timeline-tick");

            var ltext = '';
            if (hr % divz == 0 || nearest == first) {
                ltext = date.toLocaleTimeString('en-US',{hour:'numeric'});
                tick.classList.add("long");
                if (hr == 0) {
                    ltext = new Intl.DateTimeFormat('en-US').format(date);
                }
            }
            text.innerText = ltext;
            
            label.style.left = (100*(nearest-this.tape_start)/(this.tape_end-this.tape_start))+"%";

            label.labelTime = nearest;
            label.append(text);
            label.append(tick);
            this.ruler.append(label);
            nearest -= hour;
        }

        
    }

    update(time) {
        var diff = time - this.tape_end;
        this.tape_end = time;
        this.tape_start = time - this.scale;
        for (var track of this.tape.children) {
            for (var c of track.children) {
                try{
                    this.setEventPosition(c)
                }
                catch {

                }
            }
        }
        if (time > this.ruler.update_after + this.ruler.latest) {
            this.drawRuler(time);

            return;
        }

        for (var lab of document.getElementsByClassName("timeline-label")) {
            var l = (100*(lab.labelTime-this.tape_start)/this.scale)+"%";
            if (l < 0) {
                lab.remove();
            }
            else {
                lab.style.left = l;
            }
        }
        //this.drawRuler();
    }

    zoom_update() {
        this.tape.style.width=this.zoom*100+"%";
        //this.tape.style.left=-(this.zoom-1)*100*this.zoom_center+"%";
        this.drawRuler();
    }

    set zoomInButton(div) {
        div.timelineObject=this;
        div.addEventListener('click', function(ev,tl) {
            this.timelineObject.setZoom = this.timelineObject.zoom * 2;
        }, this);
    }

    set zoomOutButton(div) {
        div.timelineObject=this;
        div.addEventListener('click', function(ev,tl) {
            this.timelineObject.setZoom = this.timelineObject.zoom / 2;
        }, this);
    }

    set setZoom(val) {
        console.log("zoom set!");
        if (val < 1) val = 1;
        this.zoom = val;
        this.zoom_update();
    }
    get getZoom() {
        return this.zoom;
    }
    set setHead(val) {
        this.head = val
        console.log("zoom center set@");
        this.zoom_center = (val-this.tape_start)/this.scale;
        this.zoom_update();
    }
    reset() {
        //this.tape.textContent = "";
        for (var t of this.tracks) {
            t.textContent = '';
        }
        this.scale = this.tape_end - this.tape_start;
    }
    set set_tape_start(val) {
        this.reset();
    }
    set set_tape_end(val) {
        this.reset();
    }
}