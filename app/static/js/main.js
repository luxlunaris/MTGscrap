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
            const cards = this.$refs.cards.value;
            console.log("beginning of post")
            const response = await axios.post("/search", cards);
            console.log("end of post")
            search.searchResult = response;
        }
    }
})