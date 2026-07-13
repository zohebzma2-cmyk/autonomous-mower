# good-first-issue seeds (create with one command each — public write, so you run it)

```bash
gh issue create --label "good first issue" -t "Add a machine profile for your ZTR (Toro / Bad Boy / Spartan / Scag)" \
  -b "Measure the 6 SECTION-1 dimensions per docs/MEASURE.md (or use the generator at zohebalvi.com/mower) and PR cad/profiles/<your-machine>.scad. CONTRIBUTING.md has the 10-minute walkthrough."

gh issue create --label "good first issue" -t "Port the badge to your mower brand" \
  -b "cad/badge.scad has PRODUCT_NAME as a parameter. PR a photo of your printed nameplate + any text-size tweaks your brand name needed."

gh issue create --label "good first issue" -t "Translate docs/00-BUILD-MANUAL.md" \
  -b "Pick a language, add docs/i18n/<lang>/00-BUILD-MANUAL.md. Safety sections must be translated completely or not at all."

gh issue create --label "good first issue" -t "Try the sim on your OS and report friction" \
  -b "python3 software/companion/app.py --sim — what broke or confused you before the UI loaded? Every papercut you report gets fixed."
```
