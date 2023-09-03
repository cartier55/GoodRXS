import json

def build_drug_info_payload(drug, form, dosage):
    payload = {
        "query": """
        query DrugConcept(
            $drug: String, 
            $dosage: String, 
            $form: String, 
            $label: String, 
            $includeRelatedDrugs: Boolean = true, 
            $includeRelatedConditions: Boolean = true) {
            drugConcept: apiV4DrugConcept(
            input: {concept: $drug, dosage: $dosage, form: $form, label: $label}
            ) {
                selected_index
                name
                slug
                description
                titles {
                    name
                    __typename
                }
                subtitles {
                    words {
                        label
                        slug
                        __typename
                    }
                    prefix
                    __typename
                }
                conditions @include(if: $includeRelatedConditions) {
                    name
                    slug
                    __typename
                }
                choices {
                    attributes
                    default_quantity
                    display_info {
                        has_medicare_prices
                        has_drug_info
                        has_side_effects
                        has_images
                        image_count
                        __typename
                    }
                    default_dosage
                    default_form
                    schedule
                    dosage {
                        name
                        slug
                        __typename
                    }
                    form {
                        name
                        slug
                        singular
                        plural
                        __typename
                    }
                    id
                    image {
                        src
                        alt_text
                        width
                        height
                        __typename
                    }
                    image_transparent {
                        src
                        alt_text
                        width
                        height
                        __typename
                    }
                    label {
                        name
                        slug
                        __typename
                    }
                    label_type
                    lifecycle
                    plural_display
                    singular_display
                    quantities
                    __typename
                }
                drug_class {
                    name
                    slug
                    __typename
                }
                similar_drugs @include(if: $includeRelatedDrugs) {
                    name
                    slug
                    __typename
                }
                __typename
            }
        }
        """,
        "variables": {
            "drug": drug,
            "form": form,
            "dosage": dosage,
        }
    }

    # Converting Python dictionary to JSON string
    payload = json.dumps(payload)

    return payload


