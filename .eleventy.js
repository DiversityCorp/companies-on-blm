const dateFns = require("date-fns");

module.exports = function (eleventyConfig) {
  eleventyConfig.addFilter("dateReadable", (date) => dateFns.format(date, "dd MMM yyyy"));

  return {
    templateFormats: ["njk", "md", "css", "png"],
    htmlTemplateEngine: "njk",
    dataTemplateEngine: "njk",
  };
};
