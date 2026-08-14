/*
  Every piece of copy on the site lives here. Nothing else in the codebase
  hard-codes a string, so this file is the single edit point until the
  admin surface exists.

  Items marked ⚠️ NEEDS CONFIRMATION are carried over from the current site
  but are either legally exposed, internally contradictory, or placeholder.
  See PLAN.md §0 and §3.4.
*/

export const company = {
  name: 'Scandic Marketing',
  /** Split for the hero wordmark — matches the two-line logo lockup. */
  nameLines: ['SCANDIC', 'MARKETING'],
  tagline: 'Film, foto och marknadsföring',
  city: 'Helsingborg',

  phone: '+46 76 929 85 01',
  phoneHref: '+46769298501',
  email: 'kontakt@scandicmarketing.se',

  street: 'Redaregatan 48',
  postcode: '252 30',
  instagram: 'https://www.instagram.com/scandicmarketing.se/',

  /*
    ⚠️ NEEDS CONFIRMATION — the current site publishes "Organisationsnummer:
    20000228-…", which is a personnummer, not an org number. It must come
    down. Fill these in once the AB exists; the footer renders nothing for
    empty strings rather than showing a placeholder.
  */
  orgNr: '',
  vatNr: '',
  /** Kommun where the board sits — required separately by ABL 28:5. */
  sate: 'Helsingborg',
  fSkatt: true,

  hours: [
    { day: 'Måndag–fredag', time: '09:00–17:00' },
    { day: 'Lördag', time: '10:00–15:00' },
    { day: 'Söndag', time: 'Stängt' },
  ],
} as const;

export const nav = [
  { label: 'Arbete', href: '#arbete' },
  { label: 'Tjänster', href: '#tjanster' },
  { label: 'Priser', href: '#hemsida' },
  { label: 'Kontakt', href: '#kontakt' },
] as const;

export const hero = {
  /** Sits under the wordmark. Replaces "Experter inom marknadsföring". */
  sub: 'Film, foto och marknadsföring — Helsingborg',
  primary: { label: 'Boka ett möte', href: '#kontakt' },
  secondary: { label: 'Se våra paket', href: '#hemsida' },
  trust: 'Betrodd av över 100 företag i Norden',
  video: {
    /** Pexels 36505159 — "Aerial view of coastal cityscape on sunny day", Efrem Efre. */
    credit: 'Efrem Efre / Pexels',
    poster: '/img/hero-poster.jpg',
    src: '/video/hero-1080.mp4',
    srcMobile: '/video/hero-720.mp4',
  },
} as const;

/*
  ⚠️ NEEDS CONFIRMATION — every one of these needs documentation on the day
  it is published. Swedish marketing law reverses the burden of proof
  (MD 2012:2); an undocumented claim is misleading by default, and a
  competing agency has standing to sue. `source` is required, not optional:
  if it can't be filled in, the stat comes off the page.
*/
export const stats = [
  { value: '18', suffix: 'M+', label: 'Omsättning genererad', source: '' },
  { value: '353', suffix: '%', label: 'Genomsnittlig ROI', source: '' },
  { value: '7', suffix: '+', label: 'År av expertis', source: '' },
] as const;

/*
  Client logos. Order and per-logo widths are carried over verbatim from the
  current site — each width is a hand-set optical correction, so a wide
  wordmark and a compact roundel read at the same visual weight. Keeping
  them means the row looks the way he already tuned it.

  ⚠️ CrossFit's logo is not in the current bundle — still needed.
  ⚠️ Written permission needed before publishing any of these.
*/
export const clientsLabel = 'Några av våra samarbeten';
export const clientsCaption = 'Förtroende från ledande företag som satsar på sin marknadsföring';

export const clients = [
  { name: 'SaunAvant', width: 288, logo: '/img/client-saunavant-logo.png' },
  { name: 'Prima EL', width: 179, logo: '/img/client-prima-el-logo.png' },
  { name: 'Walleye', width: 320, logo: '/img/client-walleye.png' },
  { name: 'Hantverkskollen', width: 312, logo: '/img/client-hantverkskollen-logo.png' },
  { name: 'Foodtel', width: 320, logo: '/img/client-foodtel.svg' },
  { name: 'Solna Byggfirma', width: 224, logo: '/img/client-solna-logo.png' },
  { name: 'Excite Trapwithus', width: 246, logo: '/img/client-excite-logo.png' },
] as const;

export type Case = {
  client: string;
  disciplines: string[];
  /** Headline result. Keep it concrete; attribute it in `source`. */
  result: string;
  body: string;
  /** ⚠️ Required before a number may be published. Metric, period, tool. */
  source: string;
  media?: string;
  featured?: boolean;
};

