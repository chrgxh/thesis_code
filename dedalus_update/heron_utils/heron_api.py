import requests
import os

class HeronApi(object):
    # HERON API SETTINGS
    HERON_DOMAIN = os.getenv("HERON_DOMAIN")
    HERON_EMAIL =  os.getenv("HERON_EMAIL")
    HERON_PASS = os.getenv("HERON_PASS")
    HERON_START_DATE = 1623828783  # 2021-06-21T07:32:56.409Z
    HERON_NANO_MUL = 1000000000  # In nanoseconds
    HERON_DATA_API_STEP = 86400 * 30  # 30 days

    def __init__(self):
        # Obtain token during initialization
        self.token = self._get_token()
        if not all([self.HERON_DOMAIN, self.HERON_EMAIL, self.HERON_PASS]):
                raise RuntimeError(
                    "HeronApi: Missing one of HERON_DOMAIN, HERON_EMAIL, HERON_PASS"
                )

    def _get_token(self):
        signin_url = f"https://{self.HERON_DOMAIN}/api/v1/user/signin"
        data = {
            "email": self.HERON_EMAIL,
            "password": self.HERON_PASS
        }
        response = requests.post(signin_url, json=data)
        if response.status_code == 200:
            token = response.json()['token']
        else:
            token = None
        return token
    
    def _refresh_token(self):
        # Implement token refreshing logic here
        self.token = self._get_token()

    def _make_request(self, method, url, **kwargs):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        response = method(url, headers=headers, **kwargs)
        if response.status_code == 401:  # Unauthorized status code
            self._refresh_token()  # Refresh token
            headers['Authorization'] = f'Bearer {self.token}'  # Update authorization header
            response = method(url, headers=headers, **kwargs)
        elif response.status_code in [502, 504]:  # Bad Gateway or Gateway Timeout
            response = method(url, headers=headers, **kwargs)  # Retry the request
        return response  

    # Get Devices
    def _devices(self):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        response = requests.get(
            url=f"https://{self.HERON_DOMAIN}/api/v1/devices",
            headers=headers
        )
        # print("Devices response:")
        # print(response.content)
        return response
    
    # Get Device Details
    def _device_params(self, device_id):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        response = requests.get(
            url=f"https://{self.HERON_DOMAIN}/api/v1/devices/{device_id}",
            headers=headers
        )
        # print("Device params response:")
        # print(response.content)
        return response
    
    # Get Device Measurements
    def _device_data(self, device_id, measurement, time_from, time_to):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        response = requests.get(
            url=f"https://{self.HERON_DOMAIN}/api/v1/devices/{device_id}/data",
            headers=headers,
            params={'time_from': time_from, 'time_to': time_to, 'measurement': measurement}
        )
        # print("Device data response:")
        # print(response.content)
        if response.status_code == 401:  # Unauthorized status code
            # Token expired or invalid, refresh token and retry the request
            self._refresh_token()  # Refresh token
            headers['Authorization'] = f'Bearer {self.token}'  # Update authorization header
            response = requests.get(
                url=f"https://{self.HERON_DOMAIN}/api/v1/devices/{device_id}/data",
                headers=headers,
                params={'time_from': time_from, 'time_to': time_to, 'measurement': measurement}
            )
            # print("Retried Device data response:")
            # print(response.content)
        if response.status_code == 200:
            return response.json()  # Return the JSON data
        else:
            return None  # Return None if the response is not successful