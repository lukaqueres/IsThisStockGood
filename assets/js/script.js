class Notification extends HTMLElement {
    constructor() {
        super();

        this.attachShadow({ mode: "open" });

        const wrapper = document.createElement("div");
        wrapper.setAttribute("id", "wrapper");

        const header = wrapper.appendChild(document.createElement("div"));
        header.setAttribute("id", "header");

        if ( this.dataset.size === "small" ) {
            this.icon = header.appendChild(document.createElement("div"));
            this.icon.setAttribute("id", "icon-small");

            this.heading = header.appendChild(document.createElement("p"));
        } else {
            this.icon = wrapper.appendChild(document.createElement("div"));
            this.icon.setAttribute("id", "icon-large");

            this.heading = wrapper.appendChild(document.createElement("p"));
        }

        this.dataset.counter = 1;

        this.counter = header.appendChild(document.createElement("span"));
        this.counter.setAttribute("id", "counter");
        this.counter.appendChild(document.createTextNode(this.dataset.counter == 1 ? "" : "this.dataset.counter"));
        if ( this.dataset.counter == 1 ) {
            this.counter.setAttribute("class", "void");
        }

        const clear = header.appendChild(document.createElement("button"));
        clear.setAttribute("id", "clear-button");
        clear.appendChild(document.createElement("ion-icon")).setAttribute("name", "close-circle-outline");
        clear.addEventListener("click", (event) => { this.remove(); });

        this.heading.setAttribute("id", "heading");
        this.heading.appendChild(document.createTextNode("heading" in this.dataset ? this.dataset.heading : ""));

        this.content = wrapper.appendChild(document.createElement("div"));
        this.content.setAttribute("id", "content");
        this.content.appendChild(document.createTextNode("content" in this.dataset ? this.dataset.content : ""));

        const style = document.createElement("style");
        style.textContent = `
            :root {
                --color-accent: inherit;

                --font-color: inherit;
                --font-color-secondary: inherit;
            }

            #wrapper {
                width: 100%;
                display: flex;
                flex-direction: column;
                align-items: center;
            }

            #counter {
                width: 1rem;
                height: 1rem;
                border-radius: 10rem;
                /*border: 1px solid white;*/
                background-color: transparent;
                box-sizing: border-box;
                /*color: white;*/
                display: flex;
                align-items: center;
                justify-content: center;
            }

                #counter::before {
                    content: "x";
                }

                #counter.void {
                    display: none;
                }

            .void {
                display: none;
            }

            #clear-button {
                align-self: flex-start;
                background-color: transparent;
                border: none;
                color: white;
                text-transform: uppercase;
                transform: translate(25%, 0);
                transition: all 0.5s;
                width: 1rem;
                height: 1rem;
            }

                #clear-button > ion-icon {
                    width: 1rem;
                    height: 1rem;
                }

                #clear-button:hover {
                    cursor: pointer;
                    color: #3e1f6d;
                }

            #header {
                  display: flex;
                  justify-content: end;
                  width: 100%;
                  margin-bottom: 0.5rem;
                  align-items: center;
            }

            #heading {
                text-align: center;
                text-align: center;
                color: white;
                text-transform: uppercase;
                font-size: large;
                letter-spacing: 0.25rem;
                margin: 0.5rem 1rem;
            }

            #icon-large, #icon-small {
                color: white;
            }

                #icon-large > ion-icon {
                    width: 3rem;
                    height: 4rem;
                }

                #icon-small > ion-icon {
                    width: 2rem;
                    height: 2rem;
                }

            #content {
                text-align: justify;
                font-weight: lighter;
            }

            `;

        this.shadowRoot.append(style, wrapper);
        
        this.timeout = null;
        this.timeout_delay = null;
        this.fade(("time" in this.dataset && this.dataset.time) ? this.dataset.time : 10000);

        this.addEventListener("mouseover", (event) => {this.re_fade()});
        this.addEventListener("click", (event) => {this.re_fade()});

    }

    re_fade() {
        if ( !(this.timeout == null )) {
            this.fade(("time" in this.dataset && this.dataset.time) ? this.dataset.time : 10000);
        }
    }

    static get observedAttributes() { return ['data-heading', 'data-content', 'data-footer', 'data-time', 'data-icon', 'data-counter']; }

    attributeChangedCallback(name, oldValue, newValue) {
        if ( name == "data-heading" ) {
            this.heading.textContent = ( newValue ? newValue : "" );
        }
        if ( name == "data-content" ) {
            this.content.textContent = ( newValue ? newValue : "" );
        }
        if ( name == "data-footer" ) {
            this.footer.textContent = ( newValue ? newValue : "" );
        }
        if ( name == "data-time" ) {
            this.fade(("time" in this.dataset && this.dataset.time) ? this.dataset.time : 10000);
        }
        if ( name == "data-icon" ) {
            this.icon.innerHTML = '';
            const icon = this.icon.appendChild(document.createElement("ion-icon"));
            icon.setAttribute("name", this.dataset.icon);
        }
        if ( name == "data-counter" ) {
            this.counter.innerText = this.dataset.counter;
            if ( this.dataset.counter == 1 ) {
                this.counter.classList.add("void");
            } else {
                this.counter.classList.remove("void");
            }
            this.re_fade()
        }
    }

    fade(time) {
        window.clearTimeout(this.timeout);
        window.clearTimeout(this.timeout_delay);
        if ( time === true ) {
            this.timeout = clearTimeout(this.timeout);
            this.timeout_delay = clearTimeout(this.timeout_delay);
            return;
        }
        this.timeout_delay = setTimeout (() => {
            this.style["transition"] = `opacity 1s`;
            this.style["opacity"] = "1";
            this.timeout = setTimeout( () => {
                if ( typeof time === "number" ) {
                    this.style["transition"] = `opacity ${ time / 1000 }s`;
                    this.style["opacity"] = "0";
                    this.timeout = setTimeout(() => {
                        this.remove();
                    }, time);
                } else if ( time === true ) {

                } else {
                    console.log(`Invalid fade time value: ${time}`);
                }
            }, 2500);
        }, 10);

    }

    static from_html(html) {
        var template = document.createElement('template');
        html = html.trim();
        template.innerHTML = html;
        return template.content.firstChild;
    }

    static add(config) {
        let exists = false;
        const container = document.querySelector("#notification-container");
        for ( const element of container.childNodes) {
            if ( Object.hasOwn(config, "id") && element.dataset.id == config.id) {
                element.dataset.counter = parseInt(element.dataset.counter ? element.dataset.counter : 1) + 1;
                return ;
            }
        }

        // const notification = document.createElement("popup-notification", {dataset: {size: size, time: time}});
        let constructorStr = "<popup-notification ";
        for (const i of Object.keys(config)) {
            constructorStr += `data-${i}="${config[i]}" `;
        }
        constructorStr += "></popup-notification>"
        const notification = this.from_html(constructorStr)
        notification.setAttribute("class", "notification");
        container.prepend(notification);
    }

    static remove_all() {
        const container = document.querySelector("#notification-container");
        while (container.firstChild) {
            if ( container.firstChild.nodeName != "BUTTON" ) {
                console.log(container.firstChild.nodeName);
                container.removeChild(container.firstChild);
            } else {
                break;
            }
        }
    }
}

