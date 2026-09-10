function isValidQueryInput(input) {
  return (
    input !== null &&
    typeof input === 'object' &&
    typeof input.customerId === 'string' &&
    input.customerId.trim().length > 0 &&
    input.location !== null &&
    typeof input.location === 'object' &&
    Number.isFinite(input.location.latitude) &&
    Number.isFinite(input.location.longitude) &&
    Number.isInteger(input.page) &&
    input.page > 0
  );
}

export async function queryNearby(input, deps) {
  if (!isValidQueryInput(input)) {
    return { kind: 'invalid-input' };
  }

  const { customerId, location, page } = input;
  return deps.transport.query({ customerId, location, page });
}

export async function refreshNearby(input, deps) {
  const customerId = input?.customerId;
  const location = await deps.location.read();
  const result = await queryNearby(
    { customerId, location, page: 1 },
    { transport: deps.transport },
  );
  return { location, result };
}
