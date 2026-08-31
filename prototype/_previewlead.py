# -*- coding: utf-8 -*-
"""The preview leads the page.

It was the first card in the narrow right-hand column, above head to head -
a piece of writing, with a headline and a photograph, set narrower than the
tables beside it. That is the one thing on a preview page somebody came to
read, and it was the smallest thing on it.

It moves to the top of the wide column and gets set as a lead: bigger
headline, the photograph across the full width, and the opening paragraph
at reading size rather than caption size.
"""
import io

p = '../reference/cal-ice-hockey-app.jsx'
s = io.open(p, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:130])
    s = s.replace(old, new)


# ------------------------------------------------------------ a lead variant
sub("""function GameStory({ story, label, openPost }) {
  if (!story) return null;
  return (
    <section className="statcard gcpad gcrecap">""",
    """function GameStory({ story, label, openPost, lead }) {
  if (!story) return null;
  return (
    <section className={"statcard gcpad gcrecap" + (lead ? " lead" : "")}>""")

# ---------------------------------------------------- out of the right column
sub("""      <div className="gccol">
        <GameStory story={story} label="Preview" openPost={openPost} />
        {opp.data && (""",
    """      <div className="gccol">
        {opp.data && (""")

# ------------------------------------------------------- into the left, first
sub("""    <div className="gcgrid">
      <div className="gccol">
      {!!H2H.length && (""",
    """    <div className="gcgrid">
      <div className="gccol">
      <GameStory story={story} label="Preview" openPost={openPost} lead />
      {!!H2H.length && (""")

# -------------------------------------------------------------------- CSS
sub(""".gcrecapby { margin: 14px 0 0; font-size: 12.5px; font-weight: 700; color: var(--muted); }
.gcrecaplede { margin: 10px 0 16px; font-size: 15.5px; line-height: 1.65; color: var(--ink); }""",
    """.gcrecapby { margin: 14px 0 0; font-size: 12.5px; font-weight: 700; color: var(--muted); }
.gcrecaplede { margin: 10px 0 16px; font-size: 15.5px; line-height: 1.65; color: var(--ink); }

/* Leading the page rather than sitting in the margin of it. The one thing
   here that is meant to be read, set to be read. */
.gcrecap.lead .gcrecaptitle { font-size: clamp(1.75rem, 3.4vw, 2.6rem); margin-top: 10px; }
.gcrecap.lead .gcrecapsub { font-size: 17px; margin-top: 12px; }
.gcrecap.lead .gcrecapart { margin-top: 20px; border-radius: 14px; }
.gcrecap.lead .gcrecaplede { font-size: 17px; line-height: 1.7; margin: 14px 0 20px;
  max-width: 62ch; }
.gcrecap.lead .btn { padding: 11px 20px; font-size: 13.5px; }""")

io.open(p, 'w', encoding='utf-8').write(s)
print('preview leads the left column')
