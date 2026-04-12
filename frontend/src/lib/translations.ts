/**
 * Translations for the application UI
 */

import { Locale } from './locale'

type TranslationKey =
  | 'books'
  | 'donate'
  | 'info'
  | 'terms'
  | 'privacy'
  | 'legal'
  | 'home'
  | 'nikud'
  | 'back_to_app'
  | 'legal_last_updated'
  | 'legal_effective_date'
  | 'page_title'
  | 'site_meta_title'
  | 'site_meta_description'
  // Info page
  | 'info_title'
  | 'info_overview_title'
  | 'info_overview_text'
  | 'info_study_guide_title'
  | 'info_study_guide_text'
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
  | 'info_related_questions_title'
  | 'info_related_questions_text'
  | 'info_follow'
  | 'info_youtube_title'
  // Donate page
  | 'donate_contact_prefix'
  | 'donate_telegram_label'
  | 'donate_meta_title'
  | 'donate_meta_description'
  // Correction warning
  | 'correction_warning_text'
  | 'correction_warning_link'
  // Settings
  | 'settings_title'
  | 'on'
  | 'off'
  | 'light'
  | 'dark'
  | 'tth_not_available_book'
  | 'tth_not_available_chapter'
  | 'tth_book_unavailable_message'

const translations: Record<Locale, Record<TranslationKey, string>> = {
  en: {
    books: 'Books',
    donate: 'Donate',
    info: 'Info',
    terms: 'Terms',
    privacy: 'Privacy',
    legal: 'Legals',
    home: 'Home',
    nikud: 'Nikud',
    back_to_app: 'Back to app',
    legal_last_updated: 'Last updated',
    legal_effective_date: 'Effective date',
    page_title: 'Hebrew Besorah',
    site_meta_title: 'Shafan',
    site_meta_description:
      'Read the Hebrew Bible (Tanakh) and Besorah in Hebrew. Fast, clean, distraction-free study with Nikud controls and trusted texts. Start reading now.',
    // Info page
    info_title: 'Info',
    info_overview_title: 'How to use this page',
    info_overview_text:
      'This page explains the historical sources behind the texts on Shafan and how to read them responsibly. In short: Hutter is historically important but linguistically uneven, Delitzsch is generally more accurate for study, and the Tanakh text follows the Masoretic tradition. If you are comparing passages, start with Delitzsch, then check Hutter to see historical wording choices.',
    info_study_guide_title: 'Study approach and examples',
    info_study_guide_text:
      'Example workflow: read a chapter in Hebrew with Nikud enabled, compare key terms in Hutter and Delitzsch, and note where wording changes meaning or tone. For teaching, cite the chapter URL and mention which source was active. For research, keep chapter and verse boundaries intact and avoid mixing translations in a single quotation without labeling them.',
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
    info_related_questions_title: 'Related questions',
    info_related_questions_text:
      'Which text should beginners use first? Usually Delitzsch. Why include Hutter if it has errors? Because it is a primary historical witness to early Hebrew New Testament printing. Does this replace critical editions? No. It is a reading and comparison tool designed for accessible Hebrew study.',
    info_follow: 'Follow the project',
    info_youtube_title: "Yeshua the Messiah's Besorah",
    // Donate page
    donate_contact_prefix:
      'if you wanna know other methods to donate please contact me on',
    donate_telegram_label: 'telegram',
    donate_meta_title: 'Support Shafan',
    donate_meta_description:
      'Help keep Shafan free and growing. Support the project and reach out for more ways to donate.',
    correction_warning_text:
      'You may see errors in words, letters, or grammar. Help us improve',
    correction_warning_link: 'here',
    // Settings
    settings_title: 'Settings',
    on: 'On',
    off: 'Off',
    light: 'Light',
    dark: 'Dark',
    tth_not_available_book: 'Not available yet',
    tth_not_available_chapter: 'Not available yet',
    tth_book_unavailable_message:
      'This book is not available yet. Disable the TTH option to continue reading.',
  },
  es: {
    books: 'Libros',
    donate: 'Donar',
    info: 'Info',
    terms: 'Terminos',
    privacy: 'Privacidad',
    legal: 'Legales',
    home: 'Inicio',
    nikud: 'Nikud',
    back_to_app: 'Volver a la app',
    legal_last_updated: 'Ultima actualizacion',
    legal_effective_date: 'Fecha de vigencia',
    page_title: 'Besorah Hebrea',
    site_meta_title: 'Shafan',
    site_meta_description:
      'Lee la Biblia hebrea (Tanaj) y la Besorah en hebreo. Rápida, limpia y sin distracciones, con control de nikud y textos confiables. Empieza a leer ahora.',
    // Info page
    info_title: 'Info',
    info_overview_title: 'Cómo usar esta página',
    info_overview_text:
      'Esta página explica las fuentes históricas detrás de los textos en Shafan y cómo leerlas con criterio. En resumen: Hutter es históricamente importante pero lingüísticamente irregular, Delitzsch suele ser más preciso para el estudio, y el texto del Tanaj sigue la tradición masorética. Si vas a comparar pasajes, comienza con Delitzsch y luego revisa Hutter para observar decisiones históricas de redacción.',
    info_study_guide_title: 'Método de estudio y ejemplos',
    info_study_guide_text:
      'Ejemplo de flujo de estudio: lee un capítulo en hebreo con nikud activado, compara términos clave entre Hutter y Delitzsch, y anota dónde cambian el sentido o el tono. Para enseñanza, cita la URL canónica del capítulo e indica qué fuente de texto estaba activa. Para investigación, conserva los límites de capítulo y versículo y evita mezclar traducciones en una sola cita sin etiquetarlas.',
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
    info_related_questions_title: 'Preguntas relacionadas',
    info_related_questions_text:
      '¿Con qué texto debería empezar una persona principiante? Normalmente con Delitzsch. ¿Por qué incluir Hutter si tiene errores? Porque es un testimonio histórico primario de la impresión temprana del Nuevo Testamento en hebreo. ¿Reemplaza esto a las ediciones críticas? No. Es una herramienta de lectura y comparación diseñada para un estudio hebreo accesible.',
    info_follow: 'Sigue el proyecto',
    info_youtube_title: 'La Besorah de Yeshúa el Mesías',
    // Donate page
    donate_contact_prefix:
      'si quieres conocer otros métodos para donar por favor contáctame en',
    donate_telegram_label: 'telegram',
    donate_meta_title: 'Apoya Shafan',
    donate_meta_description:
      'Ayuda a mantener Shafan gratis y en crecimiento. Apoya el proyecto y contáctame para más formas de donar.',
    correction_warning_text:
      'Es posible que encuentres errores de palabras, letras o gramática. Ayúdanos a mejorar',
    correction_warning_link: 'aquí',
    // Settings
    settings_title: 'Configuración',
    on: 'Activado',
    off: 'Desactivado',
    light: 'Claro',
    dark: 'Oscuro',
    tth_not_available_book: 'Aún no disponible',
    tth_not_available_chapter: 'Aún no disponible',
    tth_book_unavailable_message:
      'Este libro aún no está disponible. Desactiva la opción TTH para continuar leyendo.',
  },
  he: {
    books: 'ספרים',
    donate: 'לתרום',
    info: 'מידע',
    terms: 'תנאים',
    privacy: 'פרטיות',
    legal: 'משפטי',
    home: 'בית',
    nikud: 'ניקוד',
    back_to_app: 'חזרה לאפליקציה',
    legal_last_updated: 'עודכן לאחרונה',
    legal_effective_date: 'תאריך תחילה',
    page_title: 'בְּשׂוֹרָה עברית',
    site_meta_title: 'Shafan',
    site_meta_description:
      'קראו את התנ״ך (המקרא העברי) ואת הבשורה בעברית. מהיר, נקי וללא הסחות, עם שליטה בניקוד וטקסטים מהימנים. התחילו לקרוא עכשיו.',
    // Info page
    info_title: 'מידע',
    info_overview_title: 'איך להשתמש בעמוד הזה',
    info_overview_text:
      'עמוד זה מסביר את המקורות ההיסטוריים שמאחורי הטקסטים ב־Shafan ואיך לקרוא אותם באחריות. בקצרה: הוטר חשוב מבחינה היסטורית אך לא תמיד מדויק לשונית, דליצש בדרך כלל מדויק יותר ללימוד, וטקסט התנ״ך נשען על המסורה. אם אתם משווים קטעים, התחילו בדליצש ואז בדקו גם את הוטר כדי לראות בחירות ניסוח היסטוריות.',
    info_study_guide_title: 'שיטת לימוד ודוגמאות',
    info_study_guide_text:
      'דוגמה לתהליך עבודה: קראו פרק בעברית עם ניקוד מופעל, השוו מונחים מרכזיים בין הוטר לדליצש, ורשמו היכן הניסוח משנה משמעות או טון. להוראה, צטטו את כתובת הפרק וציינו איזה מקור טקסט היה פעיל. למחקר, שמרו על גבולות פרק ופסוק והימנעו מערבוב תרגומים באותה ציטטה בלי סימון ברור.',
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
    info_related_questions_title: 'שאלות קשורות',
    info_related_questions_text:
      'עם איזה טקסט כדאי להתחיל למתחילים? בדרך כלל עם דליצש. למה לכלול את הוטר אם יש בו שגיאות? כי הוא עדות היסטורית ראשונית להדפסה מוקדמת של הברית החדשה בעברית. האם זה מחליף מהדורות ביקורתיות? לא. זהו כלי קריאה והשוואה שנועד להנגיש לימוד עברית.',
    info_follow: 'עקבו אחרי הפרויקט',
    info_youtube_title: 'בְּשׂוֹרַת יֵשׁוּעַ הַמָּשִׁיחַ',
    // Donate page
    donate_contact_prefix:
      'אם תרצה לדעת על דרכי תרומה נוספות, אפשר ליצור איתי קשר ב',
    donate_telegram_label: 'טלגרם',
    donate_meta_title: 'תמכו ב־Shafan',
    donate_meta_description:
      'עזרו לשמור את Shafan חופשי ומתפתח. תמכו בפרויקט ופנו אליי לעוד דרכי תרומה.',
    correction_warning_text:
      'ייתכן שתראו שגיאות במילים, אותיות או דקדוק. עזרו לנו לשפר',
    correction_warning_link: 'כאן',
    // Settings
    settings_title: 'הגדרות',
    on: 'פועל',
    off: 'כבוי',
    light: 'בהיר',
    dark: 'כהה',
    tth_not_available_book: 'עדיין לא זמין',
    tth_not_available_chapter: 'עדיין לא זמין',
    tth_book_unavailable_message:
      'ספר זה עדיין לא זמין. השבת את אפשרות TTH כדי להמשיך לקרוא.',
  },
}

/**
 * Get a translated string for a given key and locale
 */
export function t(key: TranslationKey, locale: Locale): string {
  return translations[locale]?.[key] || translations.en[key] || key
}

export type { TranslationKey }
