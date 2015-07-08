# BlockBuster API Guide

Note all api paths are relative to:

	'https://www.dns.name/api/v1.0'

### GET /status/{mobile}
{mobile} takes a full mobile number as a String e.g.

	/status/+447777888999

Returns a JSON document containing current blocks:

	{
		"blocks_as_blockee": [
			{
				 "blocker": "+447777888999", // Blocker's number
				 "blockee": "+447999428437", // Your number
				 "blocked_reg": "GF06UMY" // Your reg
			}
		],
		"blocks_as_blocker": [
			{
				 "blocker": "+447777888999", // Your number
				 "blockee": "+447999428437", // Blocker's number
				 "blocked_reg": "GF06UMY" // Reg you are blocking
			}
		]
	}
