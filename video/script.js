/* ------------------------------------------------------------------
   Harish budget explainer, V2 edit
   Vertical 9:16 (1080x1920). No dashes anywhere in the copy.

   RULES THIS FILE MUST OBEY
   1. No scene sets its own font size. Sizes come from TYPE in video.html.
   2. At most three sizes and two weights are visible in any one frame.
   3. Every line is hand broken to fit the 790px column, so nothing is
      ever auto shrunk. check.js enforces both of these.
   4. Screens animate as groups, not line by line.
   ------------------------------------------------------------------ */

/* Reels safe area. Sides 90px, top 180px, and the bottom 240px carries
   no critical information because of the caption and audio strip.
   RTL text hangs off a right edge of 880 with the gold rule at 912,
   which also clears the action button column on the right. */
window.LAYOUT = {
  W: 1080, H: 1920,
  padRight: 880,
  padLeft: 90,
  ruleX: 912,
  safeTop: 180,
  safeBottom: 1680,
  creamPadTop: 70,
  creamBandBottom: 1740,
  creamTextBottom: 1568
};

/* type:
     'data'       gold label, one figure, one caption. splits when it has
                  a second figure, so the two compare on a shared edge
     'statement'  one message block, optional gold tail line
     'split'      message on navy, supporting paragraph on cream
     'people'     message on navy, the four council members on cream

   enter: entry duration in ms for this screen (220 to 420)
   lead:  pause in ms before the first group enters                    */
window.SCENES = [

  /* 1. the hook: the number and the contradiction in one frame */
  { id: 'hook', dur: 4.2, type: 'data', enter: 260, lead: -200, label: 'עדכון התקציב',
    top:    { figure: '3.2 מיליון ש״ח', caption: 'פחות בשכר עובדי העירייה', hero: true },
    creamLines: ['ויותר לקבלנים, ליועצים', 'ולספקים מבחוץ.'] },

  /* 2 and 3. where it happens */
  { id: 'eng', dur: 3.8, type: 'data', enter: 240, label: 'הנדסה',
    top:    { figure: '1.325 מיליון ש״ח', caption: 'פחות בשכר עובדי העירייה' },
    bottom: { figure: '970 אלף ש״ח',      caption: 'יותר לייעוץ ולפיקוח מבחוץ' } },

  { id: 'san', dur: 3.8, type: 'data', enter: 240, label: 'תברואה',
    top:    { figure: '421 אלף ש״ח',     caption: 'פחות בשכר עובדי העירייה' },
    bottom: { figure: '2.43 מיליון ש״ח', caption: 'יותר לקבלנים' } },

  /* 5. what a resident actually meets */
  { id: 'life', dur: 4.2, type: 'statement', enter: 300,
    lines: [
      'כשהאשפה לא מפונה.',
      'כשיש מפגע ברחוב.',
      'כשקבלן לא עושה',
      'את מה שהתחייב.'
    ] },

  /* 6. first central message: continuity */
  { id: 'msg1', dur: 4.2, type: 'statement', enter: 420, lead: 140,
    lines: [
      'קבלנים מתחלפים.',
      '',
      'הידע והאחריות',
      'חייבים להישאר',
      'בעירייה.'
    ] },

  /* 7. the city keeps growing */
  { id: 'growth', dur: 3.6, type: 'split', enter: 280,
    lines: ['וחריש עדיין גדלה.'],
    creamLines: ['יותר שכונות. יותר בתי ספר.',
                 'יותר כבישים. יותר תשתיות.',
                 'יותר תושבים ויותר שירותים.'] },

  /* 8. second central message: the inverse relationship */
  { id: 'msg2', dur: 4.2, type: 'statement', enter: 300,
    lines: [
      'ככל שמעבירים',
      'יותר עבודה החוצה,',
      'צריך יותר ניהול',
      'ופיקוח בעירייה.'
    ],
    tail: 'לא פחות.' },

  /* 9. the line that carries the argument */
  { id: 'msg3', dur: 4.4, type: 'statement', enter: 380, lead: 120,
    lines: [
      'אפשר להעביר',
      'עבודה החוצה.',
      '',
      'אי אפשר להעביר',
      'החוצה את האחריות',
      'לנהל אותה.'
    ] },

  /* 10. who this is for */
  { id: 'service', dur: 4.0, type: 'split', enter: 300,
    lines: ['זו היכולת של העירייה', 'לתת שירות.'],
    creamLines: ['לילדים. למשפחות. למבוגרים.',
                 'למשרתי מילואים. לעסקים.',
                 'לכל מי שחי כאן.'] },

  /* 11. the concrete ask */
  { id: 'ask', dur: 6.0, type: 'people', enter: 360, lead: 160,
    lines: ['לעצור את', 'עדכון התקציב', 'ולהחזיר אותו לדיון.'],
    people: [
      { img: 'assets/itzik-lev.png',       name: 'איציק לב' },
      { img: 'assets/reutal-gonen.png',    name: 'רויטל גונן' },
      { img: 'assets/noga-david.png',      name: 'נגה דוד' },
      { img: 'assets/moshe-ben-zikri.png', name: 'משה בן זיקרי' }
    ] },

  /* 12. one closing sentence */
  { id: 'end', dur: 5.8, type: 'statement', enter: 380, lead: 140,
    lines: [
      'זה לא ויכוח',
      'על שורה בתקציב.',
      '',
      'זו השאלה כמה יכולת',
      'נשארת לעירייה',
      'לנהל את העיר.'
    ] }

];
