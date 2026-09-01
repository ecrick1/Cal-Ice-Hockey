/* The intermission clock, using the real functions from source. */
import fs from "fs";

const src = fs.readFileSync("../reference/cal-ice-hockey-app.jsx", "utf8");
const grab = (a, b) => {
  const i = src.indexOf(a);
  if (i < 0) throw new Error("missing: " + a);
  const j = src.indexOf(b, i);
  if (j < 0) throw new Error("missing end: " + b);
  return src.slice(i, j);
};

fs.writeFileSync("_break.tmp.mjs", [
  grab("const PERIOD_SECS =", "function fmtDateParen"),
  "export { intermissionLeft, clockTicking, liveLabel, clockLeft, fmtClock };",
].join("\n"));
const M = await import("./_break.tmp.mjs");
fs.unlinkSync("_break.tmp.mjs");

const T0 = 1_000_000_000_000;
const mins = (m) => m * 60 * 1000;
let bad = 0;
const is = (got, want, what) => {
  const ok = String(got) === String(want);
  if (!ok) bad++;
  console.log("  " + (ok ? "ok  " : "FAIL") + "  " + String(got).padEnd(22)
    + (ok ? "" : "(wanted " + want + ") ") + what);
};

// --- counting down ---
const running = { intermission: true, period: "2", breakMs: mins(15), breakAt: T0 };
is(M.fmtClock(M.intermissionLeft(running, T0)), "15:00", "just started");
is(M.fmtClock(M.intermissionLeft(running, T0 + mins(3))), "12:00", "three minutes in");
is(M.intermissionLeft(running, T0 + mins(20)), 0, "past the end, floors at zero");

// --- paused ---
const paused = { intermission: true, period: "2", breakMs: mins(7), breakAt: null };
is(M.fmtClock(M.intermissionLeft(paused, T0 + mins(99))), "7:00", "paused holds its value");

// --- not in an intermission at all ---
is(M.intermissionLeft({ intermission: false, breakMs: mins(15), breakAt: T0 }, T0), 0,
  "no break, no clock");

// --- default length when none was stored ---
is(M.fmtClock(M.intermissionLeft({ intermission: true, breakAt: T0 }, T0)), "15:00",
  "defaults to fifteen");

// --- what the public reads ---
is(M.liveLabel(running, T0 + mins(3)), "End 2nd · 12:00", "public label counts down");
is(M.liveLabel({ ...running, period: "3" }, T0 + mins(3)), "End of regulation · 12:00",
  "after the third");
is(M.liveLabel(running, T0 + mins(30)), "End 2nd", "run out: drops the clock");
is(M.liveLabel({ period: "2", running: true, clockMs: mins(12), startedAt: T0 }, T0),
  "2nd · 12:00", "normal play is unchanged");

// --- the ticker has to be awake for all of it ---
is(M.clockTicking(running), "true", "ticker runs during a live break");
is(M.clockTicking(paused), "false", "paused break needs no repaint");
is(M.clockTicking({ running: true }), "true", "ticker runs during play");
is(M.clockTicking({ running: false }), "false", "idle needs no repaint");

console.log(bad ? "\n" + bad + " failing" : "\nall good");
process.exit(bad ? 1 : 0);
