/**
 * CivicShield Pro — Dusty rose / pink palette with dark-mode support.
 * Matches the uploaded logo: gold shield, pink background, rose text.
 */
const colors = {
  light: {
    text: '#3D2535',
    tint: '#C97B8E',

    background: '#FAF7F8',
    foreground: '#3D2535',

    card: '#FFFFFF',
    cardForeground: '#3D2535',

    primary: '#C97B8E',
    primaryForeground: '#FFFFFF',

    secondary: '#C9A050',        // gold accent from logo
    secondaryForeground: '#FFFFFF',

    muted: '#F2E8EC',
    mutedForeground: '#7A5566',

    accent: '#E8B4C2',
    accentForeground: '#3D2535',

    destructive: '#E05252',
    destructiveForeground: '#FFFFFF',

    border: '#EAD5DC',
    input: '#EAD5DC',
    notification: '#C97B8E',

    tabIconDefault: '#A07888',
    tabIconSelected: '#C97B8E',
  },

  dark: {
    text: '#F5E8EE',
    tint: '#D48899',

    background: '#1C0F15',
    foreground: '#F5E8EE',

    card: '#2A1820',
    cardForeground: '#F5E8EE',

    primary: '#D48899',
    primaryForeground: '#FFFFFF',

    secondary: '#C9A050',
    secondaryForeground: '#FFFFFF',

    muted: '#2E1A22',
    mutedForeground: '#9A7080',

    accent: '#7B3A52',
    accentForeground: '#F5E8EE',

    destructive: '#C94444',
    destructiveForeground: '#FFFFFF',

    border: '#3E2030',
    input: '#3E2030',
    notification: '#D48899',

    tabIconDefault: '#6B4555',
    tabIconSelected: '#D48899',
  },

  // Shared border radius for cards, buttons, inputs
  radius: 14,
};

export default colors;
