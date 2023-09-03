from math import e
import requests
import json
from build_payload import build_coupon_payload, build_drug_info_payload, build_drug_price_query_payload
from pprint import pprint as pp
from helpers import get_case_insensitive


def coupon_query(drugId, quantity, pharmacyId, drug):
    """
    Function to get the coupon prices and available forms for a drug
    """

    url = "https://graph.goodrx.com/"
    print(drugId, quantity, pharmacyId, drug)
    payload = build_coupon_payload(drugId, quantity, pharmacyId)
    # payload = "{\"query\":\"query CouponQuery($drugId: Int!, $quantity: Int, $pharmacyId: Int, $pricingExtras: String, $platform: String, $attributionParams: AWSJSON) {\\n  coupon: apiV4Coupons(\\n    input: {drug_id: $drugId, quantity: $quantity, pharmacy_id: $pharmacyId, pricing_extras: $pricingExtras, deliver_to: \\\"\\\", delivery_method: RESPONSE, marketing_opt_in: false, platform: $platform, attribution_params: $attributionParams}\\n  ) {\\n    coupon_id\\n    adjudication_info {\\n      member_id\\n      group_id\\n      bin\\n      pcn\\n      __typename\\n    }\\n    pharmacy {\\n      name\\n      __typename\\n    }\\n    flags\\n    drug {\\n      name\\n      dosage\\n      form_display\\n      slug\\n      __typename\\n    }\\n    prices {\\n      price\\n      display\\n      __typename\\n    }\\n    all_prices {\\n      type\\n      price\\n      _network\\n      pos_discounts {\\n        final_price\\n        discount_campaign_name\\n        original_price\\n        __typename\\n      }\\n      __typename\\n    }\\n    information {\\n      customer_phone\\n      pharmacist_phone\\n      disclaimers {\\n        title\\n        copy\\n        __typename\\n      }\\n      faqs {\\n        question\\n        answer\\n        __typename\\n      }\\n      help {\\n        customer {\\n          body\\n          links {\\n            text\\n            url\\n            __typename\\n          }\\n          title\\n          __typename\\n        }\\n        pharmacist {\\n          body\\n          links {\\n            text\\n            url\\n            __typename\\n          }\\n          title\\n          __typename\\n        }\\n        title\\n        __typename\\n      }\\n      policies {\\n        title\\n        body\\n        links {\\n          text\\n          url\\n          __typename\\n        }\\n        __typename\\n      }\\n      remember {\\n        points\\n        title\\n        __typename\\n      }\\n      message_bar {\\n        title\\n        body\\n        type\\n        __typename\\n      }\\n      __typename\\n    }\\n    _analytics {\\n      prices {\\n        price\\n        display\\n        __typename\\n      }\\n      drug_id\\n      dosage\\n      network\\n      form\\n      metric_quantity\\n      cash_price\\n      pharmacy_detail {\\n        id\\n        use_discount_noun\\n        name\\n        number_of_locations\\n        has_24hr\\n        alternate_logo\\n        block_cash_price\\n        block_drug_name\\n        block_logo\\n        block_pharmacy_name\\n        closest_location\\n        disclaimer\\n        type\\n        __typename\\n      }\\n      drug_detail {\\n        conditions\\n        display\\n        dosage_display\\n        dosage_form_display\\n        dosage_form_display_short\\n        drug_information {\\n          education_available\\n          side_effects_available\\n          similar_drugs\\n          drug_class\\n          __typename\\n        }\\n        form_plural\\n        drug_page_type\\n        drug_market_type\\n        quantity\\n        type\\n        form_display\\n        label\\n        is_default\\n        drug_equivalents\\n        drug_display\\n        __typename\\n      }\\n      price_detail {\\n        type_display\\n        other_price_data\\n        __typename\\n      }\\n      __typename\\n    }\\n    display_noun\\n    pos_discount {\\n      final_price\\n      discount_campaign_name\\n      expires\\n      expires_at\\n      days_supplies {\\n        display\\n        final_price\\n        original_price\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n\",\"variables\":{\"drugId\":42521,\"quantity\":90,\"pharmacyId\":85327,\"platform\":\"DESKTOP\"}}"

    # payload = "{\"query\":\"query CouponQuery($drugId: Int!, $quantity: Int, $pharmacyId: Int, $pricingExtras: String, $platform: String, $attributionParams: AWSJSON) {\\n  coupon: apiV4Coupons(\\n    input: {drug_id: $drugId, quantity: $quantity, pharmacy_id: $pharmacyId, pricing_extras: $pricingExtras, deliver_to: \\\"\\\", delivery_method: RESPONSE, marketing_opt_in: false, platform: $platform, attribution_params: $attributionParams}\\n  ) {\\n    coupon_id\\n    adjudication_info {\\n      member_id\\n      group_id\\n      bin\\n      pcn\\n      __typename\\n    }\\n    pharmacy {\\n      name\\n      __typename\\n    }\\n    flags\\n    drug {\\n      name\\n      dosage\\n      form_display\\n      slug\\n      __typename\\n    }\\n    prices {\\n      price\\n      display\\n      __typename\\n    }\\n    all_prices {\\n      type\\n      price\\n      _network\\n      pos_discounts {\\n        final_price\\n        discount_campaign_name\\n        original_price\\n        __typename\\n      }\\n      __typename\\n    }\\n    information {\\n      customer_phone\\n      pharmacist_phone\\n      disclaimers {\\n        title\\n        copy\\n        __typename\\n      }\\n      faqs {\\n        question\\n        answer\\n        __typename\\n      }\\n      help {\\n        customer {\\n          body\\n          links {\\n            text\\n            url\\n            __typename\\n          }\\n          title\\n          __typename\\n        }\\n        pharmacist {\\n          body\\n          links {\\n            text\\n            url\\n            __typename\\n          }\\n          title\\n          __typename\\n        }\\n        title\\n        __typename\\n      }\\n      policies {\\n        title\\n        body\\n        links {\\n          text\\n          url\\n          __typename\\n        }\\n        __typename\\n      }\\n      remember {\\n        points\\n        title\\n        __typename\\n      }\\n      message_bar {\\n        title\\n        body\\n        type\\n        __typename\\n      }\\n      __typename\\n    }\\n    _analytics {\\n      prices {\\n        price\\n        display\\n        __typename\\n      }\\n      drug_id\\n      dosage\\n      network\\n      form\\n      metric_quantity\\n      cash_price\\n      pharmacy_detail {\\n        id\\n        use_discount_noun\\n        name\\n        number_of_locations\\n        has_24hr\\n        alternate_logo\\n        block_cash_price\\n        block_drug_name\\n        block_logo\\n        block_pharmacy_name\\n        closest_location\\n        disclaimer\\n        type\\n        __typename\\n      }\\n      drug_detail {\\n        conditions\\n        display\\n        dosage_display\\n        dosage_form_display\\n        dosage_form_display_short\\n        drug_information {\\n          education_available\\n          side_effects_available\\n          similar_drugs\\n          drug_class\\n          __typename\\n        }\\n        form_plural\\n        drug_page_type\\n        drug_market_type\\n        quantity\\n        type\\n        form_display\\n        label\\n        is_default\\n        drug_equivalents\\n        drug_display\\n        __typename\\n      }\\n      price_detail {\\n        type_display\\n        other_price_data\\n        __typename\\n      }\\n      __typename\\n    }\\n    display_noun\\n    pos_discount {\\n      final_price\\n      discount_campaign_name\\n      expires\\n      expires_at\\n      days_supplies {\\n        display\\n        final_price\\n        original_price\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n\",\"variables\":{\"attributionParams\":\"{}\",\"drugId\":6769,\"quantity\":30,\"pharmacyId\":2,\"pricingExtras\":\"L6acCrJp1XvtN2jQPPvgDjF6t9w= AK0T5HsibmV0d29yayI6IG51bGwsICJzZWFyY2hfdGltZSI6IDE2ODk2MzQ5MzYuMDA3NTIwNywgInByaWNlIjogNS44OTIwMjI2MDk3MTA2OTMsICJsYXQiOiAzNS45MTU0ODQsICJsb24iOiAtNzkuMDc4NTM3LCAiZGlzdGFuY2VfbWkiOiA2MCwgInppcF9jb2RlIjogIjI3NTEwIiwgInN0YXRlIjogIk5DIiwgInByaWNlX2ZpbHRlcnMiOiBbImFwcGVuZF90b3Bfc3RhdGVfcGhhcm1hY3kiLCAiaW5jX2NtbyIsICJpbmNfZ21vIiwgImluY2x1ZGVfYmRzX2NvbXB1dGVkX3Bvc19uZXR3b3JrcyIsICJpbmNsdWRlX2VzcngiLCAiaW5jbHVkZV9nb2xkX3ByaWNlcyIsICJpbmNsdWRlX29ubGluZV9jcGMiLCAiaW5jbHVkZV9yZWdpc3RlcmVkX3VzZXJfcHJpY2VzIl0sICJwaGFybV9maWx0ZXJzIjogbnVsbCwgInBvc19jYW1wYWlnbiI6ICIifQ==\",\"platform\":\"DESKTOP\"}}"

    headers = {
        'authority': 'graph.goodrx.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'apollographql-client-name': 'cwf-client',
        'content-type': 'application/json',
        'goodrx-profile-id': '20918741-0384-4152-bdfc-bcd2ec8d65c4',
        'goodrx-user-id': '64608b1338484ad5828a9b46f7271457',
        'grx-api-client-id': '7c8a864d-21fb-4d14-b243-d7546e9e6cb3',
        'origin': 'https://www.goodrx.com',
        'referer': 'https://www.goodrx.com/',
        'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'x-api-key': 'da2-wrma2xicjjhk7fyokpf3r7nimm',
        'Cookie': 'c=; client=; external_attribution_id=; gclid=; grx_unique_id=9f979cedce264f0fbb76e858c299501f; kw=; optimizelyEndUserId=9f979cedce264f0fbb76e858c299501f; _pxhd=ugNrkZxcZuB-8rwy65CvyBVj0xJaFBLY5MgQPw/KWjC0s2BEnvcipnhz8u3Z6V9egPFdly3jOTPJZ6L4-Jc81g==:OtI6m4MCg/GwhOK2OcDDMqriEpPw3RqByTRD-/pJvYRdnDbtrZts9MhoUdY8APBsfxkBhczXZXjkVDkgotp-r8QhCdctFuoFQ3HYGbycQhk='
    }

    # headers = {
    #     'authority': 'graph.goodrx.com',
    #     'accept': '*/*',
    #     'accept-language': 'en-US,en;q=0.9',
    #     'apollographql-client-name': 'cwf-client',
    #     'content-type': 'application/json',
    #     'goodrx-profile-id': '20918741-0384-4152-bdfc-bcd2ec8d65c4',
    #     'goodrx-user-id': '64608b1338484ad5828a9b46f7271457',
    #     'grx-api-client-id': '7c8a864d-21fb-4d14-b243-d7546e9e6cb3',
    #     'origin': 'https://www.goodrx.com',
    #     'referer': 'https://www.goodrx.com/',
    #     'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    #     'sec-ch-ua-mobile': '?0',
    #     'sec-ch-ua-platform': '"Windows"',
    #     'sec-fetch-dest': 'empty',
    #     'sec-fetch-mode': 'cors',
    #     'sec-fetch-site': 'same-site',
    #     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    #     'x-api-key': 'da2-wrma2xicjjhk7fyokpf3r7nimm',
    #     # 'Cookie': 'c=; client=; external_attribution_id=; gclid=; grx_sa=false; grx_unique_id=9f979cedce264f0fbb76e858c299501f; kw=; optimizelyEndUserId=9f979cedce264f0fbb76e858c299501f; _pxhd=PTN7uWD6et7j286zdlfcBu6cfIiOo9I4FW5eqYcsCP/2YCPqyNGYqNRak58V5EY-UaCF2DanyhQL98cycC8iIA==:X-hqESSdIUMrZRhtXtgAsZJEyaQeZVqKyGF2lI0m089wIof6dx26QvORABAfHwhNLd2ckyUNmDjs-YbzhVvMi0dv77/lqon/TN6GJTgh8fY='
    #     'Cookie': 'c=; client=; external_attribution_id=; gclid=; grx_unique_id=9f979cedce264f0fbb76e858c299501f; kw=; optimizelyEndUserId=9f979cedce264f0fbb76e858c299501f; _pxhd=ugNrkZxcZuB-8rwy65CvyBVj0xJaFBLY5MgQPw/KWjC0s2BEnvcipnhz8u3Z6V9egPFdly3jOTPJZ6L4-Jc81g==:OtI6m4MCg/GwhOK2OcDDMqriEpPw3RqByTRD-/pJvYRdnDbtrZts9MhoUdY8APBsfxkBhczXZXjkVDkgotp-r8QhCdctFuoFQ3HYGbycQhk='
    # }

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.status_code)
    resp = json.loads(response.text)
    # pp(resp)
    coupon = resp.get('data').get('coupon')
    # drug_eq = json.loads(coupon.get('_analytics').get('drug_detail').get('drug_equivalents'))
    # print(drug_eq.keys())
    # print(drug_eq.get('ADHAnsia XR'))
    # pp(drug_eq)
    # print(drug)
    # price = [el for el in coupon.get('all_prices') if el.get('type') == 'COUPON']
    # pharmacy = coupon.get('_analytics').get('pharmacy_detail').get('name')
    # dosage = coupon.get('_analytics').get('dosage')
    try:
        adj_info = coupon.get('adjudication_info')
        del adj_info['__typename']
        del adj_info['member_id']
    except AttributeError:
        print('no adjudication info')
        adj_info = {'group_id': '', 'bin': '', 'pcn': ''}
    # deafult_form = get_case_insensitive(drug_eq, drug).get('default_form')
    # forms = get_case_insensitive(drug_eq, drug).get('forms')
    # print('-------------------------------------------------------')
    # pp(forms)
    return [{
        'drug_name': drug,
        'drug_id': drugId,
        'qty': quantity,
        'pharmacy_id': pharmacyId,
        **adj_info,
    }]

    # return resp.get('data').get('coupon').get('_analytics').get('drug_id'), drug_eq.get('Advil').get('form_sort')


