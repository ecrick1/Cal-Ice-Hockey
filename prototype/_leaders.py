# -*- coding: utf-8 -*-
"""Give the leader of each category the room a leader deserves.

Five identical lines say nothing about who is top. The first one gets a
bigger portrait, the name set over the number at size, and a rule under it;
the rest stay a compact ranked list underneath.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:110])
    s = s.replace(old, new)


sub("""                      <p style={{ margin: "0 0 12px", fontWeight: 800, fontSize: 17, color: "var(--blue)" }}>{label}</p>
                      {leaders(key).map(({ p, v }, i) => (
                        <p className="bsm" key={p.id} style={{ display: "flex", margin: "8px 0", fontWeight: 600 }}>
                          <span style={{ color: "var(--muted)", width: 22 }}>{i + 1}.</span>
                          <button className="statname" style={{ flex: 1 }}
                            onClick={() => onPlayer(p.id)}>
                            <PlayerAvatar size={26} photo={p.photo} />
                            <span>{lastFirst(p.name)}</span>
                          </button>
                          <span style={{ fontWeight: 800, color: "var(--blue)" }}>{v}</span>
                        </p>
                      ))}
                      {!leaders(key).length && <p className="bsm" style={{ color: "var(--muted)" }}>No stats recorded.</p>}""",
    """                      <p className="cleadcat">{label}</p>
                      {leaders(key).slice(0, 1).map(({ p, v }) => (
                        <button className="cleadtop" key={p.id} onClick={() => onPlayer(p.id)}>
                          <PlayerAvatar size={56} photo={p.photo} />
                          <span className="cleadtopwho">
                            <span className="cleadtopname">{p.name}</span>
                            <span className="cleadtopmeta">
                              {[p.number ? "#" + p.number : null,
                                p.position === "D" || p.position === "G" ? p.position : p.spot || "F"]
                                .filter(Boolean).join(" \\u00b7 ")}
                            </span>
                          </span>
                          <span className="cleadtopval">{v}</span>
                        </button>
                      ))}
                      {leaders(key).slice(1).map(({ p, v }, i) => (
                        <p className="bsm cleadrow" key={p.id}>
                          <span className="cleadrank">{i + 2}.</span>
                          <button className="statname" style={{ flex: 1 }}
                            onClick={() => onPlayer(p.id)}>
                            <PlayerAvatar size={26} photo={p.photo} />
                            <span>{lastFirst(p.name)}</span>
                          </button>
                          <span className="cleadval">{v}</span>
                        </p>
                      ))}
                      {!leaders(key).length && <p className="bsm" style={{ color: "var(--muted)" }}>No stats recorded.</p>}""")

sub("""/* A game that goes by a name. Gold, because it is the thing on the schedule""",
    """/* Category leaders: the one at the top is the answer to the question the
   card asks, so it is set at size and the chasing pack sits under a rule. */
.cleadcat { margin: 0 0 14px; font-weight: 800; font-size: 17px; color: var(--blue); }
.cleadtop { display: flex; align-items: center; gap: 12px; width: 100%; text-align: left;
  background: none; border: 0; padding: 0 0 14px; margin-bottom: 12px; cursor: pointer;
  border-bottom: 1px solid var(--border); }
.cleadtopwho { display: flex; flex-direction: column; gap: 2px; min-width: 0; flex: 1 1 auto; }
.cleadtopname { font-weight: 800; font-size: 16px; color: var(--ink); line-height: 1.2;
  overflow: hidden; text-overflow: ellipsis; }
.cleadtop:hover .cleadtopname { color: var(--blue); }
.cleadtopmeta { font-size: 11.5px; font-weight: 600; color: var(--muted); }
.cleadtopval { font-family: var(--body); font-weight: 800; font-size: 30px; color: var(--blue);
  letter-spacing: -0.02em; line-height: 1; font-variant-numeric: tabular-nums; }
.cleadrow { display: flex; align-items: center; margin: 8px 0; font-weight: 600; }
.cleadrank { color: var(--muted); width: 22px; }
.cleadval { font-weight: 800; color: var(--blue); font-variant-numeric: tabular-nums; }

/* A game that goes by a name. Gold, because it is the thing on the schedule""")

io.open(p, 'w', encoding='utf-8').write(s)
print('leaders restyled')
