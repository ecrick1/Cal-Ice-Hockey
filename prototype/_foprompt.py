# -*- coding: utf-8 -*-
"""The face-off prompt asks the second question, and FO reaches the box score.

The picker now runs in two steps: who won it, and then who lost it, off the
other bench. The second step only appears when the first was answered with a
name - a side on its own is still one press and still a complete answer.

Skipping the loser is allowed and leaves the draw counted for the winner
alone, which is what it did before this and is better than a guess.

And the box score grows an FO column: draws won and lost, as a record, with
the percentage beside it. That is the point of collecting the second name -
without it a centre had a count of draws won and nothing to read it against.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ------------------------------------------------------------ the prompt
sub("""      {faceoffAsk && (
        <div className="austop">
          <span className="h6">Who won the faceoff?</span>
          <select value="" onChange={(e) => winFaceoff("us", e.target.value)}>""",
    """      {faceoffAsk && faceoffAsk.won && (
        <div className="austop">
          <span className="h6">
            {faceoffAsk.won.winner} won it \\u2014 who lost it?
          </span>
          {faceoffAsk.team === "us" ? (
            theirs.length > 0 ? (
              <select value="" onChange={(e) => pickLoser(e.target.value)}>
                <option value="">{oppName || "Them"} \\u2014 pick a player</option>
                {theirs.map((pl) => (
                  <option key={pl.id} value={pl.name}>#{pl.number} {pl.name}</option>
                ))}
              </select>
            ) : null
          ) : (
            <select value="" onChange={(e) => pickLoser(e.target.value)}>
              <option value="">{usLabel} \\u2014 pick a player</option>
              {(() => {
                const out = skaters.filter((pl) => pl.position !== "G");
                const centres = out.filter((pl) => pl.spot === "C");
                const rest = out.filter((pl) => pl.spot !== "C");
                const opt = (pl) => <option key={pl.id} value={pl.id}>#{pl.number} {pl.name}</option>;
                return centres.length
                  ? [<optgroup key="c" label="Centers">{centres.map(opt)}</optgroup>,
                     <optgroup key="r" label="Others">{rest.map(opt)}</optgroup>]
                  : out.map(opt);
              })()}
            </select>
          )}
          {/* Counted for the winner alone, which is what it did before the
              second name was asked for and better than a guess. */}
          <button className="btn bGhost bSm austopskip" onClick={() => pickLoser("")}>
            Don't know
          </button>
        </div>
      )}

      {faceoffAsk && !faceoffAsk.won && (
        <div className="austop">
          <span className="h6">Who won the faceoff?</span>
          <select value="" onChange={(e) => pickWinner("us", e.target.value)}>""")

sub("""          <button className="btn bGhost bSm" onClick={() => winFaceoff("us", "")}>
            {usLabel} won it
          </button>
          {theirs.length > 0 && (
            <select value="" onChange={(e) => winFaceoff("them", e.target.value)}>""",
    """          <button className="btn bGhost bSm" onClick={() => pickWinner("us", "")}>
            {usLabel} won it
          </button>
          {theirs.length > 0 && (
            <select value="" onChange={(e) => pickWinner("them", e.target.value)}>""")

sub("""          <button className="btn bGhost bSm" onClick={() => winFaceoff("them", "")}>
            {oppName || "Them"} won it
          </button>""",
    """          <button className="btn bGhost bSm" onClick={() => pickWinner("them", "")}>
            {oppName || "Them"} won it
          </button>""")

# ------------------------------------------------------ FO in the box score
sub("""              <th>G</th><th>A</th><th>P</th>
              <th title="Shots on goal">S</th>
              <th>PIM</th><th>PPG</th><th>SHG</th>""",
    """              <th>G</th><th>A</th><th>P</th>
              <th title="Shots on goal">S</th>
              <th title="Face-offs won and lost">FO</th>
              <th title="Face-off win percentage">FO%</th>
              <th>PIM</th><th>PPG</th><th>SHG</th>""")

sub("""                <td>{r.l.shots || 0}</td>
                <td>{r.l.pim || 0}</td>""",
    """                <td>{r.l.shots || 0}</td>
                <td>{foRecord(r.l)}</td>
                <td className="gcbtpts">{foPct(r.l)}</td>
                <td>{r.l.pim || 0}</td>""")

sub("""function pts(l) {
  return (Number(l.g) || 0) + (Number(l.a) || 0);
}""",
    """function pts(l) {
  return (Number(l.g) || 0) + (Number(l.a) || 0);
}

/* Draws won and lost. A dash rather than 0-0 for anyone who never took one,
   because never being sent to the circle and losing every draw are not the
   same thing to read. */
function foRecord(l) {
  const w = Number(l.fow) || 0, x = Number(l.fol) || 0;
  return w + x ? w + "-" + x : "\\u2014";
}
function foPct(l) {
  const w = Number(l.fow) || 0, x = Number(l.fol) || 0;
  return w + x ? Math.round((w / (w + x)) * 100) + "%" : "\\u2014";
}""")

io.open(p, 'w', encoding='utf-8').write(s)
print('two questions per draw, FO in the box')
