# -*- coding: utf-8 -*-
"""Say what is about to go public, and let a mistake be taken back.

Publish wrote the site the moment it was pressed. That is the one button on
the console with consequences outside the building, and it had less
friction than deleting a single row - which asks. It asks now, and it lists
what changes: the sections, and for anything kept as a list, how many rows
were added, changed or removed.

The counts matter more than the section names. "2026-27 schedule" tells you
nothing you did not know; "2026-27 schedule - 1 changed" against an
afternoon's work tells you something is missing, and "22 removed" tells you
to stop.

Undo and redo sit beside them. The working copy is a chain of immutable
objects that share almost everything, so keeping the last fifty costs
almost nothing - the alternative was Discard, which throws away the whole
session because one cell was typed wrong.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ------------------------------------------------------ what actually changed
sub("""function diffSections(saved, draft) {
  if (!saved || !draft) return [];
  const out = [];
  const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
  if (!same(saved.news, draft.news)) out.push("News");
  if (!same(saved.opponents, draft.opponents)) out.push("Opponents");
  if (!same(saved.settings, draft.settings)) out.push("Settings");
  if (!same(saved.account, draft.account)) out.push("Account");
  if (!same(saved.recruiting, draft.recruiting)) out.push("Recruits page");
  if (!same(saved.volunteerRoles, draft.volunteerRoles)) out.push("Volunteer roles");
  if (!same(saved.staff, draft.staff)) out.push("Staff");
  if (!same(saved.gameStats, draft.gameStats)) out.push("Game stats");
  if (saved.currentSeason !== draft.currentSeason) out.push("Current season");

  const names = new Set([...Object.keys(saved.seasons || {}), ...Object.keys(draft.seasons || {})]);
  for (const n of names) {
    const a = (saved.seasons || {})[n];
    const b = (draft.seasons || {})[n];
    if (!a || !b) { out.push(`Season ${n}`); continue; }
    if (!same(a.schedule, b.schedule)) out.push(`${n} schedule`);
    if (!same(a.roster, b.roster)) out.push(`${n} roster`);
    if (!same(a.coaches, b.coaches)) out.push(`${n} coaches`);
    if (!same(a.record, b.record)) out.push(`${n} record`);
  }
  return out;
}""",
    """/* How a list of records changed, by id. Rows without one - the odd shape
   that predates ids - fall back to their position, which is right often
   enough to be worth more than saying nothing. */
function countRows(before, after) {
  const key = (x, i) => (x && x.id != null ? "id:" + x.id : "at:" + i);
  const A = new Map((before || []).map((x, i) => [key(x, i), x]));
  const B = new Map((after || []).map((x, i) => [key(x, i), x]));
  let added = 0, removed = 0, edited = 0;
  for (const [k, x] of B) {
    const y = A.get(k);
    if (!y) added++;
    else if (JSON.stringify(x) !== JSON.stringify(y)) edited++;
  }
  for (const k of A.keys()) if (!B.has(k)) removed++;
  return { added, edited, removed };
}

function rowNote(before, after) {
  const c = countRows(before, after);
  const bits = [];
  if (c.added) bits.push(c.added + " added");
  if (c.edited) bits.push(c.edited + " changed");
  if (c.removed) bits.push(c.removed + " removed");
  return bits.join(", ");
}

/**
 * Which parts of the site differ, and by how much.
 *
 * Returns `{ label, note }`. `note` is empty for things that are not lists -
 * settings either changed or it did not, and there is nothing to count.
 */
