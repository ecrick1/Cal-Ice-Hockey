/**
 * The 2018-19 roster, as supplied.
 *
 * Real people, so nothing here is invented: number, name, position, shot,
 * height, weight and hometown are exactly what was given. Class year, stats,
 * photos and bios are left empty rather than guessed at - the roster editor is
 * where those get filled in.
 *
 * Wingers and centres are stored as F, because that is the only forward value
 * the rest of the site knows; the detail is not lost anywhere it was shown.
 */
window.__addRoster1819 = function addRoster1819(site) {
  const out = JSON.parse(JSON.stringify(site));
  const season = out.seasons["2018-19"];
  if (!season) return { site: out, report: { error: "no 2018-19 season" } };

  /* "6'1\"" as typed, in the prime characters the rest of the roster uses. */
  const ht = (s) => String(s).replace(/'/g, "′").replace(/"/g, "″");
  /* Every roster line here is American unless it says otherwise, so the
     country is dropped for US players and kept for everyone else. */
  const home = (s) => String(s).replace(/,\s*USA$/, "");

  const P = (number, name, position, height, weight, hometown, shoots) => ({
    id: Math.random().toString(36).slice(2, 9),
    number, name, position, shoots,
    year: "", height: ht(height), weight: weight + " lbs",
    hometown: home(hometown), highSchool: "", priorTeam: "", captain: "",
  });

  const roster = [
    /* Goaltenders */
    P("32", "Ethan Crick", "G", "6'1\"", 161, "Calgary, AB, CAN", "L"),
    P("35", "Sami Morse", "G", "6'0\"", 190, "Falls Church, VA, USA", "L"),
    P("1", "Conner Taherian", "G", "5'11\"", 181, "Mission Viejo, CA, USA", "L"),

    /* Defensemen */
    P("24", "Sean Butler", "D", "6'3\"", 185, "Carmel, CA, USA", "R"),
    P("4", "Matt Chorlian", "D", "5'9\"", 154, "Concord, NH, USA", "L"),
    P("9", "Devin Cox", "D", "5'8\"", 154, "Pleasanton, CA, USA", "R"),
    P("10", "Alexandre Orcutt", "D", "5'10\"", 165, "Concord, NH, USA", "R"),
    P("17", "Jordan Thompson", "D", "6'1\"", 170, "Calgary, AB, CAN", "R"),
    P("27", "Kevin Wang", "D", "5'11\"", 146, "Great Falls, VA, USA", "R"),

    /* Forwards */
    P("21", "Max Brownlee", "F", "6'2\"", 181, "Santa Rosa, CA, USA", "R"),
    P("15", "Duncan Cadeddu", "F", "6'1\"", 161, "Dallas, TX, USA", "R"),
    P("8", "Jeffrey Chen", "F", "5'10\"", 165, "Chappaqua, NY, USA", "R"),
    P("18", "Gabriel Giammarco", "F", "6'0\"", 161, "Los Angeles, CA, USA", "L"),
    P("12", "Jack Gibbons", "F", "6'0\"", 181, "New York, NY, USA", "L"),
    P("5", "Michael Leone", "F", "6'3\"", 209, "San Diego, CA, USA", "L"),
    P("19", "Darien Oliver", "F", "5'10\"", 181, "San Dimas, CA, USA", "R"),
    P("2", "Ron Paulos", "F", "5'8\"", 150, "Fullerton, CA, USA", "R"),
    P("28", "Sasha Soloviev", "F", "5'9\"", 150, "Millbrae, CA, USA", "L"),
    P("16", "William Song", "F", "5'10\"", 154, "Boxborough, MA, USA", "R"),
    P("7", "Noah Spieser", "F", "6'0\"", 170, "Palos Verdes, CA, USA", "L"),
    P("14", "Chase Swerdlick", "F", "5'10\"", 161, "Cromwell, CT, USA", "R"),
    P("6", "Patrick Tagari", "F", "5'10\"", 181, "Newbury Park, CA, USA", "R"),
    P("26", "Delfino Varela", "F", "5'11\"", 174, "Montebello, CA, USA", "R"),
    P("3", "Andrew Wong", "F", "5'5\"", 150, "South Pasadena, CA, USA", "R"),
  ];

  season.roster = roster;
  return {
    site: out,
    report: {
      total: roster.length,
      goalies: roster.filter((p) => p.position === "G").length,
      defense: roster.filter((p) => p.position === "D").length,
      forwards: roster.filter((p) => p.position === "F").length,
    },
  };
};
