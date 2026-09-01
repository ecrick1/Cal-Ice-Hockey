# -*- coding: utf-8 -*-
"""One layout for both benches on the Rosters tab.

Ours was a grid of compact columns and theirs a full-width list of editable
rows, so the two halves of one tab were built to different plans and read as
two different features.

Theirs has to stay editable - it is typed at the door - and an editable row
needs the width. So ours takes that shape: the same card, the same heading
row, the same four-column row, the same section headers. The difference is
that ours is read, not typed, because the lineup sheet is what decides it,
and the fourth column carries the netminder mark where theirs carries the
remove button.

Scratched keeps its own section rather than being folded in. Who did not
dress is a question this tab should answer, and the sheet the console
offers is only the people who did.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


sub("""          <section className="card" style={{ marginBottom: 18 }}>
            <div className="auopprosterhead">
              <p className="h6" style={{ margin: 0 }}>{usLabel} — this game</p>
              <span className="bsm" style={{ color: "var(--au-faint)" }}>
                {skaters.length} dressed
                {scratched.length ? " · " + scratched.length + " scratched" : ""}
              </span>
            </div>
            <div className="aulivesheet">
              {[["Forwards", skaters.filter((p) => p.position !== "G" && p.position !== "D")],
                ["Defense", skaters.filter((p) => p.position === "D")],
                ["Goaltenders", skaters.filter((p) => p.position === "G")]]
                .filter(([, list]) => list.length)
                .map(([title, list]) => (
                  <div className="alugroup" key={title}>
                    <div className="alugrouphead"><span>{title}</span><span>{list.length}</span></div>
                    {list.map((p) => (
                      <div className="alurow" key={p.id}>
                        <span className="alunum">#{p.number || "\\u2014"}</span>
                        <span className="aluname">{p.name}</span>
                        {live.goalieUs === p.id && <span className="alustart on">In net</span>}
                      </div>
                    ))}
                  </div>
                ))}
              {scratched.length > 0 && (
                <div className="alugroup">
                  <div className="alugrouphead"><span>Scratched</span><span>{scratched.length}</span></div>
                  {scratched.map((p) => (
                    <div className="alurow out" key={p.id}>
                      <span className="alunum">#{p.number || "\\u2014"}</span>
                      <span className="aluname">{p.name}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
            <p className="auhint" style={{ margin: "12px 0 0" }}>
              Set on the lineup sheet before the game. Anyone ejected comes off the
              pickers but stays here.
            </p>
          </section>""",
    """          <section className="card" style={{ marginBottom: 18 }}>
            <div className="boxhead">
              <p className="h6" style={{ color: "var(--au-text)", margin: 0 }}>
                {usLabel} · this game
              </p>
              <span className="bsm" style={{ color: "var(--au-faint)", marginLeft: "auto" }}>
                {skaters.length ? skaters.length + " dressed" : "nobody yet"}
              </span>
            </div>

            <p className="auhint" style={{ marginTop: 8, marginBottom: 12, maxWidth: 680 }}>
              Who dressed for us on the night. Set on the lineup sheet before the game;
              anyone ejected comes off the pickers but stays here.
            </p>

            {[["Skaters", skaters.filter((p) => p.position !== "G")],
              ["Goaltenders", skaters.filter((p) => p.position === "G")],
              ["Scratched", scratched]]
              .filter(([, list]) => list.length)
              .map(([title, list], i) => (
                <div key={title}>
                  <div className="opprow oppsheetrow head"
                    style={i ? { marginTop: 10 } : undefined}>
                    <span>#</span><span>{title}</span><span>Pos</span><span />
                  </div>
                  {list.map((p) => (
                    /* Same row as theirs, read instead of typed - the lineup
                       sheet is what decides this, not this tab. */
                    <div className={"opprow oppsheetrow ausheetread"
                      + (title === "Scratched" ? " out" : "")} key={p.id}>
                      <span>{p.number || "\\u2014"}</span>
                      <span>{p.name}</span>
                      <span>{p.position === "D" || p.position === "G" ? p.position : p.spot || "F"}</span>
                      <span>{live.goalieUs === p.id ? "In net" : ""}</span>
                    </div>
                  ))}
                </div>
              ))}
          </section>""")

# ------------------------------------------------------------------- CSS
sub("""/* The bench, read rather than edited: the same rows as the lineup sheet
   without the checkboxes, because this tab reports what was decided there. */
.adminui .aulivesheet { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
  gap: 14px; margin-top: 12px; }
.adminui .aulivesheet .alurow { padding: 5px 8px; }
.adminui .aulivesheet .aluname { font-size: 13px; }""",
    """/* Our bench in the visitors' row: same grid, read instead of typed. The
   padding matches an input's so the two lists line up column for column
   down the tab. */
.adminui .ausheetread span { padding: 7px 9px; font-size: 13.5px; color: var(--au-text);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.adminui .ausheetread span:last-child { font-size: 11px; font-weight: 700;
  color: var(--au-warn, #F5B544); text-align: center; }
.adminui .ausheetread.out span { color: var(--au-faint); }""")

io.open(p, 'w', encoding='utf-8').write(s)
print('one layout for both benches')
