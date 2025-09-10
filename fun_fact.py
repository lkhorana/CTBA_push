import requests

def get_unemployment_data():  # for the graph / to get the full dataset
    # BLS API URL
    url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

    # Series ID for US unemployment rate (16+ years, seasonally adjusted)
    payload = {
        "seriesid": ["LNS14000000"],
        "startyear": "2023",
        "endyear": "2024",
        "registrationKey": "9f06a477c6e4414c8badb6c758a76c65"  # Latisha's API key
        #Brandons API key: 62a39a9417d948298af08401d3fba81
        #Latisha API key : 58f92b2321594110917a796b5505c
        #RaKaya API key: 9f06a477c6e4414c8badb6c758a76c65
    }

    # Headers to avoid connection issues
    headers = {
        "Content-type": "application/json",
        "User-Agent": "Graduate Dashboard Project - Latisha Khorana"
    } #provided by chatGPT

    try:
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()  # convert JSON to Python dict

        # Safely get the series list
        series_list = data.get("Results", {}).get("series", [])
        if not series_list or not series_list[0].get("data"):
            return None, None  # No data available

        # Extract month labels and unemployment values
        months = [f"{item['periodName']} {item['year']}" for item in series_list[0]["data"]]
        values = [float(item["value"]) for item in series_list[0]["data"]]

        # Reverse lists so the oldest month comes first
        months.reverse()
        values.reverse()

        return months, values

    except Exception as e:
        print(f"Error fetching API data: {e}")
        return None, None


def get_unemployment_fact():  # the fun-fact / employment fact
    # Get the latest data
    months, values = get_unemployment_data()
    if not months:  # the API didn't return any usable data
        return "We're all out of fun-facts for you today. Rest easy now."

    # Create a simple statement for display
    latest_month = months[-1]  # this is the most recent month
    latest_value = values[-1]

    return f"The unemployment rate in the US, for {latest_month}, was {latest_value}%."
