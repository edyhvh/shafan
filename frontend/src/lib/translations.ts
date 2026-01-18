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
  | 'info_delitzsch_title'
  | 'info_delitzsch_text'
  | 'info_tanaj_title'
  | 'info_tanaj_text'
  | 'info_follow'
  | 'info_youtube_title'
  // Correction warning
  | 'correction_warning_text'
  | 'correction_warning_link'
  // Settings
  | 'settings_title'
  | 'on'
  | 'off'
  | 'light'
  | 'dark'

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
      "Elias Hutter (c. 1553–1605) was a German Hebraist, linguist, and printer from Görlitz. His translation of the New Testament into Hebrew, published between 1599 and 1602 as part of the Nuremberg Polyglot, represents one of the first complete Hebrew New Testaments ever printed. Please note that Hutter's translation is not linguistically accurate and contains numerous errors. We are actively working to improve and correct these texts through ongoing research and community contributions.",
    info_polyglot_title: 'The Nuremberg Polyglot',
    info_polyglot_text:
      'The Nuremberg Polyglot New Testament, published between 1599 and 1602, is a monumental work presenting the New Testament in twelve languages arranged in parallel columns. Among these languages, Hutter included his own Hebrew translation, making it one of the first complete Hebrew New Testaments ever printed. This work represents a remarkable achievement in biblical scholarship and early modern printing.',
    info_besorah_title: 'What is Besorah?',
    info_besorah_text:
      'Besorah (בְּשׂוֹרָה) means "Good News" or "Gospel" in Hebrew. This digital edition presents Hutter\'s Hebrew translation of the Greek New Testament. Unlike later translations, Hutter\'s work was created during a period of renewed interest in biblical languages, making it a unique historical document that bridges Greek Christian scripture with the Hebrew linguistic tradition.',
    info_delitzsch_title: 'Delitzsch Translation',
    info_delitzsch_text:
      "Franz Delitzsch (1813–1890) was a renowned German Lutheran theologian and Hebraist. His Hebrew translation of the New Testament represents a scholarly approach drawing from deep knowledge of both biblical Hebrew and rabbinic literature. Completed in the 19th century, Delitzsch's translation is considered more linguistically accurate and serves as the default text in this application.",
    info_tanaj_title: 'Tanakh',
    info_tanaj_text:
      "This project also includes the Hebrew Bible (Tanakh) from the Masoretic Text, the authoritative Hebrew text of the Bible that has been meticulously preserved through centuries of careful transmission by Israel's scribes.",
    info_follow: 'Follow the project',
    info_youtube_title: "Yeshua the Messiah's Besorah",
    correction_warning_text:
      'You may see errors in words, letters, or grammar. Help us improve',
    correction_warning_link: 'here',
    // Settings
    settings_title: 'Settings',
    on: 'On',
    off: 'Off',
    light: 'Light',
    dark: 'Dark',
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
      'Elias Hutter (c. 1553–1605) fue un hebraísta, lingüista e impresor alemán de Görlitz. Su traducción del Nuevo Testamento al hebreo, publicada entre 1599 y 1602 como parte de la Políglota de Núremberg, representa uno de los primeros Nuevos Testamentos hebreos completos jamás impresos. Por favor note que la traducción de Hutter no es lingüísticamente precisa y contiene numerosos errores. Estamos trabajando activamente para mejorar y corregir estos textos mediante investigación continua y contribuciones de la comunidad.',
    info_polyglot_title: 'La Políglota de Núremberg',
    info_polyglot_text:
      'La Políglota del Nuevo Testamento de Núremberg, publicada entre 1599 y 1602, es una obra monumental que presenta el Nuevo Testamento en doce idiomas dispuestos en columnas paralelas. Entre estos idiomas, Hutter incluyó su propia traducción al hebreo, convirtiéndola en uno de los primeros Nuevos Testamentos hebreos completos jamás impresos. Esta obra representa un logro notable en los estudios bíblicos y la impresión moderna temprana.',
    info_besorah_title: '¿Qué es Besorah?',
    info_besorah_text:
      'Besorah (בְּשׂוֹרָה) significa "Buenas Nuevas" o "Evangelio" en hebreo. Esta edición digital presenta la traducción hebrea de Hutter del Nuevo Testamento griego. A diferencia de traducciones posteriores, la obra de Hutter fue creada durante un período de renovado interés en las lenguas bíblicas, convirtiéndola en un documento histórico único que une las escrituras cristianas griegas con la tradición lingüística hebrea.',
    info_delitzsch_title: 'Traducción de Delitzsch',
    info_delitzsch_text:
      'Franz Delitzsch (1813–1890) fue un reconocido teólogo luterano alemán y hebraísta. Su traducción hebrea del Nuevo Testamento representa un enfoque académico basado en su profundo conocimiento tanto del hebreo bíblico como de la literatura rabínica. Completada en el siglo XIX, la traducción de Delitzsch se considera más precisa lingüísticamente y sirve como el texto predeterminado en esta aplicación.',
    info_tanaj_title: 'Tanaj',
    info_tanaj_text:
      'Este proyecto también incluye la Biblia hebrea (Tanaj) del Texto Masorético, el texto hebreo autorizado de la Biblia que ha sido meticulosamente preservado a través de siglos de transmisión cuidadosa por parte de escribas de Israel.',
    info_follow: 'Sigue el proyecto',
    info_youtube_title: 'La Besorah de Yeshúa el Mesías',
    correction_warning_text:
      'Es posible que encuentres errores de palabras, letras o gramática. Ayúdanos a mejorar',
    correction_warning_link: 'aquí',
    // Settings
    settings_title: 'Configuración',
    on: 'Activado',
    off: 'Desactivado',
    light: 'Claro',
    dark: 'Oscuro',
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
      'אליאס הוטר (1553–1605 לערך) היה חוקר עברית, בלשן ומדפיס גרמני מגרליץ. תרגומו של הברית החדשה לעברית, שפורסם בין 1599 ל-1602 כחלק מהפוליגלוטה של נירנברג, מייצג אחד מהברית החדשות העבריות המלאות הראשונות שהודפסו אי פעם. אנא שימו לב שתרגומו של הוטר אינו מדויק לשונית וכולל שגיאות רבות. אנו עובדים באופן פעיל לשפר ולתקן טקסטים אלה באמצעות מחקר מתמשך ותרומות הקהילה.',
    info_polyglot_title: 'הפוליגלוטה של נירנברג',
    info_polyglot_text:
      'הברית החדשה הפוליגלוטית של נירנברג, שפורסמה בין 1599 ל-1602, היא יצירה מונומנטלית המציגה את הברית החדשה בשתים עשרה שפות המסודרות בעמודות מקבילות. בין שפות אלו, הוטר כלל את תרגומו העברי שלו, והפך אותה לאחת מהברית החדשות העבריות המלאות הראשונות שהודפסו אי פעם. יצירה זו מייצגת הישג מרשים במדעי המקרא ובדפוס המודרני המוקדם.',
    info_besorah_title: 'מהי בשורה?',
    info_besorah_text:
      'בְּשׂוֹרָה פירושה "חדשות טובות" או "גוספל" בעברית. מהדורה דיגיטלית זו מציגה את תרגומו העברי של הוטר מהברית החדשה היוונית. בניגוד לתרגומים מאוחרים יותר, עבודתו של הוטר נוצרה בתקופה של התעניינות מחודשת בשפות המקרא, מה שהופך אותה למסמך היסטורי ייחודי המגשר בין הכתבים הנוצריים היווניים למסורת הלשונית העברית.',
    info_delitzsch_title: 'תרגום דליצש',
    info_delitzsch_text:
      'פרנץ דליצש (1813–1890) היה תיאולוג לותרני גרמני מוכר וחוקר עברית. תרגומו העברי של הברית החדשה מייצג גישה אקדמית המבוססת על ידיעתו העמוקה הן בעברית המקראית והן בספרות הרבנית. שהושלם במאה התשע עשרה, תרגומו של דליצש נחשב למדויק יותר מבחינה לשונית ומהווה את הטקסט בריר המחדל באפליקציה זו.',
    info_tanaj_title: 'תנ״ך',
    info_tanaj_text:
      'פרויקט זה כולל גם את התנ״ך מהטקסט המסורתי, הטקסט העברי הרשמי של התנ״ך ששומר בקפידה במשך מאות שנים על ידי סופרי ישראל.',
    info_follow: 'עקבו אחרי הפרויקט',
    info_youtube_title: 'בְּשׂוֹרַת יֵשׁוּעַ הַמָּשִׁיחַ',
    correction_warning_text:
      'ייתכן שתראו שגיאות במילים, אותיות או דקדוק. עזרו לנו לשפר',
    correction_warning_link: 'כאן',
    // Settings
    settings_title: 'הגדרות',
    on: 'פועל',
    off: 'כבוי',
    light: 'בהיר',
    dark: 'כהה',
  },
}

/**
 * Get a translated string for a given key and locale
 */
export function t(key: TranslationKey, locale: Locale): string {
  return translations[locale]?.[key] || translations.en[key] || key
}

export type { TranslationKey }
