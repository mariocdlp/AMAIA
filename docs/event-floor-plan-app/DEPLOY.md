# Publishing the planner on epfiesta.com (HighLevel)

The planner is **one self-contained file** — `prototype.html`, about 205 KB, with fonts, styles and logic all inlined and **no external requests**. That makes it trivially hostable, but HighLevel will not serve an arbitrary `.html` file as a page, so it has to live somewhere else and be embedded.

---

## 1. Put the file on a static host

HighLevel's media library is for assets, not pages, so use a free static host:

**Netlify Drop** — the fastest route. Go to <https://app.netlify.com/drop>, rename the file to `index.html`, drag it onto the page. You get a live URL in seconds. **Cloudflare Pages** works the same way and is equally fine.

Then point a subdomain at it so the URL matches the brand:

1. In Netlify: *Domain settings → Add custom domain →* `plan.epfiesta.com`
2. In your DNS: add a `CNAME` for `plan` pointing at the Netlify address they give you
3. HTTPS is issued automatically

To update the planner later, drag the new file onto the same site. Nothing in HighLevel changes.

---

## 2. Decide how people get access

Open `prototype.html` and edit the `CONFIG` block near the top of the `<script>`:

```js
const CONFIG = {
  accessCodes: [],          // [] = open to everyone
  gateMessage: "Enter your access code to start planning.",
  rememberAccess: true,
};
```

### Option A — gate with the HighLevel page (simplest)

Leave `accessCodes: []` and put the **HighLevel page** inside a membership / client portal product. HighLevel decides who sees the page; the planner just loads. Best when the perk is tied to something people already log in for.

### Option B — access codes (works anywhere)

```js
accessCodes: ["FIESTA26", "VIP-TENT", "WEDDING-JULY"],
```

Now the planner asks for a code. Case, spaces and dashes are ignored, so `fiesta 26` opens `FIESTA26`. Once accepted, that device remembers it and goes straight in next time.

A code can also travel in the URL — this is what makes the embed seamless:

```
https://plan.epfiesta.com/?k=FIESTA26
```

**Grant access** by giving someone a code (or a link carrying it).
**Revoke access** by deleting that code from the list and re-uploading the file. Anyone still holding it is locked out on their next visit.

> **Be clear-eyed about what this is.** An embedded page's URL is visible to anyone who views source, so access codes are *polite gating*, not security — they keep the planner feeling like a perk for your customers, they do not make it impossible to reach. Nothing in the planner is confidential (it is your public price list), so that trade is usually the right one. If you ever need real access control, that means a login in front of it and a small backend, which is a bigger build.

Using **both** options together is a reasonable default: the HighLevel membership does the real gating, and a code in the URL means members never see a prompt.

---

## 3. Embed it in the HighLevel page

Add a **Custom Code / Code** element to the page and paste this. Replace the `src` with your own URL.

```html
<div class="epf-planner">
  <iframe src="https://plan.epfiesta.com/?k=FIESTA26"
          title="Event Floor Planner" loading="lazy" allow="clipboard-write"></iframe>
</div>
<style>
  .epf-planner{max-width:560px;margin:0 auto}
  .epf-planner iframe{width:100%;height:820px;display:block;background:#FAF3E6;
    border:1px solid #E5DDC9;border-radius:16px}
  @media (max-width:600px){
    .epf-planner iframe{height:78svh;min-height:580px;border-radius:12px}
  }
</style>
```

Drop `?k=FIESTA26` if you are using Option A.

**On phones, prefer a link over an embed.** The planner wants the whole screen; in a 356 px-wide iframe it works but is cramped. Put a **"Open the planner"** button on the mobile page linking to `plan.epfiesta.com` directly, and show the embed on desktop only. Opened as a full page on iPhone, customers can also use *Share → Add to Home Screen* and get an app-like icon — the original goal, without the App Store.

---

## 4. Before customers see it

- **"Request this quote" is still a stub.** It shows a confirmation and sends nothing. This is the button that turns a planning session into a lead, so wire it to a HighLevel form, an inbound webhook, or n8n before launch.
- **The header still reads "PROTOTYPE DEMO."**
- **A reload loses the plan** — there is no persistence yet.
- **Prices are hardcoded** in the file, so a price change means re-uploading it.
- **Unpriced items are visible**: dance floors and liners read "price on request", tablecloths quote as included, and partial wall panels use an assumed quarter-of-a-kit rate. See §10 of `PLAN.md`.

---

## Verified

Checked in a real browser, served over HTTP and embedded in an iframe at both desktop and phone widths:

- no external requests — the page is fully self-contained
- characters render correctly (this needed the `<meta charset="utf-8">` fix; without it a web host serves mojibake)
- long-press menus, dragging and the prompt box all work inside the iframe
- "Save image" fires a real download outside the artifact sandbox
- all seven access paths behave: ungated, gate shown, wrong code rejected, sloppy code accepted, device remembered, `?k=` unlock, bad `?k=` still gated
