# -*- coding: utf-8 -*-
"""Wire it up: a typed reason, and the strength settling when the whistle does.

The reason box sits with the reasons rather than behind an "Other" button,
because a scorekeeper who already knows what to write should not have to
press something first to be allowed to write it. Enter files it.

And the held strength is released in the two places a whistle ends: Done on
the penalty bar, and play restarting. Restarting matters more than Done - it
is the one that happens whether or not anybody remembered - so it clears the
flag alongside the warm-up and the intermission, in the same write.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ------------------------------------------------------ a reason you type
sub("""          <button className="btn bGhost bSm austopskip" onClick={() => setStopAsk(false)}>
            Don't log it
          </button>
        </div>
      )}""",
    """          {/* With the reasons rather than behind an "Other" button: somebody
              who already knows what to write should not have to ask first. */}
          <input className="austoptext" placeholder="or type a reason…"
            onKeyDown={(e) => {
              if (e.key !== "Enter") return;
              const v = e.currentTarget.value.trim();
              if (v) logStop(v);
            }} />
          <button className="btn bGhost bSm austopskip" onClick={() => setStopAsk(false)}>
            Don't log it
          </button>
        </div>
      )}""")

sub(""".adminui .austopskip { margin-left: auto; opacity: 0.75; }""",
    """.adminui .austopskip { margin-left: auto; opacity: 0.75; }
/* Narrower than the pickers beside it: a reason is two or three words. */
.adminui .austoptext { min-width: 0; width: 170px; padding: 5px 8px; font-size: 13px; }""")

# ------------------------------------------- the whistle settles, so does it
sub("""            <button className="btn bGhost bSm austopskip" onClick={() => setPenPending(null)}>""",
    """            <button className="btn bGhost bSm austopskip" onClick={doneAssessing}>""")

sub("""    const running = {
      running: true, clockMs: left, startedAt: Date.now(),
      warmup: false, intermission: false, breakAt: null,
    };""",
    """    const running = {
      running: true, clockMs: left, startedAt: Date.now(),
      warmup: false, intermission: false, breakAt: null,
      /* Whatever was being sorted out at the whistle is sorted out now: the
         puck has dropped. This is the clearing that matters, because it
         happens whether or not anybody pressed Done. */
      assessing: false,
    };""")

io.open(p, 'w', encoding='utf-8').write(s)
print('typed reasons in, strength released with the whistle')
