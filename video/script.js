/* ------------------------------------------------------------------
   Harish budget explainer — scene script and timeline data
   Vertical 9:16 (1080x1920). All copy is written without dashes.

   TYPOGRAPHY RULE: no scene may set its own font size.
   Every element takes its size from window.TYPE in video.html.
   Lines are hand broken so that nothing ever needs to be shrunk
   to fit, which is what keeps the hierarchy identical end to end.
   Keep every statement line at 22 characters or fewer, and every
   cream paragraph line at 28 or fewer.
   ------------------------------------------------------------------ */

/* Safe area for Instagram Reels (1080x1920):
   right column 940+ is covered by action buttons,
   bottom 420px by caption / profile / audio strip,
   top 300px by the header gradient. Everything critical lives inside. */
window.LAYOUT = {
  W: 1080, H: 1920,
  padRight: 880,   // right edge of RTL text
  padLeft: 110,    // left edge of text
  ruleX: 912,      // gold vertical rule
  safeTop: 300,
  safeBottom: 1500
};

/* type:
     'statement'  full navy, right aligned block, gold rule
     'kicker'     full navy, gold lead in + statement block
     'data'       split, gold section label + two figure blocks
     'total'      split, one dominant figure
     'split'      navy statement on top, list or heading on cream
     'people'     navy statement + portrait row on cream
*/
window.SCENES = [

  { id: 'hook', dur: 5.0, type: 'statement',
    lines: [
      'עדכון התקציב הזה',
      'מסכן את היכולת של חריש',
      'לתת לתושבים',
      'שירותים בסיסיים.'
    ] },

  { id: 'direction', dur: 4.6, type: 'kicker',
    kicker: 'מה חוזר שוב ושוב בתקציב',
    lines: [
      'פחות כסף לעובדי העירייה.',
      '',
      'יותר כסף לקבלנים,',
      'ליועצים ולספקים מבחוץ.'
    ] },

  { id: 'eng-data', dur: 4.4, type: 'data', label: 'הנדסה',
    top:    { figure: '1.325 מיליון ש״ח', caption: 'פחות בשכר עובדי העירייה' },
    bottom: { figure: '970 אלף ש״ח',      caption: 'יותר לייעוץ ולפיקוח מבחוץ' } },

  { id: 'eng-why', dur: 4.2, type: 'statement',
    lines: [
      'עובדי ההנדסה מכירים',
      'את התכניות של העיר,',
      'את התשתיות, את השכונות',
      'ואת הקבלנים.'
    ] },

  { id: 'eng-why2', dur: 3.8, type: 'statement',
    lines: [
      'הם עובדים בעירייה.',
      'הם כפופים למנהלים שלה.',
      'והידע שלהם',
      'נשאר בעירייה.'
    ] },

  { id: 'san-data', dur: 4.2, type: 'data', label: 'תברואה',
    top:    { figure: '421 אלף ש״ח',     caption: 'פחות בשכר עובדי העירייה' },
    bottom: { figure: '2.43 מיליון ש״ח', caption: 'יותר לקבלנים' } },

  { id: 'san-when', dur: 3.6, type: 'statement',
    lines: [
      'כשהאשפה לא מפונה.',
      'כשיש מפגע ברחוב.',
      'כשקבלן לא עושה',
      'את מה שהתחייב.'
    ] },

  { id: 'san-need', dur: 4.0, type: 'statement',
    lines: [
      'צריך בעירייה אנשים',
      'שמכירים את השטח,',
      'שיודעים מה הוזמן',
      'ושיודעים לדרוש תיקון.'
    ] },

  { id: 'col-data', dur: 3.4, type: 'data', label: 'גבייה',
    top: { figure: '900 אלף ש״ח', caption: 'יותר לקבלנים מבחוץ' } },

  { id: 'col-list', dur: 4.0, type: 'split',
    lines: ['ארנונה.', 'חיובים.', 'טעויות.', 'בירורים מול תושבים.', 'מידע שנאסף במשך שנים.'],
    creamHeading: ['יותר ויותר מהעבודה הזו', 'עוברת לגורמים מבחוץ.'] },

  { id: 'total', dur: 4.4, type: 'total',
    kicker: 'בסך הכול',
    figure: ['3.2 מיליון ש״ח', 'פחות'],
    caption: 'בשכר של עובדי העירייה' },

  { id: 'employees', dur: 5.0, type: 'kicker',
    kicker: 'מי הם עובדי העירייה',
    lines: [
      'הם נשארים בעירייה',
      'לאורך שנים.',
      'הם צוברים ניסיון.',
      'הם מכירים את העיר.',
      'והידע שלהם נשאר',
      'גם כשהקבלן מתחלף.'
    ] },

  { id: 'growth', dur: 4.2, type: 'split',
    lines: ['וחריש עדיין גדלה.'],
    creamList: ['יותר שכונות. יותר בתי ספר.',
                'יותר כבישים. יותר תשתיות.',
                'יותר תושבים ויותר שירותים.'] },

  { id: 'meaning', dur: 4.6, type: 'statement',
    lines: [
      'ככל שיותר עבודה',
      'עוברת לגורמים מבחוץ,',
      'צריך יותר אנשי מקצוע',
      'בעירייה שיידעו לנהל',
      'ולפקח עליהם.'
    ] },

  { id: 'shrink', dur: 3.8, type: 'statement',
    lines: [
      'כשמקצצים בעובדים',
      'שמחזיקים את הידע,',
      'ומעבירים עוד ועוד',
      'עבודה החוצה,'
    ] },

  { id: 'fewer', dur: 4.4, type: 'statement',
    lines: [
      'נשארים פחות אנשים',
      'שמכירים את העירייה.',
      'פחות אנשים שמפקחים.',
      'פחות אנשים שיודעים',
      'לזהות בזמן שמשהו נשבר.'
    ] },

  { id: 'not-budget', dur: 4.6, type: 'split',
    lines: ['זו כבר לא שאלה', 'של תקציב.', '', 'זו היכולת של העירייה', 'לתת שירות.'],
    creamList: ['לילדים. למשפחות. למבוגרים.',
                'למשרתי מילואים. לעסקים.',
                'לכל מי שחי כאן.'] },

  { id: 'systems', dur: 4.8, type: 'kicker',
    kicker: 'מי שמבין בניהול יודע',
    lines: [
      'עירייה שמאבדת',
      'את האנשים ואת הידע שלה',
      'לא תוכל לאורך זמן',
      'לתת לתושבים',
      'את השירותים',
      'שהיא חייבת לתת.'
    ] },

  { id: 'people', dur: 4.8, type: 'people',
    lines: [
      'זה הזמן לשים',
      'את טובת העיר',
      'מעל כל שיקול פוליטי.',
      '',
      'להתנגד בתוקף לתיקון',
      'התקציב הזה.'
    ],
    people: [
      { img: 'assets/itzik-lev.png',        name: 'איציק לב' },
      { img: 'assets/reutal-gonen.png',     name: 'רויטל גונן' },
      { img: 'assets/noga-david.png',       name: 'נגה דוד' },
      { img: 'assets/moshe-ben-zikri.png',  name: 'משה בן זיקרי' }
    ] },

  { id: 'final', dur: 5.4, type: 'statement',
    lines: [
      'אם זה לא ייעצר,',
      'עיריית חריש לא תוכל',
      'לתת לתושבים',
      'את השירותים',
      'שהיא חייבת לתת.'
    ],
    tail: 'זה מה שעומד על הפרק.' }

];
