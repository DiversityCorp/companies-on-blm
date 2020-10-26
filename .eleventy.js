const dateFns = require("date-fns");

module.exports = function (eleventyConfig) {
  eleventyConfig.addNunjucksFilter("sortByPostedDate", (companiesCollection) =>
    companiesCollection.sort((a, b) => {
      if (a.data.blm_statements && b.data.blm_statements) {
        return a.data.blm_statements[0].date_posted - b.data.blm_statements[0].date_posted;
      }
    })
  )
  // date.toUTCString() => "Fri, 02 Feb 1996 03:04:05 GMT"
  eleventyConfig.addFilter("dateReadable", (date) => date.toUTCString().split(" ").slice(1, 4).join(" "));
  eleventyConfig.addPassthroughCopy("./images");
  eleventyConfig.addPassthroughCopy("./CNAME");
  eleventyConfig.setDataDeepMerge(true);

  eleventyConfig.addCollection("tagList", function(collection) {
    let tagSet = new Set();
    collection.getAll().forEach(function(item) {
      if( "tags" in item.data ) {
        let tags = item.data.tags;

        tags = tags.filter(function(item) {
          switch(item) {
            // this list should match the `filter` list in tags.njk
            case "all":
            case "taglist":
            case "companies":
              return false;
          }

          return true;
        });

        for (const tag of tags) {
          tagSet.add(tag);
        }
      }
    });

    // returning an array in addCollection works in Eleventy 0.5.3
    return [...tagSet];
  });

  return {
    templateFormats: ["njk", "md", "css"],
    htmlTemplateEngine: "njk",
    dataTemplateEngine: "njk",
  };
};
