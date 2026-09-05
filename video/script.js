/* ------------------------------------------------------------------
   Harish budget explainer — scene script and timeline data
   Vertical 9:16 (1080x1920). All copy is written without dashes.
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
     'kicker'     full navy, muted kicker + statement block
     'data'       split, gold section label + two figure blocks
     'total'      split, one dominant figure
     'split'      navy statement on top, list or heading on cream
     'people'     navy statement + portrait row on cream
*/
window.SCENES = [

  { id: 'hook', dur: 5.0, type: 'statement', size: 58,
    lines: [
      'עדכון התקציב הזה',
      'מעמיד בסימן שאלה',
      'את היכולת של עיריית חריש',
      'להמשיך לספק לאורך זמן',
      'שירותים בסיסיים לתושבים.'
    ] },

  { id: 'direction', dur: 4.6, type: 'kicker', size: 52,
    kicker: 'הכיוון שחוזר שוב ושוב בתקציב',
    lines: [
      'פחות כסף לאנשים שעובדים',
      'בתוך העירייה עצמה.',
      '',
      'יותר כסף לקבלנים, יועצים',
      'וספקים חיצוניים.'
    ] },

  { id: 'eng-data', dur: 4.4, type: 'data', label: 'הנדסה',
    top:    { figure: '1.325 מיליון ש״ח פחות', caption: 'בשכר עובדי העירייה' },
    bottom: { figure: '970 אלף ש״ח יותר',       caption: 'לייעוץ ולפיקוח חיצוני' } },

  { id: 'eng-why', dur: 4.0, type: 'statement', size: 50,
    lines: [
      'עובדי ההנדסה הם האנשים',
      'שמכירים לאורך זמן את התכניות,',
      'הפרויקטים, התשתיות, השכונות',
      'והקבלנים של העיר.'
    ] },

  { id: 'eng-why2', dur: 3.6, type: 'statement', size: 52,
    lines: [
      'הם עובדים בתוך העירייה.',
      'כפופים ישירות למנהלים שלה.',
      'והידע שהם צוברים',
      'נשאר בתוך המערכת.'
    ] },

  { id: 'san-data', dur: 4.2, type: 'data', label: 'תברואה',
    top:    { figure: '421 אלף ש״ח פחות',   caption: 'בשכר עובדי העירייה' },
    bottom: { figure: '2.43 מיליון ש״ח יותר', caption: 'לקבלנים' } },

  { id: 'san-when', dur: 3.4, type: 'statement', size: 54,
    lines: [
      'כשפינוי לא מתבצע.',
      'כשיש מפגע ברחוב.',
      'כשקבלן לא עומד',
      'במה שהתחייב.'
    ] },

  { id: 'san-need', dur: 4.0, type: 'statement', size: 50,
    lines: [
      'צריך בתוך העירייה אנשים',
      'שמכירים את השטח,',
      'יודעים מה הוזמן,',
      'יודעים מה אמור להתבצע',
      'ויודעים לדרוש תיקון.'
    ] },

  { id: 'col-data', dur: 3.2, type: 'data', label: 'גבייה',
    top:    { figure: '900 אלף ש״ח נוספים', caption: 'לקבלנים חיצוניים' } },

  { id: 'col-list', dur: 3.8, type: 'split', size: 50,
    lines: ['ארנונה.', 'חיובים.', 'טעויות.', 'בירורים מול תושבים.', 'מידע שנצבר לאורך שנים.'],
    creamHeading: ['יותר מהעבודה הזו', 'עוברת החוצה.'] },

  { id: 'total', dur: 4.2, type: 'total',
    kicker: 'בסך הכול',
    figure: ['3.2 מיליון ש״ח', 'פחות'],
    caption: 'בסעיפי השכר של עובדי העירייה' },

  { id: 'employees', dur: 5.2, type: 'kicker', size: 46,
    kicker: 'עובדי עירייה הם האנשים שנשארים בתוך המערכת',
    lines: [
      'הם כפופים ישירות לעירייה.',
      'הם צוברים ניסיון.',
      'הם מכירים את העיר.',
      'הם יודעים מה נעשה בעבר.',
      'והידע שלהם נשאר גם',
      'כשהקבלן או הספק מתחלף.'
    ] },

  { id: 'growth', dur: 4.0, type: 'split', size: 62,
    lines: ['וחריש עדיין גדלה.'],
    creamList: ['יותר שכונות.', 'יותר בתי ספר.', 'יותר כבישים.',
                'יותר תשתיות.', 'יותר תושבים.', 'יותר שירותים שצריך לנהל.'] },

  { id: 'meaning', dur: 4.8, type: 'statement', size: 46,
    lines: [
      'וככל שיותר עבודה עוברת',
      'לקבלנים ולספקים חיצוניים,',
      'צריך דווקא יותר אנשים מקצועיים',
      'ומנוסים בתוך העירייה',
      'שיידעו לנהל אותם, לבדוק אותם',
      'ולפקח עליהם.'
    ] },

  { id: 'shrink', dur: 3.6, type: 'statement', size: 48,
    lines: [
      'כשמצמצמים את האנשים',
      'שמחזיקים את הידע בתוך העירייה',
      'ובמקביל מעבירים',
      'עוד ועוד עבודה החוצה,'
    ] },

  { id: 'fewer', dur: 4.2, type: 'statement', size: 48,
    lines: [
      'נשארים פחות אנשים',
      'שמכירים את המערכת מבפנים.',
      'פחות אנשים שמפקחים.',
      'פחות אנשים שיודעים לזהות',
      'בזמן שמשהו לא עובד.'
    ] },

  { id: 'not-budget', dur: 4.4, type: 'split', size: 56,
    lines: ['זו כבר לא רק שאלה של תקציב.', '', 'זו היכולת של עירייה', 'לתת שירות.'],
    creamList: ['לילדים.', 'למשפחות.', 'למבוגרים.',
                'למשרתי מילואים.', 'לעסקים.', 'לכל מי שחי כאן.'] },

  { id: 'systems', dur: 4.8, type: 'kicker', size: 48,
    kicker: 'מי שמבין בניהול מערכות יודע',
    lines: [
      'עירייה שמאבדת את האנשים,',
      'הידע והיכולת לנהל את עצמה',
      'לא יכולה לאורך זמן להמשיך',
      'לספק את השירותים',
      'שהיא מחויבת לתת.'
    ] },

  { id: 'people', dur: 4.6, type: 'people', size: 44,
    lines: [
      'זה הזמן לשים את טובת העיר',
      'מעל כל שיקול פוליטי.',
      '',
      'להתנגד בתוקף לדרך ולהשלכות',
      'של תיקון התקציב הזה.'
    ],
    people: [
      { img: 'assets/itzik-lev.png',        name: 'איציק לב' },
      { img: 'assets/reutal-gonen.png',     name: 'רויטל גונן' },
      { img: 'assets/noga-david.png',       name: 'נגה דוד' },
      { img: 'assets/moshe-ben-zikri.png',  name: 'משה בן זיקרי' }
    ] },

  { id: 'final', dur: 5.2, type: 'statement', size: 48,
    lines: [
      'אם המהלך הזה לא ייעצר,',
      'עיריית חריש לא תוכל לאורך זמן',
      'להמשיך לספק לתושבים',
      'את השירותים שהיא מחויבת לתת.'
    ],
    tail: 'זה מה שעומד עכשיו על הפרק.' }

];