function diffSections(saved, draft) {
  if (!saved || !draft) return [];
  const out = [];
  const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
  const list = (label, a, b) => { if (!same(a, b)) out.push({ label, note: rowNote(a, b) }); };
  const flat = (label, a, b) => { if (!same(a, b)) out.push({ label, note: "" }); };

  list("News", saved.news, draft.news);
  list("Opponents", saved.opponents, draft.opponents);
  flat("Settings", saved.settings, draft.settings);
  flat("Account", saved.account, draft.account);
  flat("Recruits page", saved.recruiting, draft.recruiting);
  list("Volunteer roles", saved.volunteerRoles, draft.volunteerRoles);
  list("Staff", saved.staff, draft.staff);
  if (!same(saved.gameStats, draft.gameStats)) {
    const a = Object.keys(saved.gameStats || {}), b = Object.keys(draft.gameStats || {});
    const touched = b.filter((k) => JSON.stringify((saved.gameStats || {})[k])
      !== JSON.stringify((draft.gameStats || {})[k])).length;
    out.push({ label: "Game stats", note: touched ? touched + " game" + (touched === 1 ? "" : "s") : "" });
    void a;
  }
  if (saved.currentSeason !== draft.currentSeason) {
    out.push({ label: "Current season", note: saved.currentSeason + " \\u2192 " + draft.currentSeason });
  }

  const names = new Set([...Object.keys(saved.seasons || {}), ...Object.keys(draft.seasons || {})]);
  for (const n of [...names].sort().reverse()) {
    const a = (saved.seasons || {})[n];
    const b = (draft.seasons || {})[n];
    if (!a || !b) { out.push({ label: "Season " + n, note: b ? "added" : "removed" }); continue; }
    list(n + " schedule", a.schedule, b.schedule);
    list(n + " roster", a.roster, b.roster);
    list(n + " coaches", a.coaches, b.coaches);
    flat(n + " record", a.record, b.record);
  }
  return out;
}""")

# ------------------------------------------------------------ call sites
sub("""      detail: changed.join(", "),
      confirmLabel: "Discard",""",
    """      detail: changedLabels.join(", "),
      confirmLabel: "Discard",""")

sub("""        detail: changed.join(", "),""",
    """        detail: changedLabels.join(", "),""")

sub("""                    ? "Unsaved · " + changed.join(", ")""",
    """                    ? "Unsaved · " + changedLabels.join(", ")""")

sub("""  const changed = useMemo(() => diffSections(baseline, draft), [baseline, draft]);
  const dirty = changed.length > 0;""",
    """  const changed = useMemo(() => diffSections(baseline, draft), [baseline, draft]);
  const changedLabels = changed.map((c) => c.label);
  const dirty = changed.length > 0;
  /* What publishing would put on the public site. Not the same list as
     `changed` once a draft is parked: that compares against the draft, and
     this has to compare against what people can actually see. */
  const goingPublic = useMemo(() => diffSections(site, draft), [site, draft]);""")

# ------------------------------------------------------------- undo / redo
sub("""    const next = typeof updater === "function" ? updater(draftRef.current) : updater;
    draftRef.current = next;
    setDraftState(next);
  }, []);""",
    """    const next = typeof updater === "function" ? updater(draftRef.current) : updater;
    /* Each edit produces a new object that shares everything it did not
       touch, so holding the last fifty costs a few pointers rather than
       fifty copies of the site. */
    undoRef.current = [...undoRef.current, draftRef.current].slice(-50);
    redoRef.current = [];
    setSteps({ undo: undoRef.current.length, redo: 0 });
    draftRef.current = next;
    setDraftState(next);
  }, []);

  const undo = useCallback(() => {
    const stack = undoRef.current;
    if (!stack.length) return;
    const prev = stack[stack.length - 1];
    undoRef.current = stack.slice(0, -1);
    redoRef.current = [...redoRef.current, draftRef.current].slice(-50);
    draftRef.current = prev;
    setDraftState(prev);
    setSteps({ undo: undoRef.current.length, redo: redoRef.current.length });
  }, []);

  const redo = useCallback(() => {
    const stack = redoRef.current;
    if (!stack.length) return;
    const next = stack[stack.length - 1];
    redoRef.current = stack.slice(0, -1);
    undoRef.current = [...undoRef.current, draftRef.current].slice(-50);
    draftRef.current = next;
    setDraftState(next);
    setSteps({ undo: undoRef.current.length, redo: redoRef.current.length });
  }, []);""")

sub("""  const [draft, setDraftState] = useState((pending && pending.site) || site);
  const draftRef = useRef((pending && pending.site) || site);""",
    """  const [draft, setDraftState] = useState((pending && pending.site) || site);
  const draftRef = useRef((pending && pending.site) || site);
  /* Held in refs so an edit and the step count cannot disagree; the count
     is mirrored into state only so the two buttons re-render. */
  const undoRef = useRef([]);
  const redoRef = useRef([]);
  const [steps, setSteps] = useState({ undo: 0, redo: 0 });
  const clearHistory = useCallback(() => {
    undoRef.current = []; redoRef.current = []; setSteps({ undo: 0, redo: 0 });
  }, []);""")

# A publish or an outside write starts a new session; the old steps would
# undo into a state that no longer relates to anything stored.
sub("""  useEffect(() => { draftRef.current = site; setDraftState(site); }, [site]);""",
    """  useEffect(() => { draftRef.current = site; setDraftState(site); clearHistory(); }, [site]);""")

sub("""    draftRef.current = pending.site;
    setDraftState(pending.site);
  }, [pendingId]);""",
    """    draftRef.current = pending.site;
    setDraftState(pending.site);
    clearHistory();
  }, [pendingId]);""")

# --------------------------------------------------------- publish asks first
sub("""  /* Publishing a parked draft is a save that also unparks it - but only if
     the save actually happened. Declining the conflict prompt used to clear
     the draft anyway, which threw it away without ever putting it up. */
  const publish = async () => {
    const wrote = await save();
    if (wrote && pending) setPending(null);
  };""",
    """  /* Publishing a parked draft is a save that also unparks it - but only if
     the save actually happened. Declining the conflict prompt used to clear
     the draft anyway, which threw it away without ever putting it up. */
  const publish = async () => {
    if (!goingPublic.length) return;
    const ok = await ask({
      title: "Publish to the public site?",
      message: goingPublic.length + " " + (goingPublic.length === 1 ? "part" : "parts")
        + " of the site will change for everyone.",
      list: goingPublic,
      confirmLabel: "Publish",
    });
    if (!ok) return;
    const wrote = await save();
    if (wrote && pending) setPending(null);
  };""")

# The dialog gains a list.
sub("""        {needsText && (""",
    """        {!!(state.list || []).length && (
          <ul className="aumodallist">
            {state.list.map((c) => (
              <li key={c.label}>
                <span className="aumodallabel">{c.label}</span>
                {c.note && <span className="aumodalnote">{c.note}</span>}
              </li>
            ))}
          </ul>
        )}
        {needsText && (""")

# ------------------------------------------------------------- the buttons
sub("""              <button className="btn bGhost bSm" onClick={discard} disabled={!dirty}>Discard</button>""",
    """              <span className="auundo">
                <button className="iconbtn" onClick={undo} disabled={!steps.undo}
                  title={steps.undo ? "Undo the last change" : "Nothing to undo"}
                  aria-label="Undo"><IcUndo /></button>
                <button className="iconbtn" onClick={redo} disabled={!steps.redo}
                  title={steps.redo ? "Redo" : "Nothing to redo"}
                  aria-label="Redo"><IcRedo /></button>
              </span>
              <button className="btn bGhost bSm" onClick={discard} disabled={!dirty}>Discard</button>""")

# ---------------------------------------------------------------- the icons
sub("""const IcBars = (p) => <Ic {...p} d={<path d="M5 20V12M12 20V4M19 20v-6" />} />;""",
    """const IcBars = (p) => <Ic {...p} d={<path d="M5 20V12M12 20V4M19 20v-6" />} />;
/* An arrow curling back on itself, and its mirror. Stroked on the same 24
   grid as the rest of the set. */
const IcUndo = (p) => <Ic {...p} d={<><path d="M9 14l-4-4 4-4" /><path d="M5 10h9a5 5 0 0 1 0 10h-4" /></>} />;
const IcRedo = (p) => <Ic {...p} d={<><path d="M15 14l4-4-4-4" /><path d="M19 10h-9a5 5 0 0 0 0 10h4" /></>} />;""")

# -------------------------------------------------------------------- CSS
sub(""".aupending { display: flex; align-items: center; gap: 14px; flex-wrap: wrap;""",
    """.auundo { display: inline-flex; align-items: center; gap: 2px; margin-right: 4px; }
.auundo .iconbtn { width: 30px; height: 30px; border-radius: 7px; border: 0; background: none;
  color: var(--au-dim); cursor: pointer; display: inline-flex; align-items: center;
  justify-content: center; }
.auundo .iconbtn:hover:not(:disabled) { background: rgba(127,127,127,0.16); color: var(--au-text); }
.auundo .iconbtn:disabled { opacity: 0.3; cursor: default; }

/* What a publish is about to change, in the dialog that asks. */
.aumodallist { list-style: none; margin: 14px 0 0; padding: 0; display: grid; gap: 1px;
  max-height: 260px; overflow-y: auto; border-top: 1px solid var(--au-line); }
.aumodallist li { display: flex; align-items: baseline; gap: 12px; padding: 8px 2px;
  border-bottom: 1px solid var(--au-line-soft); }
.aumodallabel { font-size: 13px; font-weight: 650; color: var(--au-text); }
.aumodalnote { margin-left: auto; font-family: var(--au-mono); font-size: 11.5px;
  color: var(--au-dim); white-space: nowrap; }

.aupending { display: flex; align-items: center; gap: 14px; flex-wrap: wrap;""")

io.open(p, 'w', encoding='utf-8').write(s)
print('publish manifest and undo added')
