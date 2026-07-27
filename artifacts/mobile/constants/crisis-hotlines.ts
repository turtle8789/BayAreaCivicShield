export interface Hotline {
  id: string;
  name: string;
  number: string;
  description: string;
  available: string;
  category: 'emergency' | 'crisis' | 'legal' | 'immigration' | 'lgbtq' | 'domestic';
}

export const CRISIS_HOTLINES: Hotline[] = [
  {
    id: '911',
    name: 'Emergency Services',
    number: '911',
    description: 'Police, fire, and medical emergencies.',
    available: '24/7',
    category: 'emergency',
  },
  {
    id: '988',
    name: 'Suicide & Crisis Lifeline',
    number: '988',
    description: 'Mental health crisis support. Call or text 988.',
    available: '24/7',
    category: 'crisis',
  },
  {
    id: 'dv',
    name: 'National Domestic Violence Hotline',
    number: '1-800-799-7233',
    description: 'Safe, confidential support for domestic violence victims.',
    available: '24/7',
    category: 'domestic',
  },
  {
    id: 'aclu',
    name: 'ACLU Know Your Rights',
    number: '1-415-621-2493',
    description: 'American Civil Liberties Union of Northern CA.',
    available: 'Business hours',
    category: 'legal',
  },
  {
    id: 'immigration',
    name: 'Immigration Legal Hotline',
    number: '1-415-255-9499',
    description: 'Bay Area Legal Aid immigration assistance.',
    available: 'Business hours',
    category: 'immigration',
  },
  {
    id: 'ice',
    name: 'ICE Detention Hotline',
    number: '1-888-373-7888',
    description: 'Report if you or someone you know was detained by ICE.',
    available: '24/7',
    category: 'immigration',
  },
  {
    id: 'trevor',
    name: 'Trevor Project',
    number: '1-866-488-7386',
    description: 'Crisis intervention for LGBTQ+ youth.',
    available: '24/7',
    category: 'lgbtq',
  },
  {
    id: 'trans',
    name: 'Trans Lifeline',
    number: '877-565-8860',
    description: 'Peer support for transgender people in crisis.',
    available: '24/7',
    category: 'lgbtq',
  },
  {
    id: 'lsnc',
    name: 'Legal Services of Northern CA',
    number: '1-800-822-0048',
    description: 'Free civil legal services for low-income Californians.',
    available: 'Business hours',
    category: 'legal',
  },
  {
    id: 'national-dv-text',
    name: 'Crisis Text Line',
    number: '741741',
    description: 'Text HOME to 741741 for free crisis counseling.',
    available: '24/7',
    category: 'crisis',
  },
];

export const CATEGORY_LABELS: Record<Hotline['category'], string> = {
  emergency: 'Emergency',
  crisis: 'Crisis Support',
  legal: 'Legal Aid',
  immigration: 'Immigration',
  lgbtq: 'LGBTQ+',
  domestic: 'Domestic Violence',
};

export const CATEGORY_COLORS: Record<Hotline['category'], string> = {
  emergency: '#E05252',
  crisis: '#D89CA4',
  legal: '#C97C5D',
  immigration: '#A7B8A0',
  lgbtq: '#9B6B8E',
  domestic: '#C97C5D',
};
