export interface RightsCategory {
  id: string;
  title: string;
  icon: string;
  color: string;
  rights: string[];
}

export interface QuizQuestion {
  id: string;
  question: string;
  options: string[];
  correctIndex: number;
  explanation: string;
}

export const RIGHTS_CATEGORIES: RightsCategory[] = [
  {
    id: 'traffic',
    title: 'Traffic Stops',
    icon: 'navigation',
    color: '#C97C5D',
    rights: [
      'You must show your license, registration, and proof of insurance.',
      'You have the right to remain silent beyond providing ID documents.',
      'You can refuse a search — say clearly: "I do not consent to this search."',
      'Keep your hands visible at all times and move slowly.',
      'You can record the encounter as long as you don\'t interfere.',
      'If you are arrested, say: "I am invoking my right to remain silent and want a lawyer."',
      'Do not argue or resist — challenge it in court instead.',
    ],
  },
  {
    id: 'police',
    title: 'Police Encounters',
    icon: 'shield',
    color: '#A7B8A0',
    rights: [
      'You have the right to remain silent. Use it.',
      'You can ask: "Am I being detained or am I free to go?"',
      'If detained, you can ask why you are being held.',
      'You can film police in public — it is a protected First Amendment right.',
      'Never physically resist an officer, even if the stop is unlawful.',
      'Officers can pat down your outer clothing if they suspect a weapon.',
      'You can always say "I want a lawyer" at any point.',
    ],
  },
  {
    id: 'arrest',
    title: 'Arrest Rights',
    icon: 'alert-circle',
    color: '#D89CA4',
    rights: [
      'You have the right to know why you are being arrested.',
      'Miranda rights must be read before a custodial interrogation.',
      'You have the right to an attorney. If you can\'t afford one, one will be provided.',
      'You can remain silent — say: "I am invoking my right to remain silent."',
      'Do not sign any documents without a lawyer present.',
      'You have the right to make a phone call after being booked.',
      'You must be brought before a judge within 48 hours of arrest.',
    ],
  },
  {
    id: 'immigration',
    title: 'Immigration Rights',
    icon: 'globe',
    color: '#7B9E87',
    rights: [
      'You have the right to remain silent regardless of immigration status.',
      'You do not have to open the door to ICE without a signed judicial warrant.',
      'Ask to see the warrant — an ICE administrative warrant is NOT a court order.',
      'Do not sign any documents (like "voluntary departure") without a lawyer.',
      'You have the right to contact your consulate if detained.',
      'Anything you say can be used in immigration proceedings.',
      'Contact an immigration lawyer immediately if detained.',
    ],
  },
  {
    id: 'home',
    title: 'At Home',
    icon: 'home',
    color: '#C97C5D',
    rights: [
      'Police generally need a warrant signed by a judge to enter your home.',
      'You can ask to see the warrant through a window or door.',
      'If officers enter by force, do not resist — challenge it in court.',
      'A "knock and announce" is usually required before entry.',
      'Consent to search is voluntary — you can say no.',
      'If you open the door, step outside and close the door behind you.',
      'Anything in plain view may be seized without a warrant.',
    ],
  },
  {
    id: 'search',
    title: 'Searches & Seizures',
    icon: 'search',
    color: '#9B8E87',
    rights: [
      'The 4th Amendment protects against unreasonable searches.',
      'Police need a warrant, probable cause, or consent to search.',
      'Clearly say: "I do not consent to this search."',
      'Your refusal to consent cannot be used as probable cause.',
      'Searches can be challenged in court as unlawful.',
      'Evidence from an illegal search may be suppressed ("fruit of the poisonous tree").',
      'You can complain about an illegal search after the fact — not during.',
    ],
  },
];

