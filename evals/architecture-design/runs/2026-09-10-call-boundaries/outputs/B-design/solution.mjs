function isValidQueryInput(input) {
  return (
    input != null &&
    typeof input.customerId === 'string' &&
    input.customerId.trim().length > 0 &&
    input.location != null &&
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

  return deps.transport.query({
    customerId: input.customerId,
    location: input.location,
    page: input.page,
  });
}

export async function refreshNearby(input, deps) {
  const location = await deps.location.read();
  const result = await queryNearby(
    { customerId: input?.customerId, location, page: 1 },
    { transport: deps.transport },
  );
  return { location, result };
}
