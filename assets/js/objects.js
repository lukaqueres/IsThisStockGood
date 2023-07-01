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
                let recent = null
                try {
                    recent = JSON.parse(Cookie.get("recent_tickers"));
                } catch (error) {
                    recent = null;
                }
                if ( !recent ) {
                    recent = [];
                    recent.unshift($ticker);
                    Cookie.set("recent_tickers", JSON.stringify(recent), "31536000");
                } else {
                    if ( recent.includes($ticker) ) {
                        
                        const index = recent.indexOf($ticker);
                        if (index > -1) {
                            recent.splice(index, 1);
                        }
                        recent.unshift($ticker);
                        Cookie.set("recent_tickers", JSON.stringify(recent), "31536000");
                    } else {
                        if ( recent.length < 5 ) {
                            recent.unshift($ticker);
                            Cookie.set("recent_tickers", JSON.stringify(recent), "31536000");
                        } else {
                            recent.pop();
                            recent.unshift($ticker);
                            Cookie.set("recent_tickers", JSON.stringify(recent), "31536000");
                        }
                    }
                }
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

class FavouriteForm extends HTMLFormElement {
    constructor() {
        super();
        $(this).on('submit', (event) => { 
            this.favourite(event);
            return false;
        });
    }

    static from_html(html) {
        var template = document.createElement('template');
        html = html.trim();
        template.innerHTML = html;
        return template.content.firstChild;
    }
  
    favourite(event) {
        event.preventDefault();

        let $ticker = $('#favourite-ticker-added').val();
        if ( !$ticker ) {
            return 
        }
        if( Cookie.get("favourite-tickers") === undefined ) {
            // localStorage.setItem('color-theme', "dark");
            Cookie.set("favourite-tickers", JSON.stringify([$ticker]), "31536000");
        } else {
            let favourites = [];
            try {
                favourites = JSON.parse(Cookie.get('favourite-tickers'));
            } catch (error) {
                favourites = [];
            }
            if ( !favourites.includes($ticker) ) {
                favourites.push($ticker);
            } else {
                return 
            }
            Cookie.set("favourite-tickers", JSON.stringify(favourites), "31536000");
        }
        let new_fav = FavouriteForm.from_html(`<favourite-ticker-display data-ticker="${$ticker}"></favourite-ticker-display>`);

        document.querySelector("#favourites-container").appendChild(new_fav);


    }
    
}
  
