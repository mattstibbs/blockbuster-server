# BlockBuster API Guide

Note all api paths are relative to:

	'https://www.dns.name/api'
	
### GET /status/{mobile}
{mobile} takes a full mobile number as a String e.g.

	/status/+447793885600
	
Returns a JSON document containing current blocks:
	
	{
		"blocks_as_blockee": [
			{
				 "blocker": "+447793885600", // Blocker's number
				 "blockee": "+447980895859", // Your number
				 "blocked_reg": "GF06UMY" // Your reg
			}
		],
		"blocks_as_blocker": [
			{
				 "blocker": "+447793885600", // Your number
				 "blockee": "+447980895859", // Blocker's number
				 "blocked_reg": "GF06UMY" // Reg you are blocking
			}
		]
	}