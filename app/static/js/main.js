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
            this.cards = this.cards.split(/\r?\n/);

            if (!this.cards.length) {
                this.errors.push("List of cards cannot be empty");
                return
            }

            if (this.cards.length > 15) {
                this.errors.push("List cannot be longer than 15 cards");
            }

           for (item of this.cards) {
                if (/^ *$/.test(item)) {
                    this.errors.push("Card name cannot be empty");
                }
                else if (item.length < 3) {
                    this.errors.push("Card name cannot be shorter than 3 symbols");
                }
            };
            
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