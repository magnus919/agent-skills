# HubSpot CRM — Source Index

> **Last Updated:** 2026-08-03

This skill is a distilled operating layer over HubSpot's public developer documentation. Facts and endpoint names in this skill are grounded in the sources below; refresh this index when HubSpot ships API changes.

| Topic | Source | URL |
|---|---|---|
| CRM object model | Understanding the CRM | https://developers.hubspot.com/docs/api/crm/understanding-the-crm |
| Contacts API | Contacts | https://developers.hubspot.com/docs/api/crm/contacts |
| Deals API | Deals | https://developers.hubspot.com/docs/api/crm/deals |
| Deal pipelines API | Pipelines | https://developers.hubspot.com/docs/api/crm/pipelines |
| Search API | Search | https://developers.hubspot.com/docs/api/crm/search |
| Private apps and scopes | Private apps | https://developers.hubspot.com/docs/api/private-apps |

## Refresh procedure

- Re-check the object model when a 403 or `PROPERTY_DOES_NOT_EXIST` appears for a documented property; HubSpot object schemas evolve.
- Re-check the pipelines API before changing anything in `deals update-stage`; stage IDs are pipeline-scoped.
- Update `research_checked` in `SKILL.md` frontmatter and this file's `Last Updated` when you verify the sources again.
