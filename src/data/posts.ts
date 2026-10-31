// Blog posts. Body strings starting with "## " are subheadings, everything else is a paragraph.
export type Post = {
  slug: string;
  title: string;
  summary: string;
  date: string; // ISO
  minutes: number;
  body: string[];
};

export const posts: Post[] = [
  {
    slug: 'getting-started-after-years-off',
    title: 'Getting started after years off',
    summary: 'What a sensible first 12 weeks looks like when you have not trained properly in a long time.',
    date: '2026-10-31',
    minutes: 4,
    body: [
      'The hardest part of coming back after years off is not the training. It is deciding how much to do on day one, and most people get it wrong in one of two directions. They do far too much, are sore for a week and quit. Or they do so little that nothing changes and it all feels pointless.',
      '## Start with two sessions a week',
      'Two sessions a week is enough to start. Keep each one to about 40 to 45 minutes and finish feeling that you could have done one more set. I would rather you walk out thinking that was easy and come back on Thursday than walk out wrecked and cancel.',
      '## What the first four weeks are for',
      'The first month is for learning how you move. Squatting, hinging at the hips, pushing, pulling and carrying cover most of what you need. We use light loads and watch what your body does. A knee that drifts inward, a back that rounds, a shoulder that will not reach overhead: these tell me where to start. This is why my first session is an assessment, and why the programme is written afterwards, not before.',
      '## Weeks five to twelve',
      'From week five you add load or reps slowly, one change at a time. If you did 8 reps with 10kg last week, try 9 reps, or 12kg for 8. Do not change everything at once, because then you cannot tell what worked. If life allows, add a third session. If a week goes badly because of illness, travel or work, repeat the previous week instead of trying to catch up.',
      '## Write it down',
      'Log every set. Memory is bad at this, and a notebook or an app is not. After a few weeks you can look back and see that the weight you struggled with in week two now moves easily. That is the point where most people stop doubting the process.',
      '## What to measure',
      'Body weight is one number and it moves around for reasons unrelated to training. Also track the heaviest weight you can lift for 8 clean reps, how many sessions you attended, and how you are sleeping. Check them every four weeks, at the same time of day.',
      '## Before you begin',
      'If you have a medical condition, an injury or you are taking medication that affects exercise, check with your GP first. I hold an exercise referral qualification and I am happy to work alongside what your doctor advises.',
      'If you want a plan written for where you are now, not for where you were ten years ago, book a free consultation. We talk through your history and what has stopped you before, and I will tell you honestly whether I can help.',
    ],
  },
  {
    slug: 'training-with-bad-knees-and-backs',
    title: 'Knees, backs and other opinions',
    summary: 'How to train with the things people say you should stop doing, and when to genuinely stop.',
    date: '2026-10-31',
    minutes: 4,
    body: [
      'A lot of my clients arrive having been told to avoid squats because of their knees, or to stop lifting because of their back. Sometimes that advice was right at the time. Often it was given once, years ago, and nobody revisited it. Avoiding movement completely rarely makes a sore joint stronger.',
      '## Change the exercise before you remove it',
      'If a full squat bothers your knees, we do not drop the squat. We sit back to a box set at a comfortable height and lower it over the weeks. A split squat, where one foot is behind you, often feels better than a standard squat. A kettlebell held at your chest changes the angle again. There are usually several ways to train the same pattern, and one of them will feel fine.',
      'For backs, the hip hinge is the skill that matters most. Learning to bend from the hips with a flat back, holding a light kettlebell, teaches you to pick things up safely and builds the muscles that support your spine. Carries are another favourite of mine: walking with a heavy bag in each hand works your grip, trunk and posture at once.',
      '## A simple rule for pain',
      'My rule of thumb is this. A dull ache or tightness that stays the same during the session and settles within a day is usually fine to train around. Sharp pain, pain that gets worse as you continue, pain that wakes you at night, numbness or pins and needles in a limb are all reasons to stop and get it checked by your GP or a physiotherapist. Do not train through those.',
      '## Strength is part of the answer',
      'Stronger muscles around a joint share the load. That does not mean every sore knee or back will be fixed by lifting, and I am not a physiotherapist. It does mean that a well-built programme, started light and increased slowly, is a reasonable thing to try once you have been cleared to exercise.',
      '## What this looks like in a session',
      'We warm up the joints that complain, pick exercises that fit your range of movement today, and keep a note of how each one feels. If something flares up, we change it next session. Over time the list of things you can do gets longer, not shorter.',
      'If you have been told to stop doing something and you would like to know what you can do instead, book a free consultation. Bring your history and we will work out where to start.',
    ],
  },
  {
    slug: 'fat-loss-without-misery',
    title: 'Fat loss without misery',
    summary: 'Why sticking with a plan beats the diet of the month, and what that looks like week to week.',
    date: '2026-10-31',
    minutes: 4,
    body: [
      'Most diets work for a few weeks and fail afterwards, and the reason is usually boring. They ask for a way of eating that nobody can keep up when work gets busy, a family birthday comes round or a holiday arrives. The plan that works is the one you are still following in month four.',
      '## Eat a little less, not almost nothing',
      'A small, steady gap between what you eat and what you burn is easier to live with than a huge one. You lose weight more slowly, but you keep your energy, you sleep better and you are far less likely to end up eating a whole packet of biscuits on a Friday night. I would rather you lose weight slowly for six months than quickly for three weeks.',
      '## Protein at every meal',
      'A palm-sized portion of protein at each meal helps you feel full and helps you hold on to muscle while you lose fat. Eggs, chicken, fish, Greek yoghurt, beans and tofu all work. You do not need supplements to do this.',
      '## Walk more',
      'Steps are the least glamorous tool and one of the most useful. A daily walk burns energy, costs nothing and does not leave you too tired to train. Pick a number that is a little above your current average and keep it for a few weeks before raising it.',
      '## Lift weights',
      'Training with weights tells your body to keep its muscle while you diet. That is why two or three strength sessions a week sit at the centre of the programmes I write, with walking and some cardio around them.',
      '## Weigh yourself sensibly',
      'Body weight swings by a kilo or more from day to day with water, salt and what is in your gut. Weigh yourself at the same time a few mornings a week and look at the average. If the average has not moved for three weeks, the first thing to check is whether you have been logging what you actually eat, weekends included.',
      '## Keep the foods you like',
      'I do not ban foods. If you love chocolate, we make room for it. People who forbid things tend to binge on them later.',
      'If you want a plan with targets built around your life, book a free consultation. We start with a conversation about your goal and what has gone wrong before.',
    ],
  },
  {
    slug: 'strength-training-over-40',
    title: 'Strength for normal people',
    summary: 'What to expect from a bar, a kettlebell or your own body at 40, 50 and beyond.',
    date: '2026-10-31',
    minutes: 4,
    body: [
      'You do not need to want to look like a bodybuilder to benefit from lifting. Most of the people I train want to carry shopping without thinking about it, get off the floor easily, keep playing with their kids or grandchildren, and feel steadier on their feet. All of that is strength.',
      '## Muscle and bone respond at any age',
      'Muscle and bone both respond to being loaded, whether you are 25 or 65. You may recover more slowly than you used to, and that matters when you plan the week, but starting later does not close the door.',
      '## Two sessions a week is enough',
      'Two full-body sessions of around 45 minutes cover the main movement patterns: a squat or leg press, a hinge such as a deadlift or kettlebell swing, a push, a pull and a carry. Three sessions is better if you can fit them in, but two done every week beats four done for a month.',
      '## Which tools',
      'A barbell is great once your technique is good. Kettlebells and dumbbells are easier to start with, and machines are a sensible way to learn a movement before you load it heavily. Your own bodyweight works too: push-ups on a raised surface, squats to a box and step-ups are a good start. I use all of them and pick based on you, not on fashion.',
      '## Warm up properly',
      'Spend five to ten minutes raising your heart rate and moving the joints you are about to load. It does not need to be elaborate. A few minutes on a bike followed by light sets of your first exercise is enough.',
      '## Progress slowly',
      'Add a little each week. One extra rep, or the smallest weight increase you can find. The aim is to finish the block stronger than you started it with nothing hurting. Rest days are part of the programme, not a break from it.',
      '## If you have been away from lifting',
      'If you have a heart condition, high blood pressure, osteoporosis or any other medical condition, talk to your GP before you start. I can then write a programme that fits what they advise.',
      'If you are not sure where to begin, book a free consultation. We talk about what you want to be able to do and I will show you what the first few weeks would look like.',
    ],
  },
];
