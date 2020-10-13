module.exports = function (eleventyConfig) {
  return {
    templateFormats: ["njk", "md", "png", "css"],
    htmlTemplateEngine: "njk",
    dataTemplateEngine: "njk",
  };
};