customElements.define('favourite-form', FavouriteForm, {
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
        this.value.appendChild(document.createTextNode(Value.check_value(value)));

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

                this.value.innerText = Value.check_value(value);
                break;
        }
    }

    static check_value(value) {
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

class SideBar extends HTMLElement {
    constructor() {
        super();

        this.attachShadow({ mode: "open" });

        this.wrapper = document.createElement("div");
        this.wrapper.setAttribute("id", "wrapper");

        if ( window.localStorage.getItem("sidebar-expand") == undefined ) {
            window.localStorage.setItem("sidebar-expand", "true");
            this.dataset.expand = "true";
        } else {
            this.dataset.expand = window.localStorage.getItem("sidebar-expand");
        }

        this.resize_btn = this.wrapper.appendChild(document.createElement("button"));
        this.resize_btn.setAttribute("id", "sidebar-resize");
        this.resize_btn.setAttribute("aria-label", "Expand / Hide side panel");

        this.resize_btn.addEventListener("click", () => this.resize() );

        const resize_btn_icon = this.resize_btn.appendChild(document.createElement("ion-icon"));
        resize_btn_icon.setAttribute("name", "chevron-forward-circle");

        resize_btn_icon.setAttribute("aria-hidden", "true");
        

        const style = document.createElement("style");
        style.textContent = `

        :host {

        }

        :host([data-expand="true"]) {
            
        }

        button:hover {
            cursor: pointer;
        }

        #sidebar-resize {
            position: absolute;
            top: 4rem;
            right: -0.5rem;
            width: 1.5rem;
            height: 1.5rem;
            color: var(--accent-color);
            background-color: transparent;
            border: 1px solid transparent;
            width: 1.5rem;
            height: 1.5rem;
            transition: transform 0.2s linear;
        }

            #sidebar-resize > ion-icon {
                width: inherit;
                height: inherit;
            }

            :host([data-expand="true"]) #sidebar-resize > ion-icon {
                transform: rotate(180deg);
            }
        `;

        this.slots = document.createElement("slot");

        this.shadowRoot.append(style, this.wrapper, this.slots);

    }

    connectedCallback() {

    }

    resize() {
        if ( this.dataset.expand == "true" ) {
            this.dataset.expand = "false";
            window.localStorage.setItem("sidebar-expand", "false");
        } else {
            this.dataset.expand = "true";
            window.localStorage.setItem("sidebar-expand", "true");
        }
    }

}

customElements.define("side-bar", SideBar);

class Favourite extends HTMLElement {
    constructor() {
        super();

        this.attachShadow({ mode: "open" });

        this.wrapper = document.createElement("div");
        this.wrapper.setAttribute("id", "wrapper");

        this.ticker = this.dataset.ticker || null;

        if ( !this.ticker ) {
            this.message = this.wrapper.appendChild(document.createElement("span"));
            this.message.appendChild(document.createTextNode("We had some error"));
            return
        }

                
        this.head = this.wrapper.appendChild(document.createElement("div"));
        this.head.setAttribute("id", "head");
        
        this.ticker_disp = this.head.appendChild(document.createElement("span"));
        this.ticker_disp.setAttribute("id", "ticker");
        this.ticker_disp.appendChild(document.createTextNode(this.dataset.ticker))

        this.name = this.head.appendChild(document.createElement("span"));
        this.name.setAttribute("id", "name");

        this.remove_btn = this.head.appendChild(document.createElement("button"));
        this.remove_btn.setAttribute("id", "fav-remove");
        this.remove_btn.setAttribute("aria-label", "Remove from favourites");

        this.remove_btn.addEventListener("click", () => this.delete() );

        const remove_btn_icon = this.remove_btn.appendChild(document.createElement("ion-icon"));
        remove_btn_icon.setAttribute("name", "close-circle-outline");

        remove_btn_icon.setAttribute("aria-hidden", "true");

        this.prices = this.wrapper.appendChild(document.createElement("div"));
        this.prices.setAttribute("id", "price");

        this.sticker_price = this.prices.appendChild(document.createElement("p"));
        this.sticker_price.appendChild(document.createTextNode("Sticker Price"));

        this.current_price = this.prices.appendChild(document.createElement("p"));
        this.current_price.appendChild(document.createTextNode("Current Price"));

        this.margin_of_safety_price = this.prices.appendChild(document.createElement("p"));
        this.margin_of_safety_price.appendChild(document.createTextNode("Margin of Safety Price"));


        this.colors = this.wrapper.appendChild(document.createElement("div"));
        this.colors.setAttribute("id", "colors");

        const style = document.createElement("style");
        style.textContent = `

        :host {
            width: 100%;
            background-color: var(--background-secondary-color);
            padding: 1rem;
            border-radius: 1rem;
            display: grid;
        }

        #ticker {

        }

        #name {
            margin-left: 0.5rem;
            color: var(--accent-color);
        }

        #head {
            display: flex;
        }

        #fav-remove {
            margin-left: auto;
            border: none;
            background-color: transparent;
            width: 1.5rem;
            height: 1.5rem;
            padding: 0;
        }

            #fav-remove:hover {
                cursor: pointer;
            }

            #fav-remove > ion-icon {
                width: 1.5rem;
                height: 1.5rem;
            }

        #price {
            display: flex;
        }

            #price > * {
                background: var(--background-color);
                padding: 0.5rem 1rem;
                border-radius: 0.5rem;
                min-width: 11rem;
                margin-left: 1rem;
            }

        #colors {
            width: 100%;
            display: flex;
            height: 0.5rem;
            border-radius: 10rem;
            background: var(--background-color);
            overflow: hidden;
        }

            #colors > * {
                flex: 1;
            }

        .load {
            -webkit-animation: loading-spin 3s linear infinite;
	        animation: loading-spin 3s cubic-bezier(.79,.14,.15,.86) infinite;
        }

        @-webkit-keyframes loading-spin {
            0% { filter: brightness(100%); }
            100% { filter: brightness(50%); }
        }
        
        @keyframes loading-spin {
            0% { filter: brightness(100%); }
            50% { filter: brightness(50%);}
            100% { filter: brightness(100%); }
        }
        `;

        this.shadowRoot.append(style, this.wrapper);

        $(document).ready(() => {
            this.load();
        });

    }

    load() {
        this.name.classList.add("load");
        this.colors.classList.add("load");
        let prices = this.prices.childNodes;
        for(var i=0; i< prices.length; i++) {
            if (prices[i].nodeName.toLowerCase() == 'p') {
                prices[i].classList.add("load");
             }
        }
    }

    unload() {
        this.name.classList.remove("load");
        this.colors.classList.remove("load");
        let prices = this.prices.childNodes;
        for(var i=0; i< prices.length; i++) {
            if (prices[i].nodeName.toLowerCase() == 'p') {
                prices[i].classList.remove("load");
             }
        }
    }

    delete() {
        if( Cookie.get("favourite-tickers") === undefined ) {
            // localStorage.setItem('color-theme', "dark");
            Cookie.set("favourite-tickers", JSON.stringify([]), "31536000");
        } else {
            let favourites = [];
            try {
                favourites = JSON.parse(Cookie.get('favourite-tickers'));
            } catch (error) {
                favourites = [];
            }
            if ( favourites.includes(this.ticker) ) {
                favourites.splice(favourites.indexOf(this.ticker), 1);
            }
            Cookie.set("favourite-tickers", JSON.stringify(favourites), "31536000");
        }
        this.remove();
    }
      
    connectedCallback() {
        let getting = $.get("/search/{}".format(this.ticker))
            .fail(function (jqXHR, textStatus) {

            })
            .done((json_data, statusText, xhr) => {
                this.data(json_data);
            })  
            .always(() => {
                this.unload();
            });
    }

    data(json_data) {
        this.sticker_price.innerHTML += `: ${Value.check_value(json_data.sticker_price.value)}`;
        this.name.innerHTML = `${json_data.shortName}`;
        this.current_price.innerHTML += `: ${Value.check_value(json_data.current_price.value)}`;
        this.margin_of_safety_price.innerHTML += `: ${Value.check_value(json_data.margin_of_safety_price.value)}`;

        for ( const color of this.value_colors(json_data) ) {
            this.colors.appendChild(document.createElement("span")).style.backgroundColor = color;
        }
    }

    value_colors(json_data) {
        let colors = [];
        for (const value of Object.values(json_data)) {
            if (
                typeof value === 'object' &&
                value !== null
            ) {
                for (const n_value of Object.values(value)) {
                    if (
                        typeof n_value === 'object' &&
                        n_value !== null
                    ) {
                        if ( Object.hasOwn(n_value, 'color') ) {
                            colors.push(n_value.color);
                        }
                    }
                }
            }
        }
        return colors;
    }

}

customElements.define("favourite-ticker-display", Favourite);