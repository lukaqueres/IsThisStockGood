class Value extends HTMLElement {
    constructor(...args) {
        super(...args);

        this.#text();
    }

    value(text) {
        this.dataset.text = text
    }

    static get observedAttributes() { return ['data-content']; }

    attributeChangedCallback(name, oldValue, newValue) {
        if ( name == "data-content" ) {
            this.textContent =  "content" in this.dataset ? this.dataset.text : "-"
        }
    }

    #text() {
        this.textContent =  "content" in this.dataset ? this.dataset.text : "-"
    }
}

customElements.define("general-value", Value);

class Link extends HTMLElement {
    constructor(...args) {
        super(...args);

        this.#text();

        this.addEventListener("click", (event) => { this.onclick(event); });

    }

    value(text) {
        this.dataset.url = text;
    }

    static get observedAttributes() { return ['data-url']; }

    attributeChangedCallback(name, oldValue, newValue) {
        if ( name == "data-url" ) {
            this.#text();
        }
    }

    onclick(event) {
        if ( "url" in this.dataset ) {
            window.open( "url" in this.dataset ? this.dataset.url : "#", '_blank').focus();
        }
        return
    }

    #text() {
        this.textContent =  "url" in this.dataset ? this.dataset.url.substring(this.dataset.url.indexOf(".") + 1) : "-";
    }

}

customElements.define("link-value", Link);

class MapLink extends HTMLElement {
    constructor(...args) {
        super(...args);

        this.#text();

        this.addEventListener("click", (event) => { this.onclick(event); });

    }

    value(text) {
        this.dataset.location = text
    }

    static get observedAttributes() { return ['data-location']; }

    attributeChangedCallback(name, oldValue, newValue) {
        if ( name == "data-location" ) {
            this.#text()
        }
    }

    onclick(event) {
        if ( "location" in this.dataset ) {
            window.open(`https://maps.google.com/?q=${this.dataset.location}`, '_blank').focus();
        }
        return
    }

    #text() {

        if ("location" in this.dataset) {

            console.log(this.dataset.location.split("-")[0]);
            this.textContent = this.dataset.location.split("-")[0];
        } else {
            this.textContent = "-";
        }
    }

}

customElements.define("map-value", MapLink);

class Info extends HTMLElement {
    constructor(...args) {
        super(...args);

        this.attachShadow({ mode: "open" });

        const wrapper = document.createElement("div");
        wrapper.setAttribute("class", "wrapper");

        const icon = this.childNodes[0]

        wrapper.appendChild(icon);

        const window = wrapper.appendChild(document.createElement("div"));
        window.setAttribute("class", "window");

        this.window = window;

        const text = window.appendChild(document.createTextNode("info" in this.dataset ? this.dataset.info : "-"));

        const style = document.createElement("style");
        style.textContent = `
            :root {
                --color-accent: inherit;
                --color-primary: inherit;
                --color-primary-secondary: inherit;
                --font-color: inherit;
            }

            .wrapper {
                width: inherit;
                height: inherit;
            }

            ion-icon {
                width: inherit;
                height: inherit;
            }

            .window {
                z-index: 98;
                position: absolute;
                display: none;
                background-color: var(--color-primary);
                color: var(--font-color);
                padding: 1rem;
                border: 1px solid var(--color-accent);
                font-size: smaller;
                text-align: justify;
                width: 15rem;
                transform: translate(-1rem, 0.5rem);
                box-shadow: 0 0 2px var(--color-accent);
                border-radius: 0.2rem;
            }
                /*
                .window::before {
                    display: block;
                    content: '';
                    position: absolute;
                    width: 0;
                    height: 0;
                    transform: translate(-0.25rem, -2.5rem);
                    border: 12px solid transparent;
                      border-bottom-color: transparent;
                    border-bottom-color: var(--color-accent);
                }
                */
                .window.active {
                    display: block;
                }
            `;

        this.shadowRoot.append(style, wrapper);

        icon.addEventListener("click", (event) => { this.onclick(event); });

    }

    onclick(event) {
        if ( "info" in this.dataset ) {
            //this.window.classList.toggle("active");
            const notifications = document.querySelector("notifications-container");
            notifications.add("title" in this.dataset ? this.dataset.title : "Info", "info" in this.dataset ? this.dataset.info : "-", null, "icon" in this.dataset ? this.dataset.icon : null, null, true );
        }
    }

}

customElements.define("popup-info", Info);