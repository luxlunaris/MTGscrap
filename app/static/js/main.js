var search = new Vue({
    el: "#search-result",
    data: {
        isLoading: false,
        searchResult: "",
        isEmptyDisabled: false
    },
    delimiters: ["${", "}$"]
})

var form = new Vue({
    el: "#search-form",
    data: {
            errors: [],
            cards: "",
            allowEmpty: "",
            allowArt: ""
    },
    methods: {
        flushErrors: function (e) {
            this.errors = []
        },
        checkForm: function (e) {
            if (!this.cards) {
                this.errors.push("List of cards cannot be empty")
            }
        },
        getSearch: function (e) {
            this.flushErrors();
            this.checkForm();

            if (this.errors.length)
                return;
            
            search.isLoading = true;

            axios
                .post(
                    "/search", 
                    {
                        cards: this.cards.split(/\r?\n/),
                        allow_empty: this.allowEmpty || false,
                        allow_art: this.allowArt || false
                    }
                )
                .then(
                    function (response) {
                        search.isLoading = false;
                        search.searchResult = response.data;
                    }
                );
        }
    },
    delimiters: ["${", "}$"]
})