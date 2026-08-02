export interface HubResource {
  id: string;
  category: HubCategory;
  name: string;
  description: string;
  url: string;
  phone?: string;
  free: boolean;
  tags: string[];
}

export type HubCategory =
  | 'legal_aid'
  | 'civil_rights'
  | 'immigration'
  | 'housing'
  | 'employment'
  | 'lgbtq'
  | 'forums';

export const HUB_CATEGORIES: { value: HubCategory; label: string; labelKey: string; emoji: string; color: string }[] = [
  { value: 'legal_aid',    label: 'Free Legal Aid',    labelKey: 'hub.cat_legal_aid',    emoji: '⚖️', color: '#C97B8E' },
  { value: 'civil_rights', label: 'Civil Rights',      labelKey: 'hub.cat_civil_rights', emoji: '✊', color: '#C9A050' },
  { value: 'immigration',  label: 'Immigration',       labelKey: 'hub.cat_immigration',  emoji: '🌎', color: '#5A9E6F' },
  { value: 'housing',      label: 'Housing Rights',    labelKey: 'hub.cat_housing',      emoji: '🏠', color: '#6B8EC9' },
  { value: 'employment',   label: 'Employment Rights', labelKey: 'hub.cat_employment',   emoji: '💼', color: '#A07888' },
  { value: 'lgbtq',        label: 'LGBTQ+ Legal',      labelKey: 'hub.cat_lgbtq',        emoji: '🏳️‍🌈', color: '#9B7EC9' },
  { value: 'forums',       label: 'Community Forums',  labelKey: 'hub.cat_forums',       emoji: '💬', color: '#C97B8E' },
];

