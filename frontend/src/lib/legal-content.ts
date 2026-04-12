import { Locale } from '@/lib/locale'

export type LegalKind = 'terms' | 'privacy'

export type LegalDoc = {
  title: string
  effectiveDate: string | null
  lastUpdated: string | null
  body: string
}

type LegalContent = Record<LegalKind, string>

const LEGAL_TITLES: Record<Locale, Record<LegalKind, string>> = {
  en: {
    terms: 'Terms of Service of Shafan',
    privacy: 'Privacy Policy of Shafan',
  },
  es: {
    terms: 'Terminos de Servicio de Shafan',
    privacy: 'Politica de Privacidad de Shafan',
  },
  he: {
    terms: 'תנאי השירות של Shafan',
    privacy: 'מדיניות הפרטיות של Shafan',
  },
}

const EN_TERMS = `# Terms of Service of Shafan

**Effective Date:** April 12, 2026
**Last Updated:** April 12, 2026

Shafan is an open-source website for reading Tanakh and Hebrew Besorah texts. By using Shafan, you agree to these Terms.

## 1. Use of the Service

- You may use Shafan for personal, educational, and research purposes.
- You agree not to abuse, disrupt, or attempt to compromise the website.
- You are responsible for complying with local laws in your jurisdiction.

## 2. Content and Sources

Shafan includes texts and resources from public and third-party sources. We aim for accuracy, but we cannot guarantee that all content is error-free.

## 3. Intellectual Property

Project code is available under the repository license. Textual resources and third-party materials remain subject to their respective licenses and attribution requirements.

## 4. Service Availability

Shafan is provided on an "as is" and "as available" basis. We may update, pause, or discontinue parts of the service without notice.

## 5. Limitation of Liability

To the maximum extent permitted by law, Shafan maintainers are not liable for indirect, incidental, or consequential damages resulting from use of the service.

## 6. Changes to These Terms

We may update these Terms from time to time. Continued use after updates means you accept the revised Terms.

## 7. Contact

For legal or policy questions: hi@davar.bible
`

const EN_PRIVACY = `# Privacy Policy of Shafan

**Effective Date:** April 12, 2026
**Last Updated:** April 12, 2026

Shafan is committed to minimal data collection and transparent practices.

## 1. Data We Collect

At this time, Shafan does not require user accounts and does not intentionally collect personally identifiable information through normal reading use.

## 2. Local Preferences

Display preferences (for example, nikud, cantillation, theme, and reading options) are stored locally in your browser.

## 3. Technical Logs

Infrastructure providers may process standard technical request logs (such as IP address and request metadata) for security and delivery.

## 4. Third-Party Services

Shafan may load assets from third-party providers (such as fonts or external links). Those providers may process data according to their own privacy policies.

## 5. Children

Shafan is not directed to children under 13, and we do not knowingly collect personal data from children.

## 6. Changes to This Policy

We may revise this Privacy Policy as features evolve. Continued use after publication of updates means you accept the revised policy.

## 7. Contact

For privacy questions: hi@davar.bible
`

const ES_TERMS = `# Terminos de Servicio de Shafan

**Effective Date:** 12 de abril de 2026
**Last Updated:** 12 de abril de 2026

Shafan es un sitio web de codigo abierto para leer textos del Tanaj y la Besorah en hebreo. Al usar Shafan, aceptas estos Terminos.

## 1. Uso del servicio

- Puedes usar Shafan para fines personales, educativos y de investigacion.
- Aceptas no abusar, interrumpir ni comprometer el sitio web.
- Eres responsable de cumplir las leyes aplicables en tu jurisdiccion.

## 2. Contenido y fuentes

Shafan incluye textos y recursos de fuentes publicas y de terceros. Buscamos exactitud, pero no garantizamos que todo el contenido este libre de errores.

## 3. Propiedad intelectual

El codigo del proyecto esta disponible bajo la licencia del repositorio. Los textos y materiales de terceros se rigen por sus propias licencias y requisitos de atribucion.

## 4. Disponibilidad del servicio

Shafan se ofrece "tal cual" y "segun disponibilidad". Podemos actualizar, pausar o discontinuar partes del servicio sin aviso previo.

## 5. Limitacion de responsabilidad

En la maxima medida permitida por la ley, los mantenedores de Shafan no son responsables por danos indirectos, incidentales o consecuentes derivados del uso del servicio.

## 6. Cambios en estos Terminos

Podemos actualizar estos Terminos periodicamente. El uso continuo despues de cambios implica aceptacion de la version actualizada.

## 7. Contacto

Para consultas legales o de politica: hi@davar.bible
`

const ES_PRIVACY = `# Politica de Privacidad de Shafan

**Effective Date:** 12 de abril de 2026
**Last Updated:** 12 de abril de 2026

Shafan esta comprometido con la recoleccion minima de datos y con practicas transparentes.

## 1. Datos que recopilamos

Actualmente, Shafan no requiere cuentas de usuario y no recopila intencionalmente informacion personal identificable durante el uso normal de lectura.

## 2. Preferencias locales

Las preferencias de visualizacion (por ejemplo, nikud, cantilacion, tema y opciones de lectura) se guardan localmente en tu navegador.

## 3. Registros tecnicos

Los proveedores de infraestructura pueden procesar registros tecnicos estandar (como direccion IP y metadatos de solicitudes) para seguridad y entrega del servicio.

## 4. Servicios de terceros

Shafan puede cargar recursos desde proveedores externos (como fuentes o enlaces externos). Esos proveedores pueden procesar datos segun sus propias politicas de privacidad.

## 5. Menores

Shafan no esta dirigido a menores de 13 anos y no recopilamos intencionalmente datos personales de menores.

## 6. Cambios en esta Politica

Podemos revisar esta Politica de Privacidad a medida que evolucionen las funciones. El uso continuo despues de publicar cambios implica aceptacion de la version actualizada.

## 7. Contacto

Para consultas de privacidad: hi@davar.bible
`

