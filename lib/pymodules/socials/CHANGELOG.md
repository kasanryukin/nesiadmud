# Socials Module v1.1.0
**Git commits:** Initial..HEAD
### ADDED
- Default socials fallback system - auto-creates `misc/socials` from `default.socials` template if missing
### FIXED
- Social argument parsing for better target and modifier handling
### UPGRADE NOTES
- New installations get default socials automatically, existing installations unchanged

---

# Socials Module v1.0.0
Initial Python-based socials system converted from C
### ADDED
- Python socials system with StorageSet persistence
- OLC social editor (`socedit` command)
- Social command registration and execution
- Support for social messages, targets, modifiers, and positional requirements