export const HUB_RESOURCES: HubResource[] = [
  // ── Free Legal Aid ─────────────────────────────────────────────────────────
  {
    id: 'lh1',
    category: 'legal_aid',
    name: 'LawHelp.org',
    description: 'Find free legal aid programs in your state. Covers civil legal issues including housing, family, benefits, and more.',
    url: 'https://www.lawhelp.org',
    free: true,
    tags: ['legal aid', 'free lawyer', 'civil'],
  },
  {
    id: 'lh2',
    category: 'legal_aid',
    name: 'Legal Services Corporation',
    description: 'The largest provider of civil legal aid for low-income Americans. Locate your nearest office by ZIP code.',
    url: 'https://www.lsc.gov/what-legal-aid/find-legal-aid',
    free: true,
    tags: ['legal aid', 'low income', 'free'],
  },
  {
    id: 'lh3',
    category: 'legal_aid',
    name: 'National Lawyers Guild',
    description: 'Progressive legal organization. Provides support for civil rights, protest, and police misconduct cases.',
    url: 'https://www.nlg.org',
    phone: '212-679-5100',
    free: true,
    tags: ['civil rights', 'protest', 'police'],
  },
  {
    id: 'lh4',
    category: 'legal_aid',
    name: 'Law School Clinics Finder',
    description: 'Law school clinics offer free legal services supervised by professors. Search by state and practice area.',
    url: 'https://www.americanbar.org/groups/legal_services/flh-home/flh-clinic-directory/',
    free: true,
    tags: ['clinic', 'student lawyer', 'free'],
  },
  // ── Civil Rights ────────────────────────────────────────────────────────────
  {
    id: 'cr1',
    category: 'civil_rights',
    name: 'ACLU — Know Your Rights',
    description: 'The ACLU\'s comprehensive know-your-rights guides for police encounters, immigration, free speech, and more.',
    url: 'https://www.aclu.org/know-your-rights',
    free: true,
    tags: ['rights', 'police', 'free speech'],
  },
  {
    id: 'cr2',
    category: 'civil_rights',
    name: 'NAACP Legal Defense Fund',
    description: 'Racial justice through litigation, advocacy, and public education. File a complaint or find resources.',
    url: 'https://www.naacpldf.org',
    free: true,
    tags: ['racial justice', 'discrimination', 'civil rights'],
  },
  {
    id: 'cr3',
    category: 'civil_rights',
    name: 'ACLU Mobile Justice App',
    description: 'Record police interactions safely. Video uploads automatically if your phone is confiscated.',
    url: 'https://www.aclu.org/issues/criminal-law-reform/reforming-police/aclu-apps-record-police-conduct',
    free: true,
    tags: ['record police', 'app', 'safety'],
  },
  {
    id: 'cr4',
    category: 'civil_rights',
    name: 'National Police Accountability Project',
    description: 'Connects victims of police misconduct with attorneys who specialize in civil rights cases.',
    url: 'https://www.nlg-npap.org',
    free: true,
    tags: ['police misconduct', 'accountability', 'attorney'],
  },
  // ── Immigration ─────────────────────────────────────────────────────────────
  {
    id: 'im1',
    category: 'immigration',
    name: 'RAICES',
    description: 'Free and low-cost legal services for immigrants and refugees. Emergency family separation hotline available.',
    url: 'https://www.raicestexas.org',
    phone: '210-222-0964',
    free: true,
    tags: ['immigration', 'deportation', 'asylum', 'family'],
  },
  {
    id: 'im2',
    category: 'immigration',
    name: 'National Immigration Law Center',
    description: 'Defends and advances the rights of low-income immigrants through litigation, policy, and education.',
    url: 'https://www.nilc.org',
    free: true,
    tags: ['immigration', 'policy', 'low income'],
  },
  {
    id: 'im3',
    category: 'immigration',
    name: 'Immigration Advocates Network',
    description: 'Find accredited immigration legal services near you. Search by state and language.',
    url: 'https://www.immigrationadvocates.org/legaldirectory/',
    free: true,
    tags: ['immigration', 'legal directory', 'language'],
  },
  {
    id: 'im4',
    category: 'immigration',
    name: 'Know Your Rights at Checkpoints (ACLU)',
    description: 'Step-by-step guide on what to do at Border Patrol interior checkpoints and during ICE encounters.',
    url: 'https://www.aclu.org/know-your-rights/what-do-when-encountering-law-enforcement-immigration',
    free: true,
    tags: ['checkpoint', 'ICE', 'border patrol'],
  },
  // ── Housing ─────────────────────────────────────────────────────────────────
  {
    id: 'ho1',
    category: 'housing',
    name: 'National Housing Law Project',
    description: 'Advances housing justice through law, policy, and training. Focuses on low-income tenants.',
    url: 'https://www.nhlp.org',
    free: true,
    tags: ['housing', 'tenant', 'eviction'],
  },
  {
    id: 'ho2',
    category: 'housing',
    name: 'HUD — Find Rental Assistance',
    description: 'Official U.S. government portal to find emergency rental assistance, HUD offices, and housing counselors.',
    url: 'https://www.hud.gov/topics/rental_assistance',
    free: true,
    tags: ['HUD', 'rental assistance', 'government'],
  },
  {
    id: 'ho3',
    category: 'housing',
    name: 'Tenants Together (CA)',
    description: 'California\'s statewide renters rights organization. Free hotline and tenant resources.',
    url: 'https://www.tenantstogether.org',
    phone: '888-495-8020',
    free: true,
    tags: ['california', 'tenant', 'hotline'],
  },
  {
    id: 'ho4',
    category: 'housing',
    name: 'Emergency Rental Assistance Finder',
    description: 'Consumer Financial Protection Bureau tool to find ERA programs in your area.',
    url: 'https://www.consumerfinance.gov/coronavirus/mortgage-and-housing-assistance/renter-protections/find-help-with-rent-and-utilities/',
    free: true,
    tags: ['emergency', 'rent', 'utilities'],
  },
  // ── Employment ──────────────────────────────────────────────────────────────
  {
    id: 'em1',
    category: 'employment',
    name: 'Department of Labor — File a Wage Complaint',
    description: 'File a free, anonymous wage complaint with the WHD. Covers overtime, minimum wage, and more.',
    url: 'https://www.dol.gov/agencies/whd/contact/complaints',
    free: true,
    tags: ['wage', 'overtime', 'complaint'],
  },
  {
    id: 'em2',
    category: 'employment',
    name: 'EEOC — File a Discrimination Charge',
    description: 'The EEOC enforces federal workplace discrimination laws. File a free charge online.',
    url: 'https://www.eeoc.gov/filing-charge-discrimination',
    free: true,
    tags: ['discrimination', 'workplace', 'EEOC'],
  },
  {
    id: 'em3',
    category: 'employment',
    name: 'National Employment Law Project',
    description: 'Research and advocacy for workers\' rights. Guides on gig work, wage theft, and retaliation.',
    url: 'https://www.nelp.org',
    free: true,
    tags: ['gig economy', 'wage theft', 'retaliation'],
  },
  {
    id: 'em4',
    category: 'employment',
    name: 'Worker Center Network',
    description: 'Find a local worker center — organizations that provide support, education, and legal referrals for workers.',
    url: 'https://www.workercenternetwork.org',
    free: true,
    tags: ['worker center', 'local', 'support'],
  },
  // ── LGBTQ+ ──────────────────────────────────────────────────────────────────
  {
    id: 'lq1',
    category: 'lgbtq',
    name: 'Lambda Legal',
    description: 'Pursues litigation, education, and policy work on behalf of LGBTQ+ people and those living with HIV.',
    url: 'https://www.lambdalegal.org',
    phone: '212-809-8585',
    free: true,
    tags: ['LGBTQ', 'discrimination', 'litigation'],
  },
  {
    id: 'lq2',
    category: 'lgbtq',
    name: 'Transgender Law Center',
    description: 'Free legal information and referrals for transgender people facing discrimination, police encounters, or ID issues.',
    url: 'https://transgenderlawcenter.org',
    free: true,
    tags: ['transgender', 'discrimination', 'ID'],
  },
  {
    id: 'lq3',
    category: 'lgbtq',
    name: 'National Center for Lesbian Rights',
    description: 'Legal representation and resources for the LGBTQ+ community, including family law and employment.',
    url: 'https://www.nclrights.org',
    phone: '415-392-6257',
    free: true,
    tags: ['LGBTQ', 'family law', 'employment'],
  },
  // ── Community Forums ─────────────────────────────────────────────────────────
  {
    id: 'fo1',
    category: 'forums',
    name: 'r/legaladvice (Reddit)',
    description: 'Large online community where you can ask general legal questions and get responses from legal professionals.',
    url: 'https://www.reddit.com/r/legaladvice',
    free: true,
    tags: ['reddit', 'general', 'Q&A'],
  },
  {
    id: 'fo2',
    category: 'forums',
    name: 'r/immigration (Reddit)',
    description: 'Active community for immigration questions, visa issues, and sharing experiences.',
    url: 'https://www.reddit.com/r/immigration',
    free: true,
    tags: ['reddit', 'immigration', 'visa'],
  },
  {
    id: 'fo3',
    category: 'forums',
    name: 'Avvo Legal Q&A',
    description: 'Ask a legal question and receive free answers from licensed attorneys.',
    url: 'https://www.avvo.com/ask-a-lawyer',
    free: true,
    tags: ['attorney', 'Q&A', 'free answer'],
  },
  {
    id: 'fo4',
    category: 'forums',
    name: 'JustAnswer — Legal',
    description: 'Chat with verified lawyers. Free to ask; paid for detailed consultation.',
    url: 'https://www.justanswer.com/law',
    free: false,
    tags: ['lawyer chat', 'consultation'],
  },
];

export const HUB_DISCLAIMER =
  '⚠️ Disclaimer: Resource links are provided for informational purposes only. CivicShield Pro does not endorse or verify all content on external sites. Always confirm information directly with the organization. Not legal advice.';
