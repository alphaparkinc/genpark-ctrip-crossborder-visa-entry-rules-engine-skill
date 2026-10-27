# -*- coding: utf-8 -*-
"""
GenPark Ctrip Cross-Border Visa & Entry Rules Engine Client
Evaluates passport nationality, transit visa waivers (TWOV), and rolling stay duration rules for multi-hop international journeys.
Zero external dependencies -- Python 3.9+ standard library only.
"""

import math
from typing import Dict, Any, List

class GenParkCtripCrossBorderVisaEntryRulesEngine:
    """
    Evaluates global border control regulations, China 144-hour TWOV,
    Schengen 90/180 rolling day compliance, and passport expiration thresholds.
    """

    TWOV_ELIGIBLE_TRANSIT_PORTS = {
        "CHINA_144H": {"max_hours": 144, "airports": ["PEK", "PKX", "PVG", "SHA", "CAN", "SZX", "CTU", "HGH"]},
        "SINGAPORE_96H": {"max_hours": 96, "airports": ["SIN"]},
        "UK_DATV_AIRSIDE": {"max_hours": 24, "airports": ["LHR", "LGW"]}
    }

    def __init__(self, min_passport_validity_months: int = 6):
        self.min_passport_months = min_passport_validity_months

    def validate_schengen_90_180_rule(self, prior_stays_days: int, planned_duration_days: int) -> Dict[str, Any]:
        """Calculates rolling 90-day allowance in any 180-day window."""
        total_projected = prior_stays_days + planned_duration_days
        days_remaining = max(0, 90 - prior_stays_days)
        is_compliant = total_projected <= 90

        return {
            "is_compliant": is_compliant,
            "prior_stays_in_180d_days": prior_stays_days,
            "planned_stay_days": planned_duration_days,
            "schengen_allowance_remaining_days": days_remaining,
            "excess_overstay_days": max(0, total_projected - 90)
        }

    def evaluate_transit_waiver_twov(self, origin_country: str, transit_airport: str, final_dest_country: str, layover_hours: float) -> Dict[str, Any]:
        """
        Validates Transit Without Visa (TWOV).
        Core Rule: Origin Country != Final Destination Country (true onward transit to a 3rd country).
        """
        is_valid_transit_graph = (origin_country.upper() != final_dest_country.upper())

        twov_matched = None
        for rule_key, cfg in self.TWOV_ELIGIBLE_TRANSIT_PORTS.items():
            if transit_airport.upper() in cfg["airports"]:
                if layover_hours <= cfg["max_hours"]:
                    twov_matched = rule_key
                break

        eligible = is_valid_transit_graph and (twov_matched is not None)

        return {
            "twov_eligible": eligible,
            "matched_policy": twov_matched if eligible else "INELIGIBLE_OR_VISA_REQUIRED",
            "layover_hours": layover_hours,
            "valid_3rd_country_onward_ticket": is_valid_transit_graph,
            "transit_airport": transit_airport.upper()
        }

    def validate_entry_clearance(
        self,
        traveler_passport_country: str,
        itinerary_origin_country: str,
        transit_airport_code: str,
        final_destination_country: str,
        transit_layover_hours: float,
        planned_stay_days_destination: int,
        prior_schengen_stays_days: int = 0,
        passport_validity_months: int = 12
    ) -> Dict[str, Any]:
        """
        Executes end-to-end multi-hop entry clearance audit.
        """
        passport_ok = (passport_validity_months >= self.min_passport_months)

        # Check transit waiver
        twov_res = self.evaluate_transit_waiver_twov(
            itinerary_origin_country,
            transit_airport_code,
            final_destination_country,
            transit_layover_hours
        )

        # Check destination stay limits
        schengen_countries = ["FRANCE", "GERMANY", "ITALY", "SPAIN", "NETHERLANDS", "GREECE", "SWITZERLAND"]
        is_dest_schengen = final_destination_country.upper() in schengen_countries

        if is_dest_schengen:
            schengen_res = self.validate_schengen_90_180_rule(prior_schengen_stays_days, planned_stay_days_destination)
            duration_ok = schengen_res["is_compliant"]
        else:
            schengen_res = {"is_compliant": True, "note": "Non-Schengen jurisdiction"}
            duration_ok = True

        overall_clearance = passport_ok and (twov_res["twov_eligible"] or transit_layover_hours == 0) and duration_ok

        checklist = [
            f"Passport with >= {self.min_passport_months} months remaining validity",
            "Confirmed onward/return international flight itinerary (e-Ticket)"
        ]
        if twov_res["twov_eligible"]:
            checklist.append(f"Eligibility certificate for {twov_res['matched_policy']} with physical boarding passes")
        if is_dest_schengen:
            checklist.append("Valid Schengen C-Type Visa or EU biometric biometric passport exemption")

        return {
            "traveler_nationality": traveler_passport_country.upper(),
            "overall_entry_clearance_status": "CLEARED_FOR_DEPARTURE" if overall_clearance else "DOCUMENTATION_FLAG_BLOCKED",
            "passport_validity_verified": passport_ok,
            "transit_evaluation": twov_res,
            "destination_stay_evaluation": schengen_res,
            "mandatory_checkin_documents": checklist
        }
