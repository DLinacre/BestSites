# -*- coding: utf-8 -*-
"""Content timeline for the r/Piracy 'GTA 6 decomp' video.

Every beat matches one narration clip (audio/beatN.mp3). Scenes inside a beat
are positioned as fractions of that beat's duration, chosen to roughly track
the narration.
"""

# ---------------------------------------------------------------- comments ---
# Trimmed / lightly tidied quotes of public Reddit comments. Kept short.
CARDS = {
    "top": {
        "user": "namesallltaken",
        "tag": "TOP COMMENT",
        "time": "4h",
        "votes": "224",
        "body": [
            "gta 6 has already broken even before its release. it's already "
            "crossed $4 billion in revenue, way above its estimated dev + "
            "marketing costs of $1.5B at most. so i think rockstar can afford "
            "to take some hits from pc cracks",
        ],
    },
    "security": {
        "user": "rouncer999",
        "tag": "THE REAL ISSUE",
        "time": "4h",
        "votes": "158",
        "body": [
            "they can take hits from the pc scene sure, but I think they will "
            "be more bothered about security and how this managed to get "
            "leaked in the first place.",
            "Which is why I think they\u2019ll come after us",
        ],
    },
    "union": {
        "user": "OcelotAggravating860",
        "tag": "THE THEORY",
        "time": "4h",
        "votes": "97",
        "body": [
            "I don't think that's hard to guess at. Shouldn't have done the "
            "union busting, they shouldn't have fired the entire membership "
            "of the union. Union members will still have friends that didn't "
            "get fired in the company.",
            "Consequences are they're going to lose at least a billion for it, "
            "if not more.",
        ],
    },
    "abc": {
        "user": "justicerainsfromaahh",
        "tag": "ELI5",
        "time": "4h",
        "votes": "312",
        "body": [
            "Console speaks ABC, PC speaks 123. Humans have to figure out how "
            "to translate ABC into 123, AI speeds shit up.",
        ],
    },
    "mona": {
        "user": "Tanmay_Terminator",
        "tag": "IN THE THREAD",
        "time": "1h",
        "votes": "88",
        "body": ["YARR \u2014 WALK THE PLANK.",
                 "its like watching mona lisa getting painted"],
    },
    "fun": {
        "user": "InsidiousFartMachine",
        "tag": "SAME",
        "time": "4h",
        "votes": "140",
        "body": [
            "I think this whole decompilation effort is going to have been "
            "more fun watching, than playing the game will be for me.",
        ],
    },
    "cope": {
        "user": "Imaginary_Resource50",
        "tag": "IN THE THREAD",
        "time": "2h",
        "votes": "201",
        "body": ["We got gta 6 pc before gta 6 pc"],
    },
    "mandy": {
        "user": "Master_Thud",
        "tag": "THE PLAN",
        "time": "4h",
        "votes": "75",
        "body": ["It means soon you'll be painting walls."],
    },
    "lawyers": {
        "user": "Treat_Honest",
        "tag": "REALIST",
        "time": "1h",
        "votes": "63",
        "body": [
            "They will probably release pc with its online part... It will cost "
            "them, sure, but they won't care. Also, they already have a fleet "
            "of lawyers. They just have to work for their money now.",
        ],
    },
    "proton": {
        "user": "drinkingcarrots",
        "tag": "THE TECHNICAL ONE",
        "time": "4h",
        "votes": "186",
        "body": [
            "this is like running a Windows game on Linux, it took them a "
            "decade to get almost all games to run on Linux through "
            "wine/proton. They are essentially doing the same thing that took "
            "a decade, but more targeted (easier) by using AI.",
        ],
    },
}


def card(key, **over):
    d = dict(CARDS[key])
    d.update(over)
    return d


