# Entities Module v1.0.0
Initial entity configuration system for NakedMud
**Requires NakedMud 4.3.0 or higher** (includes modifications to `body.c` for dynamic list support).

### ADDED
- Nested class architecture with `RaceConfig`, `BodyConfig`, `Race`, and `BodyPosition` classes
- StorageSet-based entity configuration with clean separate storage files
- Entity OLC editor (`entityconfig` command) for runtime configuration
- Comprehensive race management with body templates and PC flags
- Support for custom body position types and body sizes beyond C definitions
### FEATURES
- Race categories: complete race definitions with body templates, PC flags, and size assignments
- Body configuration: custom body position types (hands, legs, feet, wings, hooves) and sizes (gigantic)
- Auto-creates `misc/entities-race-config` and `misc/entities-body-config` with sensible defaults if missing
- Save confirmation on OLC exit following NakedMud patterns
- Full backward compatibility with existing race and body configuration code
- Python scripting integration for dynamic race and body management
### API
- Retrieval functions: `get_race_config()`, `get_body_config()`, `get_entity_config()`, etc.
- Modification functions: `add_race()`, `remove_race()`, race body position management, etc.
- Validation functions: race existence checks, body position type validation, etc.
- Direct access to nested configuration objects for advanced usage
### INSTALL NOTES
- New installations get default entity configuration with sample races automatically
- Use `entityconfig` command to customize races, body types, and body sizes
- Configuration changes immediately available to scripts and world system
- Integrates with NakedMud's world system for race and body position registration
