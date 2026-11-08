# Weekly posting agent: runbook

Goal: every week, create next week's 7 Dumbbell Dads Club carousels (Mon to Sun) and schedule them in Buffer for Instagram and TikTok at **7:00 PM America/Phoenix**. Leroy does nothing. You do everything below, then send him a short summary.

Read `BRAND.md` first. It is the brand book: audience, voice, hard rules, pillars, visual rules.

## 1. Plan the week

- Week = the Monday after today through Sunday. Name it by Monday's date, e.g. `2026-11-09`.
- If `posts/week-<monday>.json` already exists, that week was already built. Check the Buffer queue: if all 14 of its posts are there, skip to step 6 and tell Leroy "Next week is already scheduled." If some are missing, schedule only the missing ones.
- Read every `posts/week-*.json` so you never repeat a topic or hook.
- One post per day:
  - Mon: The Workout (full routine)
  - Tue: Dad Fuel (food rules, swaps, drive-thru, kids' leftovers)
  - Wed: Myth Busting (with a real, checked source)
  - Thu: Dad Life (time hacks, bedtime or nap-time training). **From Thursday, November 19th, 2026, every Thursday is "Respawn Reps"** (see below).
  - Fri: The Workout (different equipment angle: one dumbbell, two light, core, mobility)
  - Sat: Myth Busting or Dad Fuel
  - Sun: weekly reset plus the call to action: the 8-week plan and the free Bedtime Lift are at the link in the Instagram bio. Never ask people to comment a keyword; there is no auto-DM.
- **Respawn Reps (Thursday series, starts 2026-11-19, the GTA VI launch day):** a 15 to 20 minute two-dumbbell session built around a gaming night after bedtime. Quiet, no jumping.
  - Episode 1 (2026-11-19), hook "Launch night. Lift first.": a short circuit done before picking up the controller, 3 rounds of goblet squat, bent-over row, push-up, plank.
  - Every later Thursday: a new episode with ONE new game rule tied to moments in any game, e.g. every respawn = 10 squats, every loading screen = 20 sec plank, every finished mission = 1 round of the circuit. Read past weeks' JSON so no rule repeats. Number the episodes (slide 1 sub line: "Respawn Reps, episode <n>").
  - Brand safety: no Rockstar or game logos, art, characters, screenshots or fonts on the slides; slides stay in our own look. The game's name may appear only in the caption and hashtags (e.g. #gta6 on launch week), never as a partnership or sponsorship. No numbers that need sources.
  - The title on TikTok starts with "Respawn Reps:".
- Hard rules (from BRAND.md): no invented people, results, testimonials or transformations; no medical claims; every number gets a real source you verified with web search this run; hooks under 8 words; no em dashes anywhere; max 5 hashtags, always ending in #dumbbelldadsclub.

## 2. Build the slides

- Copy the closest file from `templates/` to `build/<week>/<n>-<Day>.dc.html` (n = 1 for Mon through 7 for Sun) and rewrite only the slide content. Keep the `<style>` block, classes and structure exactly. Slide 1 = navy hook with ONE script line (`<span class="o">`), middle slides = cream value slides, last slide = navy CTA with `@dumbbelldadsclub`. 5 to 7 slides per post.
- Render: `python3 tools/render.py <week>` (needs network to npm the first time). It prints overflow warnings; fix any and re-render.
- Look at every slide 1 and at least two middle slides (Read the JPGs) before moving on.

## 3. Write the week spec

`posts/week-<week>.json`, same shape as `posts/week-2026-11-02.json`:
`id` (`1-Mon`), `date_label` exactly like `Monday, November 9th, 2026` (Buffer's date picker labels), `time` `7:00 PM`, `title` (TikTok title, under 60 chars), `caption` (hook line, blank line, value, blank line, question or CTA, blank line, 5 hashtags), `song_suggestion`, `images` as paths under `posts/`, e.g. `2026-11-09/1-Mon_slide1.jpg`.

Commit `build/<week>/`, `posts/<week>/` and the JSON, then push to `main`. Buffer pulls images from `https://raw.githubusercontent.com/leroymoses/dumbbell-dads-club/main/posts/`, so the push must land before step 4.

## 4. Schedule in Buffer (built-in browser on Leroy's computer)

The browser pane in the Claude desktop app is already signed in to Buffer, with both channels (Instagram and TikTok, both `dumbbelldadsclub`) connected. If a tool says the site is not allowed, call `request_access` for `https://publish.buffer.com` with scope `site` and wait.

Check the queue first (`https://publish.buffer.com/all-channels`): if this week's posts are already there, do not add them again. The free plan holds 10 posts per channel.

For each post, in order:
1. Open the composer: click the green **+** at the top right of the Publish page (a real click, not a script click). Both channels should be selected.
2. Load helpers, then attach the slides with a script:
   `(0,eval)(await (await fetch('https://raw.githubusercontent.com/leroymoses/dumbbell-dads-club/main/tools/buffer.js?'+Date.now())).text())`
   then fetch the week JSON into `window.ddcSpec`, set `window.ddcP` to the post, and put the files on `input[name=file-upload-input]` with a `DataTransfer` plus a `change` event. Wait about 6 seconds.
3. **Type the caption with real keystrokes**: click inside the caption box, `computer type` each line, `key "Enter Enter"` between paragraphs. Script text insertion (`execCommand`) shows on screen but Buffer does NOT save it. Skip the emoji when typing.
4. Check that the editor text contains the hook exactly once and ends with `#dumbbelldadsclub`.
5. `window.DDC_MODE='schedule'; await ddcFinish()`. It sets the TikTok title, the date and the time, checks them, and clicks Schedule Posts. If it returns `ABORT`, stop and fix that post by hand.

Never press Escape inside a composer with unsaved changes: it closes and throws the work away.

**Instagram posts are Reels, not carousels.** After rendering the slides, build one Reel per post: `python3 tools/render_reel.py reels/<week>/<n>-<Day>.mp4 <that post's slide JPGs in order>` (9:16, about 16 seconds, silent track). Slide 1 must say "Watch for..." not "Swipe for..." (video, not a carousel). Commit the MP4s with the slides. In Buffer, the Instagram composer: choose **Reel**, attach the MP4 the same way as images (fetch from raw.githubusercontent.com into `input[name=file-upload-input]`), type the caption, set the date and time, and set **Notify Me** like TikTok below, because Leroy adds the trending sound in the Instagram app. TikTok keeps the photo carousel.

**TikTok posts are NOT automatic.** Leroy adds a trending sound by hand, so every TikTok post must be set to **Notify Me** (Buffer sends his phone a reminder at post time and he publishes it from the TikTok app). Instagram (Reels) is Notify Me too. After scheduling the week, for each TikTok post in the queue: reload `https://publish.buffer.com/all-channels`, then run `tools/notify_me.js` with `__I__` replaced by the post's index among the "Edit post" buttons (0-based, in queue order). It opens that post, skips posts already on Notify Me, switches it from Automatic to Notify Me and saves. Reload before every post: after an editor closes, Buffer won't open the next one until the page reloads. Do the same for each Instagram Reel (same script). Finish by checking every post of the week shows Notify Me.

After the last post, reload the queue and check that every card for the week has a caption and the right slide count. Buffer shows times in the computer's clock (Pacific), so 7:00 PM Arizona can show as 6:00 PM. That is correct.

## 5. Report

Send Leroy one short message: each day's hook with its song suggestion (he adds the sound to each TikTok post when Buffer's Notify Me reminder arrives, and can add music to the Instagram post after it goes live), anything you had to fix, anything that failed. No em dashes. If the computer or the browser was unreachable, still do steps 1 to 3, say so plainly, and tell him the posts are ready in GitHub.

## 6. Update the scoreboard (every run, after scheduling)

Dashboard: `https://claude.ai/artifact/8brXkXrDXw76Kqt6LMft2U` (a Dashboard artifact). Its data lives in three JSON files the page reads, one row object per line of data. Never invent or estimate a number: if you can't read a value, leave that row out and say so in the report.

| Dataset id | Rows | Where to read it |
| --- | --- | --- |
| `sales` | `{date, product, units, gross_usd, net_usd}`, one per day per product with sales. `product` is exactly `8-Week Plan` or `Bedtime Lift` | Gumroad, signed in in the built-in browser: the Sales or Customers pages at gumroad.com. Net = what Gumroad says you keep after fees |
| `social` | `{date, platform, followers, views_7d, likes_7d, saves_7d, comments_7d, shares_7d, profile_visits_7d}`, one per app per run. `platform` is `Instagram` or `TikTok`. `date` is today | Buffer's analytics for each channel if the plan shows it; else the public profile pages (instagram.com/dumbbelldadsclub, tiktok.com/@dumbbelldadsclub) for followers, and leave the 7-day fields out if you can't see them |
| `posts` | `{date, platform, hook, views, likes, saves, comments, shares}`, one per published post per app, numbers to date | Buffer's Sent posts with their stats; else the app's public post pages. `hook` is the first caption line |

To update each file:
1. `ArtifactData get` collection `datasets`, doc id `<id>`: note its `version` and `source.url` (`/_blob/<asset id>`).
2. `Artifact read` with that url's asset id as `path` to get the current rows.
3. Merge: `sales` add only days not already there; `social` append today's rows; `posts` replace each post's row by `date`+`platform` with the new numbers.
4. Write the full array to `<id>.json` and upload it: `Artifact publish` with the dashboard `url`, `file_path`, `asset: true` (one JSON per call).
5. `ArtifactData update` doc `datasets/<id>` with `if_version`, setting `source.url` to the new `/_blob/...`, `source.name`, and `updated: {at: <now ISO>, by: "Weekly agent"}`. Do not touch the page file.

Add one line to the report: plan sales to date, net revenue, followers per app.
