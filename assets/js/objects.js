class SearchForm extends HTMLFormElement {
    constructor() {
        super();
        $(this).on('submit', (event) => { 
            this.search(event);
            return false;
        });
    }
  
    search(event) {
        event.preventDefault();
    
        let $form = $(this);
        const path = $form.attr('action');
    
        let $ticker = $('#symbol-input').val();
    
        if ( !$ticker ) {
            Notification.add({
                header: `No ticker`,
                icon: "alert-outline",
                description: "Provided ticker is empty, please input correct ticker",
                id: "no_ticker",
                type: "error"
            });
            return
        }
    
        Loading.start()
    
        let getting = $.get(path.format($ticker))
            .fail(function (jqXHR, textStatus) {
                history.pushState({ticker: $ticker}, null, `/${$ticker.toUpperCase()}`);
    
                console.log(jqXHR);
    
                Notification.add({
                    header: `${jqXHR.status} ${textStatus}`,
                    icon: "bug-outline",
                    description: jqXHR.responseJSON.error,
                    id: textStatus,
                    type: "error"
                });
            })
            .done(function(json_data, statusText, xhr) {
                history.pushState({data: json_data}, null, `/${$ticker.toUpperCase()}`);
                loadValues(json_data);
            })  
            .always(function() {
                Loading.stop();
            });
    }
    
  
    connectedCallback() {

    }
}
  
customElements.define('search-form', SearchForm, {
extends: 'form'
});

class Value extends HTMLElement {
    constructor() {
        super();

        this.attachShadow({ mode: "open" });

        this.wrapper = document.createElement("div");
        this.wrapper.setAttribute("id", "wrapper");

        this.name = this.wrapper.appendChild(document.createElement("p"));
        this.name.appendChild(document.createTextNode("name" in this.dataset ? this.dataset.name : ""));

        let value = this.dataset.value ? this.dataset.value : "-"

        this.value = this.wrapper.appendChild(document.createElement("p"));
        this.value.setAttribute("id", "value");
        this.value.appendChild(document.createTextNode(this.check_value(value)));

        this.colorIndicator = this.wrapper.appendChild(document.createElement("div"));
        this.colorIndicator.setAttribute("id", "color-indicator");

        const style = document.createElement("style");
        style.textContent = `
            :host {
                display: inline-block;
                margin-inline: 1rem;
                --background-secondary-color: #2e2c37;
                --background-color: inherit;
                --custom-value-color: transparent;
            }

            #wrapper {
                display: flex;
                justify-content: center;
                flex-direction: column;
                margin-left: 1rem;
            }

                #values-container {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }

                #wrapper > custom-value {
                    background-color: var(--background-color);
                }

            #value {
                border: 2px solid var(--background-secondary-color);
                border-radius: 0.2rem;
                padding: 1rem;
                background-color: var(--background-color);
                margin: 0;
                z-index: 5;
                position: relative;
                text-align: center;
            }

            #name {

            }

            #color-indicator {
                background-color: var(--custom-value-color);
                width: 3rem;
                height: 3rem;
                position: relative;
                border-radius: 0.2rem;
                transform: translate(-1rem, -2rem);
                z-index: 1;
            }
        `;

        this.shadowRoot.append(style, this.wrapper);

    }

    static get observedAttributes() { return ['data-name', 'data-color', 'data-value']; }

    attributeChangedCallback(name, oldValue, newValue) {
        switch (name) {
            case "data-name":
                this.name.innerText = this.dataset.name;
                break;

            case "data-color":
                const sheet = new CSSStyleSheet();
                sheet.replaceSync(`:host { --custom-value-color: ${this.dataset.color ? this.dataset.color : "transparent"};}`);
                const elemStyleSheets = this.shadowRoot.adoptedStyleSheets;
                this.shadowRoot.adoptedStyleSheets = [...elemStyleSheets, sheet];
                //this.colorIndicator.style.backgroundColor = this.dataset.color ? this.dataset.color : "transparent";
                break;

            case "data-value":

                let value = this.dataset.value ? this.dataset.value : "-"

                this.value.innerText = this.check_value(value);
                break;
        }
    }

