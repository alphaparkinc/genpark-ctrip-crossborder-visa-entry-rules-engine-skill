# -*- coding: utf-8 -*-
"""
GenPark Ctrip Cross-Border Visa & Entry Rules Engine MCP Server
Exposes cross-border immigration and transit visa validation tools via JSON-RPC 2.0 over STDIO.
"""

import sys
import json
from client import GenParkCtripCrossBorderVisaEntryRulesEngine

def handle_request(req):
    method = req.get("method")
    req_id = req.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "genpark-ctrip-crossborder-visa-entry-rules-engine", "version": "1.0.0"}
            }
        }
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "validate_entry_clearance",
                        "description": "Evaluates passport nationality, transit visa waivers (TWOV), and rolling stay duration rules for multi-hop international journeys.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "traveler_passport_country": {"type": "string"},
                                "itinerary_origin_country": {"type": "string"},
                                "transit_airport_code": {"type": "string"},
                                "final_destination_country": {"type": "string"},
                                "transit_layover_hours": {"type": "number"},
                                "planned_stay_days_destination": {"type": "integer"},
                                "passport_validity_months": {"type": "integer"}
                            },
                            "required": ["traveler_passport_country", "itinerary_origin_country", "transit_airport_code", "final_destination_country"]
                        }
                    }
                ]
            }
        }
    elif method == "tools/call":
        params = req.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})

        if tool_name == "validate_entry_clearance":
            engine = GenParkCtripCrossBorderVisaEntryRulesEngine()
            res = engine.validate_entry_clearance(
                traveler_passport_country=args.get("traveler_passport_country", "USA"),
                itinerary_origin_country=args.get("itinerary_origin_country", "USA"),
                transit_airport_code=args.get("transit_airport_code", "PVG"),
                final_destination_country=args.get("final_destination_country", "JAPAN"),
                transit_layover_hours=args.get("transit_layover_hours", 48.0),
                planned_stay_days_destination=args.get("planned_stay_days_destination", 14),
                prior_schengen_stays_days=args.get("prior_schengen_stays_days", 0),
                passport_validity_months=args.get("passport_validity_months", 18)
            )
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
            }
        else:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Tool '{tool_name}' not found"}}
    else:
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32600, "message": f"Method '{method}' not supported"}}

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("MCP Server Discovery Test OK")
        e = GenParkCtripCrossBorderVisaEntryRulesEngine()
        test_res = e.validate_entry_clearance("USA", "USA", "PVG", "JAPAN", 36.0, 10)
        print(f"Test Status: {test_res['overall_entry_clearance_status']}")
        return

    for line in sys.stdin:
        if not line.strip(): continue
        try:
            req = json.loads(line)
            resp = handle_request(req)
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(e)}}
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
