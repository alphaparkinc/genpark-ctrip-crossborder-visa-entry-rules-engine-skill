# -*- coding: utf-8 -*-
"""
Example usage of GenParkCtripCrossBorderVisaEntryRulesEngine
Demonstrates international transit visa exemption (China 144h TWOV) and Schengen rolling window checks.
"""

from client import GenParkCtripCrossBorderVisaEntryRulesEngine

def main():
    engine = GenParkCtripCrossBorderVisaEntryRulesEngine()

    cases = [
        {
            "name": "Case A: USA traveler transiting Shanghai (PVG) to Tokyo (China 144h TWOV)",
            "passport": "USA", "origin": "USA", "transit": "PVG", "dest": "JAPAN", "layover": 52.0, "dest_stay": 10, "schengen_prior": 0, "pass_m": 24
        },
        {
            "name": "Case B: Traveler exceeding 90-day Schengen allowance in Italy",
            "passport": "AUSTRALIA", "origin": "AUSTRALIA", "transit": "SIN", "dest": "ITALY", "layover": 8.0, "dest_stay": 25, "schengen_prior": 75, "pass_m": 8
        }
    ]

    print("================================================================")
    print("GenPark Ctrip Cross-Border Visa Rules Engine - Live Runs")
    print("================================================================\n")

    for c in cases:
        res = engine.validate_entry_clearance(
            traveler_passport_country=c["passport"],
            itinerary_origin_country=c["origin"],
            transit_airport_code=c["transit"],
            final_destination_country=c["dest"],
            transit_layover_hours=c["layover"],
            planned_stay_days_destination=c["dest_stay"],
            prior_schengen_stays_days=c["schengen_prior"],
            passport_validity_months=c["pass_m"]
        )
        print(f"[{c['name']}]")
        print(f"  Clearance Status      : {res['overall_entry_clearance_status']}")
        print(f"  Passport Valid Check  : {res['passport_validity_verified']}")
        print(f"  Transit Waiver (TWOV) : {res['transit_evaluation']['matched_policy']} (Eligible: {res['transit_evaluation']['twov_eligible']})")
        print(f"  Mandatory Checklist   :")
        for doc in res["mandatory_checkin_documents"]:
            print(f"    * {doc}")
        print()

if __name__ == "__main__":
    main()
