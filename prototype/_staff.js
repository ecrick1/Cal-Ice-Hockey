/**
 * The staff list, as supplied.
 *
 * Real people, so only what was given is stored: name, title, and the contact
 * details for the two who have them. Photos, start years and bios are left
 * empty for the Staff tab to fill in.
 *
 * Devin Cox is marked the lead, which gives him the top block on the public
 * page - the page allows exactly one. Michele Cox heads the executive list by
 * position in it rather than by a second lead flag.
 *
 * Note the overlap with the roster: Cox, Oliver and Chandra all skated in
 * 2018-19 or 2019-20, and Mizuno, Goebel, Storr, Comeau, Akbas and Anaka are
 * on the current team. Staff and players are separate lists, so a person can
 * appear in both without the two records interfering.
 */
window.__addStaff = function addStaff(site) {
  const out = JSON.parse(JSON.stringify(site));

  const P = (name, title, group, extra) => ({
    id: Math.random().toString(36).slice(2, 9),
    name, title, roleGroup: group,
    email: (extra && extra.email) || "",
    phone: (extra && extra.phone) || "",
    photo: null, since: "", featured: !!(extra && extra.featured),
  });

  const staff = [
    /* Coaching */
    P("Devin Cox", "Head Coach", "coaching", {
      phone: "925-216-7455", email: "devincox@calicehockey.com", featured: true,
    }),
    P("Darien Oliver", "Assistant Coach", "coaching"),
    P("Pravin Chandra", "Assistant Coach", "coaching"),
    P("Mark Arneson", "Assistant Coach", "coaching"),
    P("Everett Morton", "Goalie Coach", "coaching"),
    P("Thor Oase", "Player Development Coach", "coaching"),

    /* Executive */
    P("Michele Cox", "General Manager", "operations", {
      phone: "310-818-1003", email: "michelecox@calicehockey.com",
    }),
    P("Kodai Mizuno", "Club President", "operations"),
    P("Enzo Goebel", "Vice President", "operations"),
    P("Tyson Storr", "Senior Advisor", "operations"),
    P("Aidan Comeau", "Head of Travel", "operations"),
    P("Yusuf Akbas", "Safety Officer", "operations"),
    P("Allan Anaka", "Head of Technology / Website Design", "operations"),
    P("Roxana Nourishad", "Director of Marketing", "operations"),
    P("Auden Meyer", "Game Day Operations", "operations"),
    P("Ryan Carlson", "Director of Broadcasting", "operations"),
  ];

  out.staff = staff;
  return {
    site: out,
    report: {
      total: staff.length,
      coaching: staff.filter((p) => p.roleGroup === "coaching").length,
      executive: staff.filter((p) => p.roleGroup === "operations").length,
      withContact: staff.filter((p) => p.email || p.phone).map((p) => p.name),
      lead: (staff.find((p) => p.featured) || {}).name,
    },
  };
};
