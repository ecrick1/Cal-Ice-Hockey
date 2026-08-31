/**
 * Put the club's own article archive into the site's news list.
 *
 * REAL CONTENT. Every headline, date, paragraph and cover here was written or
 * chosen by the team and is being carried across from californiaicehockey.com
 * to the site replacing it. Nothing is paraphrased or generated - the body is
 * the club's text, and where an article carries a byline it is kept.
 *
 * The one editorial addition is `tag`. The club's site does not categorise
 * its articles, and this site displays a tag on every card, so each is
 * classified here by what it plainly is. That mapping is the only judgement
 * call in this file and it is spelt out rather than guessed by keyword.
 */
window.__applyArticles = function applyArticles(site, articles) {
  const out = JSON.parse(JSON.stringify(site));

  const TAG = {
    13: "RECAP", 12: "PREVIEW", 11: "RECAP", 10: "PREVIEW", 9: "RECAP",
    8: "RECAP", 7: "RECAP", 6: "RECAP", 5: "RECAP", 4: "RECAP",
    3: "RECAP", 2: "NEWS", 1: "FEATURE",
  };

  /* The article page for the PAC-8 playoff run is datestamped 2023, but it
     reports Devin Cox winning Coach of the Year and Aidan Comeau making
     First Team - a 2025 tournament - and the club's own index lists it under
     19 February 2025. The index date is used and the discrepancy reported. */
  const DATE_FIX = { 8: "2025-02-19" };

  const MONTH = { january: 1, february: 2, march: 3, april: 4, may: 5, june: 6,
    july: 7, august: 8, september: 9, october: 10, november: 11, december: 12 };
  const iso = (s) => {
    const m = String(s || "").match(/(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})/);
    if (!m) return "";
    const mm = MONTH[m[2].toLowerCase()];
    if (!mm) return "";
    return `${m[3]}-${String(mm).padStart(2, "0")}-${m[1].padStart(2, "0")}`;
  };

  const uid = () => "a" + Math.random().toString(36).slice(2, 9);

  const added = [];
  const news = [];

  for (const a of articles) {
    const paras = [...a.body];
    /* A trailing "By Ryan Carlson" is a byline, not a paragraph. */
    let author = "";
    const last = paras[paras.length - 1] || "";
    const by = last.match(/^By\s+(.{2,40})$/);
    if (by) { author = by[1].trim(); paras.pop(); }

    const date = DATE_FIX[a.n] || iso(a.date);
    news.push({
      id: uid(),
      date,
      tag: TAG[a.n] || "NEWS",
      title: a.title,
      blurb: a.lede,
      body: paras.join("\n\n"),
      author,
      image: a.image || null,
      published: true,
      publishAt: null,
      source: "californiaicehockey.com/article-pages/article" + a.n + ".html",
    });
    added.push(`${date}  ${TAG[a.n]}  ${author || "no byline"}  ${a.title.slice(0, 46)}`);
  }

  /* Newest first, the order every list on the site sorts by anyway. */
  news.sort((x, y) => (y.date || "").localeCompare(x.date || ""));
  out.news = [...news, ...(out.news || [])];

  return { site: out, report: { added: added.length, withCover: news.filter((n) => n.image).length,
    withByline: news.filter((n) => n.author).length, list: added } };
};
