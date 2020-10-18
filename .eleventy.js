const dateFns = require("date-fns");

module.exports = function (eleventyConfig) {
  eleventyConfig.addFilter("dateReadable", (date) => dateFns.format(date, "dd MMM yyyy"));

  return {
    templateFormats: ["njk", "md", "png", "css"],
    htmlTemplateEngine: "njk",
    dataTemplateEngine: "njk",
  };
};
