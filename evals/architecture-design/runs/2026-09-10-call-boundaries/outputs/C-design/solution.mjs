function isLocation(value) {
  return value !== null &&
    typeof value === 'object' &&
    Number.isFinite(value.latitude) &&
    Number.isFinite(value.longitude);
}

function isQueryInput(input) {
  return input !== null &&
    typeof input === 'object' &&
    typeof input.customerId === 'string' &&
    input.customerId.trim().length > 0 &&
    isLocation(input.location) &&
    Number.isInteger(input.page) &&
    input.page > 0;
}

export async function queryNearby(input, deps) {
  if (!isQueryInput(input)) {
    return { kind: 'invalid-input' };
  }

  const { customerId, location, page } = input;
  return deps.transport.query({ customerId, location, page });
}

export async function refreshNearby({ customerId, previousLocation }, deps) {
  // A refresh always obtains a new observation; previousLocation is historical.
  const location = await deps.location.read();
  const result = await queryNearby(
    { customerId, location, page: 1 },
    { transport: deps.transport },
  );
  return { location, result };
}
