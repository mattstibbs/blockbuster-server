# Release Notes
1.16.0 / 11-Aug-2014
---
Loads of stuff!

1.13.0 / 16-Jun-2014
---
Added features

- Log to console when messages are suppressed by the time restrictions
- New mobile numbers will be asked to register before they can use the service

1.12.0 / 6-Jun-2014
---
Added features

- Change wording on some response texts
- Only send SMS messages between 08:00 and 20:00

1.11.0 / 4-Jun-2014
---
Added features

- BlockBuster can now send Email notifications via SMTP!

1.10.0 / 3-Jun-2014
---
Added features

- Remaining SMS responses are sent via spsms
- WHOIS responses are logged in the Transaction Log
- Landline numbers are included in MOVE response messages


1.9.2 / 3-Jun-2014
---
Fixed Bugs

- 774 Error when processing a single 'MOVE' command


1.9.1 / 3-Jun-2014
---
Fixed Bugs


- 769 Error when supplying multiple registrations with spaces in the middle


1.9.0 / 2-Jun-2014
-------------------------------------------------------
Added features


- Can use the 'Pushover' service to send Push notifications to users.


1.8.1 / 1-Jun-2014
----------------------------------------------------------
Added features

- You can now send a single '.' to get your current block status (both as blockee and blocker).
- Ability to reply with OK to a move message to confirm acknowledge that you've received the request.
- Add analytics triggers to all functions.


1.8 / 31-May-2014
----------------------------------------------------------
Added features

- BLOCK command accepts multiple registrations
- Packages can now be automatically installed when deploying a new instance of the application.


v1.6 / 28-May-2014
----------------------------------------------------------
Added features

- Replying 'MOVE' without a registration specified will request all blockers to move their cars


v1.5 / 20-May-2014
----------------------------------------------------------
Added features

- User can reply 'UNBLOCK' without a registration specified to remove all active BLOCK sessions


v1.4 / 8-May-2014
----------------------------------------------------------
Added features

- Block is removed from database when UNBLOCK command used
- Can start app with --v parameter for verbose logging
- User can send single letter commands for BLOCK, MOVE, and UNBLOCK (e.g. 'B AB12 4FH' instead of 'BLOCK AB12 4FH')


v1.3 / 7-May-2014
----------------------------------------------------------
Added features

- User can reply 'MOVE' to a block notification to request the blockER moves their car


v1.2 / 6-May-2014
----------------------------------------------------------
Added features

- Include REGNo in response to me saying I am being blocked in


v1.1 / 3-May-2014
----------------------------------------------------------
Added features

- Store a FeatureUsage record every time a merge of a split number plate is done
- Separate DAL out from main code to set codebase up for switching persistence providers

Fixed Bugs

- Transactions are not being recorded with correct originator / recipient names.


v1.0 / 1-May-2014
----------------------------------------------------------
Added features

- User can send UNBLOCK to notify people that they are no longer blocked in
- Support registration numbers with spaces in them for people who don't read instructions :)
- Store the office name against registration records to identify which office the car was registered at
- Store requests and responses in logs
- Re-order list of registrations so that it's sorted by Surname rather than Mobile
