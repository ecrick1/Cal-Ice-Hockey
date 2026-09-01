/* Pulls the real strength functions out of the source and runs the rulebook
   cases through them, so the test exercises what ships rather than a copy. */
import fs from "fs";

const src = fs.readFileSync("../reference/cal-ice-hockey-app.jsx", "utf8");
const grab = (start, end) => {
  const i = src.indexOf(start);
  if (i < 0) throw new Error("not found: " + start);
  const j = src.indexOf(end, i);
  return src.slice(i, j);
};

const code = [
  grab("const PENALTY_KINDS = [", "const penaltyKind = (key)"),
  grab("const penaltyKind = (key)", "\nfunction activePenalties"),
  grab("function activePenalties(live, now)", "\n/* Penalties handed out"),
  grab("const penaltyStart =", "\nfunction strengthState"),
  grab("function strengthState(live, now)", "function fmtDateParen"),
  "elapsedSecs = () => 0;",
  "export { strengthState };",
].join("\n");

fs.writeFileSync("_strength.tmp.mjs", "let elapsedSecs;\n" + code);
const { strengthState } = await import("./_strength.tmp.mjs");

let id = 0;
/* start: seconds into the game the call was made. elapsedSecs is stubbed to
   0, so endsAt is simply how long is left. */
const pen = (team, mins, kind, start = 0) =>
  ({ id: "p" + ++id, team, minutes: mins, kind, endsAt: start + mins * 60, ended: false });

const cases = [
  ["clean sheet", [], "5-on-5", "EV"],
  ["one minor to us", [pen("us", 2, "minor")], "5-on-4", "PK"],
  ["one minor each, same whistle", [pen("us", 2, "minor"), pen("them", 2, "minor")], "4-on-4", "E4"],
  ["two minors each, same whistle", [pen("us", 2, "minor"), pen("us", 2, "minor"),
    pen("them", 2, "minor"), pen("them", 2, "minor")], "3-on-3", "E4"],
  ["two on us, one on them, same whistle", [pen("us", 2, "minor"), pen("us", 2, "minor"),
    pen("them", 2, "minor")], "4-on-3", "PK"],
  ["two on us, none back", [pen("us", 2, "minor"), pen("us", 2, "minor")], "5-on-3", "PK"],
  ["three on us — floor of three", [pen("us", 2, "minor"), pen("us", 2, "minor"),
    pen("us", 2, "minor")], "5-on-3", "PK"],
  ["coincidental majors (a fight)", [pen("us", 5, "major"), pen("them", 5, "major")], "5-on-5", "EV"],
  ["one major, nothing back", [pen("us", 5, "major")], "5-on-4", "PK"],
  ["minors at different whistles do not cancel",
    [pen("us", 2, "minor", 0), pen("them", 2, "minor", 40)], "4-on-4", "E4"],
  ["misconduct — served, not short", [pen("us", 10, "misconduct")], "5-on-5", "EV"],
  ["2-and-10: short for the two only",
    [pen("us", 2, "minor"), pen("us", 10, "misconduct")], "5-on-4", "PK"],
  ["their minor while we kill one", [pen("us", 2, "minor", 0), pen("them", 2, "minor", 30)],
    "4-on-4", "E4"],
];

let bad = 0;
for (const [name, penalties, wantLabel, wantKind] of cases) {
  const st = strengthState({ penalties }, 0);
  const ok = st.label === wantLabel && st.kind === wantKind;
  if (!ok) bad++;
  console.log((ok ? "  ok  " : "  FAIL") + "  " + (st.kind + " " + st.label).padEnd(12)
    + (ok ? "" : "(wanted " + wantKind + " " + wantLabel + ") ") + " " + name);
}

console.log(bad ? "\n" + bad + " failing" : "\nall " + cases.length + " match the rulebook");
process.exit(bad ? 1 : 0);
