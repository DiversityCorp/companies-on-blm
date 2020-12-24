import apsw
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import json

con=apsw.Connection("./companies-on-blm.db")
cur=con.cursor()

company_statements = list(cur.execute("select blm_statements from companies where blm_statements is not null;"))

word_cloud_text = []

stopwords = set(STOPWORDS)
stopwords.add("u")

for blm_statements in company_statements:
  for statements in blm_statements:
      statement = json.loads(statements)
      for s in statement:
        if "raw_text" in s:
          word_cloud_text.append(s["raw_text"])

text = " ".join(word_cloud_text)
wordcloud = WordCloud(stopwords=stopwords).generate(text)
plt.figure()
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.show()