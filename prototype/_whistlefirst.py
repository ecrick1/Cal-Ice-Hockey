# -*- coding: utf-8 -*-
"""The whistle asks the question, and the answer opens the right form.

A goal and a penalty only ever happen at a stoppage. The console already
knew that about penalties - stopping play asks why, and answering "Penalty"
holds the whistle until the penalty is entered - but a goal was not one of
the answers, so the one thing everyone is there to record was the one thing
the whistle did not ask about. You stopped the clock, said "Puck out of
play" or nothing at all, and then went and found the goal form.

Goal is a reason now, and the first one, because it is the answer most worth
having. Picking it opens the goal form and writes nothing on its own: a goal
is its own record of why play stopped, and a stoppage play beside it would
be the same fact twice.

The two forms fold away while the clock runs. They are unreachable moments
in the game - nobody scores during play, they score to end it - so they were
two panels of dropdowns sitting under the only controls that do work with
the clock running, which are the shot counters. Folded, the running console
is the scoreboard, the shots and the whistle.

They fold rather than disappear, because a whistle does get missed. A goal
noticed after play restarted, a penalty typed in late, a correction the next
morning - all of those need the form without the whistle, and a heading you
can click is a smaller price than a flow that only works when the
scorekeeper is keeping up. Typing up a finished game leaves both open
throughout: there is no clock to stop, so there is no whistle to wait for.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ------------------------------------------- a goal is why play stopped
sub("""const STOP_REASONS = [
  "Icing", "Offside", "Penalty", "Puck out of play", "Goalie freeze",
  "Injury", "Net off moorings", "Other",
];""",
    """/* Goal first: it is the answer most worth having and the one everyone is
   there to record. Goal and Penalty open a form rather than being logged -
   a goal is already its own record of why play stopped, and a stoppage
   written beside it would be the same fact twice. */
const STOP_REASONS = [
  "Goal", "Penalty", "Icing", "Offside", "Puck out of play", "Goalie freeze",
  "Injury", "Net off moorings", "Other",
];
const OPENS_A_FORM = { Goal: "goal", Penalty: "penalty" };

/* A panel that folds away when what it records cannot be happening. */
function FoldHead({ label, open, lock, onClick }) {
  if (lock) return <p className="h6" style={{ marginBottom: 12 }}>{label}</p>;
  return (
    <button className="aufoldhead" onClick={onClick} aria-expanded={open}>
      <span className="h6">{label}</span>
      <span className="aufoldmark" aria-hidden="true">{open ? "\\u2212" : "+"}</span>
    </button>
  );
}""")

# ------------------------------------------------------- what is open
sub("""  const [stopAsk, setStopAsk] = useState(false);""",
    """  const [stopAsk, setStopAsk] = useState(false);
  /* Which entry form is open. Nothing while the clock runs, because neither
     a goal nor a penalty happens during play - they are what ends it. */
  const [openForm, setOpenForm] = useState(null);
  /* Typing up a finished game has no clock to stop and so no whistle to wait
     for; both forms stay open throughout. */
  const formOpen = (k) => retro || openForm === k;""")

sub("""            <button className="btn bGhost bSm" key={r}
              onClick={() => (r === "Penalty" ? holdForPenalty() : logStop(r))}>{r}</button>""",
    """            <button className={"btn bSm " + (OPENS_A_FORM[r] ? "bNavy" : "bGhost")} key={r}
              onClick={() => {
                const form = OPENS_A_FORM[r];
                if (!form) return logStop(r);
                /* Neither writes a stoppage: the goal or the penalty is the
                   record. The penalty holds the whistle as it always has. */
                if (r === "Penalty") holdForPenalty(); else setStopAsk(false);
                setOpenForm(form);
              }}>{r}</button>""")

# The forms close again when play restarts - the moment they stop applying.
sub("""    setStopAsk(false);
    /* Play has restarted, so the question about the last whistle has gone
       with it - the stoppage keeps its reason and no name, the same as
       pressing skip. */
    setStopWho(null);""",
    """    setStopAsk(false);
    setOpenForm(null);
    /* Play has restarted, so the question about the last whistle has gone
       with it - the stoppage keeps its reason and no name, the same as
       pressing skip. */
    setStopWho(null);""")

# ------------------------------------------------------- the two panels
sub("""          <section className="card">
            <p className="h6" style={{ marginBottom: 12 }}>Goal</p>
            <div className="autoggle">""",
    """          <section className={"card aufold" + (formOpen("goal") ? " on" : "")}>
            <FoldHead label="Goal" open={formOpen("goal")} lock={retro}
              onClick={() => setOpenForm(openForm === "goal" ? null : "goal")} />
            <div hidden={!formOpen("goal")}>
            <div className="autoggle">""")

sub("""              {goalMissing && <span className="bsm auaddwhy">{goalMissing}</span>}
            </div>
          </section>

          <section className="card" style={{ marginTop: 16 }}>
            <p className="h6" style={{ marginBottom: 12 }}>Penalty</p>
            <div className="autoggle">""",
    """              {goalMissing && <span className="bsm auaddwhy">{goalMissing}</span>}
            </div>
            </div>
          </section>

          <section className={"card aufold" + (formOpen("penalty") ? " on" : "")}
            style={{ marginTop: 16 }}>
            <FoldHead label="Penalty" open={formOpen("penalty")} lock={retro}
              onClick={() => setOpenForm(openForm === "penalty" ? null : "penalty")} />
            <div hidden={!formOpen("penalty")}>
            <div className="autoggle">""")

sub("""              {penMissing && <span className="bsm auaddwhy">{penMissing}</span>}
            </div>
          </section>
        </div>""",
    """              {penMissing && <span className="bsm auaddwhy">{penMissing}</span>}
            </div>
            </div>
          </section>
        </div>""")

# ------------------------------------------------------------------- CSS
sub(""".adminui .aupenwait { border-left: 3px solid var(--au-warn, #F5B544); }""",
    """.adminui .aupenwait { border-left: 3px solid var(--au-warn, #F5B544); }
/* A folded panel is a heading and nothing else, so the heading has to look
   like the control it is: full width, and the sign on the right says which
   way it goes. */
.adminui .aufoldhead { display: flex; align-items: center; justify-content: space-between;
  width: 100%; gap: 10px; padding: 0; margin: 0; background: none; border: 0;
  cursor: pointer; text-align: left; color: inherit; }
.adminui .aufold.on .aufoldhead { margin-bottom: 12px; }
.adminui .aufoldhead .h6 { margin: 0; }
.adminui .aufoldmark { font-family: var(--au-mono, monospace); font-size: 15px;
  font-weight: 700; color: var(--au-faint); line-height: 1; }
.adminui .aufoldhead:hover .aufoldmark { color: var(--au-text); }""")

io.open(p, 'w', encoding='utf-8').write(s)
print('the whistle opens the form')
