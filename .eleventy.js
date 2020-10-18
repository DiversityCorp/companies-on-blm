const dateFns = require("date-fns");

module.exports = function (eleventyConfig) {
  eleventyConfig.addFilter("dateReadable", (date) => dateFns.format(date, "dd MMM yyyy"));
  eleventyConfig.addPassthroughCopy("images");

  return {
    templateFormats: ["njk", "md", "css"],
    htmlTemplateEngine: "njk",
    dataTemplateEngine: "njk",
  };
};
