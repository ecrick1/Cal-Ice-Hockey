"""Fold the newly-read EliteProspects seasons into _ephistory.json.

2011-12, 2015-16 and 2016-17 exist on EliteProspects but are not linked from
the team page's season list, which is why the first pass missed them. The
roster tab also carries a birthplace, so 2017-18 and 2010-11 gain hometowns
they did not have.

Run: python _epmerge.py
"""
import io
import json

p = '_ephistory.json'
d = json.load(io.open(p, encoding='utf-8'))

d['source'] = ("eliteprospects.com/team/10366 - each season's roster tab and stats tab, "
               "read in the browser")
d['note'] = ("S = name~pos~GP~G~A~PIM   G = name~GP~GAA~SV%~SO~TOI~SVS   "
             "B = name~number~pos~height~weight~shoots~birthplace")
d['gap'] = ("EliteProspects has no Cal roster for 2012-13, 2013-14 or 2014-15 - those season "
            "URLs fall back to the current season. The ACHA's own system starts at 2020-21, "
            "where Cal is listed as a member with no roster and no games (the COVID year). "
            "Nothing exists to import for any of them.")

by = {s['season']: s for s in d['seasons']}

# Birthplaces from each season's roster tab. A trailing ", USA" is dropped to
# match the site's existing convention; a bare state code is spelled out.
HOME = {
    '2017-18': {
        'Ethan Crick': 'Calgary, AB, CAN', 'Sami Morse': 'Falls Church, VA',
        'Everett Morton': 'Telluride, CO', 'Devin Cox': 'Pleasanton, CA',
        'Alexandre Orcutt': 'Concord, NH', 'Jordan Thompson': 'Calgary, AB, CAN',
        'Kevin Wang': 'Great Falls, VA', 'Steve Bagley': 'Napa, CA',
        'Duncan Cadeddu': 'Dallas, TX', 'Jeffrey Chen': 'Chappaqua, NY',
        'Gabriel Giammarco': 'Los Angeles, CA', 'Laurent Hsia': 'Taipei, TWN',
        'Michael Leone': 'San Diego, CA', 'Yuki Obata': 'London, GBR',
        'Darien Oliver': 'San Dimas, CA', 'Peter Shin': 'Montrose, CA',
        'William Song': 'Boxborough, MA', 'Noah Spieser': 'Palos Verdes, CA',
        'Chase Swerdlick': 'Cromwell, CT', 'Patrick Tagari': 'Newbury Park, CA',
        'Delfino Varela': 'Montebello, CA',
    },
    '2010-11': {
        'Mathew Bloomfield': 'Manteca, CA', 'Peter Christian Tartaglia': 'Thousand Oaks, CA',
        'Arash Amirnezami': 'Los Angeles, CA', 'Grant Brown': 'Redwood City, CA',
        'Matt Henry': 'San Francisco, CA', 'Hayley Moore': 'San Jose, CA',
        'Alex Niu': 'McCall, ID', 'Michael Scruton': '', 'Daniel Sulitzer': 'Calabasas, CA',
        'Sam Birch': 'LaSalle, MI', 'Wesley Borja': 'San Jose, CA',
        'David Carlson': 'California', 'Mike Fina': 'Glen Ellyn, IL', 'Mike Gilroy': '',
        'Alex Gordon': 'Pleasant Hill, CA', 'Sean Haq': 'Shrewsbury, MA',
        'Peter Kler': 'San Diego, CA', 'Alex Linz': 'Los Angeles, CA',
        'J.P. McNicholas': 'San Jose, CA', "Peter O'Reilly": 'California',
        'Patrick Paul': 'California', 'Eugene Shuster': 'Santa Rosa, CA',
        'Jeff Spinardi': 'Merced, CA', 'Ian Stewart': '', 'Keisuke Teeple': 'Menlo Park, CA',
        'Zhikai Wang': 'Carlsbad, CA', 'T.J. Wynn': 'Benicia, CA',
    },
}
for key, homes in HOME.items():
    rows = []
    for r in by[key]['B']:
        name = r.split('~')[0]
        assert name in homes, (key, name)
        rows.append(r + '~' + homes[name])
    by[key]['B'] = rows