def build_coupon_payload(drug_id, quantity, pharmacy_id, dosage=None):
    if dosage == None:
        return f'''{{
            "query": "query CouponQuery($drugId: Int!, $quantity: Int, $pharmacyId: Int, $pricingExtras: String, $platform: String, $attributionParams: AWSJSON) {{\\n  coupon: apiV4Coupons(\\n    input: {{drug_id: $drugId, quantity: $quantity, pharmacy_id: $pharmacyId, pricing_extras: $pricingExtras, deliver_to: \\\"\\\", delivery_method: RESPONSE, marketing_opt_in: false, platform: $platform, attribution_params: $attributionParams}}\\n  ) {{\\n    coupon_id\\n    adjudication_info {{\\n      member_id\\n      group_id\\n      bin\\n      pcn\\n      __typename\\n    }}\\n    pharmacy {{\\n      name\\n      __typename\\n    }}\\n    flags\\n    drug {{\\n      name\\n      dosage\\n      form_display\\n      slug\\n      __typename\\n    }}\\n    prices {{\\n      price\\n      display\\n      __typename\\n    }}\\n    all_prices {{\\n      type\\n      price\\n      _network\\n      pos_discounts {{\\n        final_price\\n        discount_campaign_name\\n        original_price\\n        __typename\\n      }}\\n      __typename\\n    }}\\n    information {{\\n      customer_phone\\n      pharmacist_phone\\n      disclaimers {{\\n        title\\n        copy\\n        __typename\\n      }}\\n      faqs {{\\n        question\\n        answer\\n        __typename\\n      }}\\n      help {{\\n        customer {{\\n          body\\n          links {{\\n            text\\n            url\\n            __typename\\n          }}\\n          title\\n          __typename\\n        }}\\n        pharmacist {{\\n          body\\n          links {{\\n            text\\n            url\\n            __typename\\n          }}\\n          title\\n          __typename\\n        }}\\n        title\\n        __typename\\n      }}\\n      policies {{\\n        title\\n        body\\n        links {{\\n          text\\n          url\\n          __typename\\n        }}\\n        __typename\\n      }}\\n      remember {{\\n        points\\n        title\\n        __typename\\n      }}\\n      message_bar {{\\n        title\\n        body\\n        type\\n        __typename\\n      }}\\n      __typename\\n    }}\\n    _analytics {{\\n      prices {{\\n        price\\n        display\\n        __typename\\n      }}\\n      drug_id\\n      dosage\\n      network\\n      form\\n      metric_quantity\\n      cash_price\\n      pharmacy_detail {{\\n        id\\n        use_discount_noun\\n        name\\n        number_of_locations\\n        has_24hr\\n        alternate_logo\\n        block_cash_price\\n        block_drug_name\\n        block_logo\\n        block_pharmacy_name\\n        closest_location\\n        disclaimer\\n        type\\n        __typename\\n      }}\\n      drug_detail {{\\n        conditions\\n        display\\n        dosage_display\\n        dosage_form_display\\n        dosage_form_display_short\\n        drug_information {{\\n          education_available\\n          side_effects_available\\n          similar_drugs\\n          drug_class\\n          __typename\\n        }}\\n        form_plural\\n        drug_page_type\\n        drug_market_type\\n        quantity\\n        type\\n        form_display\\n        label\\n        is_default\\n        drug_equivalents\\n        drug_display\\n        __typename\\n      }}\\n      price_detail {{\\n        type_display\\n        other_price_data\\n        __typename\\n      }}\\n      __typename\\n    }}\\n    display_noun\\n    pos_discount {{\\n      final_price\\n      discount_campaign_name\\n      expires\\n      expires_at\\n      days_supplies {{\\n        display\\n        final_price\\n        original_price\\n        __typename\\n      }}\\n      __typename\\n    }}\\n    __typename\\n  }}\\n}}\\n",
            "variables": {{
                "drugId": {drug_id},
                "quantity": {quantity},
                "pharmacyId": {pharmacy_id},
                "platform": "DESKTOP"
            }}
        }}'''
    else:
        return f'''{{
            "query": "query CouponQuery($drugId: Int!, $quantity: Int, $dosage: Int, $pharmacyId: Int, $pricingExtras: String, $platform: String, $attributionParams: AWSJSON) {{\\n  coupon: apiV4Coupons(\\n    input: {{drug_id: $drugId, quantity: $quantity, pharmacy_id: $pharmacyId, pricing_extras: $pricingExtras, deliver_to: \\\"\\\", delivery_method: RESPONSE, marketing_opt_in: false, platform: $platform, attribution_params: $attributionParams}}\\n  ) {{\\n    coupon_id\\n    adjudication_info {{\\n      member_id\\n      group_id\\n      bin\\n      pcn\\n      __typename\\n    }}\\n    pharmacy {{\\n      name\\n      __typename\\n    }}\\n    flags\\n    drug {{\\n      name\\n      dosage\\n      form_display\\n      slug\\n      __typename\\n    }}\\n    prices {{\\n      price\\n      display\\n      __typename\\n    }}\\n    all_prices {{\\n      type\\n      price\\n      _network\\n      pos_discounts {{\\n        final_price\\n        discount_campaign_name\\n        original_price\\n        __typename\\n      }}\\n      __typename\\n    }}\\n    information {{\\n      customer_phone\\n      pharmacist_phone\\n      disclaimers {{\\n        title\\n        copy\\n        __typename\\n      }}\\n      faqs {{\\n        question\\n        answer\\n        __typename\\n      }}\\n      help {{\\n        customer {{\\n          body\\n          links {{\\n            text\\n            url\\n            __typename\\n          }}\\n          title\\n          __typename\\n        }}\\n        pharmacist {{\\n          body\\n          links {{\\n            text\\n            url\\n            __typename\\n          }}\\n          title\\n          __typename\\n        }}\\n        title\\n        __typename\\n      }}\\n      policies {{\\n        title\\n        body\\n        links {{\\n          text\\n          url\\n          __typename\\n        }}\\n        __typename\\n      }}\\n      remember {{\\n        points\\n        title\\n        __typename\\n      }}\\n      message_bar {{\\n        title\\n        body\\n        type\\n        __typename\\n      }}\\n      __typename\\n    }}\\n    _analytics {{\\n      prices {{\\n        price\\n        display\\n        __typename\\n      }}\\n      drug_id\\n      dosage\\n      network\\n      form\\n      metric_quantity\\n      cash_price\\n      pharmacy_detail {{\\n        id\\n        use_discount_noun\\n        name\\n        number_of_locations\\n        has_24hr\\n        alternate_logo\\n        block_cash_price\\n        block_drug_name\\n        block_logo\\n        block_pharmacy_name\\n        closest_location\\n        disclaimer\\n        type\\n        __typename\\n      }}\\n      drug_detail {{\\n        conditions\\n        display\\n        dosage_display\\n        dosage_form_display\\n        dosage_form_display_short\\n        drug_information {{\\n          education_available\\n          side_effects_available\\n          similar_drugs\\n          drug_class\\n          __typename\\n        }}\\n        form_plural\\n        drug_page_type\\n        drug_market_type\\n        quantity\\n        type\\n        form_display\\n        label\\n        is_default\\n        drug_equivalents\\n        drug_display\\n        __typename\\n      }}\\n      price_detail {{\\n        type_display\\n        other_price_data\\n        __typename\\n      }}\\n      __typename\\n    }}\\n    display_noun\\n    pos_discount {{\\n      final_price\\n      discount_campaign_name\\n      expires\\n      expires_at\\n      days_supplies {{\\n        display\\n        final_price\\n        original_price\\n        __typename\\n      }}\\n      __typename\\n    }}\\n    __typename\\n  }}\\n}}\\n",
            "variables": {{
                "attributionParams": "{{}}",
                "drugId": {drug_id},
                "quantity": {quantity},
                "dosage": "{dosage}",
                "pharmacyId": {pharmacy_id},
                "pricingExtras": "L6acCrJp1XvtN2jQPPvgDjF6t9w= AK0T5HsibmV0d29yayI6IG51bGwsICJzZWFyY2hfdGltZSI6IDE2ODk2MzQ5MzYuMDA3NTIwNywgInByaWNlIjogNS44OTIwMjI2MDk3MTA2OTMsICJsYXQiOiAzNS45MTU0ODQsICJsb24iOiAtNzkuMDc4NTM3LCAiZGlzdGFuY2VfbWkiOiA2MCwgInppcF9jb2RlIjogIjI3NTEwIiwgInN0YXRlIjogIk5DIiwgInByaWNlX2ZpbHRlcnMiOiBbImFwcGVuZF90b3Bfc3RhdGVfcGhhcm1hY3kiLCAiaW5jX2NtbyIsICJpbmNfZ21vIiwgImluY2x1ZGVfYmRzX2NvbXB1dGVkX3Bvc19uZXR3b3JrcyIsICJpbmNsdWRlX2VzcngiLCAiaW5jbHVkZV9nb2xkX3ByaWNlcyIsICJpbmNsdWRlX29ubGluZV9jcGMiLCAiaW5jbHVkZV9yZWdpc3RlcmVkX3VzZXJfcHJpY2VzIl0sICJwaGFybV9maWx0ZXJzIjogbnVsbCwgInBvc19jYW1wYWlnbiI6ICIifQ==",
                "platform": "DESKTOP"
            }}
        }}'''


