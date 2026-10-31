// Single source of truth for all site copy.
// Prices and package names are CONFIRMED by the client (Oct 2026).

export const site = {
  name: 'PTPN',
  tagline: 'Be fit',
  url: 'https://www.ptpn.co.uk',
  email: 'info@ptpn.co.uk',
  appPath: 'https://nevespedropt-prog.github.io/PTPN/',
  area: 'Bush Hill Park, Enfield, London',
  areaShort: 'Enfield',
  title: 'PTPN | Personal Training in Enfield | Be fit',
  description:
    'One-to-one personal training in Enfield. Programmed for you, measured every session, with your plan and progress in your own coaching app. Packages from £32.50 a session.',
  // Set to the real business address before launch if it should appear publicly.
  address: null as string | null,
};

export const coach = {
  name: 'Pedro',
  headline: 'I am Pedro. I coach people who are done starting over.',
  intro:
    'I love helping people improve their strength and fitness, and as an ex-basketball player, physical activity and sport have always been part of my life.',
  story: [
    'Being a coach since 2016, my mission as a personal trainer is to help people change their lives for the better, become the best version of themselves, and feel more confident. It does not matter whether you are fit or inactive, I will give you the best advice to make sure you reach your goals.',
    'You will get premium support, motivation, counselling, a training plan, goal setting and a positive mindset. My attention to detail and your commitment are the key ingredients to your success, and I will coach you every step of the way.',
    'After more than 10 years in the fitness industry, taking multiple PT and fitness certificates, and delivering over 10,000 personal training sessions and classes, I can say experience has taught me a lot and I am prepared to tackle any challenge.',
  ],
  specialisms: [
    'Weight loss',
    'Strength training',
    'Hypertrophy training',
    'Flexibility',
    'Endurance and cardio',
    'Boxing training',
    'Calisthenics',
    'Overall health',
  ],
  qualifications: [
    'Level 3 Personal Trainer',
    'Level 1 Nutrition and Weight Management Adviser',
    'Circuit Training Expert',
    'Sports Conditioning Coach',
    'Spin Instructor',
    'Outdoor and Indoor Group Exercise Coach',
    'Exercise Referral, for various medical conditions',
  ],
};

export type Pkg = {
  name: string;
  sessions: number;
  minutes: number;
  perSession: number;
  total: number;
  tagline: string;
  best?: boolean;
  entry?: boolean;
  goodIfYou: string;
  includes: string[];
};

export const packages: Pkg[] = [
  {
    name: 'Express',
    sessions: 12,
    minutes: 30,
    perSession: 32.5,
    total: 390,
    tagline: 'Twelve 30-minute sessions',
    entry: true,
    goodIfYou: 'Want focused, short sessions that fit a busy week',
    includes: ['Focused, high-density training', 'Full programme included', 'App access included'],
  },
  {
    name: 'Ignition',
    sessions: 4,
    minutes: 60,
    perSession: 54,
    total: 216,
    tagline: 'Four one-hour sessions',
    goodIfYou: 'Want to try coaching properly before committing',
    includes: ['Ideal to trial coaching', 'Full programme included', 'App access included'],
  },
  {
    name: 'Momentum',
    sessions: 8,
    minutes: 60,
    perSession: 48,
    total: 384,
    tagline: 'Eight one-hour sessions',
    goodIfYou: 'Want a mid-size block to build the habit',
    includes: ['Committed but flexible', 'Full programme included', 'App access included'],
  },
  {
    name: 'Signature',
    sessions: 12,
    minutes: 60,
    perSession: 40,
    total: 480,
    tagline: 'Twelve one-hour sessions',
    best: true,
    goodIfYou: 'Are committing to a full block',
    includes: ['Lowest per-session rate', 'Full programme included', 'App access included'],
  },
];

export const duo = {
  name: 'Duo',
  price: 100,
  period: 'month',
  tagline: 'Small group personal training',
  detail: 'Train with a partner or a friend. Minimum two people, minimum one session a week.',
};

export const packageRows = [
  { label: 'Session length', key: 'minutes' },
  { label: 'Personal programme', value: 'Included' },
  { label: 'Technique coached every rep', value: 'Yes' },
  { label: 'PTPN app access', value: 'Included' },
  { label: 'Nutrition targets and meal plans', value: 'Included' },
] as const;

export const testimonials = [
  {
    quote:
      'Pedro has improved my strength and fitness, pushing me harder over time, within my limits.',
    context:
      'For me it was my first ever time working out, at the age of 55 with dodgy knees.',
    name: 'Neil Purcell',
    meta: 'Google review',
    stars: 5,
    lead: true,
  },
  {
    quote:
      'I can honestly say Pedro is the best trainer I have ever worked with. He helped me feel more comfortable and confident at the gym.',
    context: null,
    name: 'Diana',
    meta: 'Client · Greece',
    stars: 5,
    lead: false,
    edited: true,
  },
  {
    quote:
      "After 3 months of committing to healthier eating habits, regular exercise, and stress management techniques, I've shed 30 pounds, regained confidence, and found a newfound sense of vitality.",
    context: null,
    name: 'Anna',
    meta: 'Client · England',
    stars: 5,
    lead: false,
  },
  {
    quote:
      'After 3 months I was able to perform exercises I never imagined I could perform. I gained 5kg of muscle mass and feel more energetic and active than ever.',
    context: 'Someone who had never been to a gym before.',
    name: 'Iuri da Costa',
    meta: 'Client · cabin crew at easyJet',
    stars: 5,
    lead: false,
    edited: true,
  },
];

export const faqs = [
  {
    q: 'How much does personal training cost?',
    a: 'Packages start at £32.50 a session for Express, a twelve-session 30-minute pack. The one-hour packs are Ignition at £54 a session for four sessions, Momentum at £48 for eight, and Signature at £40 for twelve. Duo, the small group option, is £100 a month for a minimum of two people training at least once a week. All prices are per session and paid in person.',
  },
  {
    q: 'What is free?',
    a: 'The consultation is free. It is a conversation, not a training session. We talk through your goal, your training history and what has stopped you before, and you leave with a clear idea of what working together would look like. There is no charge and no pressure to book anything. The first training session is paid, and it starts with an assessment.',
  },
  {
    q: 'Do I need experience before I start?',
    a: 'No. Plenty of clients have never trained properly before. The first session is an assessment, and the programme is written around what you can do now, not what you think you should be able to do.',
  },
  {
    q: 'How many sessions a week do I need?',
    a: 'Most clients train two or three times a week. If you train with me less often than that, I will give you work to do on your own and you will log it in the app so I can see it.',
  },
  {
    q: 'What happens if I miss a session?',
    a: 'Speak to me and we rearrange. A package is a block of sessions rather than a weekly contract, so a missed week does not cost you a session.',
  },
  {
    q: 'Where do we train?',
    a: 'In a boutique gym that I manage in Bush Hill Park, Enfield. Get in touch and I will confirm the exact address and the best time to visit.',
  },
  {
    q: 'Is the app extra?',
    a: 'No. The PTPN app comes with coaching. It holds your programme, your logging and your progress, and it costs you nothing on top. You can sign in on your phone or on the website.',
  },
  {
    q: 'Do I have to use the app?',
    a: 'No, but it is how the coaching works between sessions. If you would rather not, tell me and we will find a way that suits you.',
  },
];

export const nav = [
  { href: '../#packages', label: 'Personal training' },
  { href: '../#method', label: 'How it works' },
  { href: '../#coach', label: 'Your coach' },
  { href: '../#app', label: 'The app' },
  { href: '../blog', label: 'Blog' },
];