NEW = [
    {
        'season': '2016-17',
        'S': [
            'Peter Shin~RW~15~21~21~13', 'Michael Leone~F~16~19~23~15',
            'Delfino Varela~F~16~19~16~8', 'C.J. Geering~D~16~5~15~8',
            'Chase Swerdlick~F~16~9~8~2', 'Steve Bagley~F~14~6~9~2',
            'Alex Pelletier~D~16~5~7~6', 'John Fu~F~15~5~3~4',
            'Kyle Kelly~LW~9~5~2~2', 'Nico Picciuto~D~10~5~1~2',
            'Jordan Thompson~D~16~2~4~4', 'Duncan Cadeddu~F~15~0~5~6',
            'Robert Maxwell~LW~3~1~1~0', 'Travis Sherman~D~7~0~1~2',
            'Kenan Kurtkan~F~2~0~0~0', 'William Song~C~4~0~0~0',
        ],
        'G': ['Sami Morse~13~3.40~.864~-~-~-'],
        'B': [
            'Sami Morse~30~G~6\'0"~190~L~Falls Church, VA',
            'C.J. Geering~6~D~6\'0"~170~R~Berkeley, CA',
            'Alex Pelletier~9~D~6\'2"~185~R~Tracy, CA',
            'Nico Picciuto~2~D~6\'0"~174~L~Santa Ana, CA',
            'Travis Sherman~~D~5\'10"~185~R~San Diego, CA',
            'Jordan Thompson~17~D~6\'1"~170~R~Calgary, AB, CAN',
            'Steve Bagley~13~F~5\'11"~170~L~Napa, CA',
            'Duncan Cadeddu~25~F~6\'1"~161~R~Dallas, TX',
            'John Fu~12~F~5\'8"~141~R~Hong Kong, HKG',
            'Kyle Kelly~15~F~6\'3"~201~L~San Diego, CA',
            'Kenan Kurtkan~8~F~5\'9"~161~~',
            'Michael Leone~5~F~6\'3"~209~L~San Diego, CA',
            'Robert Maxwell~11~F~5\'11"~174~~Oakland, CA',
            'Peter Shin~4~F~5\'6"~154~R~Montrose, CA',
            'William Song~27~F~5\'10"~154~R~Boxborough, MA',
            'Chase Swerdlick~14~F~5\'10"~161~R~Cromwell, CT',
            'Delfino Varela~26~F~5\'11"~174~R~Montebello, CA',
        ],
    },
    {
        'season': '2015-16',
        'S': [
            'Michael Leone~F~12~15~12~12', 'Nic Kawasaki~D~12~12~9~16',
            'Bryce Morisako~C~11~7~9~16', 'Theo Haboucha~RW~10~9~4~2',
            'Nico Picciuto~D~12~5~8~18', 'Steve Bagley~F~12~3~10~2',
            'C.J. Geering~D~12~1~10~12', 'Kyle Kelly~LW~12~6~3~12',
            'Jeffrey Leong~D~12~1~6~6', 'John Fu~F~11~3~2~2',
            'Travis Sherman~D~8~1~2~8', 'Alexandre Orcutt~D~12~1~2~16',
            'Pei En Cong~F~12~0~3~4', 'Alex Pelletier~D~10~0~2~14',
            'Sandon Griffin~F~12~0~2~18', 'Markus Kytömaa~F~11~1~0~11',
            'Troy Skinner~LW~11~0~1~2', 'Noah Mehr~F~0~0~0~0',
            'Maxwell Klaiman~F~1~0~0~0', 'Duke Moran~LW~7~0~0~0',
            'Orian Williams~F~7~0~0~2',
        ],
        'G': ['Kyle McAllister~10~4.26~.846~-~-~-', 'Eric Esposito~2~7.50~.833~-~-~-'],
        'B': [
            'Eric Esposito~29~G~6\'4"~243~L~East Hanover, NJ',
            'Kyle McAllister~30~G~6\'5"~225~L~Kitchener, ON, CAN',
            'C.J. Geering~6~D~6\'0"~170~R~Berkeley, CA',
            'Nic Kawasaki~19~D~5\'11"~216~R~Atherton, CA',
            'Jeffrey Leong~28~D~6\'0"~209~R~Los Gatos, CA',
            'Alexandre Orcutt~10~D~5\'10"~165~R~Concord, NH',
            'Alex Pelletier~9~D~6\'2"~185~R~Tracy, CA',
            'Nico Picciuto~4~D~6\'0"~174~L~Santa Ana, CA',
            'Travis Sherman~7~D~5\'10"~185~R~San Diego, CA',
            'Steve Bagley~13~F~5\'11"~170~L~Napa, CA',
            'Pei En Cong~23~F~5\'10"~174~R~Beijing, CHN',
            'John Fu~27~F~5\'8"~141~R~Hong Kong, HKG',
            'Sandon Griffin~11~F~6\'4"~190~R~Corona del Mar, CA',
            'Theo Haboucha~25~F~5\'9"~174~R~Santa Monica, CA',
            'Kyle Kelly~15~F~6\'3"~201~L~San Diego, CA',
            'Maxwell Klaiman~12~F~6\'0"~170~R~Medina, MN',
            'Markus Kytömaa~17~F~6\'2"~181~R~Belmont, MA',
            'Michael Leone~5~F~6\'3"~209~L~San Diego, CA',
            'Noah Mehr~26~F~5\'6"~130~R~Dallas, TX',
            'Duke Moran~2~F~6\'2"~220~R~Menlo Park, CA',
            'Bryce Morisako~20~F~6\'0"~154~R~Berkeley, CA',
            'Troy Skinner~3~F~5\'10"~181~L~Carpinteria, CA',
            'Orian Williams~8~F~6\'2"~216~R~Cleveland, OH',
        ],
    },
    {
        'season': '2011-12',
        'S': [
            'J.P. McNicholas~C~8~7~4~4', 'Jake White~D~5~3~3~14',
            'Peter Kler~F~8~1~5~30', 'Sandon Griffin~F~6~2~3~4',
            'Sam Birch~LW~6~1~1~8', 'Matthew Springer~D~8~1~1~2',
            'Justin Tetyevsky~D~9~1~1~18', 'Hayley Moore~D/F~2~0~2~0',
            'Timmy Linehan~F~2~0~2~2', 'Mike Janus~F~2~1~0~0',
            'Zhikai Wang~F~5~1~0~2', 'Craig Armstrong~F~4~0~1~0',
            'Jeff Spinardi~F~1~0~0~0', 'Ryan Bena~F~1~0~0~0',
            'Grant Brown~D~5~0~0~8',
        ],
        'G': ['Mathew Bloomfield~9~11.89~.680~-~-~-'],
        'B': [
            'Mathew Bloomfield~39~G~5\'11"~161~L~Manteca, CA',
            'Grant Brown~2~D~5\'11"~174~R~Redwood City, CA',
            'Hayley Moore~59~D~5\'6"~141~R~San Jose, CA',
            'Matthew Springer~7~D~6\'7"~249~~San Marino, CA',
            'Justin Tetyevsky~22~D~5\'8"~209~~North Caldwell, NJ',
            'Jake White~27~D~5\'10"~161~L~Huntington Beach, CA',
            'Craig Armstrong~19~F~5\'10"~174~~Fresno, CA',
            'Ryan Bena~18~F~6\'0"~181~~Palos Verdes Estates, CA',
            'Sam Birch~21~F~5\'5"~150~L~LaSalle, MI',
            'Sandon Griffin~18~F~6\'4"~190~R~Corona del Mar, CA',
            'Mike Janus~28~F~~~~Moorpark, CA',
            'Peter Kler~23~F~6\'2"~181~R~San Diego, CA',
            'Timmy Linehan~16~F~5\'8"~154~R~Hawthorne, CA',
            'J.P. McNicholas~10~F~5\'9"~170~R~San Jose, CA',
            'Jeff Spinardi~20~F~6\'2"~220~R~Merced, CA',
            'Zhikai Wang~36~F~6\'0"~181~R~Carlsbad, CA',
        ],
    },
]

for s in NEW:
    by[s['season']] = s

ORDER = ['2019-20', '2018-19', '2017-18', '2016-17', '2015-16', '2011-12', '2010-11']
d['seasons'] = [by[k] for k in ORDER]

# Every stats line must have a bio line and every bio line a stats line.
for s in d['seasons']:
    stats = {r.split('~')[0] for r in s['S']} | {r.split('~')[0] for r in s['G']}
    bios = {r.split('~')[0] for r in s['B']}
    assert stats == bios, (s['season'], sorted(stats ^ bios))

io.open(p, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1))
print('seasons: ' + ', '.join(
    '%s (%d skaters, %d goalies)' % (s['season'], len(s['S']), len(s['G']))
    for s in d['seasons']))
