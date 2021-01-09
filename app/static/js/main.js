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
        getSearch: async function (e) {
            const cards = this.$refs.cards.value;
            const response = axios
                .post("/search", cards.split(/\r?\n/))
                .then(response => (search.searchResult = response));
        }
    }
})