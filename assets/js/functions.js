String.prototype.format = function () {
  var i = 0, args = arguments;
    return this.replace(/{}/g, function () {
      return typeof args[i] != 'undefined' ? args[i++] : '';
    });
};
  
class Cookie {

	static get(cname) {
		return document.cookie
		.split("; ")
		.find((row) => row.startsWith(`${cname}=`))
		?.split("=")[1];
	}

	static set(cname, cvalue, cex = null) {
		if ( cex === null ) {
			document.cookie = cname + "=" + cvalue + ";path=/";
		} else {
			document.cookie = cname + "=" + cvalue + ";max-age=" + cex + ";SameSite=Lax;path=/";
		}
	}

}

class Loading {
    static timeout = null

    static start() {
        const submit_ticker = document.querySelector("#sumbit-ticker");
        submit_ticker.disabled = true;

        const submit_ticker_icon = submit_ticker.querySelector("ion-icon");
        submit_ticker_icon.setAttribute("name", "sync-outline");
        submit_ticker_icon.classList.add("load");

        const symbol_input = document.querySelector("#symbol-input");
        symbol_input.disabled = true;

        this.timeout = setTimeout(() => {
            this.stop()
          }, 300000);
          
    }

    static stop() {
        clearTimeout(this.timeout);
        const submit_ticker = document.querySelector("#sumbit-ticker");
        submit_ticker.disabled = false;

        const submit_ticker_icon = submit_ticker.querySelector("ion-icon");
        submit_ticker_icon.setAttribute("name", "search-outline");
        submit_ticker_icon.classList.remove("load");

        const symbol_input = document.querySelector("#symbol-input");
        symbol_input.disabled = false;
    }
}
