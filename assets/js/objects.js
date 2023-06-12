class SearchForm extends HTMLFormElement {
    constructor() {
        super();
        $(this).on('submit', (event) => { 
            event.preventDefault();
            this.search(event);
            console.log(event);
            return false;
        });

        this.prototype.search = function (event) {
            this.search(event);
        };
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