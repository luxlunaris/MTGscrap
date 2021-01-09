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
    methods: {
        getSearch: function (e) {
            const response = axios
                .post(
                    "/search", 
                    {
                        cards: this.$refs.cards.value.split(/\r?\n/),
                        allow_empty: this.$refs.empty.value,
                        allow_art: this.$refs.art.value
                    }
                )
                .then(response => (search.searchResult = response.data));
        }
    }
})