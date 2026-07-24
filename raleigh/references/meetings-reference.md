# eSCRIBE Public Meetings Reference

Raleigh publishes public meeting information through its eSCRIBE publication site.

## Base URL

```text
https://pub-raleighnc.escribemeetings.com/
```

The meeting listing is available at:

```text
https://pub-raleighnc.escribemeetings.com/?MeetingViewId=2
```

The City links to this site from its agendas and minutes page.

## Meeting Detail

```text
https://pub-raleighnc.escribemeetings.com/Meeting.aspx?Id={id}&lang=English
```

Historical meetings are loaded by the site's own read-only page method:

```text
POST /MeetingsCalendarView.aspx/PastMeetings?MeetingViewId=2&Year={year}
{"type": "{meeting type}", "pageNumber": 1}
```

The adapter discovers meeting types from the public listing, follows the
reported pagination count with a fixed page ceiling, and normalizes the result.

## Parser Strategy

The adapter parses server-rendered HTML for:

- Meeting ID and canonical URL
- Body/committee
- Date, time, and location
- Agenda, agenda package, and minutes links
- Video or stream links

## Notes

- This is an HTML scraper, not a documented JSON API.
- Parser failures are explicit rather than silently incomplete.
- Document downloads are performed only when requested.
- Historical pagination has a fixed per-type page ceiling.
- The legacy Legistar site is not used as a fallback.
