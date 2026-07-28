export type ForumCategory =
  | 'police'
  | 'immigration'
  | 'housing'
  | 'employment'
  | 'general'
  | 'stories';

export interface ForumReply {
  id: string;
  author: string;
  content: string;
  timestamp: string;
  helpfulCount: number;
}

export interface ForumPost {
  id: string;
  category: ForumCategory;
  title: string;
  content: string;
  author: string;
  timestamp: string;
  helpfulCount: number;
  markedHelpful: boolean;
  isUserPost: boolean;
  replies: ForumReply[];
}

export const FORUM_CATEGORIES: { value: ForumCategory; label: string; emoji: string; color: string }[] = [
  { value: 'police',      label: 'Police Encounters', emoji: '🚔', color: '#C97B8E' },
  { value: 'immigration', label: 'Immigration',        emoji: '🌎', color: '#5A9E6F' },
  { value: 'housing',     label: 'Housing Rights',     emoji: '🏠', color: '#C9A050' },
  { value: 'employment',  label: 'Employment',         emoji: '💼', color: '#6B8EC9' },
  { value: 'general',     label: 'General Q&A',        emoji: '❓', color: '#A07888' },
  { value: 'stories',     label: 'Share Your Story',   emoji: '📖', color: '#9B7EC9' },
];

