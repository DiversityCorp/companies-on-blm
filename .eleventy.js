const dateFns = require("date-fns");

module.exports = function (eleventyConfig) {
  eleventyConfig.addCollection("companiesSortedByBLMStatementDate", (collectionApi) => collectionApi.getFilteredByTag("companies").sort((a, b) => {
    if (a.data.blm_statements && b.data.blm_statements) {
      return a.data.blm_statements[0].date_posted - b.data.blm_statements[0].date_posted;
    }
  }));
  eleventyConfig.addFilter("dateReadable", (date) => dateFns.format(date, "dd MMM yyyy"));
  eleventyConfig.addPassthroughCopy("./images");
  eleventyConfig.addPassthroughCopy("./CNAME");

  return {
    templateFormats: ["njk", "md", "css"],
    htmlTemplateEngine: "njk",
    dataTemplateEngine: "njk",
  };
};
