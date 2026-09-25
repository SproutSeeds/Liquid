# Local configuration

Liquid loads nonsecret defaults from `settings.example.json`. Personal settings
are saved in the ignored `settings.json` file with owner-only permissions on
systems that support Unix file modes. API key fields are masked in the UI.

You can also supply `FRED_API_KEY` and `TRADERMADE_API_KEY` through your process
environment. Environment values take precedence over saved settings and are not
copied into the settings file by a settings save.

Keep local settings and runtime logs out of commits and release bundles. The
application does not log API key values. Previously committed keys remain in Git
history and must be revoked at their providers; removing files from the current
branch does not revoke credentials.
