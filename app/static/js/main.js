var search = new Vue({
    el: "#search-result",
    data: {
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

            const response = axios
                .post(
                    "/search", 
                    {
                        cards: this.cards.split(/\r?\n/),
                        allow_empty: this.allowEmpty || false,
                        allow_art: this.allowArt || false
                    }
                )
                .then(response => (search.searchResult = response.data));
        }
    },
    delimiters: ["${", "}$"]
})