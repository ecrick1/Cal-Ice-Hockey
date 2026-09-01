/* Why deleting every goal did not clear Ellis O'Dowd's assist.
   Runs the real cleanAssists from source through the old and new credit
   paths, then deletes the goal exactly the way applyRemoval does. */
import fs from "fs";

const src = fs.readFileSync("../reference/cal-ice-hockey-app.jsx", "utf8");
const i = src.indexOf("function cleanAssists(list, scorer)");
fs.writeFileSync("_ca.tmp.mjs",
  src.slice(i, src.indexOf("const INFRACTIONS", i)) + "\nexport { cleanAssists };");
const { cleanAssists } = await import("./_ca.tmp.mjs");
fs.unlinkSync("_ca.tmp.mjs");

const SCORER = "burbank", ODOWD = "odowd";

function run(credit, label, a1, a2) {
  const line = {};                                   // the player lines
  const bump = (id, d) => { line[id] = Math.max(0, (line[id] || 0) + d); };

  // --- the goal is added ---
  const onTheGoal = cleanAssists([a1, a2], SCORER);   // what the play records
  credit([a1, a2], SCORER).forEach((id) => bump(id, +1));

  const after = { ...line };

  // --- and then deleted: applyRemoval reverses the assists THE GOAL HOLDS ---
  onTheGoal.forEach((id) => bump(id, -1));

  console.log("  " + label.padEnd(22)
    + "goal records " + JSON.stringify(onTheGoal).padEnd(11)
    + " lines after goal " + JSON.stringify(after).padEnd(16)
    + " after delete " + JSON.stringify(line));
  return line[ODOWD] || 0;
}

const OLD = (pair) => pair.filter(Boolean);          // the bug: the raw pair
const NEW = (pair, scorer) => cleanAssists(pair, scorer);

console.log("\nPicked as BOTH assists (a1 = a2 = O'Dowd):");
const oldDup = run(OLD, "old (raw pair)", ODOWD, ODOWD);
const newDup = run(NEW, "new (cleaned)", ODOWD, ODOWD);

console.log("\nPicked once, normally (a1 = O'Dowd, a2 = none):");
const oldOne = run(OLD, "old (raw pair)", ODOWD, "");
const newOne = run(NEW, "new (cleaned)", ODOWD, "");

console.log("");

const ok = oldDup === 1 && newDup === 0 && oldOne === 0 && newOne === 0;
console.log(ok
  ? "Reproduced: only the duplicate pick strands an assist, and only on the old path."
  : "Did NOT reproduce — the explanation is wrong.");
console.log("  old, picked twice -> " + oldDup + " left behind");
console.log("  new, picked twice -> " + newDup + " left behind");
process.exit(ok ? 0 : 1);
