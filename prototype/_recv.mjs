/* One-shot receiver, so the browser can hand its localStorage back to the repo.
 *
 * The site data lives in localStorage and nowhere else; the copy in the repo
 * is several revisions behind. It is four megabytes and most of that is image
 * data URIs, which are already compressed, so it will not fit back through the
 * tooling that reads the page. This takes it in one POST instead.
 *
 * Listens once, writes the body, exits. text/plain on purpose: it keeps the
 * request "simple" so the browser sends it straight out rather than asking
 * permission first, which this server would then have to know how to answer.
 */
import { createServer } from "node:http";
import { writeFileSync } from "node:fs";
import { argv, exit } from "node:process";

const out = argv[2];
if (!out) { console.error("usage: node _recv.mjs <outfile>"); exit(1); }

const server = createServer((req, res) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  if (req.method !== "POST") { res.writeHead(405).end("post only"); return; }
  const chunks = [];
  req.on("data", (c) => chunks.push(c));
  req.on("end", () => {
    const body = Buffer.concat(chunks);
    try {
      JSON.parse(body.toString("utf8"));       // refuse to write anything but JSON
    } catch (e) {
      res.writeHead(400).end("not json: " + e.message);
      console.error("rejected: body did not parse");
      return;
    }
    writeFileSync(out, body);
    res.writeHead(200).end(String(body.length));
    console.log("wrote " + body.length + " bytes to " + out);
    server.close(() => exit(0));
  });
});
server.listen(3999, "127.0.0.1", () => console.log("listening on 3999"));
setTimeout(() => { console.error("timed out with nothing received"); exit(2); }, 120000);
