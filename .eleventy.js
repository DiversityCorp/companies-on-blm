module.exports = function (eleventyConfig) {
  return {
    templateFormats: ["njk", "md", "png"],
    htmlTemplateEngine: "njk",
    dataTemplateEngine: "njk",
  };
};
