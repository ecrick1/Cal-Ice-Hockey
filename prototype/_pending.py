# -*- coding: utf-8 -*-
"""Park edits without publishing them, or set them to go live later.

Until now the console had two states: edited and not yet written, or written
and immediately public. That is fine for a score, and wrong for everything
that takes more than one sitting - next season's schedule, a roster being
typed in over a week, a rebrand. Closing the tab lost the work; saving it
put half-finished work on the front page.

So a save can now go to one of two places. Publish writes the site the way
it always did. Save draft parks the whole working copy beside it, where the
console will find it next time and the public site will not look. A parked
draft can carry a moment to go live, and then it publishes itself.

Nothing runs on a timer. The draft is applied when the app loads, which is
the same guarantee the scheduled-story feature already relies on and the
same one an ISR rebuild gives: it goes live for the first visitor after its
moment. The real build needs no cron for this either.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ------------------------------------------------------------------- key
sub("""const ALUMNI_KEY = "cal-hockey-alumni";""",
    """const ALUMNI_KEY = "cal-hockey-alumni";
/* A whole working copy of the site, parked but not published. Separate from
   SITE_KEY so the public pages never see it. */
const PENDING_KEY = "cal-hockey-pending";""")

# ------------------------------------------------------------------ state
sub("""  const loaded = useRef(false);

  /* Load persisted data once */""",
    """  const loaded = useRef(false);
  /* { site, savedAt, publishAt } or null. Held here rather than in the
     console because the app has to look at it on load, before anyone has
     opened the console, to see whether it is due. */
  const [pending, setPendingState] = useState(null);

  /* Load persisted data once */""")

sub("""      const s = await loadKey(SITE_KEY, SEED_SITE);
      const r = await loadKey(RECRUITS_KEY, []);
      const al = await loadKey(ALUMNI_KEY, []);""",
    """      let s = await loadKey(SITE_KEY, SEED_SITE);
      const r = await loadKey(RECRUITS_KEY, []);
      const al = await loadKey(ALUMNI_KEY, []);
      /* A parked draft whose moment has passed goes live here, on the first
         load after it. No timer, no cron - the same way a scheduled story
         becomes visible. */
      let pend = await loadKey(PENDING_KEY, null);
      if (pend && pend.site && pend.publishAt
          && new Date(pend.publishAt).getTime() <= Date.now()) {
        s = { ...pend.site, rev: Number(s.rev || 0) + 1 };
        pend = null;
        await saveKey(SITE_KEY, s);
        await saveKey(PENDING_KEY, null);
      }
      setPendingState(pend);""")

sub("""  useEffect(() => { if (loaded.current) saveKey(ALUMNI_KEY, alumni); }, [alumni]);""",
    """  useEffect(() => { if (loaded.current) saveKey(ALUMNI_KEY, alumni); }, [alumni]);
  const setPending = useCallback((next) => {
    setPendingState(next);
    saveKey(PENDING_KEY, next);
  }, []);""")

sub("""        <Admin site={site} setSite={setSite} recruits={recruits} setRecruits={setRecruits}
          alumni={alumni} setAlumni={setAlumni}
          authed={authed} setAuthed={setAuthed} goto={setView} />""",
    """        <Admin site={site} setSite={setSite} recruits={recruits} setRecruits={setRecruits}
          alumni={alumni} setAlumni={setAlumni} pending={pending} setPending={setPending}
          authed={authed} setAuthed={setAuthed} goto={setView} />""")

# ----------------------------------------------------------------- console
sub("""function Admin({ site, setSite, recruits, setRecruits, alumni, setAlumni, authed, setAuthed, goto }) {""",
    """function Admin({ site, setSite, recruits, setRecruits, alumni, setAlumni,
  pending, setPending, authed, setAuthed, goto }) {""")

sub("""  const [draft, setDraftState] = useState(site);
  const draftRef = useRef(site);""",
    """  /* Opens on the parked draft when there is one: that is where the work
     was left. The published site is still what everyone else sees. */
  const [draft, setDraftState] = useState((pending && pending.site) || site);
  const draftRef = useRef((pending && pending.site) || site);""")

sub("""  useEffect(() => { draftRef.current = site; setDraftState(site); }, [site]);""",
    """  useEffect(() => { draftRef.current = site; setDraftState(site); }, [site]);
  /* A draft parked in another tab, or one that just went live, replaces
     what is on screen - otherwise this console would keep editing a copy
     that no longer exists anywhere. */
  const pendingId = pending ? pending.savedAt : "";
  useEffect(() => {
    if (!pending || !pending.site) return;
    draftRef.current = pending.site;
    setDraftState(pending.site);
  }, [pendingId]);""")

# The three ways out of an edit.
sub("""  const save = async () => {
    const next = draftRef.current;""",
    """  /* Park the working copy without publishing it. `at` is a local
     "YYYY-MM-DDTHH:mm" - the value a datetime-local input gives - or empty
     for a draft that waits to be published by hand. */
  const saveDraft = (at) => {
    setPending({ site: draftRef.current, savedAt: new Date().toISOString(), publishAt: at || null });
  };

  const publish = async () => {
    await save();
    if (pending) setPending(null);
  };

  const save = async () => {
    const next = draftRef.current;""")

sub("""              <button className="btn bGhost bSm" onClick={discard} disabled={!dirty}>Discard</button>
              <button className="btn bNavy bSm" onClick={save} disabled={!dirty}>Save</button>
            </div>
          </header>""",
    """              <button className="btn bGhost bSm" onClick={discard} disabled={!dirty && !pending}>
                Discard
              </button>
              <button className="btn bGhost bSm" onClick={() => saveDraft(pending && pending.publishAt)}
                disabled={!dirty}
                title="Keep this work without putting it on the site">
                Save draft
              </button>
              <button className="btn bNavy bSm" onClick={publish} disabled={!dirty && !pending}>
                Publish
              </button>
            </div>
          </header>

          {pending && <PendingBar pending={pending} dirty={dirty}
            onSchedule={(at) => saveDraft(at)}
            onPublish={publish}
            onDiscard={async () => {
              const ok = await ask({
                title: "Discard the saved draft?",
                message: "Everything in it goes, and the console goes back to what is published.",
                confirmLabel: "Discard draft", danger: true,
              });
              if (ok) { setPending(null); setDraft(site); }
            }} />}""")

# Discard has to clear the parked draft too, or it comes straight back.
sub("""      confirmLabel: "Discard",
      danger: true,
    });
    if (ok) setDraft(site);""",
    """      confirmLabel: "Discard",
      danger: true,
    });
    if (ok) { setDraft(site); if (pending) setPending(null); }""")

# ------------------------------------------------------------------- the bar
sub("""/* ---------------- Confirmation dialog ----------------""",
    """/**
 * The strip under the console header when a draft is parked.
 *
 * It says three things, in this order: that what you are looking at is not
 * what the public sees, when it will become so if a moment is set, and the
 * two ways out.
 */