export const QUIZ_QUESTIONS: QuizQuestion[] = [
  {
    id: 'q1',
    question: 'During a traffic stop, which documents must you provide?',
    options: [
      'License only',
      'License, registration, and proof of insurance',
      'Nothing — you can remain silent',
      'Only your name',
    ],
    correctIndex: 1,
    explanation: 'Drivers must provide their license, vehicle registration, and proof of insurance when lawfully stopped.',
  },
  {
    id: 'q2',
    question: 'How do you properly invoke your right to remain silent?',
    options: [
      'Just stay quiet without saying anything',
      'Say "I plead the fifth" repeatedly',
      'Clearly say "I am invoking my right to remain silent"',
      'Walk away from the officer',
    ],
    correctIndex: 2,
    explanation: 'Since 2013 (Salinas v. Texas), you must explicitly state you are invoking your right to silence — staying quiet alone may not protect you.',
  },
  {
    id: 'q3',
    question: 'Can you legally record the police in public?',
    options: [
      'Never — it is always illegal',
      'Only with written permission',
      'Yes, it is a protected First Amendment right',
      'Only in California',
    ],
    correctIndex: 2,
    explanation: 'Recording police performing their duties in public is protected by the First Amendment across the US, as long as you don\'t physically interfere.',
  },
  {
    id: 'q4',
    question: 'If ICE comes to your door, must you let them in?',
    options: [
      'Yes, always',
      'Only if they show any badge',
      'No — only if they have a signed judicial warrant',
      'Yes, if they identify themselves as officers',
    ],
    correctIndex: 2,
    explanation: 'An ICE administrative warrant is not a court order. You only must allow entry with a judicial (signed by a judge) warrant.',
  },
  {
    id: 'q5',
    question: 'When can you ask "Am I free to go?" during a stop?',
    options: [
      'Never — you must wait to be released',
      'Only after 15 minutes',
      'At any point during the encounter',
      'Only if you are not under arrest',
    ],
    correctIndex: 2,
    explanation: 'You can ask at any time whether you are free to go. If not detained, you may calmly walk away.',
  },
  {
    id: 'q6',
    question: 'What should you do if police enter your home without a warrant?',
    options: [
      'Physically block them from entering',
      'Comply and challenge the entry in court afterward',
      'Call 911 immediately',
      'Lock all the doors',
    ],
    correctIndex: 1,
    explanation: 'Never physically resist even an unlawful entry — it can lead to additional charges. Document everything and challenge it in court.',
  },
  {
    id: 'q7',
    question: 'What is the "fruit of the poisonous tree" doctrine?',
    options: [
      'Agricultural regulations on police property',
      'Evidence gathered from an illegal search can be excluded in court',
      'A rule about planting evidence',
      'Police must disclose all evidence before trial',
    ],
    correctIndex: 1,
    explanation: 'Under this exclusionary rule, evidence obtained from an unlawful search or seizure may be suppressed — it cannot be used against you in court.',
  },
  {
    id: 'q8',
    question: 'How long can you legally be held after arrest before seeing a judge?',
    options: [
      '24 hours',
      '48 hours',
      '72 hours',
      'Until trial',
    ],
    correctIndex: 1,
    explanation: 'In California and most US jurisdictions, you must be brought before a judge within 48 hours of arrest (excluding weekends/holidays in some cases).',
  },
  {
    id: 'q9',
    question: 'Does refusing a police search give officers probable cause?',
    options: [
      'Yes, it looks suspicious',
      'Only at night',
      'No — your refusal cannot be used as probable cause',
      'Yes, in high-crime areas',
    ],
    correctIndex: 2,
    explanation: 'The Supreme Court has held that exercising your 4th Amendment right to refuse a search cannot by itself constitute probable cause for a search.',
  },
  {
    id: 'q10',
    question: 'When must Miranda rights be read to you?',
    options: [
      'Immediately upon arrest',
      'Before any police questioning ever',
      'Before a custodial interrogation',
      'Only at the police station',
    ],
    correctIndex: 2,
    explanation: 'Miranda warnings are required before a custodial interrogation — when you are in custody and being questioned. Not merely upon arrest.',
  },
];