# ------------------------------------------------------------------- scenes ---
# kind: title | stat | quote | card | explain | decomp | money | end
# frac: (start, end) inside the beat.  layers created by the renderer.
BEATS = [
    {
        "id": "b1",
        "scenes": [
            {
                "kind": "title",
                "frac": (0.0, 0.24),
                "kicker": "r/Piracy  \u2022  sort by: new",
                "l1": "GTA VI",
                "l2": "IS ALREADY",
                "l3": "ON PC",
                "sub": "five days after launch.  there is no PC version.",
                "accent": "orange",
            },
            {
                "kind": "stat",
                "frac": (0.24, 0.50),
                "big": "$4,000,000,000",
                "label": "REVENUE",
                "sub": "before a single PC copy was sold",
                "ghost": "4B",
                "accent": "orange",
            },
            {
                "kind": "stat",
                "frac": (0.50, 0.76),
                "big": "1.5B",
                "label": "MAX ESTIMATED DEV + MARKETING",
                "sub": "allegedly. per the thread. i'm not an accountant.",
                "ghost": "1.5",
                "accent": "teal",
            },
            {
                "kind": "quote",
                "frac": (0.76, 1.0),
                "l1": "SO THE INTERNET",
                "l2": "REBUILT IT.",
                "sub": "by hand.  in public.  with AI.  obviously.",
                "ghost": "YARR",
                "accent": "pink",
            },
        ],
    },
    {
        "id": "b2",
        "scenes": [
            {
                "kind": "card",
                "frac": (0.0, 0.30),
                "comment": card("top"),
                "accent": "orange",
                "glow": True,
            },
            {
                "kind": "money",
                "frac": (0.30, 0.60),
                "label": "IN",
                "target": 4_000_000_000,
                "sub": "$4B in.  $1.5B out.  that's a rounding error.",
                "accent": "orange",
            },
            {
                "kind": "quote",
                "frac": (0.60, 0.82),
                "l1": "ROCKSTAR CAN",
                "l2": "AFFORD THE HITS.",
                "sub": "a few cracked copies vs four billion dollars",
                "ghost": "$$$",
                "accent": "teal",
            },
            {
                "kind": "quote",
                "frac": (0.82, 1.0),
                "l1": "ROCKSTAR: \u201cWE\u2019LL BE FINE.\u201d",
                "l2": "ROCKSTAR: HIRES MORE LAWYERS.",
                "sub": "",
                "ghost": "S.A.",
                "accent": "pink",
            },
        ],
    },
    {
        "id": "b3",
        "scenes": [
            {
                "kind": "quote",
                "frac": (0.0, 0.40),
                "l1": "IT\u2019S NOT THE MONEY.",
                "l2": "IT\u2019S THE BREACH.",
                "sub": "rockstar cares enormously about being embarrassed",
                "ghost": "SEC",
                "accent": "pink",
            },
            {
                "kind": "card",
                "frac": (0.40, 0.76),
                "comment": card("security"),
                "accent": "orange",
            },
            {
                "kind": "quote",
                "frac": (0.76, 1.0),
                "l1": "SO THEY\u2019RE",
                "l2": "COMING FOR US.",
                "sub": "",
                "ghost": "RUN",
                "accent": "orange",
            },
        ],
    },
    {
        "id": "b4",
        "scenes": [
            {
                "kind": "card",
                "frac": (0.0, 0.34),
                "comment": card("union"),
                "accent": "orange",
            },
            {
                "kind": "quote",
                "frac": (0.34, 0.66),
                "l1": "FIRE THE UNION.",
                "l2": "KEEP THE GRUDGE.",
                "sub": "consequences: at least a billion. allegedly.",
                "ghost": "UNION",
                "accent": "teal",
            },
            {
                "kind": "quote",
                "frac": (0.66, 1.0),
                "l1": "I\u2019M NOT A LAWYER.",
                "l2": "I\u2019M BARELY A NARRATOR.",
                "sub": "",
                "ghost": "IANAL",
                "accent": "pink",
            },
        ],
    },
    {
        "id": "b5",
        "scenes": [
            {
                "kind": "quote",
                "frac": (0.0, 0.30),
                "l1": "\u201cIT WOULD\u2019VE BEEN",
                "l2": "PIRATED ANYWAY.\u201d",
                "sub": "the demand was always there",
                "ghost": "EVER",
                "accent": "teal",
            },
            {
                "kind": "quote",
                "frac": (0.30, 0.62),
                "l1": "BUT 6\u201312 MONTHS",
                "l2": "EARLY HITS DIFFERENT",
                "sub": "a portion of early players never pay up",
                "ghost": "-6mo",
                "accent": "pink",
            },
            {
                "kind": "quote",
                "frac": (0.62, 1.0),
                "l1": "BOTH ARE RIGHT.",
                "l2": "THE WORST KIND OF ARGUMENT.",
                "sub": "",
                "ghost": "VS",
                "accent": "orange",
            },
        ],
    },
    {
        "id": "b6",
        "scenes": [
            {
                "kind": "card",
                "frac": (0.0, 0.32),
                "comment": card("abc"),
                "accent": "orange",
            },
            {
                "kind": "explain",
                "frac": (0.32, 0.64),
                "l1": "LEGO \u2192 PLAY-DOH",
                "l2": "THE SAME MANSION, REBUILT.",
                "sub": "console speaks ABC. pc speaks 123. the thread translates.",
                "accent": "teal",
            },
            {
                "kind": "decomp",
                "frac": (0.64, 1.0),
                "l1": "LIVE DECOMPILATION",
                "l2": "NOT A SINGLE COMPILE ERROR (LIE)",
                "sub": "proton took ten years. this took a weekend.",
                "accent": "pink",
            },
        ],
    },
    {
        "id": "b7",
        "scenes": [
            {
                "kind": "card",
                "frac": (0.0, 0.30),
                "comment": card("mona"),
                "accent": "orange",
            },
            {
                "kind": "card",
                "frac": (0.30, 0.56),
                "comment": card("cope"),
                "accent": "orange",
            },
            {
                "kind": "card",
                "frac": (0.56, 0.78),
                "comment": card("mandy"),
                "accent": "orange",
            },
            {
                "kind": "quote",
                "frac": (0.78, 1.0),
                "l1": "YARR.",
                "l2": "COMPILE MANDY FIRST.",
                "sub": "sail safe. don't click random links.",
                "ghost": "YARR",
                "accent": "teal",
            },
        ],
    },
    {
        "id": "b8",
        "scenes": [
            {
                "kind": "quote",
                "frac": (0.0, 0.34),
                "l1": "WILL IT WORK?",
                "l2": "UNKNOWN.",
                "sub": "will take-two panic-release the PC version?  almost certainly not.",
                "ghost": "?",
                "accent": "teal",
            },
            {
                "kind": "quote",
                "frac": (0.34, 0.64),
                "l1": "STILL THE MOST FUN",
                "l2": "ON THE INTERNET.",
                "sub": "and it isn\u2019t even playable yet",
                "ghost": "FUN",
                "accent": "pink",
            },
            {
                "kind": "end",
                "frac": (0.64, 1.0),
                "l1": "GTA VI: PC EDITION*",
                "l2": "*NOT OFFICIAL. NOT LEGAL ADVICE.",
                "l3": "NOT PLAYABLE.",
                "sub": "r/Piracy  \u2022  sail safe  \u2022  don\u2019t click random links",
                "accent": "orange",
            },
        ],
    },
]

