# MSSP Module v1.0.0
Initial MSSP (Mud Server Status Protocol) implementation for NakedMud
### ADDED
- StorageSet-based MSSP configuration with proper data types (string/int/bool)
- Default MSSP config template with auto-creation fallback
- MSSP OLC editor (`msspedit` command) for runtime configuration
- Dynamic MSSP data reloading after config changes
### FEATURES
- Typed StorageSet methods (`readInt`/`storeInt`, `readBool`/`storeBool`)
- Config changes immediately reflect in MSSP protocol responses
- Admin-level permissions required for configuration
- Auto-creates `misc/mssp-config` from `default.mssp` template if missing
- MSSP variable support (CONTACT, WEBSITE, FAMILY, GENRE, etc.)
### INSTALL NOTES
- New installations get default MSSP config automatically
- Use `msspedit` command to configure server information
- All MSSP variables properly typed and validated