export const SEED_POSTS: ForumPost[] = [
  {
    id: 'seed_1',
    category: 'police',
    title: 'What are my rights during a traffic stop?',
    content:
      'I got pulled over last week and wasn\'t sure what I had to do. I ended up just handing over everything they asked for. Later found out I had more rights than I realized. Does anyone have a quick breakdown of what you must provide vs. what you can refuse?',
    author: 'Anonymous',
    timestamp: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
    helpfulCount: 34,
    markedHelpful: false,
    isUserPost: false,
    replies: [
      {
        id: 'sr_1a',
        author: 'CommunityHelper',
        content:
          'You must provide: driver\'s license, registration, and proof of insurance. You do NOT have to consent to a search — just say clearly "I do not consent to a search." You can also ask "Am I free to go?" If they say yes, leave calmly.',
        timestamp: new Date(Date.now() - 1.8 * 24 * 60 * 60 * 1000).toISOString(),
        helpfulCount: 22,
      },
      {
        id: 'sr_1b',
        author: 'Anonymous',
        content:
          'The Know Your Rights tab in this app has a great breakdown for traffic stops specifically. Helped me a lot.',
        timestamp: new Date(Date.now() - 1.5 * 24 * 60 * 60 * 1000).toISOString(),
        helpfulCount: 10,
      },
    ],
  },
  {
    id: 'seed_2',
    category: 'housing',
    title: 'Got a 3-day eviction notice — what do I do first?',
    content:
      'Landlord slipped a 3-day "pay or quit" notice under my door this morning. I\'m one month behind on rent due to a medical emergency. I\'m scared. What are the first steps I should take? I\'m in Texas.',
    author: 'Worried Tenant',
    timestamp: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
    helpfulCount: 51,
    markedHelpful: false,
    isUserPost: false,
    replies: [
      {
        id: 'sr_2a',
        author: 'HousingAdvocate',
        content:
          'First — don\'t panic, a 3-day notice is NOT an eviction. The landlord still has to file in court and you\'ll get a chance to respond. Immediately contact a local legal aid office (check the Resource Hub in this app). Many have emergency housing lines.',
        timestamp: new Date(Date.now() - 2.9 * 24 * 60 * 60 * 1000).toISOString(),
        helpfulCount: 38,
      },
      {
        id: 'sr_2b',
        author: 'Anonymous',
        content:
          'Also look into Emergency Rental Assistance programs in your county — Texas still has some funds available. Google "Texas ERA program."',
        timestamp: new Date(Date.now() - 2.5 * 24 * 60 * 60 * 1000).toISOString(),
        helpfulCount: 19,
      },
    ],
  },
  {
    id: 'seed_3',
    category: 'immigration',
    title: 'ICE checkpoint on the highway — what do I say?',
    content:
      'My family drives through a checkpoint regularly for work. Sometimes agents ask everyone where they were born. We\'re nervous. What exactly do we have to answer? Do we have to roll down the window all the way?',
    author: 'Anonymous',
    timestamp: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
    helpfulCount: 87,
    markedHelpful: false,
    isUserPost: false,
    replies: [
      {
        id: 'sr_3a',
        author: 'ImmigrationHelper',
        content:
          'At interior checkpoints you may assert your 5th Amendment right to remain silent. You can say "I am exercising my right to remain silent." You do not have to answer questions about citizenship. Keep windows up enough to pass documents through if asked. The ACLU has a good "know your rights at checkpoints" guide.',
        timestamp: new Date(Date.now() - 4.8 * 24 * 60 * 60 * 1000).toISOString(),
        helpfulCount: 61,
      },
    ],
  },
  {
    id: 'seed_4',
    category: 'employment',
    title: 'Boss told me I\'m "salary" so I don\'t get overtime — is that true?',
    content:
      'I\'m working 55+ hours a week at a small restaurant. My manager says since I have a "manager" title and get paid salary I don\'t qualify for overtime. But I\'m doing the same work as everyone else. Something feels off.',
    author: 'Overworked',
    timestamp: new Date(Date.now() - 4 * 24 * 60 * 60 * 1000).toISOString(),
    helpfulCount: 43,
    markedHelpful: false,
    isUserPost: false,
    replies: [
      {
        id: 'sr_4a',
        author: 'LaborRightsInfo',
        content:
          'The salary label alone does NOT exempt you from overtime. Under the FLSA, you must BOTH earn above $684/week AND pass a "duties test" to be truly exempt. Many employers misclassify workers — file a complaint with the Department of Labor at dol.gov. It\'s free and anonymous.',
        timestamp: new Date(Date.now() - 3.9 * 24 * 60 * 60 * 1000).toISOString(),
        helpfulCount: 37,
      },
    ],
  },
  {
    id: 'seed_5',
    category: 'stories',
    title: 'How I got free legal help after a wrongful arrest',
    content:
      'Two years ago I was wrongfully arrested during a protest. I didn\'t know where to start. I found a local legal aid office through a friend, got a pro bono lawyer, and just last month my case was dismissed and the city agreed to a settlement. It took time but don\'t give up — free help exists.',
    author: 'Justice Prevails',
    timestamp: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
    helpfulCount: 112,
    markedHelpful: false,
    isUserPost: false,
    replies: [
      {
        id: 'sr_5a',
        author: 'Anonymous',
        content: 'Thank you for sharing this. Gives me hope. Did you use a specific organization to find the lawyer?',
        timestamp: new Date(Date.now() - 6.5 * 24 * 60 * 60 * 1000).toISOString(),
        helpfulCount: 8,
      },
      {
        id: 'sr_5b',
        author: 'Justice Prevails',
        content: 'Yes — the National Lawyers Guild in my city. They specialize in civil rights cases and never charged me anything.',
        timestamp: new Date(Date.now() - 6.2 * 24 * 60 * 60 * 1000).toISOString(),
        helpfulCount: 14,
      },
    ],
  },
  {
    id: 'seed_6',
    category: 'police',
    title: 'Can police search my phone without a warrant?',
    content:
      'I was stopped and the officer grabbed my phone and started going through it. I didn\'t know what to do. Turns out I didn\'t have to let them. Sharing this so others know.',
    author: 'Anonymous',
    timestamp: new Date(Date.now() - 6 * 24 * 60 * 60 * 1000).toISOString(),
    helpfulCount: 76,
    markedHelpful: false,
    isUserPost: false,
    replies: [
      {
        id: 'sr_6a',
        author: 'CommunityHelper',
        content:
          'Under Riley v. California (2014 Supreme Court), police CANNOT search your phone without a warrant — even after arrest. Clearly state: "I do not consent to a search of my phone." If they search anyway, document everything — it may make the evidence inadmissible.',
        timestamp: new Date(Date.now() - 5.8 * 24 * 60 * 60 * 1000).toISOString(),
        helpfulCount: 59,
      },
    ],
  },
  {
    id: 'seed_7',
    category: 'general',
    title: 'Can I record the police in public?',
    content:
      'I\'ve heard different things. Some say it\'s legal, some say you can be arrested for it. What\'s the actual law? I\'m in Florida.',
    author: 'Curious Citizen',
    timestamp: new Date(Date.now() - 8 * 24 * 60 * 60 * 1000).toISOString(),
    helpfulCount: 55,
    markedHelpful: false,
    isUserPost: false,
    replies: [
      {
        id: 'sr_7a',
        author: 'RightsInfo',
        content:
          'In all 50 states you have the right to record police performing their duties in public. Florida is a two-party consent state for private conversations, but police in public do NOT have a reasonable expectation of privacy. Keep your distance, don\'t interfere, and keep recording. The ACLU app "Mobile Justice" is also great for this.',
        timestamp: new Date(Date.now() - 7.8 * 24 * 60 * 60 * 1000).toISOString(),
        helpfulCount: 44,
      },
    ],
  },
];

export const FORUM_DISCLAIMER =
  '⚠️ Disclaimer: Community posts are shared experiences and general information only — not legal advice. Advice from other users is not reviewed by attorneys. Always consult a licensed lawyer for guidance specific to your situation. Posts are stored locally on your device.';