# print(coupon_query(6769, 30, 2))
# print(coupon_query(43739, 55, 2))
# coupon_query(43741, 55, 3, 'ADHAnsia XR')
# print(coupon_query(43739, 30, 2, 'ADHAnsia XR'))
# coupon_query(6769, 30, 3, 'Advil' )
# coupon_query(45735, 30, 3, 'afinitor' )
# print(coupon_query(44410, 40, 3, 'everolimus' ))
# pp(coupon_query(42521, 90, 85327, 'abacavir/lamivudine' ))
# pp(coupon_query(42521, 90, 85327, 'Abbott Freestyle'))


def get_drug_info(drug, form=None, dosage=None):
    """
    This function retrieves detailed information about a specific drug from the GoodRx database.

    Args:
        drug (str): Name of the drug.
        form (str, optional): The form of the drug (e.g. tablet, capsule). Defaults to None.
        dosage (str, optional): The dosage of the drug. Defaults to None.

    Returns:
        dict: A dictionary with the drug's id, class, sub_name, schedule, and description.
    """

    # Base URL for the GoodRx database
    url = "https://graph.goodrx.com/"

    # Create the payload to be sent in the request using the provided drug name, form and dosage
    payload = build_drug_info_payload(drug, form, dosage)

    # Headers required for the request to the GoodRx database
    headers = {
        'authority': 'graph.goodrx.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'apollographql-client-name': 'cwf-client',
        'content-type': 'application/json',
        'goodrx-profile-id': '20918741-0384-4152-bdfc-bcd2ec8d65c4',
        'goodrx-user-id': '64608b1338484ad5828a9b46f7271457',
        'grx-api-client-id': '7c8a864d-21fb-4d14-b243-d7546e9e6cb3',
        'origin': 'https://www.goodrx.com',
        'referer': 'https://www.goodrx.com/',
        'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'x-api-key': 'da2-wrma2xicjjhk7fyokpf3r7nimm',
        # 'Cookie': 'c=; client=; external_attribution_id=; gclid=; grx_sa=false; grx_unique_id=9f979cedce264f0fbb76e858c299501f; kw=; optimizelyEndUserId=9f979cedce264f0fbb76e858c299501f; _pxhd=5L7Vn2RtE5i1BktFgZ3rqP9vcIr1DOyKzVLR5OLAHXC4DnBunJm2kSgjDiUgO/Htdhpf-IduvrkS8geYsWpLkQ==:KlJBfla8pqechsJGijq--0sPBteZJL9WzCVtDOXbT/oW1GdZrhwGrFNNoHaM8uVW1-EnPiAKgGyr5jbaEEuBQjew8VGS/5kOfl7yA2wbDsc='
        'Cookie': 'c=; client=; external_attribution_id=; gclid=; grx_sa=false; grx_unique_id=9f979cedce264f0fbb76e858c299501f; kw=; optimizelyEndUserId=9f979cedce264f0fbb76e858c299501f; _pxhd=G450Jen8NohHPEsAhPHPHFptecJ/s3h4dLr27imOoRxbFXmLeu8Ow8yZZ0Z6Np0hszdBfoaHhDvVoJuf4JnXVA==:CxIlCJHtBcr-TI0ToiWTv2F20A0MOgJhRSxRkjyAncnJ3Kyw9/pVarlKMyROc/6u3Nc1m15TiNM56OUmngAH/zD24ZmBdI1Atv-HX8TZiII='
    }

    # Make a POST request to the GoodRx database with the headers and payload
    response = requests.request("POST", url, headers=headers, data=payload)

    # If the response status code is not 200 (OK), print the status code
    if response.status_code != 200:
        print(response.status_code)

    # Load the JSON response into a Python dictionary
    resp = json.loads(response.text)

    if resp.get('errors'):
        errors = resp.get('errors')
        for error in errors:
            return error.get('message')
        
    # Extract relevant drug information from the response
    index = resp.get('data').get('drugConcept').get('selected_index')
    desc = resp.get('data').get('drugConcept').get('description')
    selected_drug = resp.get('data').get('drugConcept').get('choices')[index]

    image_url = None
    # print(selected_drug.get('display_info'))
    if selected_drug.get('display_info'):
        display_info = selected_drug.get('display_info')
        if display_info.get('has_images'):
            image_url = selected_drug.get('image_transparent').get('src')
    # Extract sub_name, drug_class, selected_dosage, selected_form. If any of these are not present, set them to None.
    try:
        sub_name = resp.get('data').get('drugConcept').get(
            'subtitles').get('words')[0].get('label')
    except AttributeError:
        sub_name = None
    try:
        drug_class = resp.get('data').get(
            'drugConcept').get('drug_class').get('name')
    except AttributeError:
        drug_class = None
    try:
        selected_dosage = selected_drug.get('dosage').get('name')
    except AttributeError:
        selected_dosage = None
    try:
        selected_form = selected_drug.get('form').get('name')
    except AttributeError:
        selected_form = None

    # Extract other relevant information from the selected drug
    drug_id = selected_drug.get('id')
    schedule = selected_drug.get('schedule')

    # Return a dictionary with the retrieved drug information
    return {
        'drug_id': drug_id,
        'drug_class': drug_class,
        'sub_name': sub_name,
        'schedule': schedule,
        'description': desc,
        'image_url': image_url,
    }


