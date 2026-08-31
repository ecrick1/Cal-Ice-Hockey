/**
 * The 2019-20 roster, as supplied.
 *
 * Same rules as the 2018-19 import: real people, so nothing is invented. A
 * dash in the source means the figure is not on file, and is stored as blank
 * rather than as the character "-" - an empty field reads as unknown
 * everywhere on the site, a dash reads as data.
 *
 * Worth noting: Conner Taherian wears #29 this season, not the #1 he had in
 * 2018-19. Rosters are per season, so both are correct where they sit.
 */
window.__addRoster1920 = function addRoster1920(site) {
  const out = JSON.parse(JSON.stringify(site));
  const season = out.seasons["2019-20"];
  if (!season) return { site: out, report: { error: "no 2019-20 season" } };

  const blank = (v) => (v == null || v === "" || v === "-" ? "" : v);
  const ht = (s) => (blank(s) ? String(s).replace(/'/g, "′").replace(/"/g, "″") : "");
  const wt = (v) => (blank(v) ? v + " lbs" : "");
  const home = (s) => blank(s).replace(/,\s*USA$/, "");

  const P = (number, name, position, height, weight, hometown, shoots) => ({
    id: Math.random().toString(36).slice(2, 9),
    number, name, position, shoots: blank(shoots),
    year: "", height: ht(height), weight: wt(weight),
    hometown: home(hometown), highSchool: "", priorTeam: "", captain: "",
  });

  const roster = [
    /* Goaltenders */
    P("32", "Ethan Crick", "G", "6'1\"", 161, "Calgary, AB, CAN", "L"),
    P("35", "Sami Morse", "G", "6'0\"", 190, "Falls Church, VA, USA", "L"),
    P("29", "Conner Taherian", "G", "5'11\"", 181, "Mission Viejo, CA, USA", "L"),
    P("30", "Max Wiseman", "G", "6'0\"", 150, "Chevy Chase, MD, USA", "L"),

    /* Defensemen */
    P("25", "David Adams", "D", "5'11\"", 181, "San Ramon, CA, USA", "L"),
    P("24", "Sean Butler", "D", "6'3\"", 185, "Carmel, CA, USA", "R"),
    P("4", "Matt Chorlian", "D", "5'9\"", 154, "Concord, NH, USA", "L"),
    P("9", "Devin Cox", "D", "5'8\"", 154, "Pleasanton, CA, USA", "R"),
    P("11", "Jake Sitak", "D", "6'2\"", "-", "North Andover, MA, USA", "-"),
    P("17", "Jordan Thompson", "D", "6'1\"", 170, "Calgary, AB, CAN", "R"),
    P("27", "Kevin Wang", "D", "5'11\"", 146, "Great Falls, VA, USA", "R"),

    /* Forwards */
    P("21", "Max Brownlee", "F", "6'2\"", 181, "Santa Rosa, CA, USA", "R"),
    P("12", "Alexander Carbone", "F", "5'11\"", 170, "South Lake, TX, USA", "R"),
    P("16", "Pravin Chandra", "F", "-", "-", "Pleasanton, CA, USA", "L"),
    P("8", "Jeffrey Chen", "F", "5'10\"", 165, "Chappaqua, NY, USA", "R"),
    P("23", "Brian Faun", "F", "6'1\"", 185, "San Jose, CA, USA", "L"),
    P("13", "Ruslan Gabidoulline", "F", "-", "-", "", "-"),
    P("18", "Gabriel Giammarco", "F", "6'0\"", 161, "Los Angeles, CA, USA", "L"),
    P("10", "Anthony Lair", "F", "-", "-", "Plessisville, QC, CAN", "L"),
    P("22", "Nolan McMahon", "F", "-", "-", "Roseville, CA, USA", "-"),
    P("19", "Darien Oliver", "F", "5'10\"", 181, "San Dimas, CA, USA", "R"),
    P("2", "Ron Paulos", "F", "5'8\"", 150, "Fullerton, CA, USA", "R"),
    P("28", "Sasha Soloviev", "F", "5'9\"", 150, "Millbrae, CA, USA", "L"),
    P("7", "Noah Spieser", "F", "6'0\"", 170, "Palos Verdes, CA, USA", "L"),
    P("14", "Chase Swerdlick", "F", "5'10\"", 161, "Cromwell, CT, USA", "R"),
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
      blanks: roster.filter((p) => !p.height || !p.weight || !p.shoots || !p.hometown)
        .map((p) => p.name),
    },
  };
};
