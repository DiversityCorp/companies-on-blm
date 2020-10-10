module.exports = function(eleventyConfig) {
    return {
        templateFormats: [
            "njk",
            "md",
        ],
        htmlTemplateEngine: "njk",
        dataTemplateEngine: "njk",
    }
};