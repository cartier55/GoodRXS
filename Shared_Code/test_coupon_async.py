from email import errors
import httpx
import json
from build_payload import build_drug_price_query_payload, build_coupon_payload, build_drug_info_payload
from helpers import get_case_insensitive


async def get_prices_httpx(drug_id, qty, drug):
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

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=payload)
        if response.status_code != 200:
            print(response.status_code)

        resp = response.json()
        results = resp.get('data').get('apiV4Prices').get('results')

        prices = []
        if results == None or len(results) == 0:
            # print('No Prices Found')
            return [
                {
                    'drug_id': drug_id,
                    'drug_name': drug,
                    'qty': qty,
                    'pharmacy_id': '',
                    'pharmacy_name': '',
                    'type': 'COUPON',
                    'price': 'No Price Found',
                }
            ]
        for res in results:
            if res.get('pharmacy'):
                pharmacy = res.get('pharmacy')
                pharm_id = pharmacy.get('id')
                pharm_name = pharmacy.get('name')
                for price in res.get('prices'):
                    if price.get('type') == 'COUPON':
                        coupon_price = round(price.get('price'), 2)
                        prices.append({
                            'drug_id': drug_id,
                            'drug_name': drug,
                            'qty': qty,
                            'pharmacy_id': pharm_id,
                            'pharmacy_name': pharm_name,
                            'type': 'COUPON',
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
                            'type': 'CASH',
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
                            'type': 'GOLD',
                            'price': gold_price,
                        })
                        continue

        return prices


async def coupon_query_httpx(drugId, quantity, pharmacyId, drug):
    """
    Function to get the coupon prices and available forms for a drug 
    """

    url = "https://graph.goodrx.com/"

    payload = build_coupon_payload(drugId, quantity, pharmacyId)

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

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=payload)
        if response.status_code != 200:
            print(response.status_code)
        resp = response.json()

        coupon = resp.get('data').get('coupon')

        try:
            adj_info = coupon.get('adjudication_info')
            del adj_info['__typename']
            del adj_info['member_id']
        except AttributeError:
            print('no adjudication info')
            adj_info = {'group_id': '', 'bin': '', 'pcn': ''}

        return [{
            'drug_name': drug,
            'drug_id': drugId,
            'qty': quantity,
            'pharmacy_id': pharmacyId,
            **adj_info,
        }]


async def get_drug_combinations_httpx(drug_id, drug, qty=30, pharmacy_id=3):
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
    url = "https://graph.goodrx.com/"

    payload = build_coupon_payload(drug_id, qty, pharmacy_id)

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

    # Use httpx.AsyncClient() as context manager for sending a POST request
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=payload)

    if response.status_code != 200:
        print(response.status_code)

    # httpx.Response.json() method can be used directly instead of json.loads()
    resp = response.json()

    coupon = resp.get('data').get('coupon')
    if coupon is None:
        return None

    label = coupon.get('_analytics').get('drug_detail').get('label')
    display = coupon.get('_analytics').get('drug_detail').get('display')
    drug_eq = json.loads(coupon.get('_analytics').get(
        'drug_detail').get('drug_equivalents'))

    try:
        generic = get_case_insensitive(drug_eq, drug).get('generic')
    except AttributeError:
        generic = get_case_insensitive(drug_eq, display).get('generic')

    try:
        drug_forms = get_case_insensitive(drug_eq, drug).get('form_sort')
    except AttributeError:
        drug_forms = get_case_insensitive(drug_eq, display).get('form_sort')

    combos = []

    for form in drug_forms:
        try:
            cur_form = get_case_insensitive(
                drug_eq, drug).get('forms').get(form)
        except AttributeError:
            cur_form = get_case_insensitive(
                drug_eq, display).get('forms').get(form)

        dosages = cur_form.get('dosage_sort')
        dosages_obj = cur_form.get('dosages')

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


async def get_drug_info_httpx(drug, form=None, dosage=None):
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
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=payload)

    # If the response status code is not 200 (OK), print the status code
    if response.status_code != 200:
        print(response.status_code)

    # Load the JSON response into a Python dictionary
    resp = response.json()

    if resp.get('errors'):
        errors = resp.get('errors')
        for error in errors:
            return {
                'error':True,
                'err_msg':error.get('message')
                }
        
    # Extract relevant drug information from the response
    index = resp.get('data').get('drugConcept').get('selected_index')
    desc = resp.get('data').get('drugConcept').get('description')
    selected_drug = resp.get('data').get('drugConcept').get('choices')[index]

    image_url = None
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