    check_value(value) {
        if ( !isNaN(value) ) {
            value = Number(value).toFixed(2);
        } else if ( value == null || value == "null") {
            value = "-";
        }

        let leading = value.split(".")[0] || "";

        let trailing = value.split(".")[1] || "";
        trailing = trailing == "00" ? "" : trailing;
        
        return leading.replace(/(.{3})/g,"$& ").trim() + ( trailing ? `.${trailing}` : "" );
    }

}

customElements.define("custom-value", Value);

class Text extends HTMLElement {
    static map_url = "https://maps.google.com/?q={}";

    constructor() {
        super();

        this.attachShadow({ mode: "open" });

        this.wrapper = document.createElement("div");
        this.wrapper.setAttribute("id", "wrapper");

        this.name = this.wrapper.appendChild(document.createElement("p"));
        this.name.appendChild(document.createTextNode("name" in this.dataset ? this.dataset.name : ""));

        let text = this.dataset.text ? this.dataset.text : "-"

        console.log(this)

        if ( "type" in this.dataset && ( this.dataset.type == "link" || this.dataset.type == "map")) {
            this.link = this.wrapper.appendChild(document.createElement("a"));
            this.link.setAttribute("id", "text");
            this.link.setAttribute("target", "_blank");

            this.link.setAttribute("href", this.check_link(text));
            this.link.appendChild(document.createTextNode(this.check_text(text)));
        } else {
            this.text = this.wrapper.appendChild(document.createElement("p"));
            this.text.setAttribute("id", "text");
            this.text.appendChild(document.createTextNode(this.check_text(text)));
        }

        const style = document.createElement("style");
        style.textContent = `
            :host {
                display: inline-block;
                margin-inline: 1rem;
                --background-secondary-color: #2e2c37;
                --background-color: inherit;
                --custom-value-color: transparent;
            }

            #wrapper {
                display: flex;
                justify-content: center;
                flex-direction: column;
                margin-left: 1rem;
            }

                #values-container {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }

                #wrapper > custom-value {
                    background-color: var(--background-color);
                }

            #value {
                border: 2px solid var(--background-secondary-color);
                border-radius: 0.2rem;
                padding: 1rem;
                background-color: var(--background-color);
                margin: 0;
                z-index: 5;
                position: relative;
                text-align: center;
            }

            #name {

            }

        `;

        this.shadowRoot.append(style, this.wrapper);

    }

    static get observedAttributes() { return ['data-name', 'data-text']; }

    attributeChangedCallback(name, oldValue, newValue) {
        switch (name) {
            case "data-name":
                this.name.innerText = this.dataset.name;
                break;

            case "data-text":

                let text = this.dataset.text ? this.dataset.text : "-"

                if ( this.link ) {
                    this.link.innerText = this.check_text(text);
                    this.link.setAttribute("href", this.check_link(text));
                } else {
                    this.text.innerText = this.check_text(text);
                }
                break;
        }
    }

    check_text(text) {
        if ( !text || text == "null" ) {
            return "-";
        }
        if ( !"type" in this.dataset && this.dataset.type ) {
            return text || "-"
        }
        if ( this.dataset.type == "link" ) {
            var matches = text.match(/^https?\:\/\/([^\/?#]+)(?:[\/?#]|$)/i);
            text = matches && matches[1];
        } else {
            text = text;
        }
        
        return text || "-";
    }

    check_link(value) {
        if ( !"type" in this.dataset && this.dataset.type ) {
            return "#"
        }
        if ( this.dataset.type == "link" ) {
            value = value != "-" ? value : "#";
        } else if ( this.dataset.type == "map" ) {
            value = Text.map_url.format(value.replace("<road->>", " - "));
        } else {
            value = "#";
        }
        
        return value;
    }

}

customElements.define("custom-text", Text);