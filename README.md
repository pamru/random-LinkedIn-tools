# random-LinkedIn-tools
dumping grounds

## Invoice template skill

`.claude/skills/invoice-template/` is a Claude Code skill that
generates editable BLANK + SAMPLE invoice PDFs for any service niche
(mechanic, HVAC, pet grooming, plumbing, etc.). Inside this repo it
works automatically.

To use it from any project on your machine, install it globally once:

```bash
mkdir -p ~/.claude/skills
cp -r .claude/skills/invoice-template ~/.claude/skills/
```

Then in any folder, start Claude Code and say e.g. *"make me an HVAC
invoice template"* — the skill walks through the rest. See
`.claude/skills/invoice-template/SKILL.md` for details.

Dependencies: `pip3 install reportlab pymupdf`.