# Use the function
# drug_info = get_drug_info('advil', 'tablet', '200mg')
# drug_info = get_drug_info('adhansia-xr')
# drug_info = get_drug_info('afinitor')
# drug_info = get_drug_info('abacavir-lamivudine')
# drug_info = get_drug_info('Acepromazine')
# drug_info = get_drug_info('Aclaro')
# pp(drug_info)


def get_drug_combinations(drug_id, drug, qty=30, pharmacy_id=3):
    """
    This function retrieves the possible combinations of a specific drug.

    Parameters:
    - drug_id: The ID of the drug for which we are getting the combinations.
    - qty: The quantity of the drug. Defaults to 30.
    - pharmacy_id: The ID of the pharmacy where the drug is sold. Defaults to 3.
    - drug: The name of the drug.

    Returns:
    - This function doesn't return anything but prints out the drug combinations.
    """

    # The base url for the GoodRX API
    url = "https://graph.goodrx.com/"

    # Prepare the request payload by calling the build_coupon_payload function
    payload = build_coupon_payload(drug_id, qty, pharmacy_id)

    # Set the necessary headers for the request
    headers = {
        'authority': 'graph.goodrx.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'apollographql-client-name': 'cwf-client',
        'content-type': 'application/json',
        'goodrx-profile-id': '20918741-0384-4152-bdfc-bcd2ec8d65c4',
        'goodrx-user-id': '64608b1338484ad5828a9b46f7271457',
        'grx-api-client-id': '7c8a864d-21fb-4d14-b243-d7546e9e6cb3',
        'origin': 'https://www.goodrx.com',
        'referer': 'https://www.goodrx.com/',
        'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'x-api-key': 'da2-wrma2xicjjhk7fyokpf3r7nimm',
        'Cookie': 'c=; client=; external_attribution_id=; gclid=; grx_sa=false; grx_unique_id=9f979cedce264f0fbb76e858c299501f; kw=; optimizelyEndUserId=9f979cedce264f0fbb76e858c299501f; _pxhd=PTN7uWD6et7j286zdlfcBu6cfIiOo9I4FW5eqYcsCP/2YCPqyNGYqNRak58V5EY-UaCF2DanyhQL98cycC8iIA==:X-hqESSdIUMrZRhtXtgAsZJEyaQeZVqKyGF2lI0m089wIof6dx26QvORABAfHwhNLd2ckyUNmDjs-YbzhVvMi0dv77/lqon/TN6GJTgh8fY='
    }
    # Send a POST request to the GoodRX API
    response = requests.request("POST", url, headers=headers, data=payload)

    # Print the status code of the response
    print(response.status_code)

    # Parse the response from JSON format to a Python dictionary
    resp = json.loads(response.text)
    # pp(resp)
    # Get the coupon information from the response
    coupon = resp.get('data').get('coupon')
    if coupon == None:
        return None
    # name = resp.
    # Get the drug equivalents from the _analytics and drug_detail fields in the coupon
    label = coupon.get('_analytics').get('drug_detail').get('label')
    display = coupon.get('_analytics').get('drug_detail').get('display')
    drug_eq = json.loads(coupon.get('_analytics').get(
        'drug_detail').get('drug_equivalents'))
    # pp(drug_eq)
    # Get the possible forms of the drug
    # if drug == 'Abatacept':
    # drug_forms = get_case_insensitive(drug_eq, 'Orencia').get('form_sort')
    # else:
    # drug_forms = get_case_insensitive(drug_eq, drug).get('form_sort')
    try:
        generic = get_case_insensitive(drug_eq, drug).get('generic')
    except AttributeError:
        generic = get_case_insensitive(drug_eq, display).get('generic')

    try:
        drug_forms = get_case_insensitive(drug_eq, drug).get('form_sort')
    except AttributeError:
        drug_forms = get_case_insensitive(drug_eq, display).get('form_sort')

    combos = []
    # Iterate over the possible forms of the drug
    for form in drug_forms:
        # print(form)
        # Get the current form information
        # if drug == 'Abatacept':
        # cur_form = get_case_insensitive(drug_eq, 'Orencia').get('forms').get(form)
        # else:
        try:
            cur_form = get_case_insensitive(
                drug_eq, drug).get('forms').get(form)
        except AttributeError:
            cur_form = get_case_insensitive(
                drug_eq, display).get('forms').get(form)
        # Get the possible dosages for the current form
        dosages = cur_form.get('dosage_sort')
        dosages_obj = cur_form.get('dosages')

        # Iterate over the dosages and print the drug id, form, dosage, and quantities
        for dosage, val in dosages_obj.items():
            combos.append({
                'drug_id': val.get('drug_id'),
                'drug_name': drug,
                'generic_status': generic,
                'form': form,
                'dosage': dosage,
                'qtys': val.get('quantities'),
            })
    return combos
    ...


