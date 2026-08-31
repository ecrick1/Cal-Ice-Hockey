/**
 * Invented staff for the two empty sections.
 *
 * These are NOT real people. They exist so Medical & Performance and Support
 * are not blank while the design is being reviewed, and every one of them
 * carries `demo: true` - which is what makes them removable in one pass:
 *
 *   __dropDemoStaff(site)
 *
 * The names were checked against every roster on file so none of them can be
 * mistaken for someone who actually skated here. The email addresses are on
 * the club domain because that is what the card layout has to be judged
 * against, but they go nowhere. Delete these before the site is public.
 */
window.__addDemoStaff = function addDemoStaff(site) {
  const out = JSON.parse(JSON.stringify(site));

  const P = (name, title, group, extra) => ({
    id: Math.random().toString(36).slice(2, 9),
    name, title, roleGroup: group, demo: true,
    email: (extra && extra.email) || "",
    phone: (extra && extra.phone) || "",
    since: (extra && extra.since) || "",
    photo: null, featured: false,
  });

  const made = [
    /* Medical & Performance */
    P("Priya Raghavan", "Head Athletic Trainer", "medical", {
      email: "training@calicehockey.com", phone: "510-555-0142", since: "2022",
    }),
    P("Marcus Delaney", "Assistant Athletic Trainer", "medical", { since: "2024" }),
    P("Sofia Ibarra", "Strength & Conditioning Coach", "medical", { since: "2023" }),
    P("Alan Whitfield", "Team Physician", "medical"),

    /* Support */
    P("Jonah Bregman", "Equipment Manager", "other", {
      email: "equipment@calicehockey.com", since: "2021",
    }),
    P("Casey Lindqvist", "Assistant Equipment Manager", "other"),
    P("Nadia Osei", "Team Manager", "other", { since: "2023" }),
    P("Ellis Trent", "Video Coordinator", "other"),
    P("Harper Quinn", "Team Statistician", "other", { since: "2024" }),
  ];

  /* Appended, never replacing - the real sixteen stay exactly as they are. */
  out.staff = [...(out.staff || []).filter((c) => !c.demo), ...made];
  return {
    site: out,
    report: {
      added: made.length,
      medical: made.filter((c) => c.roleGroup === "medical").length,
      support: made.filter((c) => c.roleGroup === "other").length,
      realKept: (out.staff || []).filter((c) => !c.demo).length,
    },
  };
};

/* The undo. */
window.__dropDemoStaff = function dropDemoStaff(site) {
  const out = JSON.parse(JSON.stringify(site));
  const before = (out.staff || []).length;
  out.staff = (out.staff || []).filter((c) => !c.demo);
  return { site: out, report: { removed: before - out.staff.length, left: out.staff.length } };
};
