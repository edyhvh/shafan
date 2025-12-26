/**
 * Translations for the application UI
 */

import { Locale } from './locale'

type TranslationKey =
  | 'books'
  | 'donate'
  | 'info'
  | 'home'
  | 'nikud'
  | 'page_title'
  // Info page
  | 'info_title'
  | 'info_hutter_title'
  | 'info_hutter_text'
  | 'info_polyglot_title'
  | 'info_polyglot_text'
  | 'info_besorah_title'
  | 'info_besorah_text'
  | 'info_follow'
  | 'info_youtube_title'
  // Correction warning
  | 'correction_warning_text'
  | 'correction_warning_link'

const translations: Record<Locale, Record<TranslationKey, string>> = {
  en: {
    books: 'Books',
    donate: 'Donate',
    info: 'Info',
    home: 'Home',
    nikud: 'Nikud',
    page_title: 'Hebrew Besorah',
    // Info page
    info_title: 'Info',
    info_hutter_title: 'Who was Elias Hutter?',
    info_hutter_text:
      'Elias Hutter (c. 1553–1605) was a German Hebraist, linguist, and printer from Görlitz. He dedicated his life to the study and teaching of Hebrew, founding a school in Nuremberg where students could learn to read Hebrew in just four weeks using his innovative method. His passion for languages led him to create one of the most ambitious biblical projects of the Renaissance era.',
    info_polyglot_title: 'The Nuremberg Polyglot',
    info_polyglot_text:
      'The Nuremberg Polyglot New Testament, published between 1599 and 1602, is a monumental work presenting the New Testament in twelve languages arranged in parallel columns. Among these languages, Hutter included his own Hebrew translation, making it one of the first complete Hebrew New Testaments ever printed. This work represents a remarkable achievement in biblical scholarship and early modern printing.',
    info_besorah_title: 'What is Besorah?',
    info_besorah_text:
      'Besorah (בְּשׂוֹרָה) means "Good News" or "Gospel" in Hebrew. This digital edition presents Hutter\'s Hebrew translation of the Greek New Testament. Unlike later translations, Hutter\'s work was created during a period of renewed interest in biblical languages, making it a unique historical document that bridges Greek Christian scripture with the Hebrew linguistic tradition.',
    info_follow: 'Follow the project',
    info_youtube_title: "Yeshua the Messiah's Besorah",
    correction_warning_text:
      'You may see errors in words, letters, or grammar. Help us improve',
    correction_warning_link: 'here',
  },
  es: {
    books: 'Libros',
    donate: 'Donar',
    info: 'Info',
    home: 'Inicio',
    nikud: 'Nikud',
    page_title: 'Besorah Hebrea',
    // Info page
    info_title: 'Info',
    info_hutter_title: '¿Quién fue Elias Hutter?',
    info_hutter_text:
      'Elias Hutter (c. 1553–1605) fue un hebraísta, lingüista e impresor alemán de Görlitz. Dedicó su vida al estudio y enseñanza del hebreo, fundando una escuela en Núremberg donde los estudiantes podían aprender a leer hebreo en solo cuatro semanas usando su método innovador. Su pasión por los idiomas lo llevó a crear uno de los proyectos bíblicos más ambiciosos de la era del Renacimiento.',
    info_polyglot_title: 'La Políglota de Núremberg',
    info_polyglot_text:
      'La Políglota del Nuevo Testamento de Núremberg, publicada entre 1599 y 1602, es una obra monumental que presenta el Nuevo Testamento en doce idiomas dispuestos en columnas paralelas. Entre estos idiomas, Hutter incluyó su propia traducción al hebreo, convirtiéndola en uno de los primeros Nuevos Testamentos hebreos completos jamás impresos. Esta obra representa un logro notable en los estudios bíblicos y la impresión moderna temprana.',
    info_besorah_title: '¿Qué es Besorah?',
    info_besorah_text:
      'Besorah (בְּשׂוֹרָה) significa "Buenas Nuevas" o "Evangelio" en hebreo. Esta edición digital presenta la traducción hebrea de Hutter del Nuevo Testamento griego. A diferencia de traducciones posteriores, la obra de Hutter fue creada durante un período de renovado interés en las lenguas bíblicas, convirtiéndola en un documento histórico único que une las escrituras cristianas griegas con la tradición lingüística hebrea.',
    info_follow: 'Sigue el proyecto',
    info_youtube_title: 'La Besorah de Yeshúa el Mesías',
    correction_warning_text:
      'Es posible que encuentres errores de palabras, letras o gramática. Ayúdanos a mejorar',
    correction_warning_link: 'aquí',
  },
  he: {
    books: 'ספרים',
    donate: 'לתרום',
    info: 'מידע',
    home: 'בית',
    nikud: 'ניקוד',
    page_title: 'בְּשׂוֹרָה עברית',
    // Info page
    info_title: 'מידע',
    info_hutter_title: 'מי היה אליאס הוטר?',
    info_hutter_text:
      'אליאס הוטר (1553–1605 לערך) היה חוקר עברית, בלשן ומדפיס גרמני מגרליץ. הוא הקדיש את חייו ללימוד והוראת העברית, והקים בית ספר בנירנברג שבו תלמידים יכלו ללמוד לקרוא עברית תוך ארבעה שבועות בלבד באמצעות שיטתו החדשנית. תשוקתו לשפות הובילה אותו ליצור את אחד הפרויקטים המקראיים השאפתניים ביותר של עידן הרנסנס.',
    info_polyglot_title: 'הפוליגלוטה של נירנברג',
    info_polyglot_text:
      'הברית החדשה הפוליגלוטית של נירנברג, שפורסמה בין 1599 ל-1602, היא יצירה מונומנטלית המציגה את הברית החדשה בשתים עשרה שפות המסודרות בעמודות מקבילות. בין שפות אלו, הוטר כלל את תרגומו העברי שלו, והפך אותה לאחת מהברית החדשות העבריות המלאות הראשונות שהודפסו אי פעם. יצירה זו מייצגת הישג מרשים במדעי המקרא ובדפוס המודרני המוקדם.',
    info_besorah_title: 'מהי בשורה?',
    info_besorah_text:
      'בְּשׂוֹרָה פירושה "חדשות טובות" או "גוספל" בעברית. מהדורה דיגיטלית זו מציגה את תרגומו העברי של הוטר מהברית החדשה היוונית. בניגוד לתרגומים מאוחרים יותר, עבודתו של הוטר נוצרה בתקופה של התעניינות מחודשת בשפות המקרא, מה שהופך אותה למסמך היסטורי ייחודי המגשר בין הכתבים הנוצריים היווניים למסורת הלשונית העברית.',
    info_follow: 'עקבו אחרי הפרויקט',
    info_youtube_title: 'בְּשׂוֹרַת יֵשׁוּעַ הַמָּשִׁיחַ',
    correction_warning_text:
      'ייתכן שתראו שגיאות במילים, אותיות או דקדוק. עזרו לנו לשפר',
    correction_warning_link: 'כאן',
  },
}

/**
 * Get a translated string for a given key and locale
 */
export function t(key: TranslationKey, locale: Locale): string {
  return translations[locale]?.[key] || translations.en[key] || key
}

export type { TranslationKey }