# print(get_drug_combinations(44410, 40, 3, 'everolimus' ))
# print(get_drug_combinations(45330, 60, 3, 'aduhelm' ))
# print(get_drug_combinations(6769, 60, 3, 'advil' ))
# print(get_drug_combinations(66, 60, 3, 'motrin' ))
# print(get_drug_combinations(6769, 60, 3, 'motrin ib' ))
# print(get_drug_combinations(6769, 'advil' ))
# print(get_drug_combinations(37922, 'advil' ))
# print(get_drug_combinations(38895, 'Abbott Freestyle' ))
# print(get_drug_combinations(36985, 'Abatacept' ))
# print(get_drug_combinations(8523, 'Zzzquil' ))
# print(get_drug_combinations(42759, 'Abaloparatide'))
# for id in ['1', '2', '3', '4', '6', '31240', '23357', '85327', '83286']:
#     pp(get_drug_combinations(40829, 'Acetaminophen and Propoxyphene Napsylate', pharmacy_id=id))


def get_prices(drug_id, qty, drug):
    payload = build_drug_price_query_payload(drug_id, drug, qty)

    url = "https://graph.goodrx.com/"

    headers = {
        'authority': 'graph.goodrx.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'apollographql-client-name': 'cwf-client',
        'authorization': 'Bearer dGwWmwdX_fm4Kb0idRZ4vK_gPc5GynMvbM8Nh2xwbvU',
        'content-type': 'application/json',
        'goodrx-profile-id': '20918741-0384-4152-bdfc-bcd2ec8d65c4',
        'goodrx-user-id': '64608b1338484ad5828a9b46f7271457',
        'grx-api-client-id': '7c8a864d-21fb-4d14-b243-d7546e9e6cb3',
        'grx-api-version': '2022-07-26',
        'origin': 'https://www.goodrx.com',
        'referer': 'https://www.goodrx.com/',
        'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'x-api-key': 'da2-wrma2xicjjhk7fyokpf3r7nimm',
        'x-contentful-access-token': 'dGwWmwdX_fm4Kb0idRZ4vK_gPc5GynMvbM8Nh2xwbvU',
        'x-contentful-environment': 'master',
        'x-contentful-graphql': 'false',
        'x-contentful-space': '4f3rgqwzdznj',
        'Cookie': 'c=; client=; external_attribution_id=; gclid=; grx_sa=false; grx_unique_id=9f979cedce264f0fbb76e858c299501f; kw=; optimizelyEndUserId=9f979cedce264f0fbb76e858c299501f; _pxhd=ObpCjYLNrTfGggJfSqwdghl7RZEY9hPJdq2zyHU9uQmkzFNwUtQYZVPDX1F37-X1efElOuu/M1/dDhEXrUSIgw==:587LQ1jXKv2nM0GvXuNKE4w6rHYs-SWsgNxTPnGuNGHTzIJsoX9l1Ah2IwUL3eejqBt5nZVFt5zPrtAxCi11EvAtvhYPdKi1pFOHjFdt9Bo='
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.status_code)
    # pp(response.text)

    resp = json.loads(response.text)
    results = resp.get('data').get('apiV4Prices').get('results')
    # pp(results)
    # for res in results:
    #     pp(res)
    #     print(res.get('prices')[0].get('price'))
    # break
    # return
    prices = []
    if results == None or len(results) == 0:
        # return 'No Prices Found'
        print('No Prices Found')
        return [
            {
                'drug_id': drug_id,
                'drug_name': drug,
                'qty': qty,
                'pharmacy_id': '',
                'pharmacy_name': '',
                'coupon_price': 'No Price Found',
            }
        ]
    print(len(results))
    for res in results:
        if res.get('pharmacy'):
            pharmacy = res.get('pharmacy')
            pharm_id = pharmacy.get('id')
            pharm_name = pharmacy.get('name')
            print(pharm_name)
            # pp(res.get('prices'))
            for price in res.get('prices'):
                if price.get('type') == 'COUPON':
                    coupon_price = round(price.get('price'), 2)
                    prices.append({
                        'drug_id': drug_id,
                        'drug_name': drug,
                        'qty': qty,
                        'pharmacy_id': pharm_id,
                        'pharmacy_name': pharm_name,
                        'price_type': 'COUPON',
                        'price': coupon_price,
                    })
                elif price.get('type') == 'CASH':
                    cash_price = round(price.get('price'), 2)
                    prices.append({
                        'drug_id': drug_id,
                        'drug_name': drug,
                        'qty': qty,
                        'pharmacy_id': pharm_id,
                        'pharmacy_name': pharm_name,
                        'price_type': 'CASH',
                        'price': cash_price,
                    })
                elif price.get('type') == 'GOLD':
                    gold_price = round(price.get('price'), 2)
                    prices.append({
                        'drug_id': drug_id,
                        'drug_name': drug,
                        'qty': qty,
                        'pharmacy_id': pharm_id,
                        'pharmacy_name': pharm_name,
                        'price_type': 'GOLD',
                        'price': gold_price,
                    })
            # print(f'{pharm_name}, {pharm_id}: {coupon_price}')
            # pp(prices)
    return prices


