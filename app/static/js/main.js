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
            cards: "",
            allowEmpty: "",
            allowArt: ""
    },
    methods: {
        getSearch: function (e) {
            const response = axios
                .post(
                    "/search", 
                    {
                        cards: this.$refs.cards.value.split(/\r?\n/),
                        allow_empty: this.allowEmpty,
                        allow_art: this.allowArt
                    }
                )
                .then(response => (search.searchResult = response.data));
        }
    }
})