def build_drug_price_query_payload(drugId, drug, quantity):
    payload = {
        "query": """
        query DrugPriceQuery($drug: String!, $drugId: Int!, $quantity: Int, $quantityFloat: Float, $locationType: PricingGetPrices_LocationType, $locationMetroCode: String, $location: String, $sortType: PricingGetPrices_PriceRowSortType, $attributionParams: AWSJSON, $platform: PricingGetPrices_PlatformType, $includePreferredPharmacyPosDiscount: Boolean, $includeDrugNotices: Boolean = true) {
            apiV4Prices(
                input: {attribution_params: $attributionParams, location_type: $locationType, location_metro_code: $locationMetroCode, location: $location, drug_id: $drugId, quantity: $quantityFloat, sort_type: $sortType, platform: $platform, include_preferred_pharmacy_pos_discount: $includePreferredPharmacyPosDiscount}
            ) {
                avg_cash_price
                is_maintenance_drug
                non_nabp_price {
                    min_price
                    max_price
                    url
                    _network
                    pricing_extras
                    pharmacy_id
                    __typename
                }
                results {
                    est_cash_price
                    prices {
                        attestation {
                            text
                            alt_price {
                                url
                                __typename
                            }
                            __typename
                        }
                        display_noun
                        disclaimer
                        price
                        type
                        url
                        _network
                        pos_discounts {
                            coupon_url
                            discount_campaign_name
                            final_price
                            days_supplies {
                                display
                                final_price
                                original_price
                                __typename
                            }
                            __typename
                        }
                        __typename
                    }
                    pharmacy {
                        id
                        name
                        logo
                        type
                        description
                        extras
                        distance_mi
                        popularity_rank
                        __typename
                    }
                    popularity_rank
                    __typename
                }
                __typename
            }
            apiV4DrugNotices(input: {drug_id: $drugId, quantity: $quantity, concept: $drug}) @include(if: $includeDrugNotices) {
                notices {
                    id
                    name
                    title
                    short_desc
                    link {
                        text
                        url
                        __typename
                    }
                    __typename
                }
                tips {
                    name
                    title
                    short_desc
                    long_desc
                    icon_url
                    link {
                        text
                        url
                        __typename
                    }
                    __typename
                }
                warnings {
                    id
                    name
                    title
                    short_desc
                    link {
                        text
                        url
                        __typename
                    }
                    __typename
                }
                __typename
            }
        }
        """,
        "variables": {
            "drugId": drugId,
            "drug": drug,
            "quantity": quantity,
            "quantityFloat": quantity,
            "includeDrugNotices": True,
            "attributionParams": "{}",
            "sortType": "POPULARITY",
            "platform": "DESKTOP",
        }
    }

    # Converting Python dictionary to JSON string
    payload = json.dumps(payload)

    return payload
