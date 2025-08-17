import requests
import pydantic
from typing import TypeVar, Type, Optional, Dict, Any

T = TypeVar('T', bound=pydantic.BaseModel)

async def _call_service(
    service_name: str,
    path: str,
    data_model: Type[T],
    method: str = "GET",
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    timeout: int = 30
) -> T:
    """
    Call a service API endpoint and parse the result into a Pydantic model.

    Args:
        service_name: Name of the service (used to construct the URL)
        path: API endpoint path
        data_model: Pydantic model class to parse the response into
        method: HTTP method (GET, POST, PUT, DELETE, etc.)
        data: Optional data to send in the request body
        timeout: Request timeout in seconds

    Returns:
        Instance of the specified Pydantic model

    Raises:
        requests.RequestException: If the HTTP request fails
        pydantic.ValidationError: If the response cannot be parsed into the model
    """
    # Construct the full URL - adjust this based on your service discovery
    # You might want to use environment variables or a service registry
    base_url = f"http://{service_name}:8000"  # Assuming Docker container names
    url = f"{base_url}{path}"
    if params:
        url += "?" + "&".join(f"{key}={value}" for key, value in params.items())

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        # Make the HTTP request
        if method.upper() in ["POST", "PUT", "PATCH"] and data:
            response = requests.request(
                method=method.upper(),
                url=url,
                json=data,
                headers=headers,
                timeout=timeout
            )
        else:
            response = requests.request(
                method=method.upper(),
                url=url,
                headers=headers,
                timeout=timeout
            )

        # Raise an exception for bad status codes
        response.raise_for_status()

        # Parse the JSON response into the Pydantic model
        response_data = response.json()
        return data_model(**response_data)

    except requests.RequestException as e:
        raise requests.RequestException(f"Failed to call {service_name} at {path}: {str(e)}")
    except pydantic.ValidationError as e:
        raise pydantic.ValidationError(f"Failed to parse response from {service_name}: {str(e)}")


async def service_get(
    service_name: str,
    path: str,
    data_model: Type[T],
    params: Optional[Dict[str, Any]] = None,
    timeout: int = 30
) -> T:
    return await _call_service(
        service_name=service_name,
        path=path,
        data_model=data_model,
        params=params,
        method="GET",
        timeout=timeout
    )


async def service_post(
    service_name: str,
    path: str,
    data_model: Type[T],
    data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    timeout: int = 30
) -> T:
    return await _call_service(
        service_name=service_name,
        path=path,
        data_model=data_model,
        data=data,
        params=params,
        method="POST",
        timeout=timeout
    )


async def service_put(
    service_name: str,
    path: str,
    data_model: Type[T],
    data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    timeout: int = 30
) -> T:
    return await _call_service(
        service_name=service_name,
        path=path,
        data_model=data_model,
        data=data,
        params=params,
        method="PUT",
        timeout=timeout
    )


async def service_patch(
    service_name: str,
    path: str,
    data_model: Type[T],
    data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    timeout: int = 30
) -> T:
    return await _call_service(
        service_name=service_name,
        path=path,
        data_model=data_model,
        data=data,
        params=params,
        method="PATCH",
        timeout=timeout
    )


async def service_delete(
    service_name: str,
    path: str,
    data_model: Type[T],
    params: Optional[Dict[str, Any]] = None,
    timeout: int = 30
) -> T:
    return await _call_service(
        service_name=service_name,
        path=path,
        data_model=data_model,
        params=params,
        method="DELETE",
        timeout=timeout
    )