customElements.define("popup-notification", Notification);

document.querySelector("#clear-notifications").addEventListener("click", Notification.remove_all);


$(document).ready(function() {

    document.querySelector("#symbol-input").addEventListener("keydown", (event) => {     
        let key = event.key;
        if (!key.match(/[A-Za-z,.\-]/)) {
            event.preventDefault();
        } 
    });

    const order = ["dark", "light", "system"] 
    const schemes = {"dark": "moon-outline", "light": "sunny-outline", "system": "desktop-outline"};

    const button_icon = document.querySelector("#scheme-cycler").querySelector("ion-icon");

    // let scheme = localStorage.getItem('color-theme');
    let scheme = Cookie.get("color-theme");

    if( scheme === undefined || scheme === null ) {
        // localStorage.setItem('color-theme', "dark");
        Cookie.set("color-theme", "dark", "31536000");
    }

    Cookie.set("color-theme", scheme, "31536000");

    button_icon.setAttribute("name", schemes[scheme] ? schemes[scheme] : "moon-outline");

    document.querySelector("#scheme-cycler").addEventListener("click", (event) => {    

        const button_icon = document.querySelector("#scheme-cycler").querySelector("ion-icon");
        let next = order.indexOf(Cookie.get("color-theme")); // localStorage.getItem('color-theme');
        
        if ( next + 1 >= order.length) {
            next = 0;
        } else {
            next = next + 1;
        }

        let scheme = order[next];

        if ( scheme == "light" ) {
            document.documentElement.className = '';
            document.documentElement.classList.add("light");
        } else if ( scheme == "dark" ) {
            document.documentElement.className = '';
            document.documentElement.classList.add("dark");
        } else {
            document.documentElement.className = '';
        }

        // localStorage.setItem('color-theme', scheme);
        Cookie.set("color-theme", scheme, "31536000");

        button_icon.setAttribute("name", schemes[scheme]);
    });

    $(window).on('popstate',function(event) {
        const memory = event.originalEvent.state;
        if (Object.hasOwn(memory, 'data')) {
            $("#symbol-input").value = memory.data.ticker;
            loadValues(memory.data);
        } else if (Object.hasOwn(memory, 'ticker')) {
            load(memory.ticker);
        }
    });

    // $("#searchbox").submit(function(event) {
    //    search(event);
    // });

});

function loadValues(data) {
    for (const [key, value] of Object.entries(data)) {
        if ( Array.isArray(value) ) {
            for ( let i = 0; i < value.length; i++) { //
                let element = document.querySelector(`#${key}-${i}`);
                if ( !element ) {
                    continue;
                }
                let elem_value = value[i];
                element.dataset.value = elem_value["value"];
                element.dataset.color = elem_value["color"];
            }
        } else {
            let element = document.querySelector(`#${key}`);
            if ( element ) {
                if (typeof value === 'string' || value instanceof String || value === null) {
                    element.dataset.text = value;
                } else {
                    element.dataset.value = value["value"];
                    element.dataset.color = value["color"];
                }
            } else {
                if ( typeof data[key] === 'object' && data[key] != null ) {
                    for (const [sec_key, sec_value] of Object.entries(data[key])) {
                        element = document.querySelector(`#${key}-${sec_key}`);

                        if ( element ) {
                            if ( Array.isArray(sec_value) ) {
                                let j = sec_value.length - 1;
                                for (let i = 0; i < sec_value.length; i++) {
                                    element = document.querySelector(`#${key}-${sec_key}-${i}`);
                                    if ( !element ) {
                                        continue;
                                    }
                                    let elem_value = sec_value[i];
                                    element.dataset.value = elem_value["value"];
                                    element.dataset.color = elem_value["color"];
                                }
                            } else if (typeof sec_value === 'string' || sec_value instanceof String || sec_value === null) {
                                element.dataset.text = sec_value;
                            } else {
                                element.dataset.value = sec_value["value"];
                                element.dataset.color = sec_value["color"];
                            }
                        }
                    }
                }
            }
        }
    }
}

function load(ticker) {

    $(document).ready(function() {

        $("#symbol-input").val(ticker);

        $("#searchbox").submit(); 

    });
}