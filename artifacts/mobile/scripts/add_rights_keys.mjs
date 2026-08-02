/**
 * Adds rights content i18n keys (categories, rights text, quiz) + nav keys
 * to constants/i18n.ts. English values only — fill_missing_translations fills the rest.
 */
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const I18N_PATH = path.resolve(__dirname, '../constants/i18n.ts');

const NEW_KEYS = {
  // Nav tabs
  'nav.hub':  'Hub',
  'nav.log':  'Log',

  // Category titles
  'rights.cat_traffic':     'Traffic Stops',
  'rights.cat_police':      'Police Encounters',
  'rights.cat_arrest':      'Arrest Rights',
  'rights.cat_immigration': 'Immigration Rights',
  'rights.cat_home':        'At Home',
  'rights.cat_search':      'Searches & Seizures',

  // Traffic Stop rights
  'rights.traffic_r1': 'You must show your license, registration, and proof of insurance.',
  'rights.traffic_r2': 'You have the right to remain silent beyond providing ID documents.',
  'rights.traffic_r3': 'You can refuse a search — say clearly: "I do not consent to this search."',
  'rights.traffic_r4': 'Keep your hands visible at all times and move slowly.',
  'rights.traffic_r5': "You can record the encounter as long as you don't interfere.",
  'rights.traffic_r6': 'If you are arrested, say: "I am invoking my right to remain silent and want a lawyer."',
  'rights.traffic_r7': 'Do not argue or resist — challenge it in court instead.',

  // Police Encounter rights
  'rights.police_r1': 'You have the right to remain silent. Use it.',
  'rights.police_r2': 'You can ask: "Am I being detained or am I free to go?"',
  'rights.police_r3': 'If detained, you can ask why you are being held.',
  'rights.police_r4': 'You can film police in public — it is a protected First Amendment right.',
  'rights.police_r5': 'Never physically resist an officer, even if the stop is unlawful.',
  'rights.police_r6': 'Officers can pat down your outer clothing if they suspect a weapon.',
  'rights.police_r7': 'You can always say "I want a lawyer" at any point.',

  // Arrest rights
  'rights.arrest_r1': 'You have the right to know why you are being arrested.',
  'rights.arrest_r2': 'Miranda rights must be read before a custodial interrogation.',
  'rights.arrest_r3': "You have the right to an attorney. If you can't afford one, one will be provided.",
  'rights.arrest_r4': 'You can remain silent — say: "I am invoking my right to remain silent."',
  'rights.arrest_r5': 'Do not sign any documents without a lawyer present.',
  'rights.arrest_r6': 'You have the right to make a phone call after being booked.',
  'rights.arrest_r7': 'You must be brought before a judge within 48 hours of arrest.',

  // Immigration rights
  'rights.immigration_r1': 'You have the right to remain silent regardless of immigration status.',
  'rights.immigration_r2': 'You do not have to open the door to ICE without a signed judicial warrant.',
  'rights.immigration_r3': 'Ask to see the warrant — an ICE administrative warrant is NOT a court order.',
  'rights.immigration_r4': 'Do not sign any documents (like "voluntary departure") without a lawyer.',
  'rights.immigration_r5': 'You have the right to contact your consulate if detained.',
  'rights.immigration_r6': 'Anything you say can be used in immigration proceedings.',
  'rights.immigration_r7': 'Contact an immigration lawyer immediately if detained.',

  // At Home rights
  'rights.home_r1': 'Police generally need a warrant signed by a judge to enter your home.',
  'rights.home_r2': 'You can ask to see the warrant through a window or door.',
  'rights.home_r3': 'If officers enter by force, do not resist — challenge it in court.',
  'rights.home_r4': 'A "knock and announce" is usually required before entry.',
  'rights.home_r5': 'Consent to search is voluntary — you can say no.',
  'rights.home_r6': 'If you open the door, step outside and close the door behind you.',
  'rights.home_r7': 'Anything in plain view may be seized without a warrant.',

  // Searches & Seizures rights
  'rights.search_r1': 'The 4th Amendment protects against unreasonable searches.',
  'rights.search_r2': 'Police need a warrant, probable cause, or consent to search.',
  'rights.search_r3': 'Clearly say: "I do not consent to this search."',
  'rights.search_r4': 'Your refusal to consent cannot be used as probable cause.',
  'rights.search_r5': 'Searches can be challenged in court as unlawful.',
  'rights.search_r6': 'Evidence from an illegal search may be suppressed ("fruit of the poisonous tree").',
  'rights.search_r7': 'You can complain about an illegal search after the fact — not during.',

  // Quiz questions (10 questions × question + 4 options + explanation = 60 keys)
  'rights.q1_q':   'During a traffic stop, which documents must you provide?',
  'rights.q1_a0':  'License only',
  'rights.q1_a1':  'License, registration, and proof of insurance',
  'rights.q1_a2':  'Nothing — you can remain silent',
  'rights.q1_a3':  'Only your name',
  'rights.q1_exp': 'Drivers must provide their license, vehicle registration, and proof of insurance when lawfully stopped.',

  'rights.q2_q':   'How do you properly invoke your right to remain silent?',
  'rights.q2_a0':  'Just stay quiet without saying anything',
  'rights.q2_a1':  'Say "I plead the fifth" repeatedly',
  'rights.q2_a2':  'Clearly say "I am invoking my right to remain silent"',
  'rights.q2_a3':  'Walk away from the officer',
  'rights.q2_exp': 'Since 2013 (Salinas v. Texas), you must explicitly state you are invoking your right to silence — staying quiet alone may not protect you.',

  'rights.q3_q':   'Can you legally record the police in public?',
  'rights.q3_a0':  'Never — it is always illegal',
  'rights.q3_a1':  'Only with written permission',
  'rights.q3_a2':  'Yes, it is a protected First Amendment right',
  'rights.q3_a3':  'Only in California',
  'rights.q3_exp': "Recording police performing their duties in public is protected by the First Amendment across the US, as long as you don't physically interfere.",

  'rights.q4_q':   'If ICE comes to your door, must you let them in?',
  'rights.q4_a0':  'Yes, always',
  'rights.q4_a1':  'Only if they show any badge',
  'rights.q4_a2':  'No — only if they have a signed judicial warrant',
  'rights.q4_a3':  'Yes, if they identify themselves as officers',
  'rights.q4_exp': 'An ICE administrative warrant is not a court order. You only must allow entry with a judicial (signed by a judge) warrant.',

  'rights.q5_q':   'When can you ask "Am I free to go?" during a stop?',
  'rights.q5_a0':  'Never — you must wait to be released',
  'rights.q5_a1':  'Only after 15 minutes',
  'rights.q5_a2':  'At any point during the encounter',
  'rights.q5_a3':  'Only if you are not under arrest',
  'rights.q5_exp': 'You can ask at any time whether you are free to go. If not detained, you may calmly walk away.',

  'rights.q6_q':   'What should you do if police enter your home without a warrant?',
  'rights.q6_a0':  'Physically block them from entering',
  'rights.q6_a1':  'Comply and challenge the entry in court afterward',
  'rights.q6_a2':  'Call 911 immediately',
  'rights.q6_a3':  'Lock all the doors',
  'rights.q6_exp': 'Never physically resist even an unlawful entry — it can lead to additional charges. Document everything and challenge it in court.',

  'rights.q7_q':   'What is the "fruit of the poisonous tree" doctrine?',
  'rights.q7_a0':  'Agricultural regulations on police property',
  'rights.q7_a1':  'Evidence gathered from an illegal search can be excluded in court',
  'rights.q7_a2':  'A rule about planting evidence',
  'rights.q7_a3':  'Police must disclose all evidence before trial',
  'rights.q7_exp': 'Under this exclusionary rule, evidence obtained from an unlawful search or seizure may be suppressed — it cannot be used against you in court.',

  'rights.q8_q':   'How long can you legally be held after arrest before seeing a judge?',
  'rights.q8_a0':  '24 hours',
  'rights.q8_a1':  '48 hours',
  'rights.q8_a2':  '72 hours',
  'rights.q8_a3':  'Until trial',
  'rights.q8_exp': 'In California and most US jurisdictions, you must be brought before a judge within 48 hours of arrest (excluding weekends/holidays in some cases).',

  'rights.q9_q':   'Does refusing a police search give officers probable cause?',
  'rights.q9_a0':  'Yes, it looks suspicious',
  'rights.q9_a1':  'Only at night',
  'rights.q9_a2':  'No — your refusal cannot be used as probable cause',
  'rights.q9_a3':  'Yes, in high-crime areas',
  'rights.q9_exp': "The Supreme Court has held that exercising your 4th Amendment right to refuse a search cannot by itself constitute probable cause for a search.",

  'rights.q10_q':   'When must Miranda rights be read to you?',
  'rights.q10_a0':  'Immediately upon arrest',
  'rights.q10_a1':  'Before any police questioning ever',
  'rights.q10_a2':  'Before a custodial interrogation',
  'rights.q10_a3':  'Only at the police station',
  'rights.q10_exp': 'Miranda warnings are required before a custodial interrogation — when you are in custody and being questioned. Not merely upon arrest.',

  // Security screen
  'security.title':        'Privacy & Security',
  'security.recommend':    'For the safety of your encounter log, we recommend setting up an App Lock.',
  'security.setup_lock':   'Set up App Lock',
  'security.dismiss':      'Dismiss',
  'security.dont_show':    "Don't show again",
  'security.lock_enabled': 'Your app is protected',
  'security.lock_enabled_desc': 'A PIN and biometric lock are active.',
  'security.change_pin':   'Change PIN',
  'security.change_pin_desc': 'Update your 4-digit PIN',
  'security.lock_after':   'Lock after',
  'security.lock_after_desc': 'How long in background before re-locking',
  'security.app_lock':     'App Lock',
  'security.app_lock_on':  'PIN required to open the app',
  'security.app_lock_off': 'Anyone can open the app',
};

let src = fs.readFileSync(I18N_PATH, 'utf8');

// Skip keys that already exist
const toAdd = Object.entries(NEW_KEYS).filter(([key]) => !src.includes(`'${key}':`));
console.log(`Adding ${toAdd.length} new keys (${Object.keys(NEW_KEYS).length - toAdd.length} already present)`);

if (toAdd.length === 0) {
  console.log('Nothing to add.');
  process.exit(0);
}

const lines = toAdd.map(([key, enVal]) => {
  const escaped = enVal.replace(/\\/g, '\\\\').replace(/'/g, "\\'");
  return `  '${key}': {\n    en: '${escaped}',\n  },`;
});

// Insert before closing };
src = src.replace(/^};$/m, lines.join('\n') + '\n};');
fs.writeFileSync(I18N_PATH, src, 'utf8');
console.log(`✅ Done. Added ${toAdd.length} keys.`);
