# Weekly posting agent: runbook

Goal: every week, create next week's 7 Dumbbell Dads Club carousels (Mon to Sun) and schedule them in Buffer for Instagram and TikTok at **7:00 PM America/Phoenix**. Leroy does nothing. You do everything below, then send him a short summary.

Read `BRAND.md` first. It is the brand book: audience, voice, hard rules, pillars, visual rules.

## 1. Plan the week

- Week = the Monday after today through Sunday. Name it by Monday's date, e.g. `2026-11-09`.
- If `posts/week-<monday>.json` already exists, that week was already built. Check the Buffer queue: if all 14 of its posts are there, stop and tell Leroy "Next week is already scheduled." If some are missing, schedule only the missing ones.
- Read every `posts/week-*.json` so you never repeat a topic or hook.
- One post per day:
  - Mon: The Workout (full routine)
  - Tue: Dad Fuel (food rules, swaps, drive-thru, kids' leftovers)
  - Wed: Myth Busting (with a real, checked source)
  - Thu: Dad Life (time hacks, bedtime or nap-time training)
  - Fri: The Workout (different equipment angle: one dumbbell, two light, core, mobility)
  - Sat: Myth Busting or Dad Fuel
  - Sun: weekly reset plus the call to action: the 8-week plan and the free Bedtime Lift are at the link in the Instagram bio. Never ask people to comment a keyword; there is no auto-DM.
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

After the last post, reload the queue and check that every card for the week has a caption and the right slide count. Buffer shows times in the computer's clock (Pacific), so 7:00 PM Arizona can show as 6:00 PM. That is correct.

## 5. Report

Send Leroy one short message: each day's hook with its song suggestion (he adds music to the Instagram post by hand after it goes live), anything you had to fix, anything that failed. No em dashes. If the computer or the browser was unreachable, still do steps 1 to 3, say so plainly, and tell him the posts are ready in GitHub.