export const cases: Case[] = [
  {
    client: 'Hantverkskollen',
    disciplines: ['SEO', 'Google Ads'],
    result: '+500%',
    body: 'Genom optimerad SEO och Google Ads ökade Hantverkskollen sin trafik med 500 % och genererade dagliga leads.',
    source: '', // ⚠️ e.g. "Google Search Console, mars 2024–mars 2025"
    featured: true,
  },
  {
    client: 'Nordiskt e-handelsföretag',
    disciplines: ['Meta Ads', 'TikTok Ads'],
    result: '+340%',
    body: 'Genom Meta- och TikTok-kampanjer hjälpte vi ett nordiskt e-handelsföretag att tredubbla sin vanliga månadsförsäljning på bara 6 dagar.',
    source: '', // ⚠️
  },
  {
    client: 'Foodtel',
    disciplines: ['Social media', 'Video', 'Foto'],
    result: 'Varje månad',
    body: "Vi driver Foodtels LinkedIn och bidrar med professionella videos och bilder varje månad. Det har frigjort tid så att bolaget kan fokusera på det viktigaste.",
    source: '',
  },
  {
    client: 'Lokalt gatukök',
    disciplines: ['Varumärke', 'Foto'],
    result: 'Ny identitet',
    body: 'Vi hjälpte ett lokalt gatukök att förnya sin visuella identitet och digitala närvaro för att attrahera fler kunder.',
    source: '',
  },
];

export const services = [
  {
    name: 'Videoproduktion',
    blurb: 'Från koncept till färdig film. 4K, drönare och professionellt ljud — videos som berättar ditt varumärkes historia.',
    items: ['Reklamfilm', 'Drönare', 'Klipp & färg', 'Sociala format'],
  },
  {
    name: 'Fotografi',
    blurb: 'Från företagsporträtt till produktbilder — visuellt innehåll som kommunicerar professionalism och kvalitet.',
    items: ['Företagsporträtt', 'Produktbilder', 'Miljöfoto', 'Retusch'],
  },
  {
    name: 'Marknadsföring',
    blurb: 'Digital marknadsföring som genererar resultat och ökar er synlighet för rätt målgrupp.',
    items: ['Google Ads', 'Meta Ads', 'TikTok Ads', 'SEO'],
  },
  {
    name: 'Hemsida',
    blurb: 'Snabb, sökbar och säljande. Hyr istället för att köpa — allt inkluderat till ett förutsägbart månadspris.',
    items: ['Skräddarsydd design', 'Domän & e-post', 'Support ingår', 'SEO från start'],
  },
] as const;

/*
  ⚠️ NEEDS CONFIRMATION — the current site contradicts itself. One component
  renders "Hemsida Pro — 1299 kr" and "Hemsida Premium — 2999 kr"; another
  renders "Ord. pris 1299 kr — nu endast 499 kr/månad". Which is live?
*/
export const plans = [
  {
    name: 'Standard',
    price: 499,
    was: 1299,
    popular: true,
    features: [
      'Skräddarsydd hemsida, byggd från grunden',
      'Domän och e-postadress ingår',
      'Support och underhåll ingår',
      'Sökmotoroptimerad från dag ett',
    ],
  },
  {
    name: 'Premium',
    price: 1499,
    was: 2999,
    popular: false,
    features: [
      'Allt i Standard',
      'Support och underhåll dygnet runt',
      'Film och foto till startsidan',
      'Löpande innehåll och optimering',
    ],
  },
] as const;

/** The gap almost no Swedish competitor answers on the sales page. */
export const guarantees = [
  { title: 'Domänen är din', body: 'Registrerad i ditt namn från dag ett, och den följer med dig.' },
  { title: 'Allt exporterbart', body: 'Slutar du hos oss får du med dig innehållet. Inga inlåsningar.' },
  { title: 'Ingen bindningstid', body: 'Säg upp när du vill. Vi behåller kunder på resultat, inte på avtal.' },
] as const;

export const process = [
  { n: '01', title: 'Vi lyssnar', body: 'Ett kostnadsfritt möte där vi går igenom målet, budgeten och vad som redan testats.' },
  { n: '02', title: 'Vi föreslår', body: 'En plan med tydlig omfattning och pris. Passar det inte, säger vi det direkt.' },
  { n: '03', title: 'Vi producerar', body: 'Samma team hela vägen. Ingen överlämning till en junior efter tredje månaden.' },
  { n: '04', title: 'Vi mäter', body: 'Rapport på det som landar på ert konto. Rör sig inte siffrorna säger vi till.' },
] as const;

export const seo = {
  title: 'Scandic Marketing — Film, foto och marknadsföring i Helsingborg',
  description:
    'Marknadsföringsbyrå i Helsingborg. Videoproduktion, fotografi och digital annonsering för nordiska företag. Hemsida från 499 kr/mån.',
} as const;

/** kr formatting with a non-breaking thousands space, Swedish convention. */
export const kr = (n: number) => n.toLocaleString('sv-SE').replace(/ /g, ' ');