function PendingBar({ pending, dirty, onSchedule, onPublish, onDiscard }) {
  const [at, setAt] = useState(pending.publishAt || "");
  useEffect(() => { setAt(pending.publishAt || ""); }, [pending.publishAt]);
  const due = pending.publishAt ? new Date(pending.publishAt) : null;
  return (
    <div className="aupending">
      <span className="aupenddot" aria-hidden="true" />
      <span className="aupendtext">
        <strong>Draft saved{dirty ? ", with newer edits on screen" : ""}</strong>
        <span className="aupendsub">
          {due
            ? "Goes live " + fmtDateTime(pending.publishAt) + " \\u2014 on the first visit after that moment."
            : "Not on the public site. Publish when you are ready, or set a time."}
        </span>
      </span>
      <label className="aupendwhen">
        <span className="h6">Go live at</span>
        <input type="datetime-local" value={at}
          onChange={(e) => { setAt(e.target.value); onSchedule(e.target.value); }} />
      </label>
      {at && (
        <button className="btn bGhost bSm" onClick={() => { setAt(""); onSchedule(""); }}>
          Clear time
        </button>
      )}
      <span style={{ flex: 1 }} />
      <button className="btn bGhost bSm" onClick={onDiscard}>Discard draft</button>
      <button className="btn bNavy bSm" onClick={onPublish}>Publish now</button>
    </div>
  );
}

/* ---------------- Confirmation dialog ----------------""")

# -------------------------------------------------------------------- CSS
sub(""".adminui .austorystate.scheduled { color: var(--au-warn, #F5B544);""",
    """/* Parked work. Gold rather than red: nothing is wrong, it is simply not
   public yet. */
.aupending { display: flex; align-items: center; gap: 14px; flex-wrap: wrap;
  padding: 12px 22px; background: rgba(245,181,68,0.09);
  border-bottom: 1px solid var(--au-line); }
.aupenddot { width: 8px; height: 8px; border-radius: 999px; flex: 0 0 auto;
  background: var(--au-warn, #F5B544); }
.aupendtext { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.aupendtext strong { font-size: 13px; font-weight: 700; color: var(--au-text); }
.aupendsub { font-size: 12px; color: var(--au-dim); }
.aupendwhen { display: flex; align-items: center; gap: 8px; }
.aupendwhen .h6 { margin: 0; white-space: nowrap; }
.aupendwhen input { width: auto; }

.adminui .austorystate.scheduled { color: var(--au-warn, #F5B544);""")

io.open(p, 'w', encoding='utf-8').write(s)
print('drafts and scheduling added')
