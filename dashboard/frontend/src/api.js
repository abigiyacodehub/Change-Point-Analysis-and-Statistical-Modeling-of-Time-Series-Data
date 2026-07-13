// Small fetch wrapper for the Task 3 Flask API. Centralizing this here
// (rather than scattering fetch() calls through components) keeps error
// handling and the base URL configuration in one place.

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:5001";

class ApiRequestError extends Error {
  constructor(message, status) {
    super(message);
    this.name = "ApiRequestError";
    this.status = status;
  }
}

async function request(path) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`);
  } catch (networkErr) {
    throw new ApiRequestError(
      `Could not reach the dashboard API at ${API_BASE_URL}. Is the Flask backend running? (${networkErr.message})`,
      0
    );
  }

  let body;
  try {
    body = await response.json();
  } catch {
    throw new ApiRequestError("Received an invalid (non-JSON) response from the API.", response.status);
  }

  if (!response.ok) {
    throw new ApiRequestError(body.error || `Request failed with status ${response.status}`, response.status);
  }

  return body;
}

function buildQuery(params) {
  const query = new URLSearchParams();
  Object.entries(params || {}).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      query.set(key, value);
    }
  });
  const qs = query.toString();
  return qs ? `?${qs}` : "";
}

export function fetchPrices({ start, end } = {}) {
  return request(`/api/prices${buildQuery({ start, end })}`);
}

export function fetchChangePoints() {
  return request("/api/change-points");
}

export function fetchEvents({ start, end, category } = {}) {
  return request(`/api/events${buildQuery({ start, end, category })}`);
}

export { ApiRequestError };
