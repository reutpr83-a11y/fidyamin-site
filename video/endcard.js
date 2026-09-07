/* End card for the presenter cut.

   The presenter cut ends on a held frame of the speaker, which reads as a
   dropped connection rather than an ending. This card replaces that tail.

   It obeys the same law as script.js: sizes come from TYPE in video.html,
   at most three sizes and two weights in a frame, every line hand broken
   to the 790px column, and no dashes anywhere in the copy. The accent is
   the gold tail, never colour inside the message. See BRAND.md.          */

window.LAYOUT = {
  W: 1080, H: 1920,
  padRight: 880, padLeft: 90, ruleX: 912,
  safeTop: 180, safeBottom: 1680,
  creamPadTop: 70, creamBandBottom: 1740, creamTextBottom: 1568
};

window.SCENES = [

  /* The two figures land first, then the sentence, then the tail as its
     own beat 260ms later. That last pause is what makes the card read as
     a closing thought instead of a title. */
  /* lead absorbs the 500ms dissolve out of the presenter footage, so the
     lines enter on a clean navy field instead of animating underneath the
     crossfade. Change it with TRANS in append-endcard.sh. */
  { id: 'endcard', dur: 5.2, type: 'statement', enter: 380, lead: 640,
    lines: [
      'מעל 55 מיליון זזו.',
      '316 סעיפים השתנו.',
      '',
      'אף אחד לא קיבל',
      'תשובות.'
    ],
    tail: 'למה ולאן.' }

];
