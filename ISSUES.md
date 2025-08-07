KNOWN ISSUES
+-- TRIGGER SYSTEM
  🔴 [SCRIPTS] Prototype script execution stops on first error (could cause half-loaded proto and missing triggers)
  🟡 [DELETION] tdelete doesn't clean up references in prototypes/entities

+-- BUILD SYSTEM  
  🟡 [WARNINGS] Compiler warnings during build (non-critical)

+-- PERFORMANCE
  ⚫ [HEARTBEAT] Heartbeat triggers scan all mobs/objects every 2 seconds O(n) iteration acceptable for typical MUD sizes complex optimization not worth effort

+-- STATUS KEY
  🔴 NOT-FIXED   - Issue remains unresolved
  🟡 PARTIAL     - Issue partially resolved, workarounds exist  
  ⚫ WONT-FIX    - Issue will not be addressed

*Updated: 2025-08-06*
