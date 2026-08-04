# Notion — Source Index

> **Last Updated:** 2026-08-03

This skill is a distilled operating layer over Notion's public developer documentation. Facts and endpoint names in this skill are grounded in the sources below; refresh this index when Notion ships API changes.

| Topic | Source | URL |
|---|---|---|
| API reference (endpoints, versioning) | Notion API reference | https://developers.notion.com/reference |
| Versioning and the `Notion-Version` header | API versioning | https://developers.notion.com/reference/versioning |
| Authentication and integration tokens | Authorization | https://developers.notion.com/reference/authorization |
| Pages (retrieve, create, update) | Page endpoints | https://developers.notion.com/reference/patch-page |
| Database queries and filters | Query a database | https://developers.notion.com/reference/post-database-query |
| Search | Search endpoint | https://developers.notion.com/reference/post-search |
| Property types and values | Property value objects | https://developers.notion.com/reference/property-value-object |

## Refresh procedure

- Re-check the API reference when a call returns `validation_error` for a documented body shape or when `Notion-Version` deprecations are announced.
- The `Notion-Version` header is a security-adjacent contract pin: before changing the default in `notion-cli`, verify the new version's property object shapes in the versioning page.
- Update `research_checked` in `SKILL.md` frontmatter and this file's `Last Updated` when you verify the sources again.