const HE_TERMS = `# תנאי השירות של Shafan

**Effective Date:** 12 באפריל 2026
**Last Updated:** 12 באפריל 2026

Shafan הוא אתר קוד פתוח לקריאת טקסטים של התנך והבשורה בעברית. בשימוש באתר אתה מסכים לתנאים אלה.

## 1. שימוש בשירות

- ניתן להשתמש ב-Shafan למטרות אישיות, לימודיות ומחקריות.
- אין לעשות שימוש לרעה, לשבש או לנסות לפגוע באתר.
- המשתמש אחראי לעמוד בדין החל במדינתו.

## 2. תוכן ומקורות

Shafan כולל טקסטים ומשאבים ממקורות ציבוריים ומצדדים שלישיים. אנו שואפים לדיוק אך איננו מתחייבים שהמידע חף משגיאות.

## 3. קניין רוחני

קוד הפרויקט זמין לפי רישיון המאגר. טקסטים וחומרים של צד שלישי כפופים לרישיונות ולדרישות הייחוס שלהם.

## 4. זמינות השירות

Shafan ניתן "כמות שהוא" ו"כפי שהוא זמין". אנו רשאים לעדכן, להשהות או להפסיק חלקים מהשירות ללא הודעה מוקדמת.

## 5. הגבלת אחריות

במידה המרבית המותרת לפי דין, מתחזקי Shafan אינם אחראים לנזקים עקיפים, נלווים או תוצאתיים הנובעים מהשימוש בשירות.

## 6. שינויים בתנאים

אנו רשאים לעדכן תנאים אלה מעת לעת. המשך שימוש לאחר עדכון מהווה הסכמה לתנאים המעודכנים.

## 7. יצירת קשר

לשאלות משפטיות או מדיניות: hi@davar.bible
`

const HE_PRIVACY = `# מדיניות הפרטיות של Shafan

**Effective Date:** 12 באפריל 2026
**Last Updated:** 12 באפריל 2026

Shafan מחויב למינימום איסוף נתונים ולשקיפות.

## 1. מידע שאנו אוספים

נכון לעכשיו, Shafan אינו דורש חשבון משתמש ואינו אוסף באופן יזום מידע אישי מזהה בשימוש קריאה רגיל.

## 2. העדפות מקומיות

העדפות תצוגה (למשל ניקוד, טעמים, ערכת נושא ואפשרויות קריאה) נשמרות מקומית בדפדפן שלך.

## 3. לוגים טכניים

ספקי תשתית עשויים לעבד לוגים טכניים סטנדרטיים (כגון כתובת IP ומטא-דאטה של בקשות) לצורכי אבטחה ואספקת השירות.

## 4. שירותי צד שלישי

Shafan עשוי לטעון משאבים מספקים חיצוניים (כגון גופנים או קישורים חיצוניים). ספקים אלה עשויים לעבד נתונים לפי מדיניות הפרטיות שלהם.

## 5. קטינים

Shafan אינו מיועד לילדים מתחת לגיל 13, ואיננו אוספים ביודעין מידע אישי מקטינים.

## 6. שינויים במדיניות זו

אנו רשאים לעדכן מדיניות זו עם התפתחות המוצר. המשך שימוש לאחר פרסום עדכון מהווה הסכמה למדיניות המעודכנת.

## 7. יצירת קשר

לשאלות פרטיות: hi@davar.bible
`

const LEGAL_CONTENT: Record<Locale, LegalContent> = {
  en: {
    terms: EN_TERMS,
    privacy: EN_PRIVACY,
  },
  es: {
    terms: ES_TERMS,
    privacy: ES_PRIVACY,
  },
  he: {
    terms: HE_TERMS,
    privacy: HE_PRIVACY,
  },
}

const LAST_UPDATED_REGEX = /^\*\*Last Updated:\*\*\s*(.+)$/i
const EFFECTIVE_DATE_REGEX = /^\*\*Effective Date:\*\*\s*(.+)$/i
const HEADING_REGEX = /^#\s+/

export const getLegalContent = (kind: LegalKind, locale: Locale): string =>
  LEGAL_CONTENT[locale]?.[kind] ?? LEGAL_CONTENT.en[kind]

const extractLineMatch = (regex: RegExp, markdown: string): string | null => {
  const match = markdown
    .split('\n')
    .map((line) => line.trim())
    .find((line) => regex.test(line))

  if (!match) return null
  const result = regex.exec(match)
  return result?.[1]?.trim() ?? null
}

const stripHeaderLines = (markdown: string): string => {
  const lines = markdown.split('\n')
  const filtered = lines.filter((line) => {
    const trimmed = line.trim()
    if (!trimmed) return true
    if (HEADING_REGEX.test(trimmed)) return false
    if (EFFECTIVE_DATE_REGEX.test(trimmed)) return false
    if (LAST_UPDATED_REGEX.test(trimmed)) return false
    return true
  })

  return filtered.join('\n').trim()
}

export const getLegalDoc = (kind: LegalKind, locale: Locale): LegalDoc => {
  const markdown = getLegalContent(kind, locale)
  return {
    title: LEGAL_TITLES[locale]?.[kind] ?? LEGAL_TITLES.en[kind],
    effectiveDate: extractLineMatch(EFFECTIVE_DATE_REGEX, markdown),
    lastUpdated: extractLineMatch(LAST_UPDATED_REGEX, markdown),
    body: stripHeaderLines(markdown),
  }
}