# get_prices(6769, 60, 'advil')
# get_prices(45330, 60, 'aduhelm')
# print(get_prices(36206, 60, 'A-Hydrocort'))
# print(get_prices(36199, 60, 'Abacavir'))
# print()
# get_prices(44550, 1, 'Visbiome')


url = "https://graph.goodrx.com/"

payload = "{\"query\":\"query DrugPriceQuery($drug: String!, $drugId: Int!, $quantity: Int, $quantityFloat: Float, $locationType: PricingGetPrices_LocationType, $locationMetroCode: String, $location: String, $sortType: PricingGetPrices_PriceRowSortType, $attributionParams: AWSJSON, $platform: PricingGetPrices_PlatformType, $includePreferredPharmacyPosDiscount: Boolean, $includeDrugNotices: Boolean = true) {\\n  apiV4Prices(\\n    input: {attribution_params: $attributionParams, location_type: $locationType, location_metro_code: $locationMetroCode, location: $location, drug_id: $drugId, quantity: $quantityFloat, sort_type: $sortType, platform: $platform, include_preferred_pharmacy_pos_discount: $includePreferredPharmacyPosDiscount}\\n  ) {\\n    avg_cash_price\\n    is_maintenance_drug\\n    non_nabp_price {\\n      min_price\\n      max_price\\n      url\\n      _network\\n      pricing_extras\\n      pharmacy_id\\n      __typename\\n    }\\n    results {\\n      est_cash_price\\n      prices {\\n        attestation {\\n          text\\n          alt_price {\\n            url\\n            __typename\\n          }\\n          __typename\\n        }\\n        display_noun\\n        disclaimer\\n        price\\n        type\\n        url\\n        _network\\n        pos_discounts {\\n          coupon_url\\n          discount_campaign_name\\n          final_price\\n          days_supplies {\\n            display\\n            final_price\\n            original_price\\n            __typename\\n          }\\n          __typename\\n        }\\n        __typename\\n      }\\n      pharmacy {\\n        id\\n        name\\n        logo\\n        type\\n        description\\n        extras\\n        distance_mi\\n        popularity_rank\\n        __typename\\n      }\\n      popularity_rank\\n      __typename\\n    }\\n    __typename\\n  }\\n  apiV4DrugNotices(input: {drug_id: $drugId, quantity: $quantity, concept: $drug}) @include(if: $includeDrugNotices) {\\n    notices {\\n      id\\n      name\\n      title\\n      short_desc\\n      link {\\n        text\\n        url\\n        __typename\\n      }\\n      __typename\\n    }\\n    tips {\\n      name\\n      title\\n      short_desc\\n      long_desc\\n      icon_url\\n      link {\\n        text\\n        url\\n        __typename\\n      }\\n      __typename\\n    }\\n    warnings {\\n      id\\n      name\\n      title\\n      short_desc\\n      link {\\n        text\\n        url\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n\",\"variables\":{\"includeDrugNotices\":true,\"attributionParams\":\"{}\",\"sortType\":\"POPULARITY\",\"drug\":\"Visbiome\",\"quantity\":1,\"drugId\":44550,\"platform\":\"DESKTOP\",\"quantityFloat\":1}}"
headers = {
    'authority': 'graph.goodrx.com',
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'apollographql-client-name': 'cwf-client',
    'authorization': 'Bearer dGwWmwdX_fm4Kb0idRZ4vK_gPc5GynMvbM8Nh2xwbvU',
    'content-type': 'application/json',
    'goodrx-profile-id': '20918741-0384-4152-bdfc-bcd2ec8d65c4',
    'goodrx-user-id': '64608b1338484ad5828a9b46f7271457',
    'grx-api-client-id': '7c8a864d-21fb-4d14-b243-d7546e9e6cb3',
    'grx-api-version': '2022-07-26',
    'origin': 'https://www.goodrx.com',
    'referer': 'https://www.goodrx.com/',
    'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'x-api-key': 'da2-wrma2xicjjhk7fyokpf3r7nimm',
    'x-contentful-access-token': 'dGwWmwdX_fm4Kb0idRZ4vK_gPc5GynMvbM8Nh2xwbvU',
    'x-contentful-environment': 'master',
    'x-contentful-graphql': 'false',
    'x-contentful-space': '4f3rgqwzdznj',
    'Cookie': 'c=; client=; external_attribution_id=; gclid=; grx_unique_id=9f979cedce264f0fbb76e858c299501f; kw=; optimizelyEndUserId=9f979cedce264f0fbb76e858c299501f; _pxhd=29sk-d1ZX7oMBv6NTAq3/hMw6XLsb34R9ATw3BPbb0BhYcgNaonlvIBCtviOgPH5ZkAlEIbzPfKYDy8uQxHDOA==:SvbY6Ko1ftty8/oGSkKj9TuzPqKFl63xPnYaRCUrBW4navO3VHRLzfdYFZHUJo6HK3GLRdVikBaofm85TvgSszMppZpq/L8gPZrgMIoMb/Q='
}

# response = requests.request("POST", url, headers=headers, data=payload)

# # print(response.text)
# resp = json.loads(response.text)
# results = resp.get('data').get('apiV4Prices').get('results')


# # print(len(results))
# count = 0
# for res in results:
#     count += 1
#     if res.get('pharmacy') and count == 3:
#         pharmacy = res.get('pharmacy')
#         pharm_id = pharmacy.get('id')
#         pharm_name = pharmacy.get('name')
#         pp(res)
#         break
# pp(res.get('prices'))
# print(pharm_name)
# for price in res.get('prices'):
