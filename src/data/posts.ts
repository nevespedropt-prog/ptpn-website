// Blog posts. Body strings starting with "## " are subheadings, everything else is a paragraph.
// `cta` is optional: a booking box is shown only on posts where a free consultation is directly relevant.
export type CategoryKey = 'training' | 'nutrition' | 'workouts' | 'news';
export const categories: Record<CategoryKey, { label: string; title: string; blurb: string }> = {
  training: { label: 'Training', title: 'Personal training advice', blurb: 'Getting started, strength training, and training with knees, backs and other things people tell you to avoid.' },
  nutrition: { label: 'Nutrition', title: 'Nutrition and fat loss advice', blurb: 'Fat loss, protein and eating in a way you can keep up.' },
  workouts: { label: 'Workouts', title: 'Workouts you can follow', blurb: 'Full sessions to follow at the gym or at home.' },
  news: { label: 'News and events', title: 'PTPN news and events', blurb: 'Announcements from PTPN, including events and new packages.' },
};

export type Post = {
  slug: string;
  category: CategoryKey;
  title: string;
  summary: string;
  date: string; // ISO
  minutes: number;
  body: string[];
  sources?: string[];
  cta?: string;
};

export const posts: Post[] = [
  {
    slug: 'getting-started-after-years-off',
    category: 'training',
    title: 'Getting started after years off',
    summary: 'What the UK guidelines ask for, and a sensible way to build up to them when you have not trained in a long time.',
    date: '2026-10-31',
    minutes: 4,
    body: [
      "The UK Chief Medical Officers' guidelines for adults are at least 150 minutes of moderate activity a week (or 75 minutes of vigorous activity), plus strengthening activities on at least two days a week that work all the major muscle groups. After years off, that is a target to build towards, not a place to start on day one.",
      '## Start smaller than the guideline',
      'Two short strength sessions a week meet the strengthening guideline on their own, and a few brisk walks can begin to build the aerobic side. People who start with too much tend to be sore for days and stop. Increasing the amount gradually, one change at a time, is standard practice in resistance training guidance from the American College of Sports Medicine.',
      '## What the first four weeks are for',
      'The first month is for learning how you move. Squatting, hinging at the hips, pushing, pulling and carrying cover most of what a general programme needs. Loads stay light while technique settles. It also shows where you need to start: a knee that drifts inward, a back that rounds or a shoulder that will not reach overhead all change which exercises suit you.',
      '## Measure what you do',
      'Write down every set. After a few weeks you can see that the weight you struggled with in week two now moves easily, which is better evidence of progress than body weight alone. Body weight can move by a kilo or more in a day for reasons unrelated to training.',
      '## Check before you begin',
      'If you have a long-term health condition, new symptoms such as chest pain or unusual breathlessness, or you take medication that affects exercise, speak to your GP before starting.',
      '## Where personal training fits',
      'A personal trainer does the planning you would otherwise guess at. That means an initial assessment of how you move, a programme set at a suitable starting load, coaching on technique so each exercise is done safely, and a record of your sessions so every increase is deliberate. Pedro holds an exercise referral qualification, which covers working with people who have medical conditions alongside what their doctor advises.',
    ],
    sources: [
      "UK Chief Medical Officers' Physical Activity Guidelines (2019)",
      'NHS: Exercise',
      'American College of Sports Medicine: Progression models in resistance training for healthy adults (2009)',
    ],
    cta: 'If you are coming back after a long break, the free consultation is a conversation about your history, your goal and what has stopped you before. It is the step that comes before any training.',
  },
  {
    slug: 'training-with-bad-knees-and-backs',
    category: 'training',
    title: 'Knees, backs and other opinions',
    summary: 'What current UK guidance says about exercising with knee and back problems, and when to stop and get checked.',
    date: '2026-10-31',
    minutes: 4,
    body: [
      'Many people arrive having been told to avoid squats because of their knees, or to stop lifting because of their back. Current guidance points the other way for most people. NHS advice on back pain is to keep moving and carry on with normal activities where you can, rather than resting for long periods. For knee osteoarthritis, NICE recommends exercise, including strengthening and aerobic activity, as a core part of management.',
      '## Change the exercise before you remove it',
      'If a full squat bothers your knees, the pattern can usually be kept in a form that does not. Sitting back to a box set at a comfortable height, a split squat or a kettlebell held at the chest all change the load on the joint. For the back, learning to hinge at the hips with a flat back, holding a light weight, builds the muscles that support the spine. Carrying a weight in each hand trains grip, trunk and posture together.',
      '## When to stop and get checked',
      'A dull ache or tightness that stays steady during the session and settles within a day is generally manageable. Sharp pain, pain that keeps getting worse, pain that wakes you at night, and numbness or pins and needles in a limb are reasons to stop and speak to your GP or a physiotherapist. Back pain with loss of bladder or bowel control needs urgent medical help.',
      '## Strength is part of the treatment, not a cure',
      'Stronger muscles around a joint share the load, and exercise is part of NHS and NICE guidance for these conditions. That does not mean every sore knee or back will be fixed by lifting. A personal trainer does not diagnose or treat injuries, and a diagnosis comes first when something is new or unexplained.',
      '## Where personal training fits',
      'Once you have been cleared to exercise, a trainer works within your limits. The first session is an assessment of your range of movement and how each exercise feels, the programme starts light, and the load rises gradually. If something flares up, the exercise is changed the next session. Pedro holds an exercise referral qualification and works alongside what your GP or physiotherapist advises.',
    ],
    sources: [
      'NHS: Back pain',
      'NICE guideline NG226: Osteoarthritis in over 16s (2022)',
      "UK Chief Medical Officers' Physical Activity Guidelines (2019)",
    ],
    cta: 'If you have been told to avoid exercise and want to know what you can do, the free consultation is where we talk it through. The first training session is then an assessment of how you move.',
  },
  {
    slug: 'fat-loss-without-misery',
    category: 'nutrition',
    title: 'Fat loss without misery',
    summary: 'What NHS and sports nutrition guidance say about the pace of weight loss, protein and strength training.',
    date: '2026-10-31',
    minutes: 4,
    body: [
      'NHS guidance for losing weight safely is about 0.5 to 1 kg (1 to 2 lb) a week. Faster loss is harder to keep up and is more likely to cost muscle as well as fat. The plan that works is the one you are still following in month four.',
      '## A modest energy deficit',
      'Weight loss needs you to take in less energy than you use. A small, steady gap is easier to live with than a large one, because it leaves energy for training, sleep and ordinary life. If your weight has not changed for three weeks, the first thing to check is whether the food you log matches what you actually eat, weekends included.',
      '## Protein',
      'The UK reference nutrient intake for protein is 0.75 g per kg of body weight per day for adults. Sports nutrition position stands, including those of the International Society of Sports Nutrition and the American College of Sports Medicine, suggest about 1.2 to 2.0 g per kg a day for people who train regularly. For an 80 kg person that is roughly 96 to 160 g. Spreading it across meals, from foods such as eggs, fish, poultry, Greek yoghurt, beans and tofu, is a practical way to reach it.',
      '## Strength training',
      'UK guidelines recommend strengthening activity on at least two days a week. During weight loss, resistance training helps preserve muscle mass, so more of the weight you lose is fat. Walking adds energy use without the recovery cost of harder training.',
      '## Reading the scale',
      'Body weight moves by a kilo or more from day to day with water, salt and food in your gut. Weighing at the same time on a few mornings a week and looking at the average gives a more reliable picture than any single reading.',
      '## Where personal training fits',
      'A trainer sets energy and protein targets from your goal, builds a resistance programme around them and reviews your logged data to adjust both. Pedro is a Level 1 Nutrition and Weight Management Adviser, a qualification that covers general healthy-eating and weight-management advice. It does not cover treating medical conditions. If you have one, such as diabetes or an eating disorder, your GP or a registered dietitian should lead.',
    ],
    sources: [
      'NHS: Lose weight',
      'Scientific Advisory Committee on Nutrition: Dietary Reference Values for protein',
      'International Society of Sports Nutrition: Position stand on protein and exercise (2017)',
      'ACSM, Academy of Nutrition and Dietetics and Dietitians of Canada: Nutrition and athletic performance (2016)',
    ],
  },
  {
    slug: 'strength-training-over-40',
    category: 'training',
    title: 'Strength for normal people',
    summary: 'Why strength training matters from middle age, what the UK guidelines recommend, and how to start.',
    date: '2026-10-31',
    minutes: 4,
    body: [
      'Muscle mass and strength decline gradually with age unless they are trained, and bone density also falls. Resistance training is the best-supported way to slow both. You do not need to want to look like a bodybuilder to benefit. Most people want to carry shopping without thinking about it, get up from the floor easily and stay steady on their feet. All of that is strength.',
      '## What the guidelines say',
      "The UK Chief Medical Officers recommend strengthening activities on at least two days a week for adults of every age, working all the major muscle groups. For older adults they add activities that improve balance and coordination on at least two days a week. Muscle and bone both respond to being loaded at any age. Recovery may take longer than it used to, and that is worth building into the week.",
      '## Two sessions a week is enough to start',
      'Two full-body sessions of about 45 minutes cover the main movement patterns: a squat or leg press, a hinge such as a deadlift or kettlebell swing, a push, a pull and a carry. A third session adds more, but two done every week are better than four done for a month.',
      '## Choosing equipment',
      'Machines are a sensible way to learn a movement before loading it heavily. Dumbbells and kettlebells are easier to start with than a barbell, which suits people once their technique is solid. Bodyweight exercises, such as press-ups on a raised surface and squats to a box, are a good start at home.',
      '## Warm up and progress slowly',
      'Five to ten minutes of easy movement, followed by light sets of the first exercise, prepares the joints you are about to load. Progress by the smallest step available, such as one extra rep or the smallest weight increase, and keep rest days in the plan.',
      '## Health conditions',
      'If you have heart disease, high blood pressure, osteoporosis or another long-term condition, speak to your GP before you start so the programme fits what they advise.',
      '## Where personal training fits',
      'A trainer teaches the lifts, chooses loads that are challenging but safe, and tracks progression so you know you are getting stronger. For older adults the session can include balance work. Technique coaching is the main thing that is hard to get from a book or an app.',
    ],
    sources: [
      "UK Chief Medical Officers' Physical Activity Guidelines (2019)",
      'NHS: Strength exercises',
      'American College of Sports Medicine: Position stand on exercise and physical activity for older adults (2009)',
    ],
  },
  {
    slug: 'full-body-workout-30-minutes',
    category: 'workouts',
    title: 'A 30-minute full-body workout',
    summary: 'Five exercises that train all the major muscle groups in 30 minutes, with a way to make them harder each week.',
    date: '2026-11-03',
    minutes: 4,
    body: [
      "This circuit trains your legs, back, chest and trunk in about half an hour, which fits the UK recommendation of strengthening activity on at least two days a week that works all the major muscle groups. It needs very little equipment and works at the gym or at home.",
      '## Warm up for five minutes',
      'Walk or cycle easily for two minutes, then do ten slow bodyweight squats, ten hip hinges with your hands on your thighs, and ten arm circles each way. You should feel warm, not tired.',
      '## The circuit',
      'Do each exercise for 10 reps, then move to the next one. Rest for a minute after the last exercise and repeat the whole circuit. Aim for three rounds.',
      'Goblet squat: hold a dumbbell or kettlebell at your chest, sit back and down until your thighs are about parallel to the floor, then stand up.',
      'Press-up: do them on your knees, or with your hands on a bench or a kitchen worktop if a full press-up is too hard.',
      'Romanian deadlift: hold the weights in front of your thighs, push your hips back with a flat back until you feel your hamstrings stretch, then stand tall.',
      'One-arm row: rest one hand on a bench and pull the weight up towards your hip. Do all your reps on one side, then swap.',
      'Plank: hold for 30 seconds on your forearms with your body in a straight line.',
      '## Choose the weight',
      'Pick a weight where the last two reps of each set feel hard but your technique stays clean. If you could easily do five more, go heavier next time.',
      '## Make it harder each week',
      'Change one thing at a time: add a rep to each exercise, or use a slightly heavier weight, or add a fourth round. Write down what you did so you know what to beat next time. Gradual progression is the principle behind resistance training guidance from the American College of Sports Medicine.',
      '## When to skip it',
      'If something hurts in a sharp way, stop that exercise and swap it for an easier version. If you have a medical condition or an injury, check with your GP before you start.',
      '## Where personal training fits',
      'A circuit like this is a general template. A personal trainer adjusts the exercises, loads and number of sets to your assessment, your goal and any limits, and corrects technique while you do them.',
    ],
    sources: [
      "UK Chief Medical Officers' Physical Activity Guidelines (2019)",
      'NHS: Strength exercises',
      'American College of Sports Medicine: Progression models in resistance training for healthy adults (2009)',
    ],
  },
  {
    slug: 'new-ptpn-website-and-app',
    category: 'news',
    title: 'The new PTPN website and app',
    summary: 'What is on the new site, where to find the packages, and where events and announcements will be posted.',
    date: '2026-11-03',
    minutes: 2,
    body: [
      'The new PTPN website is live. You can see every package and its price in one place, read what clients say, and book a free consultation from any page.',
      '## What you will find here',
      'This blog is where Pedro will post training and nutrition advice, full workouts you can follow, and announcements. When there is an event, or spots open on a package such as Duo, it will be posted here first.',
      '## The app',
      'The PTPN app is included with personal training. It holds your programme, your logging and your progress, so your trainer can see what you did between sessions and adjust the plan. It costs nothing on top of your package. Clients can sign in from the Member log in link in the menu.',
      '## Stay in touch',
      'You can follow PTPN on Instagram and Facebook, or message Pedro on WhatsApp on 07459 020381.',
    ],
  },
]

export const sortedPosts = [...posts].sort((a, b) => b.date.localeCompare(a.date));