# ---------------------------------------------------------------- captions ---
# Punched up quotes / jokes, timed evenly across each beat's speech.
CAPTIONS = {
    "b1": [
        "console launch only. no PC version exists.",
        "and not one PC copy sold.",
        "so strangers rebuilt the whole game. with AI.",
        "in public. in five days.",
    ],
    "b2": [
        "the thread does the maths.",
        "$4B in. $1.5B out. rounding error.",
        "rockstar is fine. the lawyers are not.",
    ],
    "b3": [
        "the money is not what stings.",
        "being embarrassed is.",
        "so expect the lawyers.",
    ],
    "b4": [
        "the thread blames the union busting.",
        "fire the union, keep the grudge.",
        "consequences: at least a billion. allegedly.",
    ],
    "b5": [
        "\u201cit would\u2019ve been pirated anyway.\u201d",
        "true. also six months early is worse.",
        "both sides are right. worst argument.",
    ],
    "b6": [
        "console speaks ABC. PC speaks 123.",
        "the mansion was Lego. now it\u2019s Play-Doh.",
        "proton took a decade. this took a weekend.",
    ],
    "b7": [
        "like watching the mona lisa get painted.",
        "we got GTA 6 PC before GTA 6 PC.",
        "someone is fixing mandy\u2019s pipes as we speak.",
        "yarr.",
    ],
    "b8": [
        "unknown. almost certainly not.",
        "more fun watching than playing will be.",
        "not playable. still the best show online.",
    ],
}

# ------------------------------------------------------------------ credits ---
SOURCES = [
    "Thread: r/Piracy \u2014 \u201cGTA 6 decompilation\u201d discussion, 2026",
    "Quotes: public Reddit comments, lightly trimmed, usernames shown",
    "Revenue/cost figures: as claimed in the thread, unverified",
    "Music + visuals: procedurally generated for this video",
]